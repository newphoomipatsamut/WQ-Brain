#!/usr/bin/env python3
"""
combine_alphas.py — Generate ensemble alphas from your passing expression book.

A signal that combines two passing alphas from different factor families is
structurally uncorrelated with either parent and typically clears the
self-correlation check. This is the primary strategy for scaling past 20 alphas.

How it works:
  1. Load all passing expressions from data/ CSVs (sharpe >= 1.25, fitness >= 1.0)
  2. Keep the best expression per unique field (deduplicate)
  3. Group by dataset family (mdl177, mdl53, anl4_fs_, fundamental, etc.)
  4. Generate cross-family pairs only — same-family pairs are correlated by construction
  5. For each pair, produce:
       Sum:     -rank(norm_A + norm_B)       equal-weight composite
       Product: -rank(norm_A * norm_B)       AND filter (good on both signals)
     Each in TOP3000 and TOP200

Usage (standalone):
    python3 combine_alphas.py              # write batch file only
    python3 combine_alphas.py --simulate   # write + simulate

Usage (via orchestrator):
    python3 orchestrator.py --combine
    python3 orchestrator.py --combine --dry-run
"""

import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
BANNED_OPS = ('ts_decay_linear',)


# ─── Expression helpers ───────────────────────────────────────────────────────

def _strip_outer_rank(code: str) -> str:
    """Strip the outermost -rank() or rank() wrapper to get the inner signal."""
    code = code.strip()
    if code.startswith('-rank(') and code.endswith(')'):
        return code[6:-1]
    if code.startswith('rank(') and code.endswith(')'):
        return code[5:-1]
    return code


def _get_dataset(field: str) -> str:
    """
    Return a dataset-family key. Pairs from the same family are skipped
    because they are structurally correlated.
      mdl177_2_deepvaluefactor_ttmfcfev → 'mdl177'
      mdl53_jc5_1year                   → 'mdl53'
      anl4_fs_sales_fy1                 → 'anl4_fs'
      acquired_intangible_*             → full field name (each fundamental is its own family)
    """
    if not field:
        return 'unknown'
    f = field.lower()
    m = re.match(r'^(mdl\d+)', f)
    if m:
        return m.group(1)
    if f.startswith('anl4_'):
        parts = f.split('_')
        return '_'.join(parts[:3]) if len(parts) >= 3 else 'anl4'
    # Raw fundamental / price-volume fields — treat each as its own family
    return field


def _extract_lookback(code: str) -> int:
    """Extract the first numeric argument from an expression (the lookback), default 252."""
    m = re.search(r',\s*(\d+)\)', code)
    return int(m.group(1)) if m else 252


def _already_normalized(inner: str) -> bool:
    """True when the inner expression is already bounded (ts_rank/ts_zscore/hump output)."""
    return inner.startswith(('ts_rank(', 'ts_zscore(', 'hump('))


def _check_parens(expr: str) -> bool:
    """Quick parenthesis balance check."""
    depth = 0
    for ch in expr:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


# ─── Candidate loading ────────────────────────────────────────────────────────

def load_candidates() -> list[dict]:
    """
    Return one dict per unique passing field, best Sharpe wins.
    Drops expressions using banned operators.
    """
    from alpha_utils import load_passing_expressions
    passes = load_passing_expressions(DATA_DIR)
    passes = [p for p in passes if not any(op in p['code'] for op in BANNED_OPS)]

    seen: dict[str, dict] = {}
    for p in passes:
        field = p.get('field', '')
        if not field or field == '?':
            continue
        if field not in seen or p['sharpe'] > seen[field]['sharpe']:
            seen[field] = p

    return list(seen.values())


# ─── Combination generation ───────────────────────────────────────────────────

_BASE = {
    'neutralization': 'SUBINDUSTRY',
    'decay': 6,
    'truncation': 0.08,
    'delay': 1,
    'region': 'USA',
}


