#!/usr/bin/env python3
"""
agent.py — WQ Brain AutoAgent v2
New role: corr-checker + tuning file generator.

Flow:
  1. Watch data/ for new CSVs from completed main.py runs
  2. For each result meeting "promising" thresholds, fetch corr from WQ Brain API
  3. Flag anything with corr < 0.70 as a tuning candidate
  4. Auto-generate parameters_tune_*.py for those candidates
  5. Wait for you to run the tuning file manually

Promising thresholds (any one qualifies):
  - sharpe  >= 0.90
  - fitness >= 0.70
  - passed  >= 5

Submission thresholds (must meet ALL):
  - sharpe  >= 1.25
  - fitness >= 1.00
  - passed  >= 6
  - subsharpe passes (already in passed count)
  - corr    <  0.70

Usage:
  python3 agent.py                  # watch mode — processes new CSVs as they appear
  python3 agent.py <path/to/file.csv>  # one-shot — process a specific CSV now

Ctrl+C to stop.
"""

import os, sys, re, time, json, glob
from datetime import datetime
import requests
import pandas as pd

# ── CONFIG ────────────────────────────────────────────────────────────────────
CREDENTIALS_FILE = 'credentials.json'
LOG_FILE         = 'agent_log.txt'
STATE_FILE       = 'agent_state.json'
DATA_DIR         = 'data'
TUNE_DIR         = '.'           # tuning files written here (alongside other params files)
WATCH_INTERVAL   = 30            # seconds between scans in watch mode

# Promising thresholds — qualifies for corr check (must meet ALL, not any)
SHARPE_PROMISING  = 0.90   # minimum sharpe to bother checking corr
FITNESS_PROMISING = 0.70   # minimum fitness (weak bar — tuning can boost)
PASSED_PROMISING  = 5      # minimum checks passed

# Tuning thresholds — must meet ALL to generate a tune file (stricter than corr check)
# Goal: only tune things that have a real chance of crossing submission bar with tuning
SHARPE_TUNE_MIN   = 0.90   # sharpe must be at least here — tuning rarely adds >0.3
FITNESS_TUNE_MIN  = 0.70   # fitness must be positive and meaningful
SUBSHARPE_TUNE_MIN= 0.30   # subsharpe must show some signal

# Flip threshold — if sharpe ≤ this with a valid alpha, signal is inverted
# Suggest rank() instead of -rank() to reverse direction
# RULE: Only flip after BOTH ts_rank AND ts_zscore have been tried and both are ≤ -1.0
SHARPE_FLIP_MAX   = -1.00  # strong negative signal worth flipping

# Submission thresholds — must meet ALL
SHARPE_MIN    = 1.25
FITNESS_MIN   = 1.00
PASSED_MIN    = 6
CORR_MAX      = 0.70   # above this = corr-dead, skip entirely
CORR_HIGH     = 0.80   # 0.70-0.80 = high but worth tuning (neut/universe may lower it)

# Tuning sweep parameters
TUNE_DECAYS       = [0, 2, 4, 6, 8, 10, 13]
TUNE_TRUNCATIONS  = [0.05, 0.08, 0.10]
TUNE_NEUTRALS     = ['SUBINDUSTRY', 'INDUSTRY', 'MARKET']
TUNE_UNIVERSES    = ['TOP3000', 'TOP500', 'TOP200', 'TOPSP500']
TUNE_WINDOWS      = [252, 504]

# ── LOGGING ───────────────────────────────────────────────────────────────────
def log(msg, also_print=True):
    ts   = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    if also_print:
        print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def banner(title):
    sep = '─' * 64
    log(f'\n{sep}\n  {title}\n{sep}')

