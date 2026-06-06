#!/usr/bin/env python3
"""
alpha_miner.py — Alpha Expression Miner for WQ Brain
======================================================
Takes any passing alpha expression and generates a ready-to-run
parameters_*.py batch file covering:
  - Lookback window sweeps
  - hump() and ts_decay_linear() Fitness fix wrappers
  - Sign flip (rank vs -rank)
  - Universe variants (TOP3000, TOP500, TOP200)
  - Neutralization variants (SUBINDUSTRY, INDUSTRY, MARKET)

Usage:
  python3 alpha_miner.py
  python3 alpha_miner.py --expression "-rank(ts_rank(mdl177_2_relativevaluemodel_ttmfcfp, 252))"
  python3 alpha_miner.py --expression "..." --batch-name "my_sweep" --no-interactive

Output: parameters_miner_<batch_name>.py  (drop-in replacement for parameters.py)
"""

import re
import argparse
import itertools
from datetime import datetime
from pathlib import Path


# ─── Defaults ────────────────────────────────────────────────────────────────

BASE_SETTINGS = {
    'neutralization': 'SUBINDUSTRY',
    'decay': 6,
    'truncation': 0.08,
    'delay': 1,
    'region': 'USA',
    'universe': 'TOP3000',
}

UNIVERSE_PRESETS = {
    'TOP3000': {**BASE_SETTINGS, 'universe': 'TOP3000'},
    'TOP200':  {**BASE_SETTINGS, 'universe': 'TOP200'},
}


# ─── Expression Analysis ──────────────────────────────────────────────────────

def find_numeric_params(expression):
    """Find all numeric values in an expression with their context."""
    pattern = re.compile(r'(\b\d+\.?\d*\b)')
    matches = []
    for m in pattern.finditer(expression):
        val = m.group()
        start = max(0, m.start() - 30)
        end = min(len(expression), m.end() + 30)
        context = expression[start:end]
        matches.append({
            'value': float(val),
            'raw': val,
            'start': m.start(),
            'end': m.end(),
            'context': f'...{context}...',
        })
    return matches


def detect_outer_sign(expression):
    """Detect if the expression starts with -rank or rank."""
    expr = expression.strip()
    if expr.startswith('-rank(') or expr.startswith('(-rank('):
        return 'negative'
    elif expr.startswith('rank('):
        return 'positive'
    return 'unknown'


def flip_sign(expression):
    """Flip -rank(...) ↔ rank(...) at the outermost level."""
    expr = expression.strip()
    if expr.startswith('-rank('):
        return 'rank(' + expr[len('-rank('):]
    elif expr.startswith('rank('):
        return '-rank(' + expr[len('rank('):]
    # Try wrapping
    return f'-({expr})'


def apply_hump_wrapper(expression):
    """Wrap the inner signal with hump() to reduce turnover.

    Handles two cases:
      1. -rank(ts_rank(...))   → -rank(hump(ts_rank(...)))
      2. -rank(ANYTHING)       → -rank(hump(ANYTHING))   [general case]
    """
    expr = expression.strip()

    # Case 1: explicit ts_rank / ts_zscore inner — wrap just that
    result = re.sub(
        r'(-?rank\()(ts_rank\(|ts_zscore\()',
        r'\1hump(\2',
        expr,
        count=1
    )
    if result != expr:
        result = _close_hump(result)
        return result

    # Case 2: general — wrap everything inside the outermost rank()
    m = re.match(r'^(-?rank\()(.*)\)$', expr, re.DOTALL)
    if m:
        return f'{m.group(1)}hump({m.group(2)}))'

    return expr


def _close_hump(expression):
    """Insert closing ) for hump( before the final rank close-paren."""
    # Simple approach: find hump( and count parens to close it
    idx = expression.find('hump(')
    if idx == -1:
        return expression
    # Count from hump( forward to find matching )
    depth = 0
    for i in range(idx + 5, len(expression)):
        if expression[i] == '(':
            depth += 1
        elif expression[i] == ')':
            if depth == 0:
                return expression[:i] + ')' + expression[i:]
            depth -= 1
    return expression


