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
import contextlib
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

FIELDS_PER_BATCH = 15
MAX_TUNE_EXPRESSIONS = 50  # Cap tuning batch — fitness tuning generates more variants
TRACKER_CSV       = BASE_DIR / 'fields_tracker.csv'
PASSES_LOG        = BASE_DIR / 'passes_to_review.txt'
SESSION_LOG       = BASE_DIR / 'orchestrator_log.txt'
CORR_FAILS_FILE   = BASE_DIR / 'corr_failed_fields.json'
AUTO_KB_FILE      = BASE_DIR / 'knowledge bases' / 'auto_findings.md'

# IS thresholds
SHARPE_PASS      = 1.25
FITNESS_PASS     = 1.00
CHECKS_PASS      = 6
SHARPE_NEAR      = 0.90
FITNESS_NEAR     = 0.70
CHECKS_NEAR      = 5

# Self-correlation ceiling — passes at/above this can't be submitted
CORR_MAX         = 0.70
# Sweep robustness: a pass needs ≥1 sibling variant with |sharpe| ≥ this,
# otherwise it's likely a multiple-comparisons fluke
ROBUST_SHARPE    = 1.00

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


# Bayesian prior for category yield: assume ~3% pass rate until proven otherwise.
# Untested categories score the prior mean (exploration); proven losers (e.g.
# Analyst: 0 passes / 936 tested) sink to the bottom; proven winners rise.
PRIOR_PASSES = 1.0
PRIOR_TESTS  = 30.0


def category_scores() -> dict[str, dict]:
    """Per-category yield stats from the tracker, single pass.
    score = smoothed (passes + 0.5*near_misses) / tested."""
    stats = {cat: {'untested': 0, 'tested': 0, 'passes': 0, 'near': 0}
             for cat in CATEGORY_PRIORITY}
    with open(TRACKER_CSV) as f:
        for r in csv.DictReader(f):
            cat = r.get('category', '')
            if cat not in stats:
                continue
            s = r.get('status', '').strip()
            if not s:
                stats[cat]['untested'] += 1
            else:
                stats[cat]['tested'] += 1
                if s in ('✅ In Use', 'pass'):
                    stats[cat]['passes'] += 1
                elif s in ('🟠 Test Soon', 'near_miss'):
                    stats[cat]['near'] += 1
    for v in stats.values():
        v['score'] = (v['passes'] + 0.5 * v['near'] + PRIOR_PASSES) / \
                     (v['tested'] + PRIOR_TESTS)
    return stats


def get_next_category() -> str | None:
    """Return the eligible category with the highest historical yield score
    that still has untested fields."""
    stats = category_scores()
    candidates = [(v['score'], cat) for cat, v in stats.items()
                  if v['untested'] > 0 and cat in CATEGORY_PRIORITY]
    if not candidates:
        return None
    return max(candidates)[1]


def _write_tracker_atomic(rows: list, fieldnames):
    """Write tracker rows to a temp file then atomically replace the tracker.
    If the process is killed mid-write the original file is never touched."""
    import tempfile
    tmp_fd, tmp_path = tempfile.mkstemp(
        suffix='.tmp', prefix='tracker_', dir=TRACKER_CSV.parent
    )
    try:
        with os.fdopen(tmp_fd, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(tmp_path, TRACKER_CSV)
    except Exception:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_path)
        raise


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
        if abs(sharpe) >= SHARPE_PASS and abs(fitness) >= FITNESS_PASS and passed >= CHECKS_PASS:
            return 'pass', sharpe
        if abs(sharpe) >= SHARPE_NEAR and abs(fitness) >= FITNESS_NEAR and passed >= CHECKS_NEAR:
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

    _write_tracker_atomic(rows, fieldnames)
    return field_best


def parse_passes_and_near_misses(field_best: dict) -> tuple[list, list]:
    """Return (passes, near_misses) from field_best dict."""
    passes     = [(f, v) for f, v in field_best.items() if v['status'] == 'pass']
    near_misses = [(f, v) for f, v in field_best.items() if v['status'] == 'near_miss']
    return passes, near_misses


def parse_all_passes_from_csv(results_csv: Path) -> list:
    """Return ALL passing expressions from a CSV, keyed by unique code.
    Unlike update_tracker_from_csv, does NOT deduplicate by extracted field —
    needed for combination batches where multiple different expressions share
    the same primary field but have distinct second fields and correlations."""
    from alpha_utils import extract_field
    passes = []
    seen_links = set()
    try:
        with open(results_csv, newline='', encoding='utf-8') as f:
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
                if link in seen_links:
                    continue
                if abs(sharpe) >= SHARPE_PASS and abs(fitness) >= FITNESS_PASS and passed >= CHECKS_PASS:
                    seen_links.add(link)
                    code = row.get('code', '').strip()
                    field = extract_field(code) or '?'
                    # Key by code (truncated) so same-field combos aren't collapsed
                    key = code[:80] if code else link
                    passes.append((key, {'status': 'pass', 'sharpe': sharpe, 'row': row,
                                         '_display_field': field}))
    except Exception:
        pass
    return passes


# ─── Near-miss failure analysis ──────────────────────────────────────────────

NEAR_MISS_LOG = BASE_DIR / 'near_miss_log.csv'


def fail_reasons(row: dict) -> list[str]:
    """Which pass thresholds does this row fail? Returns e.g. ['fitness 0.84<1.0']."""
    try:
        sharpe  = float(row.get('sharpe', 0) or 0)
        fitness = float(row.get('fitness', 0) or 0)
        passed  = int(row.get('passed', 0) or 0)
    except (ValueError, TypeError):
        return ['unparseable']
    reasons = []
    if abs(sharpe) < SHARPE_PASS:
        reasons.append(f'sharpe {sharpe:.2f}<{SHARPE_PASS}')
    if abs(fitness) < FITNESS_PASS:
        reasons.append(f'fitness {fitness:.2f}<{FITNESS_PASS}')
    if passed < CHECKS_PASS:
        reasons.append(f'checks {passed}<{CHECKS_PASS}')
    return reasons


def log_near_miss_failures(near_misses: list, category: str):
    """Log WHICH metric blocks each near-miss and append to near_miss_log.csv
    so unconverting patterns become visible over time."""
    if not near_misses:
        return
    write_header = not NEAR_MISS_LOG.exists()
    with open(NEAR_MISS_LOG, 'a', newline='') as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(['timestamp', 'category', 'field', 'sharpe', 'fitness',
                        'checks', 'turnover', 'fail_reasons', 'code'])
        for field, info in near_misses:
            row = info.get('row', {})
            reasons = fail_reasons(row)
            log(f"    near-miss {field}: blocked by [{'; '.join(reasons)}]")
            w.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                category, field,
                row.get('sharpe', ''), row.get('fitness', ''),
                row.get('passed', ''), row.get('turnover', ''),
                '; '.join(reasons),
                row.get('code', ''),
            ])


# ─── Triage pass ─────────────────────────────────────────────────────────────
# Cheap first-pass: 2 best-template expressions per untested field. Only fields
# that show signal (|sharpe| >= TRIAGE_SHARPE) get the expensive full LLM batch.
# 100 fields × 2 sims = 200 sims per triage batch (~3.5 hrs, was 200→400 which stalled).
# TRIAGE_SHARPE=0.75: fields at 0.50-0.74 in triage consistently produce fitness<0.35
# in LLM batch (fundamental returns too slow to overcome 12.5% TO floor in fitness).

TRIAGE_FIELDS = 100
TRIAGE_SHARPE = 0.75

# ts_decay_linear is BANNED from generation: too correlated with submitted
# Alpha 10, Performance Comparison score change consistently negative.
# ts_decay_linear: too correlated with submitted Alpha 10
# ts_delta(close: ts_rank_confirm/med templates use rank(ts_delta(close,N)) as the
#   price-momentum leg — all such expressions are highly correlated with Alpha 9
BANNED_OPS = ('ts_decay_linear', 'ts_delta(close')

