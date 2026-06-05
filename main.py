import csv
import logging
import requests
import json
import time
from parameters import DATA
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread, Lock

class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json'):
        super().__init__()
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s')
        self.json_fn = json_fn
        self.login()
        old_get, old_post = self.get, self.post
        def new_get(*args, **kwargs):
            try:    return old_get(*args, **kwargs)
            except: return new_get(*args, **kwargs)
        def new_post(*args, **kwargs):
            try:    return old_post(*args, **kwargs)
            except: return new_post(*args, **kwargs)
        self.get, self.post = new_get, new_post
        self.login_expired = False
        self.rows_processed = []

    def login(self):
        with open(self.json_fn, 'r') as f:
            creds = json.loads(f.read())
            email, password = creds['email'], creds['password']
            self.auth = (email, password)
            r = self.post('https://api.worldquantbrain.com/authentication')
        if 'user' not in r.json():
            if 'inquiry' in r.json():
                persona_url = r.url
                inquiry_data = r.json()
                current_auth_url = f"{persona_url}/persona?inquiry={inquiry_data['inquiry']}"

                def _notify_safe(msg, urgent=False):
                    try:
                        from notify import notify
                        notify(msg, title='WQ Brain — Action Needed' if urgent else 'WQ Brain', urgent=urgent)
                    except Exception:
                        pass

                _notify_safe(f'Biometric auth required — complete on your phone, script will auto-continue.\n{current_auth_url}', urgent=True)
                logging.info(f'⏳ Biometric auth needed: {current_auth_url}')
                logging.info('   Complete it on your phone — script will continue automatically...')

                # Poll every 30s for up to 20 attempts (10 min total).
                # On each poll also re-checks authentication — if the link expired,
                # WQ issues a new inquiry automatically, and we send a fresh LINE notification.
                authed = False
                MAX_POLLS = 20
                for attempt in range(1, MAX_POLLS + 1):
                    time.sleep(30)
                    logging.info(f'   Biometric check {attempt}/{MAX_POLLS}...')
                    try:
                        # Try completing the current inquiry
                        check = self.post(f"{persona_url}/persona", json=inquiry_data)
                        if 'user' in check.json():
                            authed = True
                            break
                    except Exception:
                        pass
                    try:
                        # Re-check auth — detects completion OR gets a fresh link if expired
                        recheck = self.post('https://api.worldquantbrain.com/authentication')
                        rj = recheck.json()
                        if 'user' in rj:
                            authed = True
                            break
                        if 'inquiry' in rj:
                            new_auth_url = f"{recheck.url}/persona?inquiry={rj['inquiry']}"
                            if new_auth_url != current_auth_url:
                                # Old link expired — WQ issued a fresh one
                                inquiry_data = rj
                                persona_url = recheck.url
                                current_auth_url = new_auth_url
                                logging.info(f'   🔄 Previous link expired — new link issued')
                                _notify_safe(f'Previous biometric link expired — new link sent:\n{new_auth_url}', urgent=True)
                    except Exception:
                        pass

                if authed:
                    logging.info('✅ Biometric auth completed — continuing automatically!')
                    _notify_safe('Biometric auth done! Simulations resuming.')
                else:
                    # 10 min elapsed, last resort — ask manually
                    logging.info('⚠️  Auth polling timed out (10 min) — please press Enter in terminal.')
                    _notify_safe('⚠️ Biometric auth timed out after 10 min — check terminal.', urgent=True)
                    input(f'Complete biometric at {current_auth_url} then press Enter...')
                    self.post(f"{persona_url}/persona", json=inquiry_data)
            else:
                print(f'WARNING! {r.json()}')
                input('Press enter to quit...')
        logging.info('Logged in to WQBrain!')

    def simulate(self, data):
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
            # Stagger submissions — avoid rate-limiting when all 8 threads fire at once
            with _submit_lock:
                stagger = _submit_count[0] * 0.8  # 0.8s between each submission start
                _submit_count[0] += 1
            if stagger > 0:
                time.sleep(stagger)

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

            while True:
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
                except:
                    try:
                        if 'credentials' in r.json()['detail']:
                            self.login_expired = True
                            return
                    except:
                        logging.info(f'  ⚠ Gateway error, skipping: {label}')
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
                status = '✅ PASS' if passed >= 6 and sharpe >= 1.25 and fitness >= 1.0 else f'passed={passed}'
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
                with ThreadPoolExecutor(max_workers=8) as executor:  # WQ Brain consultant limit
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
