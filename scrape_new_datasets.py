#!/usr/bin/env python3
"""
scrape_new_datasets.py — Discover and import all new BRAIN datasets into fields_tracker.csv

Workflow (one biometric auth, one run):
  1. Fetch all available datasets from /data-sets API
  2. Compare with fields_tracker.csv to find:
       a) Brand-new datasets not yet in tracker
       b) Existing datasets that have grown (fieldCount > tracked count)
  3. Scrape fields for all new/grown datasets
  4. Merge into fields_tracker.csv (never overwrites existing status/notes)
  5. Print summary

Usage:
  python3 scrape_new_datasets.py           # auto-detect and import all new
  python3 scrape_new_datasets.py --dry-run # show what would be imported, no writes
"""

import csv
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime

FIELDS_TRACKER = os.environ.get('WQ_TRACKER', 'fields_tracker.csv')
DATA_DIR       = 'data'
REGION         = 'USA'
UNIVERSE       = 'TOP3000'
DELAY          = 1
PAGE_SIZE      = 20
SLEEP_BETWEEN  = 3.0
BASE_URL       = 'https://api.worldquantbrain.com'

DRY_RUN = '--dry-run' in sys.argv


# ── HELPERS ───────────────────────────────────────────────────────────────────

def fetch_json(wq, url, label=''):
    """GET url, retry on rate-limit, return parsed JSON."""
    while True:
        r = wq.get(url)
        try:
            data = r.json()
        except Exception as e:
            print(f'  ✗ JSON parse failed for {label}: {e} — {r.text[:200]}')
            return None
        if isinstance(data, dict) and 'rate limit' in data.get('message', '').lower():
            print(f'  ⚠ Rate limited — waiting 30s...')
            time.sleep(30)
            continue
        return data


def fetch_all_datasets(wq):
    """Return list of all dataset dicts from /data-sets."""
    url = (f'{BASE_URL}/data-sets'
           f'?instrumentType=EQUITY&region={REGION}&delay={DELAY}'
           f'&universe={UNIVERSE}&limit=50&offset=0')
    data = fetch_json(wq, url, 'data-sets')
    if not data or 'results' not in data:
        print(f'  ✗ Could not fetch dataset list: {data}')
        return []
    datasets = data['results']
    print(f'  Found {len(datasets)} datasets on BRAIN')
    return datasets


def load_tracker_state(path):
    """Return (rows_dict keyed by field, columns list, dataset_field_counts)."""
    if not os.path.exists(path):
        return {}, ['category', 'field', 'status', 'signal_strength',
                    'dataset', 'description', 'alpha_count', 'user_count',
                    'coverage', 'date_created', 'notes', 'abandon_reason'], Counter()

    rows = {}
    cols = []
    ds_counts = Counter()
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or [])
        for row in reader:
            rows[row['field']] = row
            ds_counts[row.get('dataset', '')] += 1
    return rows, cols, ds_counts


def scrape_all_fields_global(wq):
    """Fetch ALL fields from /data-fields (no dataset filter — API ignores datasetId anyway).
    Returns list of raw field dicts, each with a 'dataset.id' nested inside."""
    all_fields = []
    offset = 0
    total = None

    while True:
        url = (f'{BASE_URL}/data-fields'
               f'?delay={DELAY}&instrumentType=EQUITY'
               f'&region={REGION}&universe={UNIVERSE}'
               f'&limit={PAGE_SIZE}&offset={offset}')
        data = fetch_json(wq, url, f'global@{offset}')
        if data is None:
            break

        if 'results' not in data:
            print(f'    ✗ Unexpected response at offset {offset}: {str(data)[:200]}')
            break

        results = data['results']
        if total is None:
            total = data.get('count', 0)
            print(f'    total={total}', end='', flush=True)

        all_fields.extend(results)
        print(f' {len(all_fields)}', end='', flush=True)

        if not results or len(all_fields) >= total:
            break
        offset += PAGE_SIZE
        time.sleep(SLEEP_BETWEEN)

    print()
    return all_fields