def apply_decay_wrapper(expression, decay_period=5):
    """Wrap the inner signal with ts_decay_linear() to reduce turnover.

    Handles two cases:
      1. -rank(ts_rank(...))  → -rank(ts_decay_linear(ts_rank(...), N))
      2. -rank(ANYTHING)      → -rank(ts_decay_linear(ANYTHING, N))
    """
    expr = expression.strip()

    # Case 1: explicit ts_rank / ts_zscore inner
    result = re.sub(
        r'(-?rank\()(ts_rank\(|ts_zscore\()',
        rf'\1ts_decay_linear(\2',
        expr,
        count=1
    )
    if result != expr:
        result = _close_decay(result, decay_period)
        return result

    # Case 2: general — wrap everything inside the outermost rank()
    m = re.match(r'^(-?rank\()(.*)\)$', expr, re.DOTALL)
    if m:
        return f'{m.group(1)}ts_decay_linear({m.group(2)}, {decay_period}))'

    return expr


def _close_decay(expression, period):
    """Insert closing , period) for ts_decay_linear(."""
    idx = expression.find('ts_decay_linear(')
    if idx == -1:
        return expression
    start = idx + len('ts_decay_linear(')
    depth = 0
    for i in range(start, len(expression)):
        if expression[i] == '(':
            depth += 1
        elif expression[i] == ')':
            if depth == 0:
                return expression[:i] + f', {period})' + expression[i:]
            depth -= 1
    return expression


def sweep_lookback(expression, param_value, candidates):
    """Generate variants with different lookback values."""
    variants = []
    raw = str(int(param_value)) if param_value == int(param_value) else str(param_value)
    for c in candidates:
        new_raw = str(int(c)) if c == int(c) else str(c)
        # Only replace the specific lookback (avoid replacing wrong numbers)
        # Replace only the first occurrence of this number as a standalone arg
        new_expr = re.sub(
            r'(?<=[,()\s])' + re.escape(raw) + r'(?=[),\s])',
            new_raw,
            expression,
            count=1
        )
        if new_expr != expression:
            variants.append(new_expr)
    return variants


# ─── Variation Generator ──────────────────────────────────────────────────────

def generate_variations(expression, config):
    """
    Generate all requested expression variants from config.
    Returns list of (label, expression, universe) tuples.
    """
    variations = []
    base_expr = expression.strip()

    # 1. Base expression across requested universes
    for univ in config['universes']:
        variations.append((f'base_{univ}', base_expr, univ))

    # 2. Sign flip
    if config['flip_sign']:
        flipped = flip_sign(base_expr)
        if flipped != base_expr:
            for univ in config['universes']:
                variations.append((f'flip_{univ}', flipped, univ))

    # 3. hump() wrapper (Fitness fix)
    if config['apply_hump']:
        humped = apply_hump_wrapper(base_expr)
        if humped != base_expr:
            for univ in config['universes']:
                variations.append((f'hump_{univ}', humped, univ))

    # 4. ts_decay_linear() wrapper (Fitness fix)
    if config['apply_decay']:
        for dp in config['decay_periods']:
            decayed = apply_decay_wrapper(base_expr, dp)
            if decayed != base_expr:
                for univ in config['universes']:
                    variations.append((f'decay{dp}_{univ}', decayed, univ))

    # 5. Lookback sweep
    if config['sweep_lookbacks'] and config['lookback_candidates']:
        params = find_numeric_params(base_expr)
        # Target the largest numeric param (most likely the lookback window)
        if params:
            # Prefer params >= 20 (likely a lookback, not a small constant)
            lookback_params = [p for p in params if p['value'] >= 20]
            if not lookback_params:
                lookback_params = params
            target = lookback_params[0]  # Use first/largest
            for candidate in config['lookback_candidates']:
                if candidate == target['value']:
                    continue
                new_expr = re.sub(
                    r'(?<=[,()\s])' + re.escape(target['raw']) + r'(?=[),\s])',
                    str(int(candidate)) if candidate == int(candidate) else str(candidate),
                    base_expr,
                    count=1
                )
                if new_expr != base_expr:
                    for univ in config['universes']:
                        variations.append((f'lb{int(candidate)}_{univ}', new_expr, univ))

    # 6. Deduplicate while preserving order
    seen = set()
    unique = []
    for label, expr, univ in variations:
        key = (expr, univ)
        if key not in seen:
            seen.add(key)
            unique.append((label, expr, univ))

    return unique


