#!/usr/bin/env python3
"""
update_tracker.py — WQ-Brain Fields Tracker Updater
====================================================
Reads the latest (or specified) results CSV from data/ and updates
fields_tracker.csv with the test status and best metrics for each field.

Usage:
    # Auto-pick the latest results CSV
    python3 update_tracker.py

    # Specify a CSV explicitly
    python3 update_tracker.py data/gen_fundamental_20260520_092638_20260520_092749.csv

    # Dry run — show what would change without writing
    python3 update_tracker.py --dry-run

Status values written to fields_tracker.csv (emoji-prefixed, matches orchestrator.py):
    ✅ In Use                  — met submission thresholds (sharpe>=1.25, fitness>=1.0, passed>=6)
    🟠 Test Soon               — worth tuning (sharpe>=0.90, fitness>=0.70, passed>=5)
    🟡 Tested: Baseline Failed — tested but no signal (below promising)
    ❌ Dead                    — error / inaccessible field (no valid alpha_id returned)
"""

import argparse
import csv
import glob
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── CONFIG ────────────────────────────────────────────────────────────────────

FIELDS_CSV  = 'fields_tracker.csv'
DATA_DIR    = 'data'

# Thresholds (must match agent.py)
SHARPE_PASS       = 1.25
FITNESS_PASS      = 1.00
PASSED_PASS       = 6

SHARPE_PROMISING  = 0.90
FITNESS_PROMISING = 0.70
PASSED_PROMISING  = 5

# ── HELPERS ───────────────────────────────────────────────────────────────────

def extract_field(code):
    """Extract the data field name from an alpha expression string.
    Delegates to the canonical implementation in alpha_utils.py.
    """
    from alpha_utils import extract_field as _extract_field
    return _extract_field(code)


def classify_result(row):
    """
    Given a result row dict, return a status string and best sharpe.
    """
    try:
        sharpe  = float(row.get('sharpe', 0) or 0)
        fitness = float(row.get('fitness', 0) or 0)
        passed  = int(row.get('passed', 0) or 0)
        link    = str(row.get('link', ''))
    except (ValueError, TypeError):
        return 'dead', None, None, None

    # No valid alpha_id = simulation errored / field inaccessible
    has_alpha = bool(re.search(r'worldquantbrain\.com/alpha/[A-Za-z0-9]+', link))
    if not has_alpha:
        return 'dead', None, None, None

    if sharpe >= SHARPE_PASS and fitness >= FITNESS_PASS and passed >= PASSED_PASS:
        status = 'pass'
    elif sharpe >= SHARPE_PROMISING and fitness >= FITNESS_PROMISING and passed >= PASSED_PROMISING:
        status = 'promising'
    else:
        status = 'tested'

    return status, sharpe, fitness, passed


def load_results_csv(path):
    """
    Load a results CSV. Returns dict: field -> best result dict.
    'Best' = highest sharpe across all universes/variants tested.
    """
    field_results = {}  # field -> {status, sharpe, fitness, passed}

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            field = extract_field(row.get('code', ''))
            if not field:
                continue

            status, sharpe, fitness, passed = classify_result(row)

            # Keep best sharpe per field across all variants
            existing = field_results.get(field)
            if existing is None:
                field_results[field] = {
                    'status':  status,
                    'sharpe':  sharpe,
                    'fitness': fitness,
                    'passed':  passed,
                }
            else:
                # Upgrade status if this variant is better
                status_rank = {'dead': 0, 'tested': 1, 'promising': 2, 'pass': 3}
                if status_rank.get(status, 0) > status_rank.get(existing['status'], 0):
                    existing['status'] = status
                if sharpe is not None and (existing['sharpe'] is None or sharpe > existing['sharpe']):
                    existing['sharpe']  = sharpe
                    existing['fitness'] = fitness
                    existing['passed']  = passed

    return field_results


def load_tracker(path):
    """Load fields_tracker.csv into a list of dicts, preserving all columns."""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows


def update_tracker(headers, rows, field_results, dry_run=False):
    """
    Merge field_results into tracker rows.
    Returns (updated_rows, stats_dict).
    """
    # Ensure we have a signal_strength column (may already exist)
    extra_cols = ['signal_strength']
    for col in extra_cols:
        if col not in headers:
            headers.append(col)

    stats = {'updated': 0, 'skipped_dead': 0, 'new_pass': 0, 'new_promising': 0, 'no_change': 0}
    field_col = 'field'

    updated_rows = []
    for row in rows:
        field = row.get(field_col, '').strip()
        result = field_results.get(field)

        if result is None:
            updated_rows.append(row)
            continue

        new_status  = result['status']
        new_sharpe  = result['sharpe']
        old_status  = row.get('status', '').strip()

        # Never downgrade a field that's already marked pass/promising
        # (a later batch testing a different variant shouldn't overwrite a good result)
        # Supports both plain and emoji-prefixed status values
        # Abandoned gets rank 4 — never overwrite manually curated statuses
        status_rank = {'': 0, 'untested': 0, 'UNTESTED': 0,
                       'tested': 1, '🟡 Tested: Baseline Failed': 1,
                       'dead': 0, '❌ Dead': 0,
                       'promising': 2, '🟠 Test Soon': 2,
                       'pass': 3, '✅ In Use': 3,
                       '❌ Abandoned': 4, '⚪ Backlog': 0,
                       '🟡 Backlog: Needs Retest': 0}
        old_rank = status_rank.get(old_status, 0)
        new_rank = status_rank.get(new_status, 0)

        if new_rank < old_rank:
            # Don't downgrade
            stats['no_change'] += 1
            updated_rows.append(row)
            continue

        # Map plain status to emoji-prefixed format (matches orchestrator.py)
        emoji_status_map = {
            'tested':    '🟡 Tested: Baseline Failed',
            'promising': '🟠 Test Soon',
            'pass':      '✅ In Use',
            'dead':      '❌ Dead',
        }

        if not dry_run:
            row['status'] = emoji_status_map.get(new_status, new_status)
            if new_sharpe is not None:
                row['signal_strength'] = f"{new_sharpe:.3f}"

        # Stats
        if new_status == 'pass':
            stats['new_pass'] += 1
        elif new_status == 'promising':
            stats['new_promising'] += 1
        elif new_status == 'dead':
            stats['skipped_dead'] += 1
        stats['updated'] += 1

        updated_rows.append(row)

    return headers, updated_rows, stats