TRIAGE_SHAPES = {
    'ts_rank':             '-rank(ts_rank({f}, 252))',
    'hump_ts_rank':        '-rank(hump(ts_rank({f}, 252)))',
    'ts_zscore':           '-rank(ts_zscore({f}, 252))',
    'ts_delta_momentum':   '-rank(ts_rank(ts_delta({f}, 21), 252))',
    'group_rank':          'group_rank({f}, subindustry)',
    'group_zscore':        'group_zscore({f}, subindustry)',
    # ts_rank_confirm / ts_rank_confirm_med REMOVED — both use rank(ts_delta(close,N))
    # which is correlated with Alpha 9 (price momentum). Banned via BANNED_OPS.
    # Double neutralization: strips both industry and market effects → very low self-corr
    'double_neutral':      '-rank(group_neutralize(group_rank(ts_rank({f}, 252), subindustry), sector))',
    # Revision rate: rate of change of the fundamental over 63/126 days
    'revision_rate':       '-rank(ts_rank(ts_delta({f}, 63), 252))',
    'revision_rate_slow':  '-rank(ts_rank(ts_delta({f}, 126), 252))',
}
DEFAULT_TRIAGE = {
    'DAILY':     ['ts_rank', 'ts_delta_momentum'],
    'WEEKLY':    ['ts_rank', 'double_neutral'],
    'QUARTERLY': ['ts_rank', 'revision_rate'],
    'ANNUAL':    ['revision_rate_slow', 'double_neutral'],
    'SLOW':      ['ts_rank', 'double_neutral'],
}


def _best_triage_templates(frequency: str) -> list[str]:
    """Top-2 template shapes for this frequency by historical pass rate (≥10 runs),
    falling back to sensible defaults. Also rotates in unexplored templates once
    established templates are saturated (≥50 runs), so new shapes get bootstrapped."""
    try:
        from template_rl import load_performance, effective_passes, MIN_RUNS_FOR_RECOMMENDATION
        perf = load_performance()
    except Exception:
        perf = {}
        MIN_RUNS_FOR_RECOMMENDATION = 10
    ranked = []
    for key, v in perf.items():
        if not key.endswith(f'_{frequency}') or v.get('runs', 0) < MIN_RUNS_FOR_RECOMMENDATION:
            continue
        tmpl = key[: -len(frequency) - 1]
        if tmpl not in TRIAGE_SHAPES:
            continue
        runs = v['runs']
        eff = effective_passes(v)
        score = (eff / runs,
                 (eff + v.get('near_misses', 0)) / runs,
                 v.get('avg_sharpe', 0))
        ranked.append((score, tmpl))
    ranked.sort(reverse=True)
    templates = [t for _, t in ranked[:2]]

    # Fill remaining slots from DEFAULT_TRIAGE defaults
    for t in DEFAULT_TRIAGE.get(frequency, ['ts_rank', 'double_neutral']):
        if len(templates) >= 2:
            break
        if t not in templates:
            templates.append(t)

    # Exploration: if the 2nd slot is saturated (≥50 runs) and there are shapes
    # with no RL history yet, rotate the 2nd slot to bootstrap the least-tested one.
    # This ensures new templates (ts_rank_confirm, revision_rate, etc.) eventually
    # accumulate enough runs to be fairly evaluated by the RL system.
    if len(templates) == 2:
        second_runs = perf.get(f'{templates[1]}_{frequency}', {}).get('runs', 0)
        if second_runs >= 50:
            preferred = DEFAULT_TRIAGE.get(frequency, [])
            unexplored = sorted(
                (t for t in TRIAGE_SHAPES
                 if t not in templates
                 and t not in BANNED_OPS
                 and perf.get(f'{t}_{frequency}', {}).get('runs', 0) < MIN_RUNS_FOR_RECOMMENDATION),
                key=lambda t: (
                    perf.get(f'{t}_{frequency}', {}).get('runs', 0),
                    0 if t in preferred else 1,  # prefer DEFAULT_TRIAGE picks first
                )
            )
            if unexplored:
                templates[1] = unexplored[0]

    return templates[:2]


def build_triage_batch(category: str, n_fields: int = TRIAGE_FIELDS
                       ) -> tuple[Path | None, list[str]]:
    """Write a triage parameters file. Returns (params_file, field_names)."""
    sys.path.insert(0, str(BASE_DIR))
    from llm_alpha_generator import load_untested_fields
    from template_rl import FREQUENCY_MAP

    fields = load_untested_fields(TRACKER_CSV, category, n_fields)
    if not fields:
        return None, []

    freq = FREQUENCY_MAP.get(category, 'QUARTERLY')
    templates = _best_triage_templates(freq)
    log(f"  Triage templates for {category} ({freq}): {', '.join(templates)}")

    ts = datetime.now().strftime('%m%d_%H%M')
    slug = category.lower().replace(' ', '_').replace('-', '_').replace('/', '_')
    filename = BASE_DIR / f'parameters_triage_{slug}_{ts}.py'

    # Fundamental and Analyst fields compare best within industry peers — use INDUSTRY.
    # All other categories default to SUBINDUSTRY.
    neut = 'INDUSTRY' if category in ('Fundamental', 'Analyst') else 'SUBINDUSTRY'

    lines = [
        f'# parameters_triage_{slug}_{ts}.py',
        f'# Auto-generated TRIAGE batch — {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# {len(fields)} fields × {len(templates)} templates ({", ".join(templates)})',
        f'# Neutralization: {neut} (set by category={category!r})',
        '',
        'from commands import *',
        f"BATCH_NAME = 'triage_{slug}_{ts}'",
        '',
        f"BASE = {{'neutralization': '{neut}', 'decay': 6, 'truncation': 0.08, "
        f"'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}}",
        '',
        'DATA = [',
    ]
    for fd in fields:
        f = fd['field']
        for tmpl in templates:
            code = TRIAGE_SHAPES[tmpl].format(f=f)
            lines.append(f"    # Triage {tmpl}: {f}")
            lines.append(f"    {{**BASE, 'code': {repr(code)}}},")
    lines += [
        ']',
        '',
        'print(f"Total expressions queued: {len(DATA)}")',
        '',
    ]
    with open(filename, 'w') as fh:
        fh.write('\n'.join(lines))

    field_names = [fd['field'] for fd in fields]
    log(f"Triage batch written: {filename.name} "
        f"({len(field_names)} fields, {len(field_names) * len(templates)} expressions)")
    return filename, field_names


def triage_promising(results_csv: Path, field_names: list[str],
                     ) -> tuple[list[str], dict[str, dict]]:
    """Fields whose best triage expression shows |sharpe| >= TRIAGE_SHARPE.

    Returns (promising_fields, best_meta) where best_meta[field] =
    {'sharpe', 'code', 'turnover', 'template'} for ALL fields that had valid results.
    """
    from alpha_utils import extract_field
    from template_rl import extract_template_type
    wanted = set(field_names)
    best: dict[str, dict] = {}
    with open(results_csv) as f:
        for row in csv.DictReader(f):
            field = extract_field(row.get('code', ''))
            if not field or field not in wanted:
                continue
            if not re.search(r'worldquantbrain\.com/alpha/\w+', str(row.get('link', ''))):
                continue
            try:
                sharpe   = abs(float(row.get('sharpe', 0) or 0))
                turnover = float(row.get('turnover', 99) or 99)
            except (ValueError, TypeError):
                continue
            if field not in best or sharpe > best[field]['sharpe']:
                code = row.get('code', '')
                best[field] = {
                    'sharpe':   sharpe,
                    'code':     code,
                    'turnover': turnover,
                    'template': extract_template_type(code),
                }
    promising = sorted((f for f, m in best.items() if m['sharpe'] >= TRIAGE_SHARPE),
                       key=lambda f: -best[f]['sharpe'])
    return promising, best


# Fitness floor: WQ fitness = sharpe × sqrt(|returns| / max(TO/100, 0.125)).
# If TO < 12.5%, denominator is capped at 0.125 — only returns lever remains.
# Fundamental fields with hump template typically have TO < 1%, so fitness is
# structurally bounded regardless of sharpe. No LLM batch can fix this.
CEILING_TEMPLATE = 'hump_ts_rank'
CEILING_TO_THRESHOLD = 1.0  # TO% below which the 12.5% floor dominates


