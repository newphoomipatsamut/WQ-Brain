#!/usr/bin/env python3
"""
scrape_fields.py — WQ Brain Data Field Scraper

Scrapes all fields from a given dataset on WQ Brain API and:
  1. Saves full raw field list to data/fields_raw_DATASET_TIMESTAMP.csv
  2. Merges new fields into fields_tracker.csv (adds missing ones, never overwrites existing status)
  3. Reports a summary of new vs already-known fields

Usage:
  python3 scrape_fields.py                  # scrape Model 77 (default)
  python3 scrape_fields.py model77          # scrape Model 77 explicitly
  python3 scrape_fields.py fundamental26    # scrape a different dataset

The dataset ID is the slug from the BRAIN platform URL:
  https://platform.worldquantbrain.com/data/data-sets/MODEL_ID
"""

import csv
import json
import time
import sys
import os
from datetime import datetime
from main import WQSession

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATASET_ID       = sys.argv[1] if len(sys.argv) > 1 else 'model77'
START_OFFSET     = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # resume from offset
REGION           = 'USA'
UNIVERSE         = 'TOP3000'
INSTRUMENT_TYPE  = 'EQUITY'
DELAY            = 1
PAGE_SIZE        = 20            # max per request (API limit)
FIELDS_TRACKER   = 'fields_tracker.csv'
DATA_DIR         = 'data'
SLEEP_BETWEEN    = 3.0           # seconds between paginated requests (rate limit safe)

# API base
BASE_URL = 'https://api.worldquantbrain.com'

# ── HELPERS ───────────────────────────────────────────────────────────────────

def build_url(offset):
    return (
        f'{BASE_URL}/data-fields'
        f'?datasetId={DATASET_ID}'
        f'&delay={DELAY}'
        f'&instrumentType={INSTRUMENT_TYPE}'
        f'&region={REGION}'
        f'&universe={UNIVERSE}'
        f'&limit={PAGE_SIZE}'
        f'&offset={offset}'
    )

def scrape_all_fields(wq):
    """Paginate through all fields in the dataset. Returns list of dicts."""
    all_fields = []
    offset = START_OFFSET
    total = None
    if START_OFFSET > 0:
        print(f'  Resuming from offset={START_OFFSET}')

    while True:
        url = build_url(offset)
        print(f'  Fetching offset={offset}...', end=' ', flush=True)
        r = wq.get(url)

        try:
            data = r.json()
        except Exception as e:
            print(f'\n  ✗ Failed to parse JSON at offset {offset}: {e}')
            print(f'  Response: {r.text[:300]}')
            break

        # Retry on rate limit
        if isinstance(data, dict) and 'rate limit' in data.get('message', '').lower():
            wait = 30
            print(f'\n  ⚠ Rate limited — waiting {wait}s...', flush=True)
            time.sleep(wait)
            continue  # retry same offset

        # Print progress every 500 fields
        if len(all_fields) > 0 and len(all_fields) % 500 == 0:
            print(f'  Progress: {len(all_fields)}/{total}...')

        # Handle paginated dict response {count, next, results}
        if isinstance(data, list):
            # Shouldn't happen anymore, but handle gracefully
            all_fields.extend(data)
            print(f'  got {len(data)} (flat list)')
            break
        elif 'results' in data:
            results = data['results']
            if total is None:
                total = data.get('count', 0)
                print(f'  (total={total})')
            else:
                print(f'  got {len(results)}', flush=True)
            all_fields.extend(results)
            # Stop if no results returned or we have everything
            if not results or len(all_fields) >= total:
                break
        else:
            print(f'\n  ✗ Unexpected response: {str(data)[:300]}')
            break

        offset += PAGE_SIZE
        time.sleep(SLEEP_BETWEEN)

    return all_fields