# ── WQ BRAIN SESSION ──────────────────────────────────────────────────────────
class WQSession(requests.Session):
    def __init__(self):
        super().__init__()
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.loads(f.read())
        self.auth = (creds['email'], creds['password'])
        r = self.post('https://api.worldquantbrain.com/authentication')
        if 'user' not in r.json():
            if 'inquiry' in r.json():
                input(f"Complete biometric auth at {r.url}/persona?inquiry={r.json()['inquiry']} then press Enter...")
                self.post(f"{r.url}/persona", json=r.json())
            else:
                raise RuntimeError(f'Login failed: {r.json()}')
        log('Logged in to WQ Brain.')
        self.team_id = self.get_team_id()
        if self.team_id:
            log(f'Team ID: {self.team_id}')
        else:
            log('⚠️  Could not fetch team ID — score check will be skipped')

    def _get_with_retry(self, url, retries=3, wait=3.0):
        """GET with retry on empty body only. No throttle wait."""
        for attempt in range(retries):
            r = self.get(url)
            if r.content:
                try:
                    return r.json()
                except Exception:
                    pass
            time.sleep(wait)
        return {}

    def get_corr(self, alpha_id):
        """
        Fetch corr via /alphas/{id}/check.
        Returns float or None if WQ Brain hasn't computed it yet.
        """
        try:
            data = self._get_with_retry(
                f'https://api.worldquantbrain.com/alphas/{alpha_id}/check'
            )
            for check in data.get('is', {}).get('checks', []):
                if check.get('name') == 'SELF_CORRELATION':
                    val = check.get('value')
                    if val is not None:
                        return abs(float(val))
            return None
        except Exception as e:
            log(f'  corr fetch failed for {alpha_id}: {e}')
            return None

    def get_team_id(self):
        """Fetch the user's team ID (needed for score endpoint)."""
        try:
            r = self.get('https://api.worldquantbrain.com/users/self/teams', params={
                'status': 'ACTIVE',
                'members.self.status': 'ACCEPTED',
                'order': '-dateCreated'
            })
            results = r.json().get('results', [])
            if results:
                return results[0]['id']
        except Exception as e:
            log(f'  team_id fetch failed: {e}')
        return None

    def get_score(self, alpha_id, team_id):
        """
        Fetch performance score delta from /teams/{team_id}/alphas/{id}/before-and-after-performance.
        Returns dict with before/after/change, or None if not available.
        The 'change' is the +N shown on the platform performance comparison.
        """
        if not team_id:
            return None
        try:
            data = self._get_with_retry(
                f'https://api.worldquantbrain.com/teams/{team_id}/alphas/{alpha_id}/before-and-after-performance'
            )
            if not isinstance(data, dict):
                return None
            score = data.get('score')
            if isinstance(score, dict):
                before = score.get('before')
                after  = score.get('after')
                if before is not None and after is not None:
                    change = round(float(after) - float(before))
                    return {'before': round(float(before)), 'after': round(float(after)), 'change': change}
            return None
        except Exception as e:
            log(f'  score fetch failed for {alpha_id}: {e}')
            return None