def save_tracker(path, headers, rows):
    """Write updated tracker back to CSV."""
    # Backup first
    backup = path.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    with open(path, newline='', encoding='utf-8') as src, \
         open(backup, 'w', newline='', encoding='utf-8') as dst:
        dst.write(src.read())

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    return backup


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Update fields_tracker.csv from results CSV')
    parser.add_argument('csv_path', nargs='?', default=None,
                        help='Path to results CSV (default: latest in data/)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without writing anything')
    args = parser.parse_args()

    print('=' * 60)
    print('  WQ-Brain Tracker Updater')
    print('=' * 60)

    # ── Find results CSV ──────────────────────────────────────────
    if args.csv_path:
        csv_path = args.csv_path
    else:
        # Auto-pick latest, skip agent's evaluated_ files
        candidates = [
            f for f in sorted(glob.glob(os.path.join(DATA_DIR, '*.csv')))
            if not os.path.basename(f).startswith('evaluated_')
        ]
        if not candidates:
            print(f'\n❌ No results CSVs found in {DATA_DIR}/')
            sys.exit(1)
        csv_path = candidates[-1]

    if not os.path.exists(csv_path):
        print(f'\n❌ File not found: {csv_path}')
        sys.exit(1)

    print(f'\n[1/4] Reading results from {os.path.basename(csv_path)}...')
    field_results = load_results_csv(csv_path)
    print(f'       {len(field_results)} unique fields found in results')

    if not field_results:
        print('\n⚠️  No valid results to process.')
        sys.exit(0)

    # ── Preview what we found ─────────────────────────────────────
    passes    = [f for f, r in field_results.items() if r['status'] == 'pass']
    promising = [f for f, r in field_results.items() if r['status'] == 'promising']
    dead      = [f for f, r in field_results.items() if r['status'] == 'dead']
    tested    = [f for f, r in field_results.items() if r['status'] == 'tested']

    print(f'       ✅ pass      : {len(passes)}')
    print(f'       🔧 promising : {len(promising)}')
    print(f'       ➖ tested    : {len(tested)}')
    print(f'       ❌ dead      : {len(dead)}')

    if passes:
        print(f'\n   🎉 PASSING FIELDS:')
        for f in passes:
            r = field_results[f]
            print(f'      {f} — sharpe={r["sharpe"]:.2f} fitness={r["fitness"]:.2f}')

    if promising:
        print(f'\n   🔧 PROMISING FIELDS:')
        for f in promising:
            r = field_results[f]
            print(f'      {f} — sharpe={r["sharpe"]:.2f} fitness={r["fitness"]:.2f}')

    # ── Load and update tracker ───────────────────────────────────
    print(f'\n[2/4] Loading {FIELDS_CSV}...')
    if not os.path.exists(FIELDS_CSV):
        print(f'❌ {FIELDS_CSV} not found.')
        sys.exit(1)

    headers, rows = load_tracker(FIELDS_CSV)
    print(f'       {len(rows)} fields in tracker')

    print(f'\n[3/4] Merging results{"  (DRY RUN)" if args.dry_run else ""}...')
    headers, updated_rows, stats = update_tracker(headers, rows, field_results, dry_run=args.dry_run)

    print(f'       Updated  : {stats["updated"]} fields')
    print(f'       New pass : {stats["new_pass"]}')
    print(f'       Promising: {stats["new_promising"]}')
    print(f'       Dead     : {stats["skipped_dead"]}')
    print(f'       No change: {stats["no_change"]}')

    # ── Write back ────────────────────────────────────────────────
    if args.dry_run:
        print(f'\n[4/4] DRY RUN — no files written.')
    else:
        print(f'\n[4/4] Writing {FIELDS_CSV}...')
        backup = save_tracker(FIELDS_CSV, headers, updated_rows)
        print(f'       Backup saved to {os.path.basename(backup)}')
        print(f'       ✅ {FIELDS_CSV} updated!')

        # Also update RL template performance tracker
        try:
            from template_rl import update_from_results
            update_from_results(Path(csv_path), Path(FIELDS_CSV))
        except Exception as e:
            print(f'       [rl] Could not update template_performance.json: {e}')

    print(f'\n   Done! Run agent.py on the same CSV for corr + tuning files.')
    print()


if __name__ == '__main__':
    main()