# ─── Parameter File Writer ────────────────────────────────────────────────────

def write_parameters_file(variations, batch_name, original_expression, config, output_path):
    """Write a ready-to-run parameters_*.py file."""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'parameters_miner_{batch_name}.py'
    filepath = output_path / filename

    lines = []
    lines.append(f'# {filename}')
    lines.append(f'# Auto-generated by alpha_miner.py — {ts}')
    lines.append(f'# Source expression: {original_expression}')
    lines.append(f'# Total variants: {len(variations)}')
    lines.append(f'# Run: cp {filename} parameters.py && python3 main.py')
    lines.append('')
    lines.append('from commands import *')
    lines.append(f"BATCH_NAME = 'miner_{batch_name}'")
    lines.append('')
    lines.append('BASE   = {' + f"'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'" + '}')
    lines.append('B500   = {**BASE, ' + "'universe': 'TOP500'" + '}')
    lines.append('B200   = {**BASE, ' + "'universe': 'TOP200'" + '}')
    lines.append('')
    lines.append('UNIV = {')
    lines.append("    'TOP3000': BASE,")
    lines.append("    'TOP500':  B500,")
    lines.append("    'TOP200':  B200,")
    lines.append('}')
    lines.append('')
    lines.append('DATA = [')

    # Group by label for readability
    prev_group = None
    for label, expr, univ in variations:
        group = label.split('_')[0]
        if group != prev_group:
            lines.append(f'    # --- {group} ---')
            prev_group = group
        lines.append(f"    {{**UNIV['{univ}'], 'code': {repr(expr)}}},")

    lines.append(']')
    lines.append('')
    lines.append('print(f"Total expressions queued: {len(DATA)}")')
    lines.append(f'print("  Source: {original_expression[:60]}...")')
    univs_str = str(config['universes'])
    lines.append(f'print("  Variants: {len(variations)} | Universes: {univs_str}")')
    lines.append('print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")')
    lines.append('')

    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))

    return filepath


# ─── Interactive Mode ─────────────────────────────────────────────────────────

