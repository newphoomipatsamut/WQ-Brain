#!/usr/bin/env python3
"""
orchestrator.py — WQ Brain Fully Automated Research Loop
=========================================================
Runs the complete alpha discovery pipeline unattended:
  1. Pick next category from priority queue
  2. Generate LLM batch (llm_alpha_generator.py)
  3. Run simulations (main.py)
  4. Parse results + update tracker
  5. If passes found → PAUSE and notify (Performance Comparison must be manual)
  6. If near-misses found → auto-build tuning batch and run
  7. Repeat until all categories exhausted or user stops

Usage:
  python3 orchestrator.py --api-key YOUR_GEMINI_KEY
  python3 orchestrator.py --api-key YOUR_GEMINI_KEY --start-category "Analyst"
  python3 orchestrator.py --api-key YOUR_GEMINI_KEY --dry-run   # plan only, no runs

What requires manual action:
  - Performance Comparison panel check on WQ platform (score change + corr)
  - Alpha submission

Press Ctrl+C at any time to stop gracefully after the current batch finishes.
"""

import argparse
import csv
import glob
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent

# Category priority order — skip Options (IV dead) and Social Media (snt dead)
CATEGORY_PRIORITY = [
    'Fundamental',
    'Analyst',
    'Model',
    'Model - Analyst',
    'Model - Fundamental Scores',
    'Price Volume',
    'Model - Systematic Risk',
    'Sentiment / Analyst',
    'Credit Risk - Raw',
    'Model - Credit Risk',
    'Credit Risk - Rating Prob',
    'Credit Risk - Rating Dist',
    'Credit Risk',
    # Skip: Options - Analytics, Options - Volatility (IV dead)
    # Skip: Social Media, Sentiment (snt_* dead)
    # Skip: News (uncertain, low priority)
]

FIELDS_PER_BATCH = 20
MAX_TUNE_EXPRESSIONS = 50  # Cap tuning batch — fitness tuning generates more variants
TRACKER_CSV = BASE_DIR / 'fields_tracker.csv'
PASSES_LOG  = BASE_DIR / 'passes_to_review.txt'
SESSION_LOG = BASE_DIR / 'orchestrator_log.txt'

# IS thresholds
SHARPE_PASS      = 1.25
FITNESS_PASS     = 1.00
CHECKS_PASS      = 6
SHARPE_NEAR      = 0.90
FITNESS_NEAR     = 0.70
CHECKS_NEAR      = 5

# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg: str, also_print: bool = True):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    if also_print:
        print(line)
    with open(SESSION_LOG, 'a') as f:
        f.write(line + '\n')


def separator(char='═', width=65):
    line = char * width
    log(line)

# ─── Tracker helpers ─────────────────────────────────────────────────────────

def count_untested(category: str) -> int:
    with open(TRACKER_CSV) as f:
        return sum(
            1 for r in csv.DictReader(f)
            if r['category'] == category and not r['status'].strip()
        )


def get_next_category() -> str | None:
    """Return the first category in priority order that still has untested fields."""
    for cat in CATEGORY_PRIORITY:
        n = count_untested(cat)
        if n > 0:
            return cat
    return None