def save_raw(fields, dataset_id):
    """Save raw scraped field data to data/ directory."""
    os.makedirs(DATA_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(DATA_DIR, f'fields_raw_{dataset_id}_{ts}.csv')

    if not fields:
        print('  No fields to save.')
        return out_path

    # Flatten nested dicts for CSV
    flat_fields = []
    for f in fields:
        if not isinstance(f, dict):
            continue
        row = {
            'field':       f.get('id', ''),
            'description': f.get('description', ''),
            'type':        f.get('type', ''),
            'dataset':     f.get('dataset', {}).get('id', dataset_id) if isinstance(f.get('dataset'), dict) else f.get('dataset', dataset_id),
            'delay':       f.get('delay', DELAY),
            'universe':    f.get('universe', UNIVERSE),
            'region':      f.get('region', REGION),
            'coverage':    f.get('coverage', ''),
            'category':    f.get('category', {}).get('name', '') if isinstance(f.get('category'), dict) else f.get('category', ''),
            'subcategory': f.get('subcategory', {}).get('name', '') if isinstance(f.get('subcategory'), dict) else f.get('subcategory', ''),
        }
        flat_fields.append(row)

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat_fields[0].keys()))
        writer.writeheader()
        writer.writerows(flat_fields)

    print(f'  Raw fields saved → {out_path}')
    return out_path, flat_fields

def merge_into_tracker(new_fields, tracker_path=FIELDS_TRACKER):
    """
    Merge newly scraped fields into fields_tracker.csv.
    - Adds fields not yet in the tracker (status='', notes='')
    - Never overwrites existing status/notes
    - Returns counts: (already_known, added)
    """
    # Load existing tracker
    existing = {}
    tracker_cols = []
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tracker_cols = reader.fieldnames or []
            for row in reader:
                existing[row.get('field', '')] = row

    # Determine columns — use existing tracker columns, add any missing ones
    needed_cols = ['field', 'category', 'description', 'dataset', 'status', 'notes']
    for col in needed_cols:
        if col not in tracker_cols:
            tracker_cols.append(col)

    already_known = 0
    added = 0
    new_rows = []

    for f in new_fields:
        field_id = f['field']
        if field_id in existing:
            already_known += 1
        else:
            # New field — add with blank status
            row = {col: '' for col in tracker_cols}
            row['field']       = field_id
            row['category']    = f.get('category', '')
            row['description'] = f.get('description', '')
            row['dataset']     = f.get('dataset', DATASET_ID)
            row['status']      = ''
            row['notes']       = ''
            existing[field_id] = row
            new_rows.append(field_id)
            added += 1

    # Write back — preserve all existing rows + new ones
    with open(tracker_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=tracker_cols, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(existing.values())

    return already_known, added, new_rows


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f'\n{"="*55}')
    print(f'  WQ Brain Field Scraper')
    print(f'  Dataset : {DATASET_ID}')
    print(f'  Region  : {REGION} | Universe: {UNIVERSE} | Delay: {DELAY}')
    print(f'{"="*55}\n')

    # Login
    print('Logging in...')
    wq = WQSession()
    print()

    # Scrape
    print(f'Scraping fields from dataset "{DATASET_ID}":')
    fields = scrape_all_fields(wq)
    print(f'\n  Total fields fetched: {len(fields)}')

    if not fields:
        print('\n⚠️  No fields returned. Possible causes:')
        print('  - Dataset ID is wrong (check the URL on the platform)')
        print('  - API endpoint has changed')
        print('  - Session auth failed silently')
        print('\nTry opening DevTools → Network on the platform page to find the correct endpoint.')
        sys.exit(1)

    # Save raw
    print('\nSaving raw output...')
    result = save_raw(fields, DATASET_ID)
    if isinstance(result, tuple):
        raw_path, flat_fields = result
    else:
        print('  Could not flatten fields — check raw JSON structure above.')
        sys.exit(1)

    # Merge into tracker
    print(f'\nMerging into {FIELDS_TRACKER}...')
    already_known, added, new_rows = merge_into_tracker(flat_fields)

    print(f'\n{"="*55}')
    print(f'  ✅ Done!')
    print(f'  Fields scraped  : {len(fields)}')
    print(f'  Already in tracker: {already_known}')
    print(f'  New fields added  : {added}')
    if new_rows:
        print(f'\n  New fields:')
        for r in new_rows[:20]:
            print(f'    {r}')
        if len(new_rows) > 20:
            print(f'    ... +{len(new_rows)-20} more (see {raw_path})')
    print(f'{"="*55}\n')