def flatten_field(f, dataset_id):
    """Convert raw API field dict to flat tracker-compatible dict."""
    ds = f.get('dataset', {})
    ds_id = ds.get('id', dataset_id) if isinstance(ds, dict) else dataset_id
    cat = f.get('category', {})
    cat_name = cat.get('name', '') if isinstance(cat, dict) else str(cat)
    sub = f.get('subcategory', {})
    sub_name = sub.get('name', '') if isinstance(sub, dict) else str(sub)
    category = cat_name
    if sub_name and sub_name != cat_name:
        category = f'{cat_name} - {sub_name}' if sub_name else cat_name
    cov = f.get('dateCoverage', '') or f.get('coverage', '')
    if isinstance(cov, dict):
        cov = f'{cov.get("from", "")}/{cov.get("to", "")}'
    return {
        'field':        f.get('id', ''),
        'dataset':      ds_id,
        'category':     category,
        'description':  f.get('description', ''),
        'alpha_count':  f.get('alphaCount', 0),
        'user_count':   f.get('userCount', 0),
        'coverage':     cov or '',
        'date_created': f.get('dateCreated', ''),
        'status':       '',
        'signal_strength': '',
        'notes':        '',
        'abandon_reason': '',
    }


def merge_fields(existing_rows, cols, new_flat_fields):
    """Add new fields into existing_rows. Returns list of new field IDs added."""
    needed = ['category', 'field', 'status', 'signal_strength',
              'dataset', 'description', 'alpha_count', 'user_count',
              'coverage', 'date_created', 'notes', 'abandon_reason']
    for c in needed:
        if c not in cols:
            cols.append(c)

    added = []
    for f in new_flat_fields:
        fid = f['field']
        if not fid:
            continue
        if fid not in existing_rows:
            row = {c: '' for c in cols}
            row.update(f)
            existing_rows[fid] = row
            added.append(fid)
        else:
            row = existing_rows[fid]
            # Static metadata — only fill if blank
            if not row.get('dataset'):
                row['dataset'] = f['dataset']
            if not row.get('description'):
                row['description'] = f['description']
            if not row.get('category'):
                row['category'] = f['category']
            if not row.get('coverage'):
                row['coverage'] = f.get('coverage', '')
            if not row.get('date_created'):
                row['date_created'] = f.get('date_created', '')
            # Dynamic counts — always refresh (they grow as more researchers find alphas)
            row['alpha_count'] = f.get('alpha_count', row.get('alpha_count', ''))
            row['user_count']  = f.get('user_count',  row.get('user_count', ''))
    return added


