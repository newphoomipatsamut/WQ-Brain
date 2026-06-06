#!/usr/bin/env python3
"""
generate_batch.py — WQ-Brain Batch Generator
=============================================
Reads fields_tracker.csv and generates a parameters_*.py file
ready to drop straight into main.py.

Usage:
    # Sweep untested fields with baseline templates
    python3 generate_batch.py

    # Sweep a specific category only
    python3 generate_batch.py --category "Fundamental"

    # Limit output size (default: 300 expressions per batch)
    python3 generate_batch.py --limit 150

    # Skip fields already tested (default: on)
    python3 generate_batch.py --all-fields

    # Use your wq_alpha.db to bias toward winning operators/windows
    python3 generate_batch.py --smart

Output:
    parameters_gen_YYYYMMDD_HHMMSS.py   ← copy this to parameters.py and run main.py
"""

import argparse
import csv
import os
import random
import sqlite3
from datetime import datetime
from itertools import product

# ── CONFIG ────────────────────────────────────────────────────────────────────

FIELDS_CSV   = 'fields_tracker.csv'
RESULTS_DB   = 'wq_alpha.db'
OUTPUT_DIR   = '.'

# Baseline sweep — applied to every untested field
# Two templates × two universes = 4 expressions per field by default
TEMPLATES = [
    {'wrapper': 'ts_rank',   'window': 252, 'decay': 6,  'trunc': 0.08, 'neut': 'SUBINDUSTRY'},
    {'wrapper': 'ts_zscore', 'window': 252, 'decay': 6,  'trunc': 0.08, 'neut': 'SUBINDUSTRY'},
]

UNIVERSES = ['TOP3000', 'TOP200']   # TOP200 consistently scores best per your README

# Fields marked with these statuses in fields_tracker.csv are skipped
DEAD_STATUSES = {
    'dead', 'skip', 'corr_dead', 'error', 'DEAD', 'SKIP',
    '❌ Dead', '❌ Abandoned',
}

# Columns we expect in fields_tracker.csv
COL_FIELD    = 'field'
COL_STATUS   = 'status'
COL_CATEGORY = 'category'

# ── HELPERS ───────────────────────────────────────────────────────────────────

def load_fields(csv_path, skip_tested=True, category_filter=None):
    """
    Load fields from fields_tracker.csv.
    Returns list of field name strings.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"'{csv_path}' not found. Run this script from inside your WQ-Brain repo directory."
        )

    fields = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        has_status   = COL_STATUS   in headers
        has_category = COL_CATEGORY in headers

        for row in reader:
            field = row.get(COL_FIELD, '').strip()
            if not field:
                continue

            # Filter by category if requested
            if category_filter and has_category:
                cat = row.get(COL_CATEGORY, '').strip()
                if category_filter.lower() not in cat.lower():
                    continue

            # Skip dead fields
            if has_status:
                status = row.get(COL_STATUS, '').strip()
                if status in DEAD_STATUSES:
                    continue

                # Skip already-tested fields if requested
                if skip_tested and status and status not in {'', 'untested', 'UNTESTED', '⚪ Backlog', '🟡 Backlog: Needs Retest'}:
                    continue

            fields.append(field)

    return fields


def load_winning_patterns(db_path):
    """
    Query wq_alpha.db for operators and windows that appear most often
    in passing alphas (sharpe >= 1.25, fitness >= 1.0).
    Returns {'wrappers': [...], 'windows': [...]} sorted by win rate.
    """
    if not os.path.exists(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cur  = conn.cursor()

        # Pull all passing alpha codes
        cur.execute("""
            SELECT code FROM submittable
            WHERE sharpe >= 1.25 AND fitness >= 1.00
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return None

        wrapper_counts = {'ts_zscore': 0, 'ts_rank': 0}
        window_counts  = {}

        import re
        for (code,) in rows:
            if 'ts_zscore' in str(code):
                wrapper_counts['ts_zscore'] += 1
            elif 'ts_rank' in str(code):
                wrapper_counts['ts_rank'] += 1

            m = re.search(r',\s*(\d+)\)', str(code))
            if m:
                w = int(m.group(1))
                window_counts[w] = window_counts.get(w, 0) + 1

        best_wrappers = sorted(wrapper_counts, key=wrapper_counts.get, reverse=True)
        best_windows  = sorted(window_counts,  key=window_counts.get,  reverse=True)[:3]

        return {'wrappers': best_wrappers, 'windows': best_windows or [252]}

    except Exception as e:
        print(f"[WARN] Could not read {db_path}: {e}")
        return None


def build_expressions(fields, templates, universes, limit):
    """
    Cross-product: fields × templates × universes.
    Shuffles fields so partial runs cover diverse territory.
    Caps output at `limit`.
    """
    random.shuffle(fields)

    expressions = []
    seen = set()

    for field, tmpl, uni in product(fields, templates, universes):
        code = f"-rank({tmpl['wrapper']}({field},{tmpl['window']}))"
        key  = (code, uni, tmpl['decay'], tmpl['neut'], tmpl['trunc'])
        if key in seen:
            continue
        seen.add(key)

        expressions.append({
            'neutralization': tmpl['neut'],
            'decay':          tmpl['decay'],
            'truncation':     tmpl['trunc'],
            'delay':          1,
            'region':         'USA',
            'universe':       uni,
            'code':           code,
        })

        if len(expressions) >= limit:
            break

    return expressions


