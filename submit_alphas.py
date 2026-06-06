from main import WQSession
import time
import logging
import sys
import pandas as pd

MAX_SUBMIT_POLLS = 60  # 5 min max wait per alpha

def submit(row):
    aid = row.link.split('/')[-1]
    wq.post(f'https://api.worldquantbrain.com/alphas/{aid}/submit')
    logging.info(f'Attempting to submit https://platform.worldquantbrain.com/alpha/{aid}')
    for _ in range(MAX_SUBMIT_POLLS):
        submit_r = wq.get(f'https://api.worldquantbrain.com/alphas/{aid}/submit')
        if submit_r.status_code == 404:
            logging.info('Skipping due to status code 404, alpha is probably already submitted!')
            return False
        if submit_r.content:
            for check in submit_r.json()['is']['checks']:
                if check['name'] == 'SELF_CORRELATION':
                    check['score_before'], check['score_after'] = row.before, row.after
                    logging.info(f'Done! -- {check}')
                    return check['result'] == 'PASS'
            break
        time.sleep(5)
    logging.info(f'Submit polling timed out for {aid}')
    return False

if len(sys.argv) > 1:
    wq = WQSession()
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s: %(message)s', filename=f'data/alpha_submit_result_{int(time.time())}.log')
    for (_, row) in pd.read_csv(sys.argv[1]).sort_values(by='after', ascending=False).iterrows():
        success = submit(row)
        if success: break
else:
    print('Please specify a scraping result CSV filename as a command line argument!')
