# check_alphas.py
# Auto-fetches corr panel + performance score for alphas in a CSV
# Usage: python3 check_alphas.py [csv_file]
#        If no file given, reads the latest results_*.csv in data/
#
# Output: clean table with Sharpe, Fitness, Max Corr, vs (which alpha), Score Δ, verdict

import json, sys, time, glob, re
import requests
import pandas as pd

# ── CONFIG ──────────────────────────────────────────────────────────────────
CORR_MAX   = 0.70   # hard cutoff
SCORE_PASS = 0      # positive score change = submit

# ── COLOURS ─────────────────────────────────────────────────────────────────
GRN  = '\033[92m'
YEL  = '\033[93m'
RED  = '\033[91m'
RST  = '\033[0m'
BOLD = '\033[1m'

def col(text, c): return f'{c}{text}{RST}'

# ── SESSION ──────────────────────────────────────────────────────────────────
class WQSession(requests.Session):
    def __init__(self, json_fn='credentials.json'):
        super().__init__()
        with open(json_fn, 'r') as f:
            creds = json.loads(f.read())
        self.auth = (creds['email'], creds['password'])
        r = self.post('https://api.worldquantbrain.com/authentication')
        if 'user' not in r.json():
            if 'inquiry' in r.json():
                input(f"Complete biometric auth at {r.url}/persona?inquiry={r.json()['inquiry']} then press Enter...")
                self.post(f"{r.url}/persona", json=r.json())
            else:
                raise RuntimeError(f"Login failed: {r.json()}")
        print(f'✅ Logged in to WQ Brain  (cookies: {dict(self.cookies)})\n')

    def get_team_id(self):
        """Fetch the user's team ID (needed for score endpoint)."""
        r = self.get('https://api.worldquantbrain.com/users/self/teams', params={
            'status': 'ACTIVE',
            'members.self.status': 'ACCEPTED',
            'order': '-dateCreated'
        })
        results = r.json().get('results', [])
        if results:
            return results[0]['id']
        return None

    def _get_with_retry(self, url, retries=15, wait=5.0):
        """GET with retry on empty body or THROTTLED response."""
        for attempt in range(retries):
            r = self.get(url)
            if r.content:
                try:
                    data = r.json()
                    # Explicit THROTTLED signal
                    if isinstance(data, dict) and data.get('detail') == 'THROTTLED':
                        print(f'  [THROTTLED] waiting {wait}s... ({attempt+1}/{retries})')
                        time.sleep(wait)
                        continue
                    return data
                except Exception:
                    pass
            print(f'  [empty] waiting {wait}s... ({attempt+1}/{retries})')
            time.sleep(wait)
        return {}

    def get_alpha(self, alpha_id):
        return self._get_with_retry(f'https://api.worldquantbrain.com/alphas/{alpha_id}')

    def get_corr(self, alpha_id):
        """GET /alphas/{id}/correlations/self — heavily throttled, skip by default."""
        # This endpoint is rate-limited per-alpha; use get_checks() for max corr instead
        return {}

    def get_score(self, alpha_id, team_id):
        """GET /teams/{team_id}/alphas/{id}/before-and-after-performance"""
        return self._get_with_retry(f'https://api.worldquantbrain.com/teams/{team_id}/alphas/{alpha_id}/before-and-after-performance')

    def get_checks(self, alpha_id):
        """GET /alphas/{id}/check — includes SELF_CORRELATION check with max corr value."""
        return self._get_with_retry(f'https://api.worldquantbrain.com/alphas/{alpha_id}/check')


# ── HELPERS ──────────────────────────────────────────────────────────────────
def extract_alpha_id(link):
    """Extract alpha ID from a platform URL or raw ID."""
    m = re.search(r'/alpha/([A-Za-z0-9]+)$', str(link))
    return m.group(1) if m else str(link).strip()

def extract_var(code):
    m = re.search(r'(mdl177[^\s,)]+)', str(code))
    return m.group(1) if m else str(code)[:50]

DEBUG_RAW = False  # set True to print raw API responses for debugging