def save_tracker(path, cols, rows_dict):
    """Write tracker CSV, creating a timestamped backup first."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = path.replace('.csv', f'_backup_{ts}.csv')
        with open(path, encoding='utf-8') as src, \
             open(backup, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        print(f'  Backup: {backup}')

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows_dict.values())
    print(f'  ✅ Wrote {len(rows_dict)} rows to {path}')


def save_raw_snapshot(fields, dataset_id):
    """Save raw scraped fields to data/ for reference."""
    os.makedirs(DATA_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(DATA_DIR, f'fields_raw_{dataset_id}_{ts}.csv')
    if not fields:
        return
    keys = list(fields[0].keys()) if isinstance(fields[0], dict) else []
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        for row in fields:
            if isinstance(row, dict):
                writer.writerow(row)
    print(f'    Raw snapshot: {path}')


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f'\n{"="*60}')
    print(f'  WQ Brain — New Dataset Importer')
    print(f'  Region: {REGION} | Universe: {UNIVERSE} | Delay: {DELAY}')
    if DRY_RUN:
        print(f'  *** DRY RUN — no files will be written ***')
    print(f'{"="*60}\n')

    # ── Auth ──────────────────────────────────────────────────────
    print('[1/5] Logging in...')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from main import WQSession
    wq = WQSession()
    print('  Logged in.\n')

    # ── Load tracker ──────────────────────────────────────────────
    print(f'[2/5] Loading {FIELDS_TRACKER}...')
    existing_rows, cols, ds_counts = load_tracker_state(FIELDS_TRACKER)
    known_datasets = {ds for ds in ds_counts if ds}
    print(f'  {len(existing_rows)} fields tracked across {len(known_datasets)} datasets')
    print(f'  Known datasets: {sorted(known_datasets)}\n')

    # ── Fetch all available datasets ──────────────────────────────
    print('[3/5] Fetching available datasets from BRAIN API...')
    all_datasets = fetch_all_datasets(wq)
    if not all_datasets:
        print('  ✗ Could not fetch dataset list. Exiting.')
        sys.exit(1)

    print()
    print(f'  {"ID":<20} {"Name":<35} {"Fields":>6}  {"In tracker":>10}  Status')
    print(f'  {"-"*20} {"-"*35} {"-"*6}  {"-"*10}  ------')

    to_scrape = []
    for ds in sorted(all_datasets, key=lambda d: d.get('id', '')):
        ds_id       = ds.get('id', '')
        ds_name     = ds.get('name', '')[:34]
        field_count = ds.get('fieldCount', 0)
        tracked     = ds_counts.get(ds_id, 0)

        if ds_id not in known_datasets:
            status = '🆕 NEW'
            to_scrape.append((ds_id, ds_name, field_count, 'new'))
        elif field_count > tracked:
            status = f'📈 GROWN (+{field_count - tracked})'
            to_scrape.append((ds_id, ds_name, field_count, 'grown'))
        else:
            status = '✓ up to date'

        print(f'  {ds_id:<20} {ds_name:<35} {field_count:>6}  {tracked:>10}  {status}')

    print()
    if not to_scrape:
        print('  ✅ All datasets are already up to date. Nothing to import.')
        return

    print(f'  Datasets to scrape: {len(to_scrape)}')
    for ds_id, ds_name, fc, reason in to_scrape:
        print(f'    [{reason.upper()}] {ds_id} — {ds_name} ({fc} fields)')

    # ── Scrape ────────────────────────────────────────────────────
    # The /data-fields API ignores datasetId — it always returns all fields globally.
    # One global fetch is both correct and 16x faster than per-dataset queries.
    print(f'\n[4/5] Fetching all fields (one global pass)...\n')
    scrape_ds_ids = {ds_id for ds_id, _, _, _ in to_scrape}
    raw_fields = scrape_all_fields_global(wq)
    print(f'  Fetched {len(raw_fields)} fields total')

    if not raw_fields:
        print('  ✗ No fields returned. Exiting.')
        sys.exit(1)

    save_raw_snapshot(raw_fields, 'all')

    flat = [flatten_field(f, '') for f in raw_fields if isinstance(f, dict) and f.get('id')]

    total_added = []
    if not DRY_RUN:
        added = merge_fields(existing_rows, cols, flat)
        total_added.extend(added)
        print(f'  Added {len(added)} new fields to tracker')
        # Show breakdown by dataset
        by_ds: dict = {}
        for fid in added:
            ds = existing_rows.get(fid, {}).get('dataset', 'unknown')
            by_ds[ds] = by_ds.get(ds, 0) + 1
        if by_ds:
            print(f'  Breakdown by dataset:')
            for ds, cnt in sorted(by_ds.items(), key=lambda x: -x[1]):
                tag = ' ← targeted' if ds in scrape_ds_ids else ''
                print(f'    {ds:<25} +{cnt}{tag}')
    else:
        new_count = sum(1 for f in flat if f['field'] not in existing_rows)
        print(f'  [DRY RUN] Would add {new_count} new fields')
    print()

    # ── Save ──────────────────────────────────────────────────────
    print('[5/5] Saving...')
    if DRY_RUN:
        print(f'  [DRY RUN] Would write {len(existing_rows) + len(total_added)} rows')
    else:
        save_tracker(FIELDS_TRACKER, cols, existing_rows)

    # ── Summary ───────────────────────────────────────────────────
    print(f'\n{"="*60}')
    print(f'  Done!')
    print(f'  Datasets processed : {len(to_scrape)}')
    if not DRY_RUN:
        print(f'  New fields added   : {len(total_added)}')
        print(f'  Total in tracker   : {len(existing_rows)}')
        if total_added[:30]:
            print(f'\n  New fields (first 30):')
            for fid in total_added[:30]:
                row = existing_rows.get(fid, {})
                print(f'    [{row.get("dataset","?"):15}] {fid}')
            if len(total_added) > 30:
                print(f'    ... +{len(total_added)-30} more')
    print(f'{"="*60}\n')


if __name__ == '__main__':
    main()