def generate_combinations(candidates: list[dict]) -> list[dict]:
    """
    Return a list of simulation dicts for all valid cross-family pairs.
    Each pair produces 4 expressions: (sum, product) × (TOP3000, TOP200).
    """
    entries = []

    for i, a in enumerate(candidates):
        for b in candidates[i + 1:]:
            # Skip same-dataset pairs — structurally correlated
            if _get_dataset(a['field']) == _get_dataset(b['field']):
                continue

            inner_a = _strip_outer_rank(a['code'])
            inner_b = _strip_outer_rank(b['code'])
            lb_a = _extract_lookback(a['code'])
            lb_b = _extract_lookback(b['code'])

            # Normalize both signals to a bounded range before combining
            norm_a = inner_a if _already_normalized(inner_a) else f'ts_rank({inner_a}, {lb_a})'
            norm_b = inner_b if _already_normalized(inner_b) else f'ts_rank({inner_b}, {lb_b})'

            fa = a['field'][:28]
            fb = b['field'][:28]

            combos = [
                (f'-rank({norm_a} + {norm_b})', f'sum: {fa} + {fb}'),
                (f'-rank({norm_a} * {norm_b})', f'product: {fa} × {fb}'),
            ]

            for code, label in combos:
                if not _check_parens(code):
                    continue
                for univ in ('TOP3000', 'TOP200'):
                    entries.append({
                        **_BASE,
                        'universe': univ,
                        'code': code,
                        '_comment': f'# {label} [{univ}]',
                    })

    return entries


# ─── Batch file writer ────────────────────────────────────────────────────────

def build_combination_batch() -> Path | None:
    """
    Load candidates, generate combinations, write a parameters_combo_*.py file.
    Returns the Path to the written file, or None if nothing was generated.
    """
    print("\n" + "═" * 60)
    print("  Alpha Combination — loading passing expressions")
    print("═" * 60)

    candidates = load_candidates()
    if not candidates:
        print("No passing expressions found in data/. Run more batches first.")
        return None

    print(f"\n{len(candidates)} unique passing fields:")
    for c in candidates:
        ds = _get_dataset(c['field'])
        print(f"  [{ds:15}] {c['field'][:45]}  sharpe={c['sharpe']:.2f}")

    entries = generate_combinations(candidates)
    if not entries:
        print(
            "\nNo cross-family pairs found — all passing alphas are from the same dataset.\n"
            "Run more batches to collect passes from different factor families."
        )
        return None

    unique_codes = len(set(e['code'] for e in entries))
    print(f"\n{unique_codes} unique combinations → {len(entries)} expressions (×2 universes, ×2 templates)")

    ts = datetime.now().strftime('%m%d_%H%M')
    filename = BASE_DIR / f'parameters_combo_{ts}.py'
    batch_name = f'combo_{ts}'

    lines = [
        f'# parameters_combo_{ts}.py',
        f'# Auto-generated alpha combination batch — {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# {unique_codes} cross-family pairs × 2 templates × 2 universes = {len(entries)} expressions',
        f"BATCH_NAME = '{batch_name}'",
        '',
        'from commands import *',
        '',
        "BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}",
        "B200  = {**BASE, 'universe': 'TOP200'}",
        '',
        'DATA = [',
    ]

    for e in entries:
        var = 'B200' if e['universe'] == 'TOP200' else 'BASE'
        lines.append(f"    {e['_comment']}")
        lines.append(f"    {{**{var}, 'code': {repr(e['code'])}}},")

    lines += [
        ']',
        '',
        'print(f"Combo expressions queued: {len(DATA)}")',
        f'print(f"  Estimated runtime: ~{{len(DATA) * 1.5:.0f}} min")',
        '',
    ]

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\nBatch written → {filename.name}  ({len(entries)} expressions)")
    return filename


# ─── Standalone entry point ───────────────────────────────────────────────────

def run_combine(simulate: bool = False) -> None:
    """Called directly (python3 combine_alphas.py) or from orchestrator --combine."""
    params_file = build_combination_batch()
    if params_file is None:
        return

    if not simulate:
        print(f"\nDry run. To simulate:")
        print(f"  python3 orchestrator.py --combine")
        return

    sys.path.insert(0, str(BASE_DIR))
    from orchestrator import run_simulation
    results_csv = run_simulation(params_file)
    if results_csv:
        print(f"\nResults → {results_csv.name}")
        print("Tip: run python3 update_tracker.py to update the field tracker.")


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Generate alpha combination expressions')
    p.add_argument('--simulate', action='store_true', help='Also run the simulation (default: write file only)')
    args = p.parse_args()
    run_combine(simulate=args.simulate)