# ── STATE ─────────────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            raw = json.load(f)
        # Migrate old agent.py state format (had 'round', 'already_tested', etc.)
        if 'processed_csvs' not in raw:
            log('Old state format detected — migrating to v2 format.')
            raw = {}
    else:
        raw = {}
    return {
        'processed_csvs':  raw.get('processed_csvs', []),
        'corr_checked':    raw.get('corr_checked', {}),
        'tune_candidates': raw.get('tune_candidates', []),
        'submittable':     raw.get('submittable', []),
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# ── CSV PARSER ────────────────────────────────────────────────────────────────
def extract_alpha_id(link):
    """Extract alpha ID from platform link. Returns None for simulation (FAIL) links."""
    m = re.search(r'worldquantbrain\.com/alpha/([A-Za-z0-9]+)', str(link))
    return m.group(1) if m else None

def extract_field(code):
    """Pull the primary mdl177_* (or other named) field from an expression string."""
    m = re.search(r'(mdl177[^\s,)*\'\"]+)', str(code))
    if m:
        return m.group(1)
    # fallback: any named field with underscores
    for tok in re.findall(r'([a-z][a-z0-9]+(?:_[a-z0-9]+){1,})', str(code)):
        if tok not in {'ts_rank','ts_zscore','ts_delta','ts_mean','ts_std','rank','zscore',
                       'scale','log','abs','min','max','returns','volume','close','vwap','cap'}:
            return tok
    return str(code)[:60]

def detect_wrapper(code):
    """Detect whether expression uses ts_rank or ts_zscore."""
    if 'ts_zscore' in str(code):
        return 'ts_zscore'
    return 'ts_rank'

def flip_code(code):
    """Flip -rank(...) to rank(...) or vice versa."""
    code = str(code).strip()
    if code.startswith('-rank('):
        return code[1:]   # remove leading minus
    if code.startswith('rank('):
        return '-' + code  # add leading minus
    return code

def load_csv(path):
    """Load a results CSV, return DataFrame with alpha_id column added."""
    df = pd.read_csv(path)
    df['alpha_id'] = df['link'].apply(extract_alpha_id)
    df['field']    = df['code'].apply(extract_field)
    df['wrapper']  = df['code'].apply(detect_wrapper)
    return df

def filter_promising(df):
    """Return rows that meet ALL promising thresholds and have a valid alpha_id."""
    mask = (
        (df['sharpe']  >= SHARPE_PROMISING) &
        (df['fitness'] >= FITNESS_PROMISING) &
        (df['passed']  >= PASSED_PROMISING)
    )
    valid = df['alpha_id'].notna()
    return df[mask & valid].copy()

def is_tune_worthy(row):
    """Extra filter before adding to tune candidates — must have real signal."""
    # Allow TOP200 to bypass the subsharpe check since the API returns -1.00
    subsharpe_ok = (float(row.get('subsharpe', 0) or 0) >= SUBSHARPE_TUNE_MIN) or (str(row.get('universe', '')) == 'TOP200')
    
    return (
        float(row.get('sharpe',    0) or 0) >= SHARPE_TUNE_MIN    and
        float(row.get('fitness',   0) or 0) >= FITNESS_TUNE_MIN   and
        subsharpe_ok
    )

def is_submittable(row, score=None):
    metrics_ok = (
        float(row.get('sharpe',  0) or 0) >= SHARPE_MIN  and
        float(row.get('fitness', 0) or 0) >= FITNESS_MIN and
        int(row.get('passed',    0) or 0) >= PASSED_MIN
    )
    if not metrics_ok:
        return False
    # If score is known and negative — permanently reject
    if score is not None and score < 0:
        return False
    return True

# ── TUNING FILE GENERATOR ─────────────────────────────────────────────────────
def diagnose(candidate):
    """
    Identify which thresholds the candidate is failing or close to.
    Returns a set of weakness labels.
    """
    issues = set()
    sharpe    = candidate['sharpe']
    fitness   = candidate['fitness']
    subsharpe = candidate['subsharpe']
    passed    = candidate['passed']

    if sharpe    < SHARPE_MIN:    issues.add('sharpe')
    if fitness   < FITNESS_MIN:   issues.add('fitness')
    if subsharpe < 0.72 and candidate.get('universe') != 'TOP200': issues.add('subsharpe')
    if passed    < PASSED_MIN:    issues.add('passed')

    # Already passing all thresholds — tune to maximize score
    if not issues:
        issues.add('maximize')

    return issues

def build_tune_variants(candidate):
    """
    Diagnosis-driven tuning sweep.
    Each weakness gets targeted axes; 'maximize' gets the full grid.
    Both ts_rank and ts_zscore are always tested (zscore consistently outperforms).
    """
    field  = candidate['field']
    issues = diagnose(candidate)

    rows = []
    def e(field, wrapper, w, uni, dec, trunc, neut):
        return {
            'neutralization': neut,
            'decay':          dec,
            'truncation':     trunc,
            'delay':          1,
            'region':         'USA',
            'universe':       uni,
            'code':           f'-rank({wrapper}({field},{w}))',
        }

    # Always test both wrappers on the baseline settings first
    for wrapper in ['ts_rank', 'ts_zscore']:
        for uni in ['TOP3000', 'TOP500']:
            rows.append(e(field, wrapper, 252, uni, 6, 0.08, 'SUBINDUSTRY'))

    # ── subsharpe weak → lower decay, try MARKET neutralization ──────────────
    if 'subsharpe' in issues or 'maximize' in issues:
        for wrapper in ['ts_rank', 'ts_zscore']:
            for dec in [0, 2, 4]:   # low decay = less smoothing = better subsharpe
                for uni in ['TOP3000', 'TOP500']:
                    rows.append(e(field, wrapper, 252, uni, dec, 0.08, 'SUBINDUSTRY'))
            # MARKET neut removes broad market factor, often lifts subsharpe
            for uni in ['TOP3000', 'TOP500']:
                rows.append(e(field, wrapper, 252, uni, 6, 0.08, 'MARKET'))

    # ── sharpe weak → zscore wrapper, TOP500, higher decay ───────────────────
    if 'sharpe' in issues or 'maximize' in issues:
        for dec in [8, 10, 13]:     # higher decay = more smoothing = higher sharpe
            for uni in ['TOP3000', 'TOP500']:
                rows.append(e(field, 'ts_zscore', 252, uni, dec, 0.08, 'SUBINDUSTRY'))
        # 504w window — longer lookback often boosts sharpe
        for dec in [4, 6, 10]:
            for uni in ['TOP3000', 'TOP500']:
                rows.append(e(field, 'ts_zscore', 504, uni, dec, 0.08, 'SUBINDUSTRY'))

    # ── fitness weak → lower truncation, TOP500, zscore ──────────────────────
    if 'fitness' in issues or 'maximize' in issues:
        for trunc in [0.05, 0.06]:  # lower trunc = more concentrated = higher fitness
            for uni in ['TOP3000', 'TOP500']:
                rows.append(e(field, 'ts_zscore', 252, uni, 4, trunc, 'SUBINDUSTRY'))
                rows.append(e(field, 'ts_rank',   252, uni, 4, trunc, 'SUBINDUSTRY'))

    # ── maximize (already passing) → explore remaining universes + INDUSTRY neut
    if 'maximize' in issues:
        for wrapper in ['ts_rank', 'ts_zscore']:
            for uni in ['TOP200', 'TOPSP500']:
                rows.append(e(field, wrapper, 252, uni, 6, 0.08, 'SUBINDUSTRY'))
            for uni in ['TOP3000', 'TOP500']:
                rows.append(e(field, wrapper, 252, uni, 6, 0.08, 'INDUSTRY'))

    return rows

def write_tune_file(candidates, batch_label):
    """
    Write a parameters_tune_*.py for a list of candidate dicts.
    Each candidate: {field, wrapper, sharpe, fitness, passed, subsharpe, universe, corr}
    """
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(TUNE_DIR, f'parameters_tune_{batch_label}_{ts}.py')

    all_rows = []
    seen     = set()
    for c in candidates:
        for row in build_tune_variants(c):
            key = (row['universe'], row['code'], row['decay'], row['neutralization'], row['truncation'])
            if key not in seen:
                seen.add(key)
                all_rows.append(row)

    lines = [
        f'# {filename}',
        f'# Auto-generated by agent.py — {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# Tuning candidates ({len(candidates)}):',
    ]
    for c in candidates:
        lines.append(
            f'#   {c["field"]} ({c["wrapper"]}) — '
            f'sharpe={c["sharpe"]:.2f} fitness={c["fitness"]:.2f} '
            f'passed={c["passed"]} corr={c["corr"]}'
        )
    lines += [
        '#',
        '# Sweep: decay 0-13 | trunc 0.05-0.10 | neut SUB/IND/MKT | all universes | 252+504w',
        f'# Run: cp {os.path.basename(filename)} parameters.py && python3 main.py',
        f'# ~{len(all_rows)} expressions, ~{int(len(all_rows)*1.5)} min runtime',
        '',
        'from commands import *',
        '',
        f"BATCH_NAME = 'tune_{batch_label}'",
        '',
        'DATA = [',
    ]
    for row in all_rows:
        code = row['code'].replace("'", "\\'")
        lines.append(
            f"    {{'neutralization': '{row['neutralization']}', 'decay': {row['decay']}, "
            f"'truncation': {row['truncation']}, 'delay': 1, 'region': 'USA', "
            f"'universe': '{row['universe']}', 'code': '{code}'}},"
        )
    lines += [
        ']',
        '',
        'print(f"Total expressions queued: {len(DATA)}")',
        f'print("  Tuning: {", ".join(c["field"].split("_")[-1] for c in candidates)}")',
        'print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")',
    ]

    with open(filename, 'w') as f:
        f.write('\n'.join(lines) + '\n')

    return filename, len(all_rows)

# ── CSV PROCESSOR ─────────────────────────────────────────────────────────────
def process_csv(csv_path, session, state):
    banner(f'Processing: {csv_path}')
    df = load_csv(csv_path)
    log(f'  {len(df)} total rows, {(df["alpha_id"].notna()).sum()} valid alphas')

    promising = filter_promising(df)
    log(f'  {len(promising)} promising (sharpe≥{SHARPE_PROMISING} OR fitness≥{FITNESS_PROMISING} OR passed≥{PASSED_PROMISING})')

    if promising.empty:
        log('  Nothing promising — moving on.')
        return

    tune_candidates  = []
    new_submittable  = []
    flip_suggestions = []

    # ── Scan ALL valid alphas for strong negative signals worth flipping ───────
    all_valid = df[df['alpha_id'].notna()].copy()
    for _, row in all_valid.iterrows():
        sharpe = float(row.get('sharpe', 0) or 0)
        if sharpe <= SHARPE_FLIP_MAX:
            flip_suggestions.append({
                'alpha_id': row['alpha_id'],
                'sharpe':   sharpe,
                'fitness':  float(row.get('fitness', 0) or 0),
                'passed':   int(row.get('passed', 0) or 0),
                'universe': str(row.get('universe', '')),
                'code':     str(row.get('code', '')),
                'flipped':  flip_code(str(row.get('code', ''))),
                'link':     str(row.get('link', '')),
            })

    if flip_suggestions:
        log(f'\n  🔄 FLIP CANDIDATES (sharpe ≤ {SHARPE_FLIP_MAX}) — try rank() instead of -rank():')
        for f in flip_suggestions:
            log(f'    sharpe={f["sharpe"]:.2f}  passed={f["passed"]}  {f["universe"]}')
            log(f'    original: {f["code"]}')
            log(f'    flipped:  {f["flipped"]}')
            log(f'    link    : {f["link"]}')

    for _, row in promising.iterrows():
        alpha_id = row['alpha_id']
        field    = row['field']
        wrapper  = row['wrapper']
        sharpe   = float(row.get('sharpe',  0) or 0)
        fitness  = float(row.get('fitness', 0) or 0)
        passed   = int(row.get('passed',    0) or 0)
        subsharpe= float(row.get('subsharpe', 0) or 0)
        universe = str(row.get('universe', ''))
        link     = str(row.get('link', ''))

        log(f'\n  [{alpha_id}] sharpe={sharpe:.2f} fitness={fitness:.2f} '
            f'passed={passed} subsharpe={subsharpe:.2f} | {universe}')
        log(f'    field  : {field}')
        log(f'    link   : {link}')

        # Fetch corr if not already checked
        if alpha_id in state['corr_checked']:
            corr = state['corr_checked'][alpha_id]
            log(f'    corr   : {corr} (cached)')
        else:
            log(f'    corr   : fetching...')
            corr = session.get_corr(alpha_id)
            state['corr_checked'][alpha_id] = corr
            log(f'    corr   : {corr}')

        # Fetch performance score
        score_data = session.get_score(alpha_id, session.team_id)
        if score_data:
            change = score_data['change']
            sign = '+' if change >= 0 else ''
            if score_data['before'] is not None:
                log(f'    score  : {sign}{change} (before={score_data["before"]} → after={score_data["after"]})')
            else:
                log(f'    score  : {sign}{change}')
        else:
            score_data = None
            log(f'    score  : N/A')

        corr_ok      = (corr is not None and corr < CORR_MAX)
        corr_high    = (corr is not None and CORR_MAX <= corr < CORR_HIGH)  # 0.70-0.80: tune, may lower
        corr_dead    = (corr is not None and corr >= CORR_HIGH)             # ≥0.80: skip
        corr_na      = (corr is None)

        # Submittable?
        score_change = score_data['change'] if score_data else None
        score_str = f'+{score_change}' if (score_change is not None and score_change >= 0) else str(score_change) if score_change is not None else 'N/A'

        metrics_pass = is_submittable(row, score=None)  # check IS metrics only first
        score_ok     = (score_change is None or score_change > 0)
        score_dead   = (score_change is not None and score_change < 0)

        if score_dead and metrics_pass:
            log(f'    ❌ NEGATIVE SCORE ({score_str}) — rejected permanently regardless of IS metrics')
        elif is_submittable(row, score=score_change) and corr_ok:
            log(f'    ✅ SUBMITTABLE — sharpe={sharpe:.2f} fitness={fitness:.2f} corr={corr:.3f} score={score_str}')
            new_submittable.append({
                'alpha_id': alpha_id, 'field': field, 'wrapper': wrapper,
                'sharpe': sharpe, 'fitness': fitness, 'passed': passed,
                'subsharpe': subsharpe, 'universe': universe,
                'corr': corr, 'link': link,
                'score': score_change,
            })
        elif metrics_pass and corr_na:
            log(f'    ⚠️  SUBMIT-QUALITY but corr N/A — will still tune, check platform too')
            log(f'    → {link}')
        elif metrics_pass and corr_high:
            log(f'    🔧 HIGH CORR ({corr:.3f}, 0.70-0.80) — tuning may lower it')
        elif corr_dead:
            log(f'    ❌ corr={corr:.3f} ≥ {CORR_HIGH} — corr-dead, skip')
            continue
        elif corr_ok or corr_na or corr_high:
            if is_tune_worthy(row):
                log(f'    🔧 TUNE CANDIDATE — corr={corr} sharpe={sharpe:.2f} fitness={fitness:.2f} subsharpe={subsharpe:.2f}')
            else:
                log(f'    ⬇️  signal too weak to tune (sharpe={sharpe:.2f} fitness={fitness:.2f} subsharpe={subsharpe:.2f}) — skip')

        # Add to tuning if corr is clean, unknown, or high-but-not-dead AND signal is strong enough
        if (corr_ok or corr_na or corr_high) and is_tune_worthy(row):
            c_dict = {
                'field': field, 'wrapper': wrapper,
                'sharpe': sharpe, 'fitness': fitness,
                'passed': passed, 'subsharpe': subsharpe,
                'universe': universe, 'corr': corr,
                'alpha_id': alpha_id, 'link': link,
            }
            issues = diagnose(c_dict)
            log(f'    diagnosis: {", ".join(sorted(issues))}')
            tune_candidates.append(c_dict)

    # Update submittable list
    existing_ids = {s['alpha_id'] for s in state['submittable']}
    for s in new_submittable:
        if s['alpha_id'] not in existing_ids:
            state['submittable'].append(s)

    # ── Export process log to CSV ──────────────────────────────────────────────
    if tune_candidates or new_submittable:
        output_data = []
        for c in tune_candidates:
            c_copy = dict(c)
            c_copy['status'] = 'TUNE'
            output_data.append(c_copy)
        for s in new_submittable:
            s_copy = dict(s)
            s_copy['status'] = 'SUBMITTABLE'
            output_data.append(s_copy)
            
        if output_data:
            out_df = pd.DataFrame(output_data)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            label = os.path.splitext(os.path.basename(csv_path))[0]
            out_csv_path = os.path.join(DATA_DIR, f'evaluated_{label}_{ts}.csv')
            out_df.to_csv(out_csv_path, index=False)
            log(f'\n  [💾] Saved evaluation results to {out_csv_path}')

    # Write flip file if we have flip candidates
    if flip_suggestions:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        label = os.path.splitext(os.path.basename(csv_path))[0]
        flip_file = os.path.join(TUNE_DIR, f'parameters_flip_{label}_{ts}.py')
        lines = [
            f'# parameters_flip_{label}_{ts}.py',
            f'# Auto-generated by agent.py — flipped expressions (rank instead of -rank)',
            f'# These had sharpe ≤ {SHARPE_FLIP_MAX} — strong inverted signal, flip direction',
            f'# Run: cp {os.path.basename(flip_file)} parameters.py && python3 main.py',
            '',
            'from commands import *',
            f"BATCH_NAME = 'flip_{label}'",
            '',
            'BASE = {\'neutralization\': \'SUBINDUSTRY\', \'decay\': 6, \'truncation\': 0.08,',
            '        \'delay\': 1, \'region\': \'USA\', \'universe\': \'TOP3000\'}',
            'B500 = {**BASE, \'universe\': \'TOP500\'}',
            '',
            'DATA = [',
        ]
        seen_flip = set()
        for f in flip_suggestions:
            flipped = f['flipped']
            uni = f['universe']
            if (uni, flipped) not in seen_flip:
                seen_flip.add((uni, flipped))
                code = flipped.replace("'", "\\'")
                base_dict = "B500" if uni == "TOP500" else "BASE"
                lines.append(f"    {{**{base_dict}, 'code': '{code}'}},")
        lines += [
            ']',
            'print(f"Total flipped expressions: {len(DATA)}")',
        ]
        with open(flip_file, 'w') as f:
            f.write('\n'.join(lines) + '\n')
        log(f'\n  🔄 Created {flip_file} for {len(seen_flip)} inverted signals.')

    if tune_candidates:
        batch_label = os.path.splitext(os.path.basename(csv_path))[0]
        tune_file, n_expr = write_tune_file(tune_candidates, batch_label)
        log(f'\n  🔧 Created {tune_file} with {n_expr} variants for {len(tune_candidates)} candidates.')

    state['processed_csvs'].append(csv_path)
    save_state(state)
    log(f'\n  Finished {csv_path}. Added {len(new_submittable)} submittable, {len(tune_candidates)} tuning.')

# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
def main():
    banner('WQ Brain AutoAgent v2')
    log(f'Targeting: Sharpe≥{SHARPE_MIN}, Fitness≥{FITNESS_MIN}, Corr<{CORR_MAX}')

    try:
        session = WQSession()
    except Exception as e:
        log(f'Auth Failed: {e}')
        sys.exit(1)

    state = load_state()

    # If a specific CSV was passed as an argument, run just that
    if len(sys.argv) > 1 and sys.argv[1].endswith('.csv'):
        target_csv = sys.argv[1]
        if not os.path.exists(target_csv):
            log(f'File not found: {target_csv}')
            sys.exit(1)
        process_csv(target_csv, session, state)
        sys.exit(0)

    # Watch mode
    log(f'Watching {DATA_DIR}/ for new CSVs (checking every {WATCH_INTERVAL}s)...')
    try:
        while True:
            csv_files = sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
            # filter out agent's own eval files
            csv_files = [f for f in csv_files if not os.path.basename(f).startswith('evaluated_')]
            
            for csv_path in csv_files:
                if csv_path not in state['processed_csvs']:
                    process_csv(csv_path, session, state)
            time.sleep(WATCH_INTERVAL)
    except KeyboardInterrupt:
        log('\nAgent stopped by user.')

if __name__ == '__main__':
    # Reset state: python3 agent.py --reset
    if '--reset' in sys.argv:
        save_state({
            'processed_csvs': [],
            'corr_checked':   {},
            'tune_candidates': [],
            'submittable':    [],
        })
        print('✅ agent_state.json reset.')

    # Interactive corr entry: python3 agent.py --corr
    # Prompts for each alpha with null corr, you just type the number
    elif '--corr' in sys.argv:
        state = load_state()
        nulls = [(aid, val) for aid, val in state['corr_checked'].items() if val is None]
        if not nulls:
            print('No alphas with missing corr in state.')
        else:
            print(f'Enter corr values for {len(nulls)} alpha(s). Type the number and press Enter. Press Enter to skip.\n')
            for (aid, _) in nulls:
                link = f'https://platform.worldquantbrain.com/alpha/{aid}'
                print(f'  → {link}')
                while True:
                    raw = input(f'  corr for {aid}: ').strip()
                    if raw == '':
                        print('  Skipped.')
                        break
                    try:
                        state['corr_checked'][aid] = float(raw)
                        print(f'  ✅ Saved {float(raw)}\n')
                        break
                    except ValueError:
                        print('  Invalid — enter a number like 0.45')
            save_state(state)
            print('Done. Run agent.py again to reprocess.')

    else:
        main()