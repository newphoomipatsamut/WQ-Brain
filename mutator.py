#!/usr/bin/env python3
"""
mutator.py — Genetic Mutation Engine for WQ-Brain Alpha Expressions
====================================================================
Takes passing or near-miss alpha expressions and generates variants via:
  1. Operator swaps (ts_rank <-> ts_zscore <-> ts_decay_linear)
  2. Lookback window mutations (shorter/longer)
  3. Wrapper additions (hump, log, abs, sigmoid)
  4. Group argument swaps (sector <-> industry <-> subindustry)
  5. Arithmetic crossover (combine two alphas)
  6. Neutralization swaps

Inspired by worldquant-miner's genetic evolution approach.

Usage:
  # Generate mutations from historical passes
  python3 mutator.py --count 40

  # Mutate a specific expression
  python3 mutator.py --expr "-rank(ts_rank(sales_ps, 252))" --count 10

  # Programmatic
  from mutator import mutate_expression, mutate_batch, crossover
"""

import argparse
import random
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ─── Mutation operators ─────────────────────────────────────────────────────

# Swappable time-series wrappers (structurally similar)
TS_WRAPPERS = ['ts_rank', 'ts_zscore', 'ts_std_dev', 'ts_mean']

# Swappable outer wrappers
OUTER_WRAPPERS = ['rank', 'sigmoid', 'zscore', 'scale']

# Signal smoothers that can wrap a field
SMOOTHERS = ['hump', 'log', 'abs']

# Lookback windows to try
LOOKBACKS = [22, 42, 63, 126, 252, 504]

# Group arguments
GROUPS = ['market', 'sector', 'industry', 'subindustry']

# Universes
UNIVERSES = ['TOP3000', 'TOP200']

# Neutralization options
NEUTRALIZATIONS = ['SUBINDUSTRY', 'INDUSTRY', 'SECTOR', 'MARKET']

# Decay values
DECAYS = [0, 2, 4, 6, 8, 10, 13]


def _swap_ts_wrapper(code: str) -> list[str]:
    """Swap one time-series wrapper for another."""
    variants = []
    for old_op in TS_WRAPPERS:
        if old_op in code:
            for new_op in TS_WRAPPERS:
                if new_op != old_op:
                    new_code = code.replace(old_op, new_op, 1)
                    variants.append(new_code)
            break
    return variants


def _mutate_lookback(code: str) -> list[str]:
    """Change lookback window parameters."""
    variants = []
    # Find all numeric lookback parameters in ts_* calls
    for m in re.finditer(r'(ts_\w+\([^,]+,\s*)(\d+)', code):
        current_lb = int(m.group(2))
        for new_lb in LOOKBACKS:
            if new_lb != current_lb:
                new_code = code[:m.start(2)] + str(new_lb) + code[m.end(2):]
                variants.append(new_code)
    return variants


def _add_smoother(code: str) -> list[str]:
    """Wrap the inner field with a smoother function."""
    variants = []
    # Find the innermost field in a ts_* or rank() call
    m = re.search(r'(ts_\w+|rank)\((\w+)', code)
    if m:
        op, field = m.group(1), m.group(2)
        # Don't wrap if already wrapped
        for smoother in SMOOTHERS:
            if smoother not in code and field not in {'rank', 'ts_rank', 'ts_zscore'}:
                new_code = code.replace(f'{op}({field}', f'{op}({smoother}({field})', 1)
                # Balance parentheses
                if new_code.count('(') != new_code.count(')'):
                    new_code += ')'
                variants.append(new_code)
    return variants


def _swap_group(code: str) -> list[str]:
    """Swap group_rank/group_zscore group arguments."""
    variants = []
    m = re.search(r'(group_\w+\(.+?,\s*)(\w+)(\))', code)
    if m:
        current_group = m.group(2)
        if current_group in GROUPS:
            for new_group in GROUPS:
                if new_group != current_group:
                    new_code = m.group(1) + new_group + m.group(3)
                    # Preserve anything before and after the match
                    new_code = code[:m.start()] + new_code + code[m.end():]
                    variants.append(new_code)
    return variants


def _swap_outer_wrapper(code: str) -> list[str]:
    """Swap the outermost wrapper (rank -> sigmoid, etc.)."""
    variants = []
    # Match -rank( or rank( at the start
    m = re.match(r'^(-?)(rank|sigmoid|zscore|scale)\(', code)
    if m:
        sign, current = m.group(1), m.group(2)
        for new_wrap in OUTER_WRAPPERS:
            if new_wrap != current:
                new_code = sign + new_wrap + code[m.end()-1:]
                variants.append(new_code)
        # Also try flipping the sign
        if sign == '-':
            variants.append(code[1:])  # remove minus
        else:
            variants.append('-' + code)  # add minus
    return variants


def _add_momentum_factor(code: str) -> list[str]:
    """Multiply by a momentum factor (delta or volume)."""
    variants = []
    # Only if not already using multiplication
    if ' * ' not in code and '*rank' not in code:
        for factor in ['rank(ts_delta(close, 5))', 'rank(volume/adv20)', 'rank(returns)']:
            variants.append(f'{code} * {factor}')
            variants.append(f'-({code} * {factor})')
    return variants


def _to_decay_linear(code: str) -> list[str]:
    """DISABLED — ts_decay_linear is banned: too correlated with submitted
    Alpha 10, Performance Comparison score change consistently negative."""
    return []


