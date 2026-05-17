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
                input(f"Please complete biometric authentication at {r.url}/persona?inquiry={r.json()['inquiry']} before continuing...")
                self.post(f"{r.url}/persona", json=r.json())
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

        def process_simulation(writer, f, simulation):
            if self.login_expired: return

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
                with ThreadPoolExecutor(max_workers=3) as executor:  # WQ Brain platform limit
                    executor.map(lambda sim: process_simulation(writer, f, sim), data)
        except Exception as e:
            print(f'Issue occurred! {type(e).__name__}: {e}')
        # Return anything not processed (errors/expired) + timed-out for retry
        failed = [sim for sim in data if sim not in self.rows_processed and sim not in self._timed_out]
        return self._timed_out + failed

if __name__ == '__main__':
    TOTAL = len(DATA)
    attempt = 0
    while DATA:
        attempt += 1
        remaining = len(DATA)
        done = TOTAL - remaining
        print(f'\n{"="*50}')
        print(f'  Attempt #{attempt} | {done}/{TOTAL} done | {remaining} queued')
        print(f'{"="*50}')
        DATA = WQSession().simulate(DATA)
        if DATA:
            print(f'\n  ↩ {len(DATA)} timed-out — retrying in 30s...')
            time.sleep(30)
    print(f'\n✅ All {TOTAL} simulations complete!')