def interactive_config(expression):
    """Walk the user through sweep configuration interactively."""
    print('\n' + '='*60)
    print('  Alpha Expression Miner — Interactive Setup')
    print('='*60)
    print(f'\nExpression: {expression}')

    # Detect numeric params
    params = find_numeric_params(expression)
    if params:
        print('\nNumeric parameters detected:')
        for i, p in enumerate(params):
            print(f'  {i+1}. Value: {p["value"]} | Context: {p["context"]}')

    config = {}

    # Universes
    print('\nUniverses to test (default: TOP3000 TOP200):')
    print('  Options: TOP3000, TOP500, TOP200 (space-separated, or press Enter for default)')
    raw = input('  > ').strip()
    if raw:
        config['universes'] = [u.strip().upper() for u in raw.split()]
    else:
        config['universes'] = ['TOP3000', 'TOP200']

    # Sign flip
    sign = detect_outer_sign(expression)
    print(f'\nSign detected: {sign}')
    raw = input('  Generate flipped sign variant? (y/n, default y): ').strip().lower()
    config['flip_sign'] = raw != 'n'

    # hump() wrapper
    print('\nApply hump() wrapper to reduce turnover (Fitness fix)?')
    raw = input('  (y/n, default y): ').strip().lower()
    config['apply_hump'] = raw != 'n'

    # ts_decay_linear() wrapper
    print('\nApply ts_decay_linear() wrapper to reduce turnover?')
    raw = input('  (y/n, default y): ').strip().lower()
    config['apply_decay'] = raw != 'n'
    config['decay_periods'] = [5, 10]
    if config['apply_decay']:
        raw = input('  Decay periods (default: 5 10, space-separated): ').strip()
        if raw:
            config['decay_periods'] = [int(x) for x in raw.split()]

    # Lookback sweep
    print('\nSweep lookback windows?')
    raw = input('  (y/n, default y): ').strip().lower()
    config['sweep_lookbacks'] = raw != 'n'
    config['lookback_candidates'] = []
    if config['sweep_lookbacks'] and params:
        lookback_params = [p for p in params if p['value'] >= 20]
        if lookback_params:
            target = lookback_params[0]
            print(f'\n  Target lookback: {target["value"]} | Context: {target["context"]}')
            print('  Enter sweep range (e.g. "10" for ±10, or "100,300" for explicit range):')
            raw = input('  > ').strip()
            if raw:
                if ',' in raw:
                    parts = raw.split(',')
                    lo, hi = int(parts[0]), int(parts[1])
                    print('  Step size (default 21): ', end='')
                    step_raw = input().strip()
                    step = int(step_raw) if step_raw else 21
                    config['lookback_candidates'] = list(range(lo, hi + 1, step))
                else:
                    delta = int(raw)
                    base = int(target['value'])
                    step = max(1, delta // 5)
                    config['lookback_candidates'] = list(range(
                        max(5, base - delta), base + delta + 1, step
                    ))
        else:
            print('  No lookback parameters found (no values >= 20). Skipping sweep.')

    # Batch name
    print('\nBatch name (default: sweep):')
    raw = input('  > ').strip()
    config['batch_name'] = raw if raw else 'sweep'

    return config


def default_config(batch_name='sweep'):
    """Return a sensible default config without user interaction."""
    return {
        'universes': ['TOP3000', 'TOP200'],
        'flip_sign': True,
        'apply_hump': True,
        'apply_decay': True,
        'decay_periods': [5, 10],
        'sweep_lookbacks': True,
        'lookback_candidates': [126, 189, 252, 315, 378],  # 6m, 9m, 12m, 15m, 18m
        'batch_name': batch_name,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Generate WQ Brain parameter sweep batches from a single expression.'
    )
    parser.add_argument(
        '--expression', '-e',
        type=str,
        help='Alpha expression to mine (e.g. "-rank(ts_rank(FIELD, 252))")'
    )
    parser.add_argument(
        '--batch-name', '-b',
        type=str,
        default=None,
        help='Name for the batch (used in filename and BATCH_NAME)'
    )
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Use default settings without prompting'
    )
    parser.add_argument(
        '--universes',
        type=str,
        default=None,
        help='Universes to test, comma-separated (e.g. TOP3000,TOP200)'
    )
    parser.add_argument(
        '--lookbacks',
        type=str,
        default=None,
        help='Lookback windows, comma-separated (e.g. 126,189,252,315)'
    )
    args = parser.parse_args()

    print('\n' + '='*60)
    print('  WQ Brain Alpha Expression Miner')
    print('='*60)

    # Get expression
    if args.expression:
        expression = args.expression.strip()
    else:
        print('\nEnter the alpha expression to mine:')
        expression = input('  > ').strip()

    if not expression:
        print('ERROR: No expression provided.')
        return

    # Get config
    if args.no_interactive:
        batch_name = args.batch_name or 'sweep'
        config = default_config(batch_name)
        if args.universes:
            config['universes'] = [u.strip().upper() for u in args.universes.split(',')]
        if args.lookbacks:
            config['lookback_candidates'] = [int(x) for x in args.lookbacks.split(',')]
        config['batch_name'] = batch_name
    else:
        config = interactive_config(expression)
        if args.batch_name:
            config['batch_name'] = args.batch_name

    # Generate variations
    print(f'\nGenerating variations...')
    variations = generate_variations(expression, config)
    print(f'  Generated {len(variations)} unique variants')

    if not variations:
        print('ERROR: No variations generated. Check your expression.')
        return

    # Preview
    print('\nPreview (first 10):')
    for label, expr, univ in variations[:10]:
        print(f'  [{univ}] {label}: {expr[:70]}{"..." if len(expr) > 70 else ""}')
    if len(variations) > 10:
        print(f'  ... and {len(variations) - 10} more')

    # Write file
    output_path = Path(__file__).parent
    filepath = write_parameters_file(
        variations,
        config['batch_name'],
        expression,
        config,
        output_path
    )

    print(f'\n✅ Written: {filepath.name}')
    print(f'\nTo run:')
    print(f'  cp {filepath.name} parameters.py && python3 main.py')
    print(f'\nEstimated runtime: ~{len(variations) * 1.5:.0f} min ({len(variations)} simulations)')


if __name__ == '__main__':
    main()