def mutate_expression(code: str, max_variants: int = 10) -> list[str]:
    """
    Generate mutated variants of an alpha expression.
    Returns a deduplicated list of valid variant expressions.
    """
    all_variants = []

    all_variants.extend(_swap_ts_wrapper(code))
    all_variants.extend(_mutate_lookback(code))
    all_variants.extend(_add_smoother(code))
    all_variants.extend(_swap_group(code))
    all_variants.extend(_swap_outer_wrapper(code))
    all_variants.extend(_add_momentum_factor(code))
    all_variants.extend(_to_decay_linear(code))

    # Deduplicate and filter
    seen = {code}  # exclude original
    unique = []
    for v in all_variants:
        v = v.strip()
        if v not in seen and v != code:
            # Basic validation: balanced parentheses
            if v.count('(') == v.count(')'):
                seen.add(v)
                unique.append(v)

    # Shuffle and cap
    random.shuffle(unique)
    return unique[:max_variants]


def crossover(code1: str, code2: str) -> list[str]:
    """
    Combine two alpha expressions into new ones.
    Strategies: arithmetic combination, conditional, correlation.
    """
    variants = []

    # Strategy 1: Additive combination (equal weight)
    variants.append(f'rank({code1}) + rank({code2})')
    variants.append(f'rank({code1}) * rank({code2})')

    # Strategy 2: Use one as a filter for the other
    # If code1 is positive, use code2
    variants.append(f'({code1} > 0) ? {code2} : (-1 * {code2})')

    # Strategy 3: Correlation between the two
    from alpha_utils import extract_field
    f1, f2 = extract_field(code1), extract_field(code2)
    if f1 and f2 and f1 != f2:
        variants.append(f'-rank(ts_corr({f1}, {f2}, 63))')
        variants.append(f'-rank(ts_corr({f1}, {f2}, 252))')

    return variants


def mutate_batch(expressions: list[dict], count: int = 40,
                 universe: str = 'TOP3000') -> Path | None:
    """
    Generate a mutation batch from a list of expression dicts.
    Each dict must have 'code' and optionally 'universe', 'field'.

    Returns path to the generated parameters file.
    """
    if not expressions:
        print("No expressions to mutate.")
        return None

    ts = datetime.now().strftime('%m%d_%H%M')
    filename = BASE_DIR / f'parameters_mutant_{ts}.py'

    all_entries = []  # (universe, code, comment)

    for expr_dict in expressions:
        code = expr_dict['code']
        field = expr_dict.get('field', '?')
        orig_univ = expr_dict.get('universe', universe)

        variants = mutate_expression(code, max_variants=8)
        for v in variants:
            all_entries.append((orig_univ, v, f'# Mutant of {field}: {code[:50]}'))
            # Also try on the other universe
            other_univ = 'TOP200' if orig_univ == 'TOP3000' else 'TOP3000'
            all_entries.append((other_univ, v, f'# Mutant+{other_univ} of {field}'))

    # Crossover: pair up expressions and combine
    if len(expressions) >= 2:
        pairs = []
        for i in range(min(5, len(expressions))):
            j = (i + 1) % len(expressions)
            pairs.append((expressions[i], expressions[j]))

        for e1, e2 in pairs:
            crosses = crossover(e1['code'], e2['code'])
            f1 = e1.get('field', '?')
            f2 = e2.get('field', '?')
            for c in crosses:
                all_entries.append((universe, c, f'# Crossover: {f1} x {f2}'))

    # Deduplicate
    seen = set()
    deduped = []
    for univ, code, comment in all_entries:
        key = (univ, code)
        if key not in seen:
            seen.add(key)
            deduped.append((univ, code, comment))
    all_entries = deduped

    # Cap
    if len(all_entries) > count:
        random.shuffle(all_entries)
        all_entries = all_entries[:count]

    univ_map = {'TOP3000': 'BASE', 'TOP500': 'B500', 'TOP200': 'B200'}

    lines = [
        f'# parameters_mutant_{ts}.py',
        f'# Genetic mutations of {len(expressions)} parent expressions',
        f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# Run: cp {filename.name} parameters.py && python3 main.py',
        '',
        'from commands import *',
        f"BATCH_NAME = 'mutant_{ts}'",
        '',
        "BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}",
        "B500 = {**BASE, 'universe': 'TOP500'}",
        "B200 = {**BASE, 'universe': 'TOP200'}",
        '',
        'DATA = [',
    ]

    for univ, code, comment in all_entries:
        var = univ_map.get(univ, 'BASE')
        lines.append(f"    {comment}")
        lines.append(f"    {{**{var}, 'code': {repr(code)}}},")

    lines += [
        ']',
        '',
        'print(f"Total mutant expressions: {len(DATA)}")',
        f'print(f"  Estimated runtime: ~{{len(DATA)*1.5:.0f}} min")',
        '',
    ]

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Mutation batch written: {filename.name} ({len(all_entries)} expressions from {len(expressions)} parents)")
    return filename


def main():
    parser = argparse.ArgumentParser(description='Generate mutated alpha expressions')
    parser.add_argument('--count', '-n', type=int, default=40, help='Max mutations to generate')
    parser.add_argument('--expr', '-e', default=None, help='Mutate a specific expression')
    parser.add_argument('--universe', '-u', default='TOP3000', choices=['TOP3000', 'TOP500', 'TOP200'])
    args = parser.parse_args()

    if args.expr:
        # Single expression mode
        variants = mutate_expression(args.expr, max_variants=args.count)
        print(f"\nMutations of: {args.expr}\n")
        for i, v in enumerate(variants, 1):
            print(f"  {i:>2}. {v}")
        print(f"\n{len(variants)} variants generated.")
        return

    # Batch mode: load passing expressions from data/
    from alpha_utils import load_passing_expressions
    passes = load_passing_expressions(BASE_DIR / 'data')

    if not passes:
        print("No passing expressions found in data/. Try --expr to mutate a specific expression.")
        return

    print(f"Found {len(passes)} passing expressions. Generating mutations...")
    mutate_batch(passes[:10], count=args.count, universe=args.universe)


if __name__ == '__main__':
    main()