def parse_corr(corr_data):
    """Return (max_corr, corr_with_name) from /correlations/self response.
    Response shape: {schema: {...}, records: [[id, name, instrType, region, uni, corr, ...], ...]}"""
    if DEBUG_RAW:
        print(f'  [DBG corr raw] type={type(corr_data).__name__}  val={str(corr_data)[:600]}')
    if not corr_data or not isinstance(corr_data, dict):
        return None, None
    records = corr_data.get('records', [])
    if not records:
        return None, None  # throttled / no data — will fall back to /check
    # schema says index 5 = correlation (id, name, instrumentType, region, universe, correlation, ...)
    others = [r for r in records if isinstance(r, list) and len(r) > 5 and abs(r[5]) < 0.9999]
    if not others:
        return 0.0, None
    best = max(others, key=lambda r: abs(r[5]))
    return abs(best[5]), best[1] if len(best) > 1 else '?'

def parse_score(score_data):
    """Return (score_before, score_after, delta) from before-and-after-performance.
    Top-level key 'score' contains {before: int, after: int} — the D1 integer score."""
    if not score_data or not isinstance(score_data, dict):
        return None, None, None
    score = score_data.get('score')
    if isinstance(score, dict):
        before = score.get('before')
        after  = score.get('after')
        if before is not None and after is not None:
            return float(before), float(after), float(after) - float(before)
    return None, None, None

def parse_corr_from_checks(checks_data):
    """Fallback: extract SELF_CORRELATION value from /check response."""
    if DEBUG_RAW:
        print(f'  [DBG checks raw] type={type(checks_data).__name__}  val={str(checks_data)[:400]}')
    if not checks_data or not isinstance(checks_data, dict):
        return None
    for check in checks_data.get('is', {}).get('checks', []):
        if check.get('name') == 'SELF_CORRELATION':
            return check.get('value')
    return None

def parse_subsharpe(alpha_data):
    """Return subsharpe value from alpha IS checks, or None."""
    for check in alpha_data.get('is', {}).get('checks', []):
        if check.get('name') == 'LOW_SUB_UNIVERSE_SHARPE':
            return check.get('value')
    return None


