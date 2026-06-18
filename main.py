import csv
import logging
import os
import requests
import json
import sys
import time
from parameters import DATA
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread, Lock

# Concurrent simulation slots. Regular accounts get ~3; consultants get 8-10.
# Override without editing code:  export WQ_CONCURRENCY=N
MAX_WORKERS = int(os.environ.get('WQ_CONCURRENCY', 3))

class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json'):
        super().__init__()
        for handler in list(logging.root.handlers):
            logging.root.removeHandler(handler)
        logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')
        self.json_fn = json_fn
        self.login()
        old_get, old_post = self.get, self.post
        MAX_RETRIES = 5
        def new_get(*args, _retries=0, **kwargs):
            try:
                return old_get(*args, **kwargs)
            except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
                if _retries >= MAX_RETRIES:
                    logging.warning(f'GET failed after {MAX_RETRIES} retries: {e}')
                    raise
                time.sleep(min(2 ** _retries, 30))
                return new_get(*args, _retries=_retries + 1, **kwargs)
        def new_post(*args, _retries=0, **kwargs):
            try:
                return old_post(*args, **kwargs)
            except (requests.exceptions.RequestException, ConnectionError, TimeoutError) as e:
                if _retries >= MAX_RETRIES:
                    logging.warning(f'POST failed after {MAX_RETRIES} retries: {e}')
                    raise
                time.sleep(min(2 ** _retries, 30))
                return new_post(*args, _retries=_retries + 1, **kwargs)
        self.get, self.post = new_get, new_post
        self.login_expired = False
        self.rows_processed = []

    def _load_creds(self) -> tuple[str, str]:
        """Return (email, password). Env vars take priority over credentials.json."""
        email = os.environ.get('WQ_EMAIL')
        password = os.environ.get('WQ_PASSWORD')
        if email and password:
            return email, password
        with open(self.json_fn, 'r') as f:
            creds = json.loads(f.read())
        return creds['email'], creds['password']

    def login(self):
        email, password = self._load_creds()
        self.auth = (email, password)

        while True:  # outer loop: re-requests a fresh link if previous one expires
            r = self.post('https://api.worldquantbrain.com/authentication')
            resp = r.json()

            if 'user' in resp:
                break  # already authenticated

            if 'inquiry' not in resp:
                print(f'WARNING! {resp}')
                input('Press enter to quit...')
                break

            auth_url = f"{r.url}/persona?inquiry={resp['inquiry']}"
            try:
                from notify import notify
                notify(f'Biometric auth required — tap link (expires ~5 min):\n{auth_url}',
                       title='WQ Brain — Action Needed', urgent=True)
            except Exception:
                pass
            print(f"\n{'='*60}")
            print(f"  Biometric auth required. Link sent to LINE.")
            print(f"  URL: {auth_url}")
            print(f"  Checking every 10s — auto-refreshes link before it expires.")
            print(f"{'='*60}\n")

            # Poll every 10s for up to 4 min, then re-request a fresh link.
            # WQ auth links expire in ~5 min; refresh at 4 min to stay ahead.
            deadline = time.time() + 240
            authed = False
            while time.time() < deadline:
                time.sleep(10)
                try:
                    result = self.post(f"{r.url}/persona", json=resp)
                    if 'user' in result.json():
                        logging.info('Biometric auth confirmed — continuing automatically.')
                        authed = True
                        break
                except Exception:
                    pass
                remaining = int(deadline - time.time())
                logging.info(f'Waiting for biometric auth... ({remaining}s before link refresh)')

            if authed:
                break

            # 4 min elapsed — link likely expired; loop back to request a fresh one
            logging.info('Auth link may have expired — requesting a fresh link...')
            try:
                from notify import notify
                notify('Auth link expired — new link incoming now...',
                       title='WQ Brain — Refreshing Auth', urgent=False)
            except Exception:
                pass

        logging.info('Logged in to WQBrain!')

    # Operators/patterns banned from simulation entirely:
    # ts_decay_linear: correlated with Alpha 10 (score change always negative)
    # ts_delta(close: rank(ts_delta(close,N)) momentum leg correlated with Alpha 9
    BANNED_OPS = ('ts_decay_linear', 'ts_delta(close')

    def simulate(self, data):
        banned = [d for d in data
                  if any(op in d.get('code', '') for op in self.BANNED_OPS)]
        if banned:
            print(f'⚠ Dropping {len(banned)} expression(s) using banned ops {self.BANNED_OPS}')
            data = [d for d in data if d not in banned]
        self.rows_processed = []
        self._timed_out = []
        self._lock = Lock()
        total = len(data)
        done_count = [0]  # mutable for closure

        def short_code(alpha):
            # Show last meaningful part of code for clean log
            return alpha.strip()[-60:] if len(alpha.strip()) > 60 else alpha.strip()

        _submit_lock = Lock()
        _submit_count = [0]

        def process_simulation(writer, f, simulation):
            if self.login_expired: return
            # Stagger only the INITIAL burst — after the first wave, workers are
            # naturally desynchronized by simulation runtimes. (Old code slept
            # position*0.8s for EVERY task: expression #150 waited 2 min for nothing.)
            with _submit_lock:
                idx = _submit_count[0]
                _submit_count[0] += 1
            if idx < MAX_WORKERS:
                time.sleep(idx * 0.8)

            alpha = simulation['code'].strip()
            delay = simulation.get('delay', 1)
            universe = simulation.get('universe', 'TOP3000')
            truncation = simulation.get('truncation', 0.1)
            region = simulation.get('region', 'USA')
            decay = simulation.get('decay', 6)
            neutralization = simulation.get('neutralization', 'SUBINDUSTRY').upper()
            pasteurization = simulation.get('pasteurization', 'ON')
            nan = simulation.get('nanHandling', 'OFF')

            label = f"[{universe} d{delay}] {short_code(alpha)}"
            logging.info(f"▶ Simulating: {label}")

            submit_retries = 0
            MAX_SUBMIT_RETRIES = 10
            while True:
                r = None
                try:
                    r = self.post('https://api.worldquantbrain.com/simulations', json={
                        'regular': alpha,
                        'type': 'REGULAR',
                        'settings': {
                            "nanHandling": nan,
                            "instrumentType": "EQUITY",
                            "delay": delay,
                            "universe": universe,
                            "truncation": truncation,
                            "unitHandling": "VERIFY",
                            "pasteurization": pasteurization,
                            "region": region,
                            "language": "FASTEXPR",
                            "decay": decay,
                            "neutralization": neutralization,
                            "visualization": False
                        }
                    })
                    nxt = r.headers['Location']
                    break
                except (requests.exceptions.RequestException, KeyError) as e:
                    # Figure out WHY the platform rejected the POST
                    status = getattr(r, 'status_code', None)
                    try:
                        body = r.json()
                    except Exception:
                        body = {}
                    if 'credentials' in str(body.get('detail', '')):
                        self.login_expired = True
                        return
                    # Rate-limit / concurrency cap → wait and retry, don't skip
                    if status == 429 or 'LIMIT' in str(body).upper():
                        submit_retries += 1
                        if submit_retries > MAX_SUBMIT_RETRIES:
                            logging.info(f'  ⚠ Rate-limited {MAX_SUBMIT_RETRIES}x, giving up: {label}')
                            return
                        try:
                            wait = float(r.headers.get('Retry-After', 0)) or 15.0
                        except Exception:
                            wait = 15.0
                        wait = min(wait * submit_retries, 120)
                        logging.info(f'  ⏳ Rate-limited (429), retry {submit_retries}/{MAX_SUBMIT_RETRIES} in {wait:.0f}s: {label}')
                        time.sleep(wait)
                        continue
                    # Anything else: log status + body so the reason is visible
                    reason = body or repr(e)
                    logging.info(f'  ⚠ Simulation rejected (HTTP {status}), skipping: {label} | {reason}')
                    return

            ok = True
            MAX_WAIT = 10 * 60
            elapsed = 0
            last_pct = -1
            while True:
                r = self.get(nxt).json()
                if 'alpha' in r:
                    alpha_link = r['alpha']
                    break
                try:
                    pct = int(100 * r['progress'])
                    if pct != last_pct:
                        logging.info(f"  ⏳ {pct}% — {label}")
                        last_pct = pct
                except Exception as e:
                    ok = (False, r.get('message', str(e))); break
                time.sleep(10)
                elapsed += 10
                if elapsed >= MAX_WAIT:
                    ok = (False, f'Timeout at {int(100*r.get("progress",0))}%')
                    break

            if ok != True:
                logging.info(f"  ↩ {ok[1]} — will retry: {label}")
                with self._lock:
                    self._timed_out.append(simulation)
                return  # NOT added to rows_processed → will be retried
            else:
                r = self.get(f'https://api.worldquantbrain.com/alphas/{alpha_link}').json()
                passed = 0
                weight_check = 'N/A'
                subsharpe = -1
                for check in r['is']['checks']:
                    passed += check['result'] == 'PASS'
                    if check['name'] == 'CONCENTRATED_WEIGHT':
                        weight_check = check['result']
                    if check['name'] == 'LOW_SUB_UNIVERSE_SHARPE':
                        subsharpe = check['value']
                sharpe = r['is']['sharpe']
                fitness = r['is']['fitness']
                status = '✅ PASS' if passed >= 6 and abs(sharpe) >= 1.25 and abs(fitness) >= 1.0 else f'passed={passed}'
                link = f'https://platform.worldquantbrain.com/alpha/{alpha_link}'
                logging.info(f"  ✔ {status} | sharpe={sharpe} fit={fitness} sub={subsharpe} | {link}")
                row = [
                    passed, sharpe, fitness,
                    round(100 * r['is']['turnover'], 2),
                    weight_check, subsharpe,
                    universe, delay, link, alpha
                ]
                with self._lock:
                    writer.writerow(row)
                    f.flush()
                    self.rows_processed.append(simulation)
                    done_count[0] += 1
                    logging.info(f"  [{done_count[0]}/{total}] done")

        try:
            for handler in logging.root.handlers:
                logging.root.removeHandler(handler)
            from datetime import datetime
            # Orchestrator sets WQ_BATCH_NAME before each run to avoid stale module cache
            _bn = os.environ.get('WQ_BATCH_NAME', '')
            if not _bn:
                try:
                    from parameters import BATCH_NAME as _bn
                except ImportError:
                    _bn = 'agent'
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file = f"data/{_bn}_{ts}.csv"
            log_file = f"data/{_bn}_{ts}.log"
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)
            fmt = logging.Formatter('%(asctime)s  %(message)s', datefmt='%H:%M:%S')
            fh = logging.FileHandler(log_file, encoding='utf-8')
            fh.setFormatter(fmt)
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            logger.addHandler(fh)
            logger.addHandler(sh)
            logging.info(f'Batch: {_bn} | {total} alphas | CSV → {csv_file}')
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['passed', 'sharpe', 'fitness', 'turnover',
                                 'weight', 'subsharpe', 'universe', 'delay', 'link', 'code'])
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    executor.map(lambda sim: process_simulation(writer, f, sim), data)
        except Exception as e:
            print(f'Issue occurred! {type(e).__name__}: {e}')
        # Return anything not processed (errors/expired) + timed-out for retry
        failed = [sim for sim in data if sim not in self.rows_processed and sim not in self._timed_out]
        return self._timed_out + failed

if __name__ == '__main__':
    TOTAL = len(DATA)
    MAX_ATTEMPTS = 2
    for attempt in range(1, MAX_ATTEMPTS + 1):
        remaining = len(DATA)
        done = TOTAL - remaining
        print(f'\n{"="*50}')
        print(f'  Attempt #{attempt}/{MAX_ATTEMPTS} | {done}/{TOTAL} done | {remaining} queued')
        print(f'{"="*50}')
        DATA = WQSession().simulate(DATA)
        if not DATA:
            break
        if attempt < MAX_ATTEMPTS:
            print(f'\n  ↩ {len(DATA)} timed-out — retrying in 30s...')
            time.sleep(30)
        else:
            print(f'\n  ⚠ {len(DATA)} expressions still failed after {MAX_ATTEMPTS} attempts — skipping.')
    print(f'\n✅ Done! {TOTAL - len(DATA)}/{TOTAL} simulations completed.')