def update_tracker_from_csv(results_csv: Path):
    """Parse a results CSV and update fields_tracker.csv."""
    from alpha_utils import extract_field

    def classify(row):
        try:
            sharpe  = float(row.get('sharpe', 0) or 0)
            fitness = float(row.get('fitness', 0) or 0)
            passed  = int(row.get('passed', 0) or 0)
            link    = str(row.get('link', ''))
        except (ValueError, TypeError):
            return None, None
        if not re.search(r'worldquantbrain\.com/alpha/\w+', link):
            return 'dead', None
        if sharpe >= SHARPE_PASS and fitness >= FITNESS_PASS and passed >= CHECKS_PASS:
            return 'pass', sharpe
        if sharpe >= SHARPE_NEAR and fitness >= FITNESS_NEAR and passed >= CHECKS_NEAR:
            return 'near_miss', sharpe
        return 'tested', sharpe

    field_best = {}
    with open(results_csv) as f:
        for row in csv.DictReader(f):
            field = extract_field(row.get('code', ''))
            if not field:
                continue
            status, sharpe = classify(row)
            if status is None:
                continue
            rank = {'dead':0,'tested':1,'near_miss':2,'pass':3}
            existing = field_best.get(field)
            if existing is None or rank.get(status,0) > rank.get(existing['status'],0):
                field_best[field] = {'status': status, 'sharpe': sharpe,
                                     'row': row}
            elif sharpe and existing['sharpe'] and sharpe > existing['sharpe']:
                field_best[field]['sharpe'] = sharpe
                field_best[field]['row'] = row

    # Write back to tracker
    with open(TRACKER_CSV) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Supports both plain and emoji-prefixed status values
    # Abandoned/Backlog get rank 4 — never overwrite manually curated statuses
    status_rank = {
        '': 0, 'untested': 0, 'UNTESTED': 0,
        'tested': 1, '🟡 Tested: Baseline Failed': 1,
        'dead': 0, '❌ Dead': 0,
        'near_miss': 2, '🟠 Test Soon': 2,
        'pass': 3, '✅ In Use': 3,
        '❌ Abandoned': 4, '⚪ Backlog': 0,
        '🟡 Backlog: Needs Retest': 0,
    }
    updated = 0
    for r in rows:
        result = field_best.get(r['field'])
        if not result:
            continue
        old_rank = status_rank.get(r.get('status', '').strip(), 0)
        new_rank = status_rank.get(result['status'], 0)
        if new_rank > old_rank:
            status_map = {
                'tested':    '🟡 Tested: Baseline Failed',
                'near_miss': '🟠 Test Soon',
                'pass':      '✅ In Use',
                'dead':      '❌ Dead',
            }
            r['status'] = status_map.get(result['status'], r['status'])
            if result['sharpe']:
                r['signal_strength'] = f"{result['sharpe']:.3f}"
            updated += 1

    with open(TRACKER_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return field_best


def parse_passes_and_near_misses(field_best: dict) -> tuple[list, list]:
    """Return (passes, near_misses) from field_best dict."""
    passes     = [(f, v) for f, v in field_best.items() if v['status'] == 'pass']
    near_misses = [(f, v) for f, v in field_best.items() if v['status'] == 'near_miss']
    return passes, near_misses


# ─── Batch generation ────────────────────────────────────────────────────────

def generate_batch(api_key: str, category: str, count: int = FIELDS_PER_BATCH,
                    groq_key: str = None) -> Path | None:
    """Call llm_alpha_generator.py and return the generated parameters file path."""
    log(f"Generating LLM batch: category='{category}', count={count}")
    cmd = [
        sys.executable, str(BASE_DIR / 'llm_alpha_generator.py'),
        '--api-key', api_key,
        '--category', category,
        '--count', str(count),
    ]
    if groq_key:
        cmd.extend(['--groq-key', groq_key])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
    print(result.stdout)
    if result.returncode != 0:
        log(f"ERROR generating batch: {result.stderr}")
        return None

    # Find the most recently created parameters_llm_*.py
    files = sorted(BASE_DIR.glob('parameters_llm_*.py'), key=lambda p: p.stat().st_mtime)
    if not files:
        log("ERROR: No parameters_llm_*.py found after generation")
        return None
    return files[-1]


def _tune_expression(code: str, univ: str, field: str) -> list[tuple[str, str, str]]:
    """
    Generate tuning variants for a single expression based on its template type.
    Returns list of (universe, code, comment) tuples.
    """
    entries = []
    # TOP500 dropped from tuning (0 passes from 145 tests) — always flip to TOP200 or TOP3000
    other_univ = 'TOP3000' if univ == 'TOP200' else 'TOP200'

    # ── ts_rank / ts_zscore / ts_std_dev — tune lookback ─────────────────
    for op in ['ts_rank', 'ts_zscore', 'ts_std_dev', 'ts_mean']:
        m = re.search(rf'{op}\((\w+),\s*(\d+)\)', code)
        if m:
            fname, lb = m.group(1), int(m.group(2))
            for new_lb in [22, 63, 126, 252, 504]:
                if new_lb != lb:
                    new_code = re.sub(rf'{op}\({re.escape(fname)},\s*{lb}\)',
                                      f'{op}({fname}, {new_lb})', code)
                    entries.append((univ, new_code, f'# Tune {op} lb={new_lb}: {fname}'))
            entries.append((other_univ, code, f'# Tune universe {other_univ}: {fname}'))
            break

    # ── ts_decay_linear — tune decay period ──────────────────────────────
    m = re.search(r'ts_decay_linear\((\w+),\s*(\d+)\)', code)
    if m and not entries:
        fname, decay = m.group(1), int(m.group(2))
        for new_d in [10, 15, 21, 30, 40, 60]:
            if new_d != decay:
                new_code = re.sub(rf'ts_decay_linear\({re.escape(fname)},\s*{decay}\)',
                                  f'ts_decay_linear({fname}, {new_d})', code)
                entries.append((univ, new_code, f'# Tune decay={new_d}: {fname}'))
        entries.append((other_univ, code, f'# Tune universe {other_univ}: {fname}'))

    # ── ts_regression — tune lookback + rettype ───────────────────────────
    m = re.search(r'ts_regression\((\w+),\s*ts_step\(1\),\s*(\d+)', code)
    if m and not entries:
        fname, lb = m.group(1), int(m.group(2))
        for new_lb in [63, 126, 252, 504]:
            if new_lb != lb:
                new_code = re.sub(rf'ts_regression\({re.escape(fname)},\s*ts_step\(1\),\s*{lb}',
                                  f'ts_regression({fname}, ts_step(1), {new_lb}', code)
                entries.append((univ, new_code, f'# Tune regression lb={new_lb}: {fname}'))
        # Also try rettype=0 (residual) and rettype=1 (intercept)
        for rt in [0, 1, 6]:
            new_code = re.sub(r'rettype=\d', f'rettype={rt}', code)
            if new_code != code:
                entries.append((univ, new_code, f'# Tune rettype={rt}: {fname}'))
        entries.append((other_univ, code, f'# Tune universe {other_univ}: {fname}'))

    # ── group_rank / group_zscore — tune group argument ───────────────────
    m = re.search(r'group_(?:rank|zscore)\(.*?,\s*(\w+)\)', code)
    if m and not entries:
        current_group = m.group(1)
        for grp in ['sector', 'industry', 'subindustry']:
            if grp != current_group:
                new_code = re.sub(rf',\s*{current_group}\)', f', {grp})', code)
                entries.append((univ, new_code, f'# Tune group={grp}: {field}'))
        entries.append((other_univ, code, f'# Tune universe {other_univ}: {field}'))
        # Also try with hump wrapper
        if 'hump' not in code:
            inner = code[7:] if code.startswith('-rank(') else code
            entries.append((univ, f'-rank(hump({inner})', f'# Tune hump: {field}'))

    # ── ts_corr — tune lookback and second field ──────────────────────────
    m = re.search(r'ts_corr\((\w+),\s*(\w+),\s*(\d+)\)', code)
    if m and not entries:
        fname, field2, lb = m.group(1), m.group(2), int(m.group(3))
        for new_lb in [22, 63, 126]:
            if new_lb != lb:
                new_code = re.sub(rf'ts_corr\({re.escape(fname)},\s*{field2},\s*{lb}\)',
                                  f'ts_corr({fname}, {field2}, {new_lb})', code)
                entries.append((univ, new_code, f'# Tune corr lb={new_lb}: {fname}'))
        # Try alternative second field
        alt = 'returns' if field2 == 'close' else 'close'
        new_code = re.sub(rf'ts_corr\({re.escape(fname)},\s*{field2},', f'ts_corr({fname}, {alt},', code)
        entries.append((univ, new_code, f'# Tune corr vs {alt}: {fname}'))
        entries.append((other_univ, code, f'# Tune universe {other_univ}: {fname}'))

    # ── Fallback: hump + universe flip ───────────────────────────────────
    if not entries:
        entries.append((other_univ, code, f'# Tune universe {other_univ}: {field}'))
        if 'hump' not in code and code.startswith('-rank('):
            entries.append((univ, f'-rank(hump({code[6:]})', f'# Tune hump: {field}'))

    return entries


def _fitness_tune(code: str, univ: str, field: str, fitness: float) -> list[tuple[str, str, str]]:
    """
    Generate tuning variants specifically aimed at fixing fitness < 1.00 (turnover too high).
    Strategies: increase decay, add hump wrapper, switch to TOP200, replace ts_decay_linear
    with ts_rank (lower turnover by design).
    """
    entries = []

    # Strategy 1: Always try TOP200 — smaller universe = lower turnover
    if univ != 'TOP200':
        entries.append(('TOP200', code, f'# Fitness fix TOP200: {field}'))

    # Strategy 2: Add hump() wrapper — smooths signal, reduces turnover
    if 'hump' not in code and code.startswith('-rank('):
        entries.append((univ, f'-rank(hump({code[6:]})', f'# Fitness fix hump: {field}'))
        if univ != 'TOP200':
            entries.append(('TOP200', f'-rank(hump({code[6:]})', f'# Fitness fix hump+TOP200: {field}'))

    # Strategy 3: If using ts_decay_linear, try longer decay periods
    m = re.search(r'ts_decay_linear\((.+?),\s*(\d+)\)', code)
    if m:
        current_decay = int(m.group(2))
        for new_d in [30, 40, 60]:
            if new_d > current_decay:
                new_code = re.sub(r'ts_decay_linear\((.+?),\s*\d+\)',
                                  rf'ts_decay_linear(\1, {new_d})', code)
                entries.append((univ, new_code, f'# Fitness fix decay={new_d}: {field}'))

    # Strategy 4: If using ts_decay_linear template, try pure ts_rank instead
    # ts_rank has structurally lower turnover than ts_decay_linear * momentum
    if 'ts_decay_linear' in code and '* rank(ts_delta' in code:
        # Extract inner field from ts_decay_linear(FIELD, N) * rank(ts_delta(close, M))
        inner_m = re.search(r'ts_decay_linear\((\w+),', code)
        if inner_m:
            fname = inner_m.group(1)
            for lb in [126, 252, 504]:
                entries.append((univ, f'-rank(ts_rank({fname}, {lb}))',
                               f'# Fitness fix ts_rank lb={lb}: {fname}'))
                if univ != 'TOP200':
                    entries.append(('TOP200', f'-rank(ts_rank({fname}, {lb}))',
                                   f'# Fitness fix ts_rank+TOP200 lb={lb}: {fname}'))

    # Strategy 5: If fitness is very close (>= 0.90), try increasing decay in settings
    # The base settings use decay=6. Try decay=10 for reduced turnover.
    if fitness >= 0.90:
        entries.append((univ, code, f'# Fitness fix decay=10: {field}', {'decay': 10}))

    return entries


def build_tuning_batch(passes: list, near_misses: list) -> Path | None:
    """Build a tuning batch for passes and near-misses, handling all template types.
    Now separates fitness-blocked vs sharpe-blocked near-misses for targeted tuning."""
    if not passes and not near_misses:
        return None

    ts = datetime.now().strftime('%m%d_%H%M')
    filename = BASE_DIR / f'parameters_auto_tune_{ts}.py'
    entries = []

    for field, info in passes[:5]:
        row = info.get('row', {})
        code, univ = row.get('code', '').strip(), row.get('universe', 'TOP200')
        if not code:
            continue
        new_entries = _tune_expression(code, univ, field)
        entries.extend(new_entries)

    for field, info in near_misses[:5]:
        row = info.get('row', {})
        code, univ = row.get('code', '').strip(), row.get('universe', 'TOP200')
        if not code:
            continue
        fitness = float(row.get('fitness', 0) or 0)

        if fitness < 1.00:
            # Fitness-blocked: use targeted fitness tuning
            entries.extend(_fitness_tune(code, univ, field, fitness))
        else:
            # Sharpe/checks-blocked: use standard tuning (lookback, universe)
            entries.append(('TOP200', code, f'# Near-miss TOP200: {field}'))
            if 'hump' not in code and code.startswith('-rank('):
                entries.append((univ, f'-rank(hump({code[6:]})', f'# Near-miss hump: {field}'))
            entries.extend(_tune_expression(code, univ, field)[:5])

    # Normalize all entries to 4-tuples: (universe, code, comment, overrides)
    normalized = []
    for e in entries:
        if len(e) == 3:
            normalized.append((e[0], e[1], e[2], {}))
        else:
            normalized.append(e)
    entries = normalized

    # Deduplicate tuning entries
    seen_tune = set()
    deduped_entries = []
    for e in entries:
        key = (e[1], e[0], tuple(sorted(e[3].items())) if e[3] else ())
        if key not in seen_tune:
            seen_tune.add(key)
            deduped_entries.append(e)
    entries = deduped_entries

    if not entries:
        return None

    # Cap tuning batch to prevent runaway simulation time
    if len(entries) > MAX_TUNE_EXPRESSIONS:
        log(f"  Tuning batch capped: {len(entries)} → {MAX_TUNE_EXPRESSIONS} expressions")
        entries = entries[:MAX_TUNE_EXPRESSIONS]

    univ_map = {
        'TOP3000': "BASE",
        'TOP500':  "B500",
        'TOP200':  "B200",
    }

    lines = [
        f'# parameters_auto_tune_{ts}.py',
        f'# Auto-generated tuning batch — {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# {len(passes)} passes + {len(near_misses)} near-misses',
        f'# Run: cp {filename.name} parameters.py && python3 main.py',
        '',
        'from commands import *',
        f"BATCH_NAME = 'auto_tune_{ts}'",
        '',
        "BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}",
        "B500 = {**BASE, 'universe': 'TOP500'}",
        "B200 = {**BASE, 'universe': 'TOP200'}",
        '',
        'DATA = [',
    ]
    for univ, code, comment, overrides in entries:
        var = univ_map.get(univ, 'B200')
        lines.append(f"    {comment}")
        if overrides:
            override_str = ', '.join(f"'{k}': {repr(v)}" for k, v in overrides.items())
            lines.append(f"    {{**{var}, {override_str}, 'code': {repr(code)}}},")
        else:
            lines.append(f"    {{**{var}, 'code': {repr(code)}}},")

    lines += [
        ']',
        '',
        'print(f"Total expressions queued: {len(DATA)}")',
        f'print(f"  Estimated runtime: ~{{len(DATA)*1.5:.0f}} min")',
        '',
    ]

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    log(f"Tuning batch written: {filename.name} ({len(entries)} expressions)")
    return filename


# ─── Simulation runner ───────────────────────────────────────────────────────

# ─── Shared WQ session — authenticate ONCE, reuse across all batches ─────────
_wq_session = None

def _get_session():
    """Get or create the shared WQSession. Only authenticates on first call."""
    global _wq_session
    if _wq_session is None:
        sys.path.insert(0, str(BASE_DIR))
        from main import WQSession
        _wq_session = WQSession()
    return _wq_session


def run_simulation(params_file: Path) -> Path | None:
    """Load params file and run simulation using shared session.
    Returns path to results CSV."""
    log(f"Running: {params_file.name}")

    # Load DATA from the parameters file
    import importlib.util
    spec = importlib.util.spec_from_file_location('params', params_file)
    params_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(params_mod)
    data = params_mod.DATA

    if not data:
        log(f"  No expressions in {params_file.name}, skipping...")
        return None

    session = _get_session()

    # Run simulation with retries (same as main.py __main__)
    total = len(data)
    MAX_ATTEMPTS = 2
    for attempt in range(1, MAX_ATTEMPTS + 1):
        remaining = len(data)
        done = total - remaining
        log(f"  Attempt #{attempt}/{MAX_ATTEMPTS} | {done}/{total} done | {remaining} queued")
        data = session.simulate(data)
        if not data:
            break
        if attempt < MAX_ATTEMPTS:
            log(f"  ↩ {len(data)} timed-out — retrying in 30s...")
            import time as _time
            _time.sleep(30)
        else:
            log(f"  ⚠ {len(data)} expressions still failed after {MAX_ATTEMPTS} attempts — skipping.")
    log(f"  ✅ Done! {total - len(data)}/{total} simulations completed.")

    # Find the CSV that was just created
    all_csvs = sorted(glob.glob(str(BASE_DIR / 'data' / '*.csv')),
                     key=os.path.getmtime)
    return Path(all_csvs[-1]) if all_csvs else None


# ─── Pass notification ────────────────────────────────────────────────────────

def notify_passes(passes: list, results_csv: Path):
    """Print a clear notification and write to passes_to_review.txt."""
    separator('★')
    log(f"  🎉 {len(passes)} PASSING ALPHA(S) FOUND — MANUAL REVIEW NEEDED")
    separator('★')

    # Push notification
    try:
        from notify import notify
        fields = ', '.join(f for f, _ in passes[:3])
        notify(
            f'{len(passes)} alpha(s) passed IS!\nFields: {fields}\nCheck passes_to_review.txt',
            title='WQ Brain — Alpha Passed! 🎉',
            urgent=True,
        )
    except Exception:
        pass

    lines = []
    for field, info in passes:
        row = info.get('row', {})
        sharpe  = info['sharpe']
        fitness = float(row.get('fitness', 0))
        passed  = row.get('passed', '?')
        TO      = row.get('turnover', '?')
        link    = row.get('link', '')
        code    = row.get('code', '')
        univ    = row.get('universe', '')

        msg = (
            f"\n  Field   : {field}\n"
            f"  Expr    : {code}\n"
            f"  Universe: {univ}\n"
            f"  Sharpe  : {sharpe:.2f} | Fitness: {fitness:.2f} | Checks: {passed}/7 | TO: {TO}%\n"
            f"  Link    : {link}\n"
            f"  → Open link, check Performance Comparison panel\n"
            f"  → If score > 0 and corr < 0.70 → SUBMIT\n"
            f"  → If score < 0 or corr > 0.70  → REJECT\n"
        )
        log(msg)
        lines.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {msg}")

    with open(PASSES_LOG, 'a') as f:
        f.write(f'\n{"="*60}\n')
        f.write('\n'.join(lines))

    log(f"  Passes logged to: {PASSES_LOG.name}")


def wait_for_user_confirmation(auto_continue_minutes: int = 30):
    """
    Pause for user to review passes. Auto-continues after auto_continue_minutes
    so the orchestrator never freezes permanently when you're away.
    """
    import select as _select
    log("")
    log(f"  ⏸  Paused — check Performance Comparison panel, then press Enter.")
    log(f"  ⏸  Will auto-continue in {auto_continue_minutes} min if no input.")
    try:
        from notify import notify
        notify(
            f'Alpha passed! Check Performance Comparison panel on WQ Brain.\n'
            f'Orchestrator auto-continues in {auto_continue_minutes} min.',
            title='WQ Brain — Action Needed', urgent=False
        )
    except Exception:
        pass

    import sys, time as _time
    deadline = _time.time() + auto_continue_minutes * 60
    while _time.time() < deadline:
        remaining = int((deadline - _time.time()) / 60)
        try:
            # Non-blocking stdin check (Unix only)
            ready, _, _ = _select.select([sys.stdin], [], [], 5)
            if ready:
                sys.stdin.readline()
                log("  ▶ User confirmed — continuing.")
                return
        except Exception:
            # On Windows or non-interactive, just sleep and auto-continue
            _time.sleep(5)
    log(f"  ▶ Auto-continuing after {auto_continue_minutes} min timeout.")


# ─── Main orchestration loop ─────────────────────────────────────────────────

def run_orchestrator(api_key: str, start_category: str = None, dry_run: bool = False,
                     groq_key: str = None):
    separator()
    log("  WQ Brain Orchestrator — Automated Research Loop")
    log(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  Dry run: {dry_run}")
    separator()

    # If start_category given, rotate the list so it starts there — don't remove anything
    if start_category and start_category in CATEGORY_PRIORITY:
        idx = CATEGORY_PRIORITY.index(start_category)
        CATEGORY_PRIORITY[:] = CATEGORY_PRIORITY[idx:] + CATEGORY_PRIORITY[:idx]
        log(f"  Resuming from: {start_category} (skipped categories moved to end)")

    # Print category queue
    log("  Category queue:")
    for i, cat in enumerate(CATEGORY_PRIORITY, 1):
        n = count_untested(cat)
        if n > 0:
            log(f"    {i}. {cat} ({n} untested)")

    log("")
    skipping = False  # rotation handles start_category, no longer need to skip

    try:
        batch_num = 0
        while True:
            cat = get_next_category()
            if cat is None:
                log("✅ All categories exhausted. Research complete!")
                break


            batch_num += 1
            n_untested = count_untested(cat)
            separator('─')
            log(f"  Batch #{batch_num} | Category: {cat} | Untested: {n_untested}")
            separator('─')

            if dry_run:
                log(f"  [DRY RUN] Would generate {FIELDS_PER_BATCH} fields from '{cat}'")
                log(f"  [DRY RUN] Would run ~{FIELDS_PER_BATCH*4*1.5:.0f} min simulation")
                # Simulate moving through categories for planning
                if n_untested <= FIELDS_PER_BATCH:
                    CATEGORY_PRIORITY.remove(cat)
                continue

            # ── Step 1: Generate batch ────────────────────────────────────
            params_file = generate_batch(api_key, cat, FIELDS_PER_BATCH, groq_key=groq_key)
            if not params_file:
                log(f"Batch generation failed for {cat}, skipping...")
                continue

            # ── Step 2: Run simulation ────────────────────────────────────
            results_csv = run_simulation(params_file)
            if not results_csv:
                log("No results CSV found, skipping analysis...")
                continue
            log(f"Results CSV: {results_csv.name}")

            # ── Step 3: Parse + update tracker + RL performance ──────────
            field_best = update_tracker_from_csv(results_csv)
            passes, near_misses = parse_passes_and_near_misses(field_best)
            try:
                from template_rl import update_from_results
                update_from_results(results_csv, TRACKER_CSV)
            except Exception as e:
                log(f'  [rl] Could not update template performance: {e}')

            # Summary
            status_counts = Counter(v['status'] for v in field_best.values())
            log(f"  Results: {status_counts.get('pass',0)} pass | "
                f"{status_counts.get('near_miss',0)} near-miss | "
                f"{status_counts.get('tested',0)} tested | "
                f"{status_counts.get('dead',0)} dead")

            # ── Step 4: Handle passes ─────────────────────────────────────
            if passes:
                notify_passes(passes, results_csv)

                # Build tuning batch
                tune_file = build_tuning_batch(passes, near_misses)
                if tune_file:
                    log(f"  Running tuning batch: {tune_file.name}")
                    tune_csv = run_simulation(tune_file)
                    if tune_csv:
                        tune_best = update_tracker_from_csv(tune_csv)
                        try:
                            from template_rl import update_from_results
                            update_from_results(tune_csv, TRACKER_CSV)
                        except Exception:
                            pass
                        tune_passes, _ = parse_passes_and_near_misses(tune_best)
                        if tune_passes:
                            log(f"  Tuning found {len(tune_passes)} additional passes!")
                            notify_passes(tune_passes, tune_csv)

                # Pause for manual review
                wait_for_user_confirmation()

            elif near_misses:
                log(f"  {len(near_misses)} near-misses — building quick tuning sweep...")
                tune_file = build_tuning_batch([], near_misses)
                if tune_file:
                    tune_csv = run_simulation(tune_file)
                    if tune_csv:
                        tune_best = update_tracker_from_csv(tune_csv)
                        tune_passes, _ = parse_passes_and_near_misses(tune_best)
                        if tune_passes:
                            notify_passes(tune_passes, tune_csv)
                            wait_for_user_confirmation()

            log("")

    except KeyboardInterrupt:
        log("\n  ⏹ Stopped by user (Ctrl+C). Tracker has been updated.")

    separator()
    log(f"  Session complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  Passes log: {PASSES_LOG}")
    log(f"  Full log:   {SESSION_LOG}")
    separator()


# ─── Retune historical near-misses ───────────────────────────────────────────

def scan_historical_near_misses() -> list[tuple[str, dict]]:
    """Scan all data/*.csv files for near-misses that were never tuned.
    Returns list of (field, info) tuples compatible with build_tuning_batch."""
    from alpha_utils import extract_field

    near_misses = {}  # field → best near-miss row
    for csv_path in sorted(glob.glob(str(BASE_DIR / 'data' / '*.csv'))):
        try:
            with open(csv_path) as f:
                for row in csv.DictReader(f):
                    try:
                        sharpe  = float(row.get('sharpe', 0) or 0)
                        fitness = float(row.get('fitness', 0) or 0)
                        passed  = int(row.get('passed', 0) or 0)
                        link    = str(row.get('link', ''))
                    except (ValueError, TypeError):
                        continue
                    if not re.search(r'worldquantbrain\.com/alpha/\w+', link):
                        continue
                    # Near-miss: sharpe >= 0.90 but didn't pass all three thresholds
                    is_pass = sharpe >= SHARPE_PASS and fitness >= FITNESS_PASS and passed >= CHECKS_PASS
                    is_near = sharpe >= SHARPE_NEAR and fitness >= FITNESS_NEAR and passed >= CHECKS_NEAR
                    if is_near and not is_pass:
                        field = extract_field(row.get('code', ''))
                        if not field:
                            continue
                        existing = near_misses.get(field)
                        if existing is None or sharpe > existing['sharpe']:
                            near_misses[field] = {
                                'status': 'near_miss', 'sharpe': sharpe, 'row': row
                            }
        except Exception:
            pass

    # Sort by sharpe descending — best chances first
    results = sorted(near_misses.items(), key=lambda x: x[1]['sharpe'], reverse=True)
    return results


def run_retune():
    """Scan historical near-misses and build a tuning batch for the best candidates."""
    separator()
    log("  WQ Brain — Retune Historical Near-Misses")
    separator()

    near_misses = scan_historical_near_misses()
    if not near_misses:
        log("  No historical near-misses found.")
        return

    # Categorize by blocker type
    fitness_blocked = [(f, v) for f, v in near_misses
                       if float(v['row'].get('fitness', 0) or 0) < FITNESS_PASS]
    checks_blocked  = [(f, v) for f, v in near_misses
                       if float(v['row'].get('fitness', 0) or 0) >= FITNESS_PASS
                       and int(v['row'].get('passed', 0) or 0) < CHECKS_PASS]
    sharpe_blocked  = [(f, v) for f, v in near_misses
                       if float(v['row'].get('fitness', 0) or 0) >= FITNESS_PASS
                       and int(v['row'].get('passed', 0) or 0) >= CHECKS_PASS]

    log(f"  Found {len(near_misses)} historical near-misses:")
    log(f"    Fitness-blocked (fit < 1.00): {len(fitness_blocked)}")
    log(f"    Checks-blocked  (chk < 6):    {len(checks_blocked)}")
    log(f"    Sharpe-only     (sharpe < 1.25): {len(sharpe_blocked)}")

    # Show top candidates
    log("\n  Top 10 candidates for tuning:")
    for field, info in near_misses[:10]:
        row = info['row']
        log(f"    sharpe={info['sharpe']:.3f} fit={float(row.get('fitness',0)):.2f} "
            f"chk={row.get('passed','?')} univ={row.get('universe','?'):<7} "
            f"{row.get('code','')[:60]}")

    # Build tuning batch — prioritize checks-blocked (closest to passing),
    # then fitness-blocked with highest sharpe
    tune_candidates = checks_blocked[:5] + sharpe_blocked[:5] + fitness_blocked[:10]
    tune_file = build_tuning_batch([], tune_candidates)

    if tune_file:
        log(f"\n  ✅ Tuning batch written: {tune_file.name}")
        log(f"  To run:")
        log(f"    cp {tune_file.name} parameters.py && python3 main.py")
    else:
        log("  Could not build tuning batch.")

    separator()


# ─── Seed alphas mode ───────────────────────────────────────────────────────

def run_seed(category: str = None):
    """Generate and optionally run a batch from curated seed alphas."""
    separator()
    log("  WQ Brain — Seed Alphas (101 Formulaic + Curated)")
    separator()

    try:
        from seed_alphas import get_seeds, generate_seed_batch
    except ImportError:
        log("ERROR: seed_alphas.py not found.")
        return

    seeds = get_seeds(category=category)
    log(f"  Available seeds: {len(seeds)}" + (f" (category: {category})" if category else ""))

    if not seeds:
        log("  No seeds found.")
        return

    batch_file = generate_seed_batch(count=30, universe='TOP3000', category=category)
    if batch_file:
        log(f"\n  Seed batch written: {batch_file.name}")
        log(f"  To run:")
        log(f"    cp {batch_file.name} parameters.py && python3 main.py")

    separator()


# ─── Mutation mode ──────────────────────────────────────────────────────────

def run_mutate(count: int = 40):
    """Generate mutations from passing alphas."""
    separator()
    log("  WQ Brain — Genetic Mutation Engine")
    separator()

    try:
        from mutator import mutate_batch
        from alpha_utils import load_passing_expressions
    except ImportError as e:
        log(f"ERROR: Required module not found: {e}")
        return

    passes = load_passing_expressions(BASE_DIR / 'data')
    if not passes:
        log("  No passing expressions found in data/.")
        log("  Try running seed alphas first: python3 orchestrator.py --seed")
        return

    log(f"  Found {len(passes)} passing expressions.")
    log(f"  Top 5 parents:")
    for p in passes[:5]:
        log(f"    sharpe={p['sharpe']:.2f} {p['universe']:<7} {p['code'][:60]}")

    # Mutate top 10 parents
    batch_file = mutate_batch(passes[:10], count=count, universe='TOP3000')
    if batch_file:
        log(f"\n  Mutation batch written: {batch_file.name}")
        log(f"  To run:")
        log(f"    cp {batch_file.name} parameters.py && python3 main.py")

    separator()


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='WQ Brain automated alpha research orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full loop from beginning
  python3 orchestrator.py --api-key YOUR_GEMINI_KEY

  # Start from a specific category (skip earlier ones)
  python3 orchestrator.py --api-key YOUR_GEMINI_KEY --start-category "Analyst"

  # Plan only — show what would run without actually running
  python3 orchestrator.py --api-key YOUR_GEMINI_KEY --dry-run

  # Retune historical near-misses (no API key needed)
  python3 orchestrator.py --retune

  # Use environment variable instead of flag
  export GEMINI_API_KEY=YOUR_KEY
  python3 orchestrator.py
        """
    )
    parser.add_argument('--api-key', '-k', default=None,
                        help='Gemini API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--groq-key', default=None,
                        help='Groq API key for fallback (or set GROQ_API_KEY env var). Free at console.groq.com')
    parser.add_argument('--start-category', '-s', default=None,
                        help='Skip categories before this one')
    parser.add_argument('--dry-run', action='store_true',
                        help='Plan only — no LLM calls or simulations')
    parser.add_argument('--retune', action='store_true',
                        help='Scan historical near-misses and build a tuning batch')
    parser.add_argument('--seed', action='store_true',
                        help='Run seed alphas from curated 101 Formulaic Alphas database')
    parser.add_argument('--seed-category', default=None,
                        help='Filter seed alphas by category (e.g., price_volume, fundamental)')
    parser.add_argument('--mutate', action='store_true',
                        help='Generate mutations of passing alphas')
    parser.add_argument('--mutate-count', type=int, default=40,
                        help='Number of mutations to generate (default: 40)')
    args = parser.parse_args()

    if args.retune:
        run_retune()
        return

    if args.seed:
        run_seed(args.seed_category)
        return

    if args.mutate:
        run_mutate(args.mutate_count)
        return

    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key and not args.dry_run:
        print("ERROR: No API key. Pass --api-key or set GEMINI_API_KEY env var.")
        sys.exit(1)

    groq_key = args.groq_key or os.environ.get('GROQ_API_KEY')
    run_orchestrator(api_key, args.start_category, args.dry_run, groq_key=groq_key)


if __name__ == '__main__':
    main()