# ── VERDICT LOGIC ────────────────────────────────────────────────────────────
def verdict(corr, score_delta, subsharpe, sharpe, fitness, passed):
    issues = []

    if sharpe < 1.25:  issues.append('sharpe<1.25')
    if fitness < 1.00: issues.append('fitness<1')
    if passed < 6:     issues.append(f'passed={passed}/7')

    if corr is not None and corr >= CORR_MAX:
        issues.append(f'corr={corr:.2f}≥0.70')

    if score_delta is not None and score_delta <= SCORE_PASS:
        issues.append(f'score={score_delta:+.0f}')

    sub_issue = subsharpe is not None and subsharpe < 0.72
    if sub_issue:
        issues.append(f'subsharpe={subsharpe:.2f}')

    if not issues:
        return col('✅ SUBMIT', GRN)
    elif score_delta is not None and score_delta < 0:
        return col(f'❌ DEAD ({", ".join(issues)})', RED)
    else:
        return col(f'⚠️  CHECK ({", ".join(issues)})', YEL)


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    global DEBUG_RAW
    args = [a for a in sys.argv[1:] if a != '--debug']
    if '--debug' in sys.argv:
        DEBUG_RAW = True
        print('🔍 Debug mode ON — printing raw API responses\n')

    # ── Pick CSV ──────────────────────────────────────────────────────────────
    if args:
        csv_path = args[0]
    else:
        files = sorted(glob.glob('data/results_*.csv') + glob.glob('data/api_*.csv'))
        if not files:
            print('No CSV files found in data/. Run main.py first.')
            return
        csv_path = files[-1]
        print(f'Using latest CSV: {csv_path}')

    df = pd.read_csv(csv_path)
    if 'link' not in df.columns:
        print('CSV has no "link" column — cannot proceed.')
        return

    # Only process rows that have a valid link (passed simulations)
    df = df[df['link'].notna() & df['link'].str.startswith('http')].copy()
    if df.empty:
        print('No valid alpha links found in CSV.')
        return

    print(f'Found {len(df)} alphas to check.\n')

    # ── Login ─────────────────────────────────────────────────────────────────
    wq = WQSession()
    team_id = wq.get_team_id()
    if team_id:
        print(f'Team ID: {team_id}\n')
    else:
        print('⚠️  Could not fetch team ID — score check will be skipped\n')

    # ── Check each alpha ──────────────────────────────────────────────────────
    rows = []
    for _, r in df.iterrows():
        alpha_id  = extract_alpha_id(r['link'])
        code      = r.get('code', '')
        var_name  = extract_var(code)
        sharpe    = float(r.get('sharpe', 0))
        fitness   = float(r.get('fitness', 0))
        turnover  = float(r.get('turnover', 0))
        passed    = int(r.get('passed', 0))
        universe  = r.get('universe', 'TOP3000')
        delay     = int(r.get('delay', 1) or 1)

        print(f'Checking {alpha_id}  ({var_name[:40]})')

        score_before = score_after = score_delta = None

        try:
            score_data  = wq.get_score(alpha_id, team_id) if team_id else {}
            time.sleep(2)
            alpha_data  = wq.get_alpha(alpha_id)
            time.sleep(1)
            checks_data = wq.get_checks(alpha_id)
            time.sleep(2)
            corr_data   = {}  # /correlations/self is too throttled; corr comes from /check

            pass  # debug removed

            max_corr, corr_with = parse_corr(corr_data)
            # Fallback: use SELF_CORRELATION check value if /correlations/self gave nothing
            if max_corr is None or max_corr == 0.0:
                chk_corr = parse_corr_from_checks(checks_data)
                if chk_corr is not None:
                    max_corr  = chk_corr
                    corr_with = '(from /check)'

            score_before, score_after, score_delta = parse_score(score_data)
            subsharpe = parse_subsharpe(alpha_data)
            verdict_str = verdict(max_corr, score_delta, subsharpe, sharpe, fitness, passed)

        except Exception as e:
            max_corr = corr_with = subsharpe = None
            verdict_str = col(f'ERROR: {e}', RED)

        rows.append({
            'alpha_id':     alpha_id,
            'var':          var_name,
            'universe':     universe,
            'delay':        delay,
            'sharpe':       sharpe,
            'fitness':      fitness,
            'to':           turnover,
            'passed':       passed,
            'max_corr':     max_corr,
            'corr_with':    corr_with,
            'score_before': score_before,
            'score_after':  score_after,
            'score_delta':  score_delta,
            'subsharpe':    subsharpe,
            'verdict':      verdict_str,
            'verdict_plain': verdict_str,
            'link':         r['link'],
        })

    # ── Print table ───────────────────────────────────────────────────────────
    print()
    print('━' * 110)
    print(f"  {'ALPHA':<10} {'UNI':<8} {'SHP':>5} {'FIT':>5} {'TO':>6} {'P/7':>4} {'CORR':>6} {'VS':>10} {'SCORE':>7}   VERDICT")
    print('━' * 110)

    submittable, dead, check = [], [], []

    for r in rows:
        mc   = f"{r['max_corr']:.2f}" if r['max_corr'] is not None else ' N/A'
        sc   = f"{r['score_delta']:+.0f}" if r['score_delta'] is not None else ' N/A'
        sb   = f"{r['score_before']:.0f}→{r['score_after']:.0f}" if r['score_before'] is not None else ''
        cv   = str(r['corr_with'] or '')[-20:]
        sub  = f"  sub={r['subsharpe']:.2f}" if r['subsharpe'] is not None else ''

        print(f"  {r['alpha_id']:<10} {r['universe']:<8} {r['sharpe']:>5.2f} {r['fitness']:>5.2f} {r['to']:>6.1f}% {r['passed']:>3}/7  corr={mc}  score={sc} ({sb})   {r['verdict']}{sub}")
        print(f"    Var : {r['var']}")
        print(f"    Link: {r['link']}")
        print()

        if '✅' in r['verdict']:   submittable.append(r)
        elif '❌' in r['verdict']: dead.append(r)
        else:                       check.append(r)

    print('━' * 110)
    print(f"\n  Summary:  {col(f'{len(submittable)} SUBMIT', GRN)}  |  {col(f'{len(check)} CHECK', YEL)}  |  {col(f'{len(dead)} DEAD', RED)}\n")

    if submittable:
        print(col('━━ SUBMIT QUEUE (sorted by score) ━━', GRN))
        for r in sorted(submittable, key=lambda x: x['score_delta'] or 0, reverse=True):
            sc = f"{r['score_delta']:+.0f}" if r['score_delta'] is not None else 'N/A'
            print(f"  {col(sc, GRN):>8}  {r['var']}")
            print(f"           {r['link']}")
        print()

    # ── Save enriched CSV ─────────────────────────────────────────────────────
    out_df = pd.DataFrame(rows)
    out_df['verdict_plain'] = out_df['verdict'].apply(lambda v: re.sub(r'\033\[[0-9;]+m', '', v))
    base = csv_path.replace('.csv', '')
    out_path = f"{base}_checked.csv"
    out_df.to_csv(out_path, index=False)
    print(f'Enriched CSV saved: {out_path}')


if __name__ == '__main__':
    main()