def _mark_fitness_ceiling(field: str, sharpe: float, turnover: float):
    """Mark a fitness-ceiling field as Tested:Baseline-Failed with abandon notes.

    Uses rank-1 status deliberately so winner_clusters() won't treat this field's
    dataset as a cluster attractor — it's a structural dead end, not a near-miss.
    """
    with open(TRACKER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    changed = False
    for r in rows:
        if r.get('field', '').strip() != field:
            continue
        r['status'] = '🟡 Tested: Baseline Failed'
        r['signal_strength'] = f"{sharpe:.3f}"
        r['notes'] = (f"best: sharpe={sharpe:.2f} TO={turnover:.2f}% (hump triage) "
                      f"— fitness ceiling detected")
        r['abandon_reason'] = (
            f"fitness ceiling: hump+TO={turnover:.1f}%<1% hits max(TO/100,0.125) "
            f"floor; denominator locked at 0.125; only returns lever remains; "
            f"fundamental returns too slow to reach fitness>=1.0"
        )
        changed = True
        break
    if changed:
        _write_tracker_atomic(rows, fieldnames)


def _reset_fields_to_untested(fields: list[str]):
    """Reset overflow-promising triage fields back to untested status.

    Fields that showed |sharpe| >= TRIAGE_SHARPE in triage but were cut by the
    FIELDS_PER_BATCH slice limit are marked 'Tested: Baseline Failed' by
    update_tracker_from_csv. That status permanently excludes them from future
    triage since load_untested_fields only fetches empty-status fields.
    Clearing their status here lets the next triage batch pick them up.
    Only clears if status is exactly the triage-assigned value (rank 1) —
    never downgrades a near_miss or pass.
    """
    if not fields:
        return
    with open(TRACKER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    target = set(fields)
    changed = 0
    for r in rows:
        if r.get('field') in target and r.get('status', '').strip() == '🟡 Tested: Baseline Failed':
            r['status'] = ''
            changed += 1
    if changed:
        _write_tracker_atomic(rows, fieldnames)


def _inject_triage_seeds(params_file: Path, seed_exprs: dict[str, dict]):
    """Prepend triage-winning expressions to an LLM batch params file.

    Seeds are inserted first in DATA[] so they run even if the batch is cut
    short by token limits. Each seed is tested in both TOP3000 and TOP200.
    """
    seed_lines: list[str] = []
    for field, meta in seed_exprs.items():
        code = meta['code']
        if any(op in code for op in BANNED_OPS):
            continue
        sharpe   = meta.get('sharpe', 0)
        turnover = meta.get('turnover', 0)
        seed_lines.append(
            f"    # triage seed: {field} (sharpe={sharpe:.2f}, TO={turnover:.1f}%)"
        )
        seed_lines.append(f"    {{**UNIV['TOP3000'], 'code': {repr(code)}}},")
        seed_lines.append(f"    {{**UNIV['TOP200'],  'code': {repr(code)}}},")
    if not seed_lines:
        return
    content = params_file.read_text(encoding='utf-8')
    marker = 'DATA = [\n'
    idx = content.find(marker)
    if idx == -1:
        log(f"  [seeds] DATA = [ not found in {params_file.name} — skipping seed injection")
        return
    insert_at = idx + len(marker)
    header = '    # ── Triage seeds (run first; guaranteed even on truncated batch) ──\n'
    injected = (content[:insert_at] + header
                + '\n'.join(seed_lines) + '\n'
                + content[insert_at:])
    params_file.write_text(injected, encoding='utf-8')
    log(f"  [seeds] Injected {len(seed_exprs)} triage-winning expression(s) into {params_file.name}")


def _recover_on_startup():
    """At startup, apply any results CSVs created in the last 24 h to the tracker.

    If the orchestrator crashed mid-simulation, main.py's incremental flush
    (f.flush() after each row) ensures partial CSVs exist on disk.  This call
    makes those results durable before starting a fresh run.

    Only update_tracker_from_csv is called (idempotent — never downgrades statuses).
    update_from_results is intentionally skipped: it is NOT idempotent and would
    double-count RL statistics for CSVs that were already processed last session.
    """
    cutoff = time.time() - 24 * 3600
    recent = sorted(
        [p for p in glob.glob(str(BASE_DIR / 'data' / '*.csv'))
         if os.path.getmtime(p) >= cutoff],
        key=os.path.getmtime,
    )
    if not recent:
        return
    log(f"  [startup] Scanning {len(recent)} recent CSV(s) for unprocessed results...")
    for csv_path in recent:
        try:
            update_tracker_from_csv(Path(csv_path))
        except Exception as e:
            log(f"  [startup] Could not recover {Path(csv_path).name}: {e}")
    log("  [startup] Recovery scan complete.")


# ─── Exploit mode: mine clusters that already produced winners ───────────────
# Confirmed-signal datasets (e.g. the mdl177 Model-Analyst cluster: 10 passes
# from 261 tests) are far higher-prior than cold exploration. Exploit mode
# tests ONLY untested fields belonging to winner datasets/prefixes.

GENERIC_PREFIXES = {'close', 'open', 'high', 'low', 'volume', 'returns',
                    'vwap', 'adv20', 'cap', 'sharesout', 'split', 'dividend'}


def winner_clusters() -> tuple[dict, dict]:
    """Identify clusters of In Use / Test Soon fields, weighted by winner count.
    Returns (datasets, prefixes) as dicts cluster → n_winners. Prefixes qualify
    if they look like dataset codes (contain a digit, e.g. 'mdl177') or are
    shared by ≥2 winners."""
    datasets, prefix_counts = Counter(), Counter()
    with open(TRACKER_CSV) as f:
        for r in csv.DictReader(f):
            if r.get('status', '').strip() not in ('✅ In Use', '🟠 Test Soon'):
                continue
            ds = r.get('dataset', '').strip().lower()
            if ds:
                datasets[ds] += 1
            pre = r.get('field', '').strip().split('_')[0].lower()
            if pre and pre not in GENERIC_PREFIXES:
                prefix_counts[pre] += 1
    prefixes = {p: n for p, n in prefix_counts.items()
                if any(ch.isdigit() for ch in p) or n >= 2}
    return dict(datasets), prefixes


def untested_fields_in_clusters(datasets: dict, prefixes: dict) -> list[str]:
    """Untested numeric fields in winner clusters, hottest cluster first —
    the mdl177 cluster (10 winners) gets mined before a 1-winner dataset."""
    try:
        from llm_alpha_generator import _is_categorical_field
    except Exception:
        _is_categorical_field = lambda f, d: False
    weighted = []
    with open(TRACKER_CSV) as f:
        for r in csv.DictReader(f):
            if r.get('status', '').strip():
                continue
            field = r.get('field', '').strip()
            if not field:
                continue
            if _is_categorical_field(field, r.get('description', '')):
                continue
            ds = r.get('dataset', '').strip().lower()
            pre = field.split('_')[0].lower()
            weight = max(datasets.get(ds, 0), prefixes.get(pre, 0))
            if weight > 0:
                weighted.append((weight, field))
    weighted.sort(key=lambda x: -x[0])
    return [f for _, f in weighted]


def run_exploit(api_key: str, groq_key: str = None, max_batches: int = 10):
    """Deep-test untested fields in datasets that already produced winners.
    No triage — these fields are high-prior, they get full LLM batches."""
    separator()
    log("  WQ Brain — Exploit Mode: mining winner clusters")
    separator()
    datasets, prefixes = winner_clusters()
    log(f"  Winner datasets: {sorted(datasets) or '—'}")
    log(f"  Winner prefixes: {sorted(prefixes) or '—'}")
    pool = untested_fields_in_clusters(datasets, prefixes)
    log(f"  Untested fields in winner clusters: {len(pool)}")
    if not pool:
        log("  Nothing to exploit — all winner-cluster fields are tested.")
        return

    batch_num = 0
    try:
        while pool and batch_num < max_batches:
            batch_num += 1
            chunk, pool = pool[:FIELDS_PER_BATCH], pool[FIELDS_PER_BATCH:]
            separator('─')
            log(f"  Exploit batch #{batch_num}/{max_batches} | {len(chunk)} fields "
                f"| {len(pool)} remaining in pool")
            separator('─')

            params_file = generate_batch(api_key, None, len(chunk),
                                         groq_key=groq_key, fields=chunk)
            if not params_file:
                log("  Generation failed — stopping exploit run.")
                break
            results_csv = run_simulation(params_file)
            if not results_csv:
                continue
            field_best = update_tracker_from_csv(results_csv)
            try:
                from template_rl import update_from_results
                update_from_results(results_csv, TRACKER_CSV)
            except Exception as e:
                log(f'  [rl] Could not update template performance: {e}')
            passes, near_misses = parse_passes_and_near_misses(field_best)
            status_counts = Counter(v['status'] for v in field_best.values())
            log(f"  Results: {status_counts.get('pass',0)} pass | "
                f"{status_counts.get('near_miss',0)} near-miss | "
                f"{status_counts.get('tested',0)} tested | "
                f"{status_counts.get('dead',0)} dead")
            log_near_miss_failures(near_misses, 'Exploit')

            if passes:
                clean = handle_passes(passes, results_csv)
                tune_file = build_tuning_batch(passes, near_misses)
                if tune_file:
                    tune_csv = run_simulation(tune_file)
                    if tune_csv:
                        tune_best = update_tracker_from_csv(tune_csv)
                        tune_passes, _ = parse_passes_and_near_misses(tune_best)
                        clean += handle_passes(tune_passes, tune_csv)
                if clean:
                    wait_for_user_confirmation()
            log("")
    except KeyboardInterrupt:
        log("\n  ⏹ Exploit run stopped by user. Tracker has been updated.")
    log("  Exploit run complete.")


# ─── Batch generation ────────────────────────────────────────────────────────

def generate_batch(api_key: str, category: str, count: int = FIELDS_PER_BATCH,
                    groq_key: str = None, fields: list[str] = None) -> Path | None:
    """Call llm_alpha_generator.py and return the generated parameters file path."""
    log(f"Generating LLM batch: category='{category or 'exploit/mixed'}', count={count}"
        + (f", restricted to {len(fields)} specified fields" if fields else ""))
    cmd = [
        sys.executable, str(BASE_DIR / 'llm_alpha_generator.py'),
        '--api-key', api_key,
        '--count', str(count),
    ]
    if category:
        cmd.extend(['--category', category])
    if fields:
        cmd.extend(['--fields', ','.join(fields)])
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

    # ── ts_decay_linear — BANNED family: convert to ts_rank instead ──────
    # (too correlated with submitted Alpha 10, score change always negative)
    m = re.search(r'ts_decay_linear\((\w+),\s*(\d+)\)', code)
    if m and not entries:
        fname = m.group(1)
        for lb in [126, 252, 504]:
            entries.append((univ, f'-rank(ts_rank({fname}, {lb}))',
                           f'# Convert banned decay → ts_rank lb={lb}: {fname}'))

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
            inner = code[6:] if code.startswith('-rank(') else code
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


def _fitness_tune(code: str, univ: str, field: str, fitness: float,
                  turnover: float = 99.0) -> list[tuple[str, str, str]]:
    """
    Generate tuning variants aimed at raising fitness >= 1.0.

    Diagnosis first — different root causes need different fixes:
    - High TO (> 12%): hump(), TOP200, higher decay reduce churn
    - Low TO (≤ 12%): turnover is NOT the issue; instead vary lookback,
      decay, truncation, or neutralization to improve year-consistency
    """
    entries = []
    high_to = turnover > 12.0

    # Strategy 1: Always try TOP200 — larger caps tend to have cleaner fundamentals
    if univ != 'TOP200':
        entries.append(('TOP200', code, f'# Fitness fix TOP200: {field}'))

    # Strategy 2: hump() wrapper — ONLY when TO is high (it smooths churn)
    # When TO is already low, hump() just destroys the signal without helping fitness
    if high_to and 'hump' not in code and code.startswith('-rank('):
        entries.append((univ, f'-rank(hump({code[6:]})', f'# Fitness fix hump: {field}'))
        if univ != 'TOP200':
            entries.append(('TOP200', f'-rank(hump({code[6:]})', f'# Fitness fix hump+TOP200: {field}'))

    # Strategy 3: Lookback variation — a different window may be more year-consistent
    # Applies to ts_rank, ts_zscore, ts_std_dev, ts_mean embedded at any level
    for op in ['ts_rank', 'ts_zscore', 'ts_std_dev', 'ts_mean']:
        m = re.search(rf'{op}\((\w+),\s*(\d+)\)', code)
        if m:
            fname, lb = m.group(1), int(m.group(2))
            for new_lb in [126, 252, 504]:
                if new_lb != lb:
                    new_code = re.sub(rf'{op}\({re.escape(fname)},\s*{lb}\)',
                                      f'{op}({fname}, {new_lb})', code)
                    entries.append((univ, new_code, f'# Fitness fix lb={new_lb}: {fname}'))
            break

    # Strategy 4: Decay variation — higher decay = less frequent rebalancing = better year-consistency
    # Previously only triggered at fitness >= 0.90, but useful at any fitness level
    entries.append((univ, code, f'# Fitness fix decay=10: {field}', {'decay': 10}))
    entries.append((univ, code, f'# Fitness fix decay=15: {field}', {'decay': 15}))

    # Strategy 5: Truncation variation — tighter cap reduces outlier impact on fitness
    entries.append((univ, code, f'# Fitness fix trunc=0.05: {field}', {'truncation': 0.05}))

    # Strategy 6: double_neutral — adds sector neutralization for tighter risk control
    # Applies when expression uses group_rank/group_zscore with an industry group
    m_grp = re.search(r'(group_(?:rank|zscore)\(.*?(?:industry|subindustry|sector)\))', code)
    if m_grp and 'group_neutralize' not in code and code.startswith('-rank('):
        inner = code[6:]  # strip leading -rank(
        dn_code = f'-rank(group_neutralize({inner}, sector))'
        entries.append((univ, dn_code, f'# Fitness fix double_neutral: {field}'))

    # Strategy 7 (legacy): ts_decay_linear → ts_rank conversion (banned family)
    if 'ts_decay_linear' in code and '* rank(ts_delta' in code:
        inner_m = re.search(r'ts_decay_linear\((\w+),', code)
        if inner_m:
            fname = inner_m.group(1)
            for lb in [126, 252, 504]:
                entries.append((univ, f'-rank(ts_rank({fname}, {lb}))',
                               f'# Fitness fix ts_rank lb={lb}: {fname}'))

    return entries


def build_sign_flip_batch(results_csv: Path) -> Path | None:
    """Detect expressions with good abs(sharpe/fitness) but negative sharpe,
    which the platform scores as FAIL on LOW_SHARPE/LOW_FITNESS checks.
    Flipping -rank(...) → rank(...) inverts the signal and should resolve both
    failing checks, pushing passed count from ~4 to ~6.
    Returns a params file path, or None if nothing to flip."""
    flippable = []
    seen_codes = set()
    try:
        with open(results_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    sharpe  = float(row.get('sharpe', 0) or 0)
                    fitness = float(row.get('fitness', 0) or 0)
                    code    = row.get('code', '').strip()
                except (ValueError, TypeError):
                    continue
                if (sharpe < 0
                        and abs(sharpe) >= SHARPE_PASS
                        and abs(fitness) >= FITNESS_PASS
                        and code.startswith('-rank(')
                        and code not in seen_codes):
                    seen_codes.add(code)
                    flipped = code[1:]  # drop leading '-'
                    flippable.append({
                        'original': code,
                        'flipped':  flipped,
                        'sharpe':   sharpe,
                        'fitness':  fitness,
                        'universe': row.get('universe', 'TOP3000'),
                    })
    except Exception as e:
        log(f"  [flip] Could not read {results_csv.name}: {e}")
        return None

    if not flippable:
        return None

    log(f"  [flip] {len(flippable)} negative-sharpe expression(s) to flip:")
    for e in flippable:
        log(f"    sharpe={e['sharpe']:.2f} fit={e['fitness']:.2f}  {e['original'][:70]}")

    ts = datetime.now().strftime('%m%d_%H%M')
    filename = BASE_DIR / f'parameters_flip_{ts}.py'
    base_settings = "{'neutralization':'SUBINDUSTRY','decay':6,'truncation':0.08,'delay':1,'region':'USA'}"

    lines = [
        f"# parameters_flip_{ts}.py — sign-flipped expressions (rank vs -rank)",
        f"BATCH_NAME = 'flip_{ts}'",
        "",
        "from commands import *",
        "",
        f"_BASE = {base_settings}",
        "",
        "DATA = [",
    ]
    for e in flippable:
        univ = e['universe']
        lines.append(f"    # original sharpe={e['sharpe']:.2f} fit={e['fitness']:.2f}")
        lines.append(f"    {{**_BASE, 'universe': {repr(univ)}, 'code': {repr(e['flipped'])}}},")
    lines += ["]", "", f'print(f"Sign-flip batch: {{len(DATA)}} expressions")', ""]

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    log(f"  [flip] Batch written → {filename.name} ({len(flippable)} expressions)")
    return filename


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

    # Data-driven sweep skip: (template × frequency) buckets with ≥20 historical
    # near-misses and 0 passes don't convert — don't waste sims sweeping them.
    # (e.g. ts_decay_linear_QUARTERLY: 39 near-misses, 0 passes in 303 runs)
    try:
        from template_rl import (extract_template_type, _load_field_frequencies,
                                 load_performance)
        _perf = load_performance()
        _field_freq = _load_field_frequencies(TRACKER_CSV)
    except Exception:
        _perf, _field_freq = {}, {}

    def _unproductive_bucket(code: str, field: str) -> str | None:
        if not _perf:
            return None
        key = f"{extract_template_type(code)}_{_field_freq.get(field, 'QUARTERLY')}"
        v = _perf.get(key, {})
        if v.get('near_misses', 0) >= 20 and v.get('passes', 0) == 0:
            return key
        return None

    for field, info in near_misses[:5]:
        row = info.get('row', {})
        code, univ = row.get('code', '').strip(), row.get('universe', 'TOP200')
        if not code:
            continue

        bucket = _unproductive_bucket(code, field)
        if bucket:
            log(f"  Skipping near-miss sweep for {field}: bucket '{bucket}' has "
                f"never converted ({_perf[bucket]['near_misses']} near-misses, 0 passes)")
            continue

        fitness  = float(row.get('fitness',  0) or 0)
        turnover = float(row.get('turnover', 99) or 99)

        if fitness < 1.00:
            # Fitness-blocked: use targeted fitness tuning
            entries.extend(_fitness_tune(code, univ, field, fitness, turnover))
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

    # Safety net: drop any entry that still uses a banned operator
    before = len(entries)
    entries = [e for e in entries if not any(op in e[1] for op in BANNED_OPS)]
    if len(entries) < before:
        log(f"  Dropped {before - len(entries)} tuning entries using banned ops {BANNED_OPS}")

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

def _get_session(force_reauth: bool = False):
    """Get or create the shared WQSession. Re-authenticates if session expired."""
    global _wq_session
    expired = _wq_session is not None and getattr(_wq_session, 'login_expired', False)
    if _wq_session is None or force_reauth or expired:
        if expired:
            log("⚠ WQ session expired — sending notification and re-authenticating...")
            try:
                from notify import notify
                notify('WQ session expired — biometric auth required again',
                       title='WQ Brain — Re-auth Needed', urgent=True)
            except Exception:
                pass
        sys.path.insert(0, str(BASE_DIR))
        from main import WQSession
        _wq_session = WQSession()
    return _wq_session


def _run_attempts(session, data: list, total: int, label: str = '') -> list:
    """Run up to 2 simulation attempts, logging progress. Returns remaining (failed) data."""
    MAX_ATTEMPTS = 2
    prefix = f'[{label}] ' if label else ''
    for attempt in range(1, MAX_ATTEMPTS + 1):
        done = total - len(data)
        log(f"  {prefix}Attempt #{attempt}/{MAX_ATTEMPTS} | {done}/{total} done | {len(data)} queued")
        data = session.simulate(data)
        if not data:
            break
        if attempt < MAX_ATTEMPTS:
            log(f"  ↩ {len(data)} timed-out — retrying in 30s...")
            time.sleep(30)
        else:
            log(f"  ⚠ {len(data)} expressions still failed after {MAX_ATTEMPTS} attempts — skipping.")
    return data


def run_simulation(params_file: Path) -> Path | None:
    """Load params file and run simulation using shared session.
    Returns path to results CSV."""
    log(f"Running: {params_file.name}")
    start_time = time.time()

    # Load DATA from the parameters file
    import importlib.util
    spec = importlib.util.spec_from_file_location('params', params_file)
    params_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(params_mod)
    original_data = list(params_mod.DATA)

    if not original_data:
        log(f"  No expressions in {params_file.name}, skipping...")
        return None

    # Tell main.py which batch name to use for the CSV filename — avoids
    # stale cached module name from a previous manual run (parameters.py)
    os.environ['WQ_BATCH_NAME'] = getattr(params_mod, 'BATCH_NAME', 'agent')

    session = _get_session()
    total = len(original_data)
    data = _run_attempts(session, list(original_data), total)

    # If session expired mid-batch, re-authenticate and retry only the remaining failures.
    # Completed expressions are already in the CSV (main.py flushes each row), so
    # re-running original_data in full would waste quota re-submitting 60-70 done ones.
    if data and session.login_expired:
        log(f"  ↩ Session expired with {len(data)} expression(s) remaining "
            f"— re-authenticating and retrying failed subset...")
        session = _get_session()   # sends LINE notification + biometric polling
        data = _run_attempts(session, data, total, label='post-reauth')

    log(f"  ✅ Done! {total - len(data)}/{total} simulations completed.")

    # Collect ALL CSVs created during this run (main batch + any retry files).
    # _run_attempts calls simulate() twice when there are timeouts, each call
    # creates a separate CSV. We must merge them so near-misses in the main
    # batch aren't lost when the orchestrator only sees the tiny retry CSV.
    new_csvs = sorted(
        [p for p in glob.glob(str(BASE_DIR / 'data' / '*.csv'))
         if os.path.getmtime(p) >= start_time],
        key=os.path.getmtime
    )
    if not new_csvs:
        log("  ⚠ No new results CSV produced by this run — skipping analysis.")
        return None

    main_csv = Path(new_csvs[0])
    for extra in new_csvs[1:]:
        # Append retry rows into the main CSV
        with open(extra, newline='', encoding='utf-8') as src:
            reader = csv.DictReader(src)
            rows = list(reader)
        if rows:
            with open(main_csv, 'a', newline='', encoding='utf-8') as dst:
                writer = csv.DictWriter(dst, fieldnames=rows[0].keys())
                writer.writerows(rows)
        os.remove(extra)
        log(f"  Merged retry CSV {Path(extra).name} → {main_csv.name}")

    return main_csv


# ─── Pass validation: self-correlation + sweep robustness ────────────────────

_CORR_POLL_INTERVAL = 15   # seconds between polls
_CORR_MAX_POLLS     = 24   # 24 × 15s = 6 minutes max per alpha


def check_pass_correlations(passes: list) -> dict:
    """Fetch SELF_CORRELATION for each pass from the platform check endpoint.
    SELF_CORRELATION is computed asynchronously — result starts as 'PENDING'
    with no value, then resolves to PASS/FAIL with a numeric value.
    Polls up to 6 minutes per alpha before giving up.
    Returns field → abs(corr) or None if still pending / unavailable."""
    corrs = {}
    try:
        session = _get_session()
    except Exception as e:
        log(f"  ⚠ Corr check skipped (no session): {e}")
        return corrs
    for field, info in passes:
        link = str(info.get('row', {}).get('link', ''))
        m = re.search(r'worldquantbrain\.com/alpha/(\w+)', link)
        if not m:
            corrs[field] = None
            continue
        alpha_id = m.group(1)
        corr = None
        for attempt in range(_CORR_MAX_POLLS):
            try:
                r = session.get(
                    f'https://api.worldquantbrain.com/alphas/{alpha_id}/check')
                if r.status_code == 429:
                    wait = int(r.headers.get('Retry-After', _CORR_POLL_INTERVAL))
                    time.sleep(wait)
                    continue
                if r.status_code == 200:
                    for chk in r.json().get('is', {}).get('checks', []):
                        if chk.get('name') != 'SELF_CORRELATION':
                            continue
                        if chk.get('result') == 'PENDING':
                            break  # not ready — sleep and retry
                        # Result is definitive (PASS or FAIL)
                        val = chk.get('value')
                        corr = abs(float(val)) if val is not None else 0.0
                        break
            except Exception:
                pass
            if corr is not None:
                break
            elapsed_min = (attempt + 1) * _CORR_POLL_INTERVAL // 60
            log(f"    self-corr {field}: PENDING "
                f"({(attempt+1)*_CORR_POLL_INTERVAL}s elapsed) — retrying...")
            time.sleep(_CORR_POLL_INTERVAL)

        corrs[field] = corr
        if corr is None:
            log(f"    self-corr {field}: still PENDING after "
                f"{_CORR_MAX_POLLS * _CORR_POLL_INTERVAL // 60}min "
                f"— check manually: {link}")
        else:
            verdict = f"✗ TOO HIGH (≥{CORR_MAX})" if corr >= CORR_MAX else "✓ OK"
            log(f"    self-corr {field}: {corr:.2f} {verdict}")
    return corrs


def check_alpha_grades(passes: list) -> dict:
    """Fetch the WQ-assigned grade string for each pass ('INFERIOR'/'GOOD'/'EXCELLENT').
    Available pre-submission from GET /alphas/{id}.
    Returns field → grade string or None."""
    grades = {}
    try:
        session = _get_session()
    except Exception:
        return grades
    for field, info in passes:
        link = str(info.get('row', {}).get('link', ''))
        m = re.search(r'worldquantbrain\.com/alpha/(\w+)', link)
        if not m:
            grades[field] = None
            continue
        alpha_id = m.group(1)
        try:
            r = session.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
            if r.status_code == 200:
                grades[field] = r.json().get('grade')  # e.g. "INFERIOR", "GOOD", "EXCELLENT"
            else:
                grades[field] = None
        except Exception:
            grades[field] = None
    return grades


def sweep_robustness(results_csv: Path, passes: list) -> dict:
    """For each passing field, count sibling variants in the same batch with
    |sharpe| >= ROBUST_SHARPE. A pass whose neighbors are all noise is likely
    a multiple-comparisons fluke. Returns field → (n_support, n_siblings)."""
    from alpha_utils import extract_field
    siblings = {}
    try:
        with open(results_csv) as f:
            for row in csv.DictReader(f):
                fld = extract_field(row.get('code', ''))
                if not fld:
                    continue
                if not re.search(r'worldquantbrain\.com/alpha/\w+',
                                 str(row.get('link', ''))):
                    continue
                try:
                    siblings.setdefault(fld, []).append(
                        abs(float(row.get('sharpe', 0) or 0)))
                except (ValueError, TypeError):
                    pass
    except Exception:
        return {}
    out = {}
    for field, _info in passes:
        sh = sorted(siblings.get(field, []), reverse=True)
        # exclude the best row (the pass itself) — count supporting neighbors
        support = sum(1 for s in sh[1:] if s >= ROBUST_SHARPE)
        out[field] = (support, max(len(sh) - 1, 0))
    return out


def _load_corr_fails() -> dict:
    if CORR_FAILS_FILE.exists():
        with open(CORR_FAILS_FILE) as f:
            return json.load(f)
    return {}


def _save_corr_fails(data: dict):
    with open(CORR_FAILS_FILE, 'w') as f:
        json.dump(data, f, indent=2, sort_keys=True)


def record_corr_failed_field(field: str, corr: float, code: str, link: str):
    """Persist a field that failed self-correlation so it appears in the auto KB."""
    data = _load_corr_fails()
    entry = data.get(field, {'corr_values': [], 'expressions': [], 'link': link})
    if corr not in entry['corr_values']:
        entry['corr_values'].append(round(corr, 2))
    expr_short = code[:80]
    if expr_short not in entry['expressions']:
        entry['expressions'].append(expr_short)
    entry['date'] = datetime.now().strftime('%Y-%m-%d')
    data[field] = entry
    _save_corr_fails(data)


def update_auto_knowledge_base():
    """Regenerate knowledge bases/auto_findings.md from live project data.
    Called after each batch so Gemini always has up-to-date context."""
    from template_rl import load_performance, BANNED_TEMPLATES

    lines = [
        '# WQ-Brain Auto-Generated Research Findings',
        f'_Auto-updated after each batch. Last update: {datetime.now().strftime("%Y-%m-%d %H:%M")}_',
        '_Do not edit — regenerated automatically by orchestrator.py._',
        '',
    ]

    # ── Banned operators ──────────────────────────────────────────────────────
    lines += [
        '## Banned Operators / Patterns',
        'NEVER use these in any expression — they are dropped before simulation:',
        '',
        '- `ts_decay_linear(field, N)` — correlated with submitted Alpha 10;'
        ' Performance Comparison score always negative regardless of IS metrics.',
        '- `ts_delta(close, N)` / `rank(ts_delta(close, N))` — correlated with'
        ' Alpha 9 (price momentum). Self-corr 0.75–0.84 on every combination tested.',
        '',
    ]

    # ── Submitted alphas (avoid replicating) ─────────────────────────────────
    submitted = []
    try:
        with open(TRACKER_CSV, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if '✅' in row.get('status', ''):
                    submitted.append((row.get('field', '').strip(), row.get('category', '')))
    except Exception:
        pass
    if submitted:
        lines += [
            '## Submitted Alphas Already In Book',
            'These fields are already submitted — generating expressions using them risks high self-correlation:',
            '',
        ]
        for field, cat in submitted:
            lines.append(f'- `{field}` ({cat})')
        lines.append('')

    # ── Corr-failed fields ────────────────────────────────────────────────────
    corr_fails = _load_corr_fails()
    if corr_fails:
        lines += [
            '## Fields Confirmed Too Correlated With Book (Self-Corr ≥ 0.70)',
            'These produced IS passes but CANNOT be submitted. Avoid as primary signal:',
            '',
        ]
        for field, info in sorted(corr_fails.items()):
            corrs = info.get('corr_values', [])
            corr_str = f"{min(corrs):.2f}–{max(corrs):.2f}" if len(corrs) > 1 else f"{corrs[0]:.2f}" if corrs else '?'
            n = len(info.get('expressions', []))
            lines.append(f'- `{field}`: self-corr {corr_str} ({n} expression(s) tested, all rejected)')
        lines.append('')

    # ── Template performance ──────────────────────────────────────────────────
    perf = load_performance()
    lines += ['## Template Performance Summary', '']
    for freq in ['QUARTERLY', 'WEEKLY', 'DAILY', 'SLOW']:
        relevant = {
            k: v for k, v in perf.items()
            if k.endswith(f'_{freq}') and v.get('runs', 0) >= 10
            and k[:-(len(freq)+1)] not in BANNED_TEMPLATES
        }
        if not relevant:
            continue
        lines.append(f'### {freq}')
        ranked = sorted(relevant.items(),
                        key=lambda x: (x[1].get('passes', 0) / max(x[1]['runs'], 1),
                                       x[1].get('avg_sharpe', 0)), reverse=True)
        for key, v in ranked:
            tmpl = key.replace(f'_{freq}', '')
            runs = v['runs']
            pr = v['passes'] / runs * 100
            lines.append(f'- `{tmpl}`: pass_rate={pr:.1f}% ({v["passes"]}/{runs} runs)'
                         f', avg_sharpe={v.get("avg_sharpe", 0):.2f}')
        if ranked:
            best = ranked[0][0].replace(f'_{freq}', '')
            lines.append(f'→ **Best for {freq}: `{best}`**')
        lines.append('')

    # ── Category yield ────────────────────────────────────────────────────────
    try:
        stats = category_scores()
        lines += ['## Category Yield (Historical)', '']
        for cat in sorted(stats, key=lambda c: stats[c].get('score', 0), reverse=True):
            v = stats[cat]
            if v['tested'] == 0:
                continue
            pr = v['passes'] / v['tested'] * 100 if v['tested'] else 0
            lines.append(f'- **{cat}**: {v["passes"]} passes / {v["tested"]} tested'
                         f' ({pr:.1f}%) | {v["untested"]} fields remaining')
        lines.append('')
    except Exception:
        pass

    content = '\n'.join(lines)
    try:
        AUTO_KB_FILE.parent.mkdir(exist_ok=True)
        AUTO_KB_FILE.write_text(content, encoding='utf-8')
        log(f'  [kb] Auto knowledge base updated → {AUTO_KB_FILE.name}')
    except Exception as e:
        log(f'  [kb] Could not write auto KB: {e}')


def handle_passes(passes: list, results_csv: Path) -> list:
    """Corr-check, grade, and robustness-annotate passes. Notifies only submittable
    ones; corr-fails are logged and fed back into RL stats. Returns clean passes."""
    if not passes:
        return []
    corrs  = check_pass_correlations(passes)
    grades = check_alpha_grades(passes)
    robust = sweep_robustness(results_csv, passes)
    clean, failed = [], []
    for f, v in passes:
        c = corrs.get(f)
        if c is not None and c >= CORR_MAX:
            failed.append((f, v, c))
        else:
            clean.append((f, v))
    for f, v, c in failed:
        grade = grades.get(f, 'unknown')
        row   = v.get('row', {})
        log(f"  ✗ CORR-FAIL {f[:60]}: self-corr {c:.2f} ≥ {CORR_MAX} | "
            f"grade={grade} | sharpe={v['sharpe']:.2f} | {row.get('link','')}")
        log(f"    expr: {row.get('code','')[:80]}")
        log(f"    → not submittable, penalizing template bucket")
        try:
            from template_rl import record_corr_fail
            record_corr_fail(row.get('code', ''))
        except Exception as e:
            log(f"    [rl] could not record corr fail: {e}")
        # Persist field-level corr failure so it appears in auto KB
        display = v.get('_display_field', f)
        record_corr_failed_field(display, c, row.get('code', ''), row.get('link', ''))
    if clean:
        notify_passes(clean, results_csv, corrs=corrs, robustness=robust, grades=grades)
    return clean


# ─── Pass notification ────────────────────────────────────────────────────────

def notify_passes(passes: list, results_csv: Path, corrs: dict = None,
                  robustness: dict = None, grades: dict = None):
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
        # For combination alphas, _display_field holds the human-readable field name
        display_field = info.get('_display_field', field)

        corr = (corrs or {}).get(field)
        if corr is None:
            corr_str = 'still pending — check manually'
        elif corr >= CORR_MAX:
            corr_str = f"{corr:.2f} ✗ TOO HIGH"
        else:
            corr_str = f"{corr:.2f} ✓ OK"

        support, total = (robustness or {}).get(field, (None, None))
        if support is None:
            robust_str = 'n/a'
        else:
            robust_str = f"{support}/{total} siblings ≥ {ROBUST_SHARPE}"
            if support == 0 and total and total > 0:
                robust_str += "  ⚠ FRAGILE — likely sweep overfit, be skeptical"

        grade = (grades or {}).get(field)
        grade_str = grade if grade else 'unknown'

        msg = (
            f"\n  Field   : {display_field}\n"
            f"  Expr    : {code}\n"
            f"  Universe: {univ}\n"
            f"  Sharpe  : {sharpe:.2f} | Fitness: {fitness:.2f} | Checks: {passed}/7 | TO: {TO}%\n"
            f"  SelfCorr: {corr_str}\n"
            f"  Grade   : {grade_str} | Robustness: {robust_str}\n"
            f"  Link    : {link}\n"
            f"  → Open link → Performance Comparison panel\n"
            f"  → If Performance score > 0 and SelfCorr < {CORR_MAX} → SUBMIT\n"
            f"  → If Performance score < 0 or SelfCorr ≥ {CORR_MAX}  → REJECT\n"
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
                     groq_key: str = None, triage: bool = True):
    separator()
    log("  WQ Brain Orchestrator — Automated Research Loop")
    log(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"  Dry run: {dry_run}")
    separator()

    # If start_category given, force it as the first batch only — after that,
    # selection is yield-based.
    forced_first = None
    if start_category and start_category in CATEGORY_PRIORITY:
        forced_first = start_category
        log(f"  First batch forced to: {start_category} (yield-based after that)")

    # Print category queue ranked by historical yield
    stats = category_scores()
    ranked = sorted(((v['score'], cat, v) for cat, v in stats.items()
                     if v['untested'] > 0), reverse=True)
    log("  Category queue (ranked by yield score = smoothed pass rate):")
    for i, (score, cat, v) in enumerate(ranked, 1):
        log(f"    {i}. {cat} (score={score:.3f} | "
            f"{v['passes']}p/{v['near']}n/{v['tested']}t | {v['untested']} untested)")

    log("")
    _recover_on_startup()
    try:
        update_auto_knowledge_base()
    except Exception as e:
        log(f'  [kb] KB update after startup recovery failed: {e}')
    skipping = False  # rotation handles start_category, no longer need to skip

    try:
        batch_num = 0
        consecutive_gen_failures = 0
        MAX_CONSECUTIVE_GEN_FAILURES = 3
        while True:
            if forced_first:
                cat, forced_first = forced_first, None
            else:
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
                log(f"  [DRY RUN] Would triage {TRIAGE_FIELDS} fields from '{cat}', "
                    f"then LLM-batch promising ones")
                # Remove so the dry-run plan lists each category once
                CATEGORY_PRIORITY.remove(cat)
                continue

            # ── Step 1a: Triage — cheap 2-template scan of untested fields ─
            promising = None
            triage_seeds: dict[str, dict] = {}
            if triage:
                triage_file, triage_fields = build_triage_batch(cat, TRIAGE_FIELDS)
                if triage_file:
                    triage_csv = run_simulation(triage_file)
                    if triage_csv:
                        update_tracker_from_csv(triage_csv)
                        try:
                            from template_rl import update_from_results
                            update_from_results(triage_csv, TRACKER_CSV)
                        except Exception as e:
                            log(f'  [rl] Could not update template performance: {e}')
                        promising, triage_meta = triage_promising(triage_csv, triage_fields)
                        log(f"  Triage: {len(promising)}/{len(triage_fields)} fields "
                            f"promising (|sharpe| ≥ {TRIAGE_SHARPE})")
                        if not promising:
                            log("  No promising fields in this triage batch — moving on.")
                            continue

                        # Fitness-ceiling filter: hump+TO<1% → max(TO/100,0.125) floor
                        # locks denominator; fundamentals can't reach fitness=1.0
                        ceiling = [
                            f for f in promising
                            if (triage_meta.get(f, {}).get('template') == CEILING_TEMPLATE
                                and triage_meta.get(f, {}).get('turnover', 99) < CEILING_TO_THRESHOLD)
                        ]
                        if ceiling:
                            log(f"  [ceiling] {len(ceiling)} field(s) show "
                                f"hump+TO<{CEILING_TO_THRESHOLD}% fitness ceiling "
                                f"— marking tested, skipping LLM:")
                            for f in ceiling:
                                m = triage_meta[f]
                                log(f"    {f}: sharpe={m['sharpe']:.2f} TO={m['turnover']:.2f}%")
                                _mark_fitness_ceiling(f, m['sharpe'], m['turnover'])
                            ceiling_set = set(ceiling)
                            promising = [f for f in promising if f not in ceiling_set]

                        if not promising:
                            log("  All triage-promising fields show fitness ceiling — moving on.")
                            continue

                        # Slice first, then build seeds from exactly the LLM-batched fields.
                        # Save the overflow before slicing — those fields are currently
                        # marked 'Tested: Baseline Failed' by update_tracker_from_csv
                        # but deserve a full LLM batch; reset them to untested so a
                        # future triage pass can pick them up.
                        overflow_promising = promising[FIELDS_PER_BATCH:]
                        promising = promising[:FIELDS_PER_BATCH]
                        triage_seeds = {f: triage_meta[f] for f in promising}
                        if overflow_promising:
                            log(f"  [overflow] {len(overflow_promising)} promising field(s) "
                                f"cut by FIELDS_PER_BATCH={FIELDS_PER_BATCH} limit "
                                f"— resetting to untested for future batches")
                            _reset_fields_to_untested(overflow_promising)

                        # Persist KB now — captures any triage near-misses before
                        # the LLM batch starts, so a crash between steps doesn't
                        # leave auto_findings.md stale.
                        try:
                            update_auto_knowledge_base()
                        except Exception as e:
                            log(f'  [kb] KB update after triage failed: {e}')

            # ── Step 1b: Generate LLM batch (full templates) ──────────────
            params_file = generate_batch(api_key, cat, FIELDS_PER_BATCH,
                                         groq_key=groq_key, fields=promising)
            if params_file and triage_seeds:
                _inject_triage_seeds(params_file, triage_seeds)
            if not params_file:
                consecutive_gen_failures += 1
                log(f"Batch generation failed for {cat} ({consecutive_gen_failures}/{MAX_CONSECUTIVE_GEN_FAILURES}).")
                if consecutive_gen_failures >= MAX_CONSECUTIVE_GEN_FAILURES:
                    msg = (f"LLM generation failed {MAX_CONSECUTIVE_GEN_FAILURES} batches in a row. "
                           f"Likely Gemini quota exhausted (20 req/day limit). "
                           f"Stopping — restart tomorrow when quota resets.")
                    log(msg)
                    try:
                        from notify import notify
                        notify(msg, title='WQ Brain — Quota Exhausted', urgent=True)
                    except Exception:
                        pass
                    break
                continue
            consecutive_gen_failures = 0

            # ── Step 2: Run simulation ────────────────────────────────────
            results_csv = run_simulation(params_file)
            if not results_csv:
                log("No results CSV found, skipping analysis...")
                continue
            log(f"Results CSV: {results_csv.name}")

            # ── Step 3: Parse + update tracker + RL performance ──────────
            field_best = update_tracker_from_csv(results_csv)
            try:
                from template_rl import update_from_results
                update_from_results(results_csv, TRACKER_CSV)
            except Exception as e:
                log(f'  [rl] Could not update template performance: {e}')

            # Sign-flip: re-simulate negative-sharpe expressions as rank(...)
            flip_file = build_sign_flip_batch(results_csv)
            if flip_file:
                flip_csv = run_simulation(flip_file)
                if flip_csv:
                    flip_best = update_tracker_from_csv(flip_csv)
                    try:
                        from template_rl import update_from_results
                        update_from_results(flip_csv, TRACKER_CSV)
                    except Exception:
                        pass
                    rank_map = {'dead':0,'tested':1,'near_miss':2,'pass':3}
                    for fld, info in flip_best.items():
                        existing = field_best.get(fld)
                        if existing is None or rank_map.get(info['status'],0) > rank_map.get(existing['status'],0):
                            field_best[fld] = info

            passes, near_misses = parse_passes_and_near_misses(field_best)

            # Summary
            status_counts = Counter(v['status'] for v in field_best.values())
            log(f"  Results: {status_counts.get('pass',0)} pass | "
                f"{status_counts.get('near_miss',0)} near-miss | "
                f"{status_counts.get('tested',0)} tested | "
                f"{status_counts.get('dead',0)} dead")

            # Log which metric blocks each near-miss (feeds near_miss_log.csv)
            log_near_miss_failures(near_misses, cat)

            # Update auto knowledge base with latest findings
            try:
                update_auto_knowledge_base()
            except Exception as e:
                log(f'  [kb] KB update failed: {e}')

            # ── Step 4: Handle passes (corr-check + robustness first) ─────
            if passes:
                clean = handle_passes(passes, results_csv)

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
                            clean += handle_passes(tune_passes, tune_csv)

                # Pause for manual review only if something is actually submittable
                if clean:
                    wait_for_user_confirmation()

            elif near_misses:
                log(f"  {len(near_misses)} near-misses — building quick tuning sweep...")
                tune_file = build_tuning_batch([], near_misses)
                if tune_file:
                    tune_csv = run_simulation(tune_file)
                    if tune_csv:
                        tune_best = update_tracker_from_csv(tune_csv)
                        tune_passes, _ = parse_passes_and_near_misses(tune_best)
                        if handle_passes(tune_passes, tune_csv):
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
                    is_pass = abs(sharpe) >= SHARPE_PASS and abs(fitness) >= FITNESS_PASS and passed >= CHECKS_PASS
                    is_near = abs(sharpe) >= SHARPE_NEAR and abs(fitness) >= FITNESS_NEAR and passed >= CHECKS_NEAR
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
                       if abs(float(v['row'].get('fitness', 0) or 0)) < FITNESS_PASS]
    checks_blocked  = [(f, v) for f, v in near_misses
                       if abs(float(v['row'].get('fitness', 0) or 0)) >= FITNESS_PASS
                       and int(v['row'].get('passed', 0) or 0) < CHECKS_PASS]
    sharpe_blocked  = [(f, v) for f, v in near_misses
                       if abs(float(v['row'].get('fitness', 0) or 0)) >= FITNESS_PASS
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
    parser.add_argument('--no-triage', action='store_true',
                        help='Skip the cheap triage pass — send every field straight to full LLM batches')
    parser.add_argument('--exploit', action='store_true',
                        help='Exploit mode: deep-test untested fields in datasets that already produced winners')
    parser.add_argument('--exploit-batches', type=int, default=10,
                        help='Max batches in exploit mode (default: 10)')
    parser.add_argument('--combine', action='store_true',
                        help='Combination mode: generate ensemble alphas from passing expressions')
    parser.add_argument('--check-passes', metavar='CSV',
                        help='Run corr + grade check on all passes in an existing results CSV (no re-simulation)')
    args = parser.parse_args()

    if args.check_passes:
        csv_path = Path(args.check_passes)
        if not csv_path.exists():
            # try relative to data/
            csv_path = BASE_DIR / 'data' / args.check_passes
        if not csv_path.exists():
            print(f"ERROR: CSV not found: {args.check_passes}")
            sys.exit(1)
        passes = parse_all_passes_from_csv(csv_path)
        if not passes:
            log(f"No passes found in {csv_path.name} (thresholds: sharpe≥{SHARPE_PASS}, fitness≥{FITNESS_PASS}, checks≥{CHECKS_PASS})")
        else:
            log(f"Found {len(passes)} pass(es) in {csv_path.name} — checking corr + grade...")
            clean = handle_passes(passes, csv_path)
            if clean:
                wait_for_user_confirmation()
        return

    if args.retune:
        run_retune()
        return

    if args.seed:
        run_seed(args.seed_category)
        return

    if args.mutate:
        run_mutate(args.mutate_count)
        return

    if args.combine:
        from combine_alphas import build_combination_batch
        params_file = build_combination_batch()
        if params_file and not args.dry_run:
            results_csv = run_simulation(params_file)
            if results_csv:
                log(f"Combo results → {results_csv.name}")
                field_best = update_tracker_from_csv(results_csv)
                try:
                    from template_rl import update_from_results
                    update_from_results(results_csv, TRACKER_CSV)
                except Exception as e:
                    log(f'  [rl] Could not update template performance: {e}')

                # Sign-flip: re-simulate negative-sharpe expressions as rank(...)
                # Use parse_all_passes_from_csv (code-keyed) so each unique
                # combination expression gets its own corr check — not collapsed
                # by shared primary field like update_tracker_from_csv does.
                flip_file = build_sign_flip_batch(results_csv)
                if flip_file:
                    flip_csv = run_simulation(flip_file)
                    if flip_csv:
                        flip_passes = parse_all_passes_from_csv(flip_csv)
                        if flip_passes:
                            log(f"  [flip] {len(flip_passes)} pass(es) — checking corr + grade individually")
                            clean = handle_passes(flip_passes, flip_csv)
                            if clean:
                                wait_for_user_confirmation()

                # Original combine passes (non-flipped) — also code-keyed
                combo_passes = parse_all_passes_from_csv(results_csv)
                near_misses_field, _ = parse_passes_and_near_misses(field_best)  # for near-miss log
                log_near_miss_failures(
                    [(f, v) for f, v in field_best.items() if v['status'] == 'near_miss'],
                    'Combine'
                )
                if combo_passes:
                    clean = handle_passes(combo_passes, results_csv)
                    if clean:
                        wait_for_user_confirmation()

                try:
                    update_auto_knowledge_base()
                except Exception as e:
                    log(f'  [kb] KB update failed: {e}')
        return

    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key and not args.dry_run:
        print("ERROR: No API key. Pass --api-key or set GEMINI_API_KEY env var.")
        sys.exit(1)

    groq_key = args.groq_key or os.environ.get('GROQ_API_KEY')

    if args.exploit:
        run_exploit(api_key, groq_key=groq_key, max_batches=args.exploit_batches)
        return

    run_orchestrator(api_key, args.start_category, args.dry_run, groq_key=groq_key,
                     triage=not args.no_triage)


if __name__ == '__main__':
    main()