def write_parameters_file(expressions, batch_name, fields_used, smart_mode):
    """Write a parameters_gen_*.py file compatible with main.py."""
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(OUTPUT_DIR, f'parameters_gen_{ts}.py')

    lines = [
        f'# parameters_gen_{ts}.py',
        f'# Auto-generated by generate_batch.py — {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# Fields covered : {len(fields_used)}',
        f'# Expressions    : {len(expressions)}',
        f'# Smart mode     : {smart_mode}',
        f'# Est. runtime   : ~{int(len(expressions) * 1.5)} min (3 concurrent sims)',
        f'#',
        f'# Run:',
        f'#   cp {os.path.basename(filename)} parameters.py',
        f'#   python3 main.py',
        f'#   python3 agent.py data/<output>.csv   # after run completes',
        '',
        'from commands import *',
        '',
        f"BATCH_NAME = '{batch_name}'",
        '',
        'DATA = [',
    ]

    for expr in expressions:
        code = expr['code'].replace("'", "\\'")
        lines.append(
            f"    {{'neutralization': '{expr['neutralization']}', "
            f"'decay': {expr['decay']}, "
            f"'truncation': {expr['truncation']}, "
            f"'delay': {expr['delay']}, "
            f"'region': '{expr['region']}', "
            f"'universe': '{expr['universe']}', "
            f"'code': '{code}'}},"
        )

    lines += [
        ']',
        '',
        'print(f"Batch    : {BATCH_NAME}")',
        'print(f"Queued   : {len(DATA)} expressions")',
        f'print(f"Est. time: ~{int(len(expressions) * 1.5)} min")',
        '',
    ]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    return filename


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='WQ-Brain batch expression generator')
    parser.add_argument('--category',   type=str,  default=None,
                        help='Filter fields by category substring (e.g. "Fundamental")')
    parser.add_argument('--limit',      type=int,  default=300,
                        help='Max expressions per batch (default: 300)')
    parser.add_argument('--all-fields', action='store_true',
                        help='Include already-tested fields (not just untested)')
    parser.add_argument('--smart',      action='store_true',
                        help='Bias templates toward winning operators/windows from wq_alpha.db')
    args = parser.parse_args()

    skip_tested = not args.all_fields

    print('=' * 60)
    print('  WQ-Brain Batch Generator')
    print('=' * 60)

    # ── Load fields ───────────────────────────────────────────────
    print(f'\n[1/4] Loading fields from {FIELDS_CSV}...')
    try:
        fields = load_fields(FIELDS_CSV, skip_tested=skip_tested, category_filter=args.category)
    except FileNotFoundError as e:
        print(f'\n❌ {e}')
        return

    if not fields:
        print('\n⚠️  No fields found matching your filters.')
        print('    Try --all-fields or remove --category filter.')
        return

    print(f'       {len(fields)} fields loaded')
    if args.category:
        print(f'       Category filter: "{args.category}"')
    if skip_tested:
        print(f'       Skipping already-tested fields (use --all-fields to include them)')

    # ── Smart mode: bias templates toward winners ─────────────────
    templates  = list(TEMPLATES)
    smart_info = ''

    if args.smart:
        print(f'\n[2/4] Analysing {RESULTS_DB} for winning patterns...')
        patterns = load_winning_patterns(RESULTS_DB)

        if patterns:
            best_wrapper = patterns['wrappers'][0]
            best_windows = patterns['windows']
            print(f'       Best wrapper : {best_wrapper}')
            print(f'       Best windows : {best_windows}')

            # Replace default templates with winner-biased ones
            templates = []
            for w in best_windows:
                templates.append({'wrapper': best_wrapper, 'window': w,
                                   'decay': 6, 'trunc': 0.08, 'neut': 'SUBINDUSTRY'})
            # Always include a ts_zscore baseline as a second opinion
            if best_wrapper != 'ts_zscore':
                templates.append({'wrapper': 'ts_zscore', 'window': best_windows[0],
                                   'decay': 6, 'trunc': 0.08, 'neut': 'SUBINDUSTRY'})

            smart_info = f'winner-biased ({best_wrapper}, windows={best_windows})'
        else:
            print(f'       No passing alphas in DB yet — using default templates')
            smart_info = 'default (no DB data)'
    else:
        print(f'\n[2/4] Using default templates (add --smart to bias from DB)')
        smart_info = 'off'

    # ── Build expressions ─────────────────────────────────────────
    print(f'\n[3/4] Building expressions (limit={args.limit})...')
    expressions = build_expressions(fields, templates, UNIVERSES, args.limit)
    fields_used = list({
        e['code'].split('(', 2)[2].rsplit(',', 1)[0]   # extract field name from code
        for e in expressions
    })
    print(f'       {len(expressions)} expressions across {len(fields_used)} fields')

    # ── Write output ──────────────────────────────────────────────
    ts         = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_name = f'gen_{ts}'
    if args.category:
        safe_cat   = args.category.lower().replace(' ', '_')[:20]
        batch_name = f'gen_{safe_cat}_{ts}'

    print(f'\n[4/4] Writing parameters file...')
    out_path = write_parameters_file(expressions, batch_name, fields_used, smart_info)

    print(f'\n✅ Done!')
    print(f'\n   Output  : {os.path.basename(out_path)}')
    print(f'   Exprs   : {len(expressions)}')
    print(f'   Runtime : ~{int(len(expressions) * 1.5)} min')
    print(f'\n   Next steps:')
    print(f'     cp {os.path.basename(out_path)} parameters.py')
    print(f'     python3 main.py')
    print(f'     python3 agent.py data/<output>.csv')
    print()


if __name__ == '__main__':
    main()
