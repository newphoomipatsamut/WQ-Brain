#!/usr/bin/env python3
"""
diagnose_alpha_api.py — Dump raw API responses so we can see the real data structure.

Run AFTER the orchestrator finishes (to avoid rate limits):
    python3 diagnose_alpha_api.py [alpha_id]

If no alpha_id given, uses the first link found in data/*.csv.
"""
import json
import re
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# ── Find an alpha ID ──────────────────────────────────────────────────────────
alpha_id = None
if len(sys.argv) > 1:
    raw = sys.argv[1].strip()
    m = re.search(r'/alpha/(\w+)', raw)
    alpha_id = m.group(1) if m else raw
else:
    for csv_file in sorted((BASE_DIR / 'data').glob('*.csv')):
        if csv_file.name.startswith('_'):
            continue
        for line in csv_file.read_text(errors='ignore').splitlines():
            m = re.search(r'worldquantbrain\.com/alpha/(\w+)', line)
            if m:
                alpha_id = m.group(1)
                print(f"Using alpha from {csv_file.name}: {alpha_id}\n")
                break
        if alpha_id:
            break

if not alpha_id:
    print("No alpha ID found. Pass one as an argument: python3 diagnose_alpha_api.py <id>")
    sys.exit(1)

# ── Authenticate using the full WQSession login flow ─────────────────────────
from main import WQSession
print("Logging in...")
session = WQSession()   # handles biometric polling, cookies, everything
print()

BASE_URL = 'https://api.worldquantbrain.com'


def dump(label: str, url: str, retries: int = 3):
    print("=" * 60)
    print(label)
    print("=" * 60)
    for attempt in range(retries):
        r = session.get(url)
        print(f"Status: {r.status_code}")
        if r.status_code == 429:
            wait = int(r.headers.get('Retry-After', 30))
            print(f"Rate limited — waiting {wait}s before retry {attempt + 1}/{retries}...")
            time.sleep(wait)
            continue
        try:
            print(json.dumps(r.json(), indent=2, default=str))
        except Exception:
            print(r.text[:3000])
        break
    print()


dump(f"GET /alphas/{alpha_id}", f"{BASE_URL}/alphas/{alpha_id}")
dump(f"GET /alphas/{alpha_id}/check", f"{BASE_URL}/alphas/{alpha_id}/check")
