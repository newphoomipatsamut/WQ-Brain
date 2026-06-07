#!/usr/bin/env python3
"""
seed_alphas.py — 101 Formulaic Alphas + Curated Seeds for WQ-Brain Pipeline
============================================================================
Sourced from "101 Formulaic Alphas" (Kakushadze, 2015) and jglazar/notes.
These are starting points — most need tuning (decay, neutralization, universe)
before they'll pass WQ Brain IS thresholds.

Usage:
  # Generate a parameters file from seed alphas
  python3 seed_alphas.py --count 30 --universe TOP3000

  # Generate from a specific category
  python3 seed_alphas.py --category price_volume --count 20

  # List all categories
  python3 seed_alphas.py --list

  # Import into orchestrator (programmatic)
  from seed_alphas import get_seeds, generate_seed_batch
"""

import argparse
import random
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ─── Seed Alpha Database ────────────────────────────────────────────────────
# Each entry: (expression, category, notes)
# Categories: price_volume, fundamental, analyst, sentiment, technical, model

SEED_ALPHAS = [
    # ── Price-Volume (from 101 Formulaic Alphas — FASTEXPR-translated) ──
    ('-rank(((1 - (open / close))^1))', 'price_volume', '#33 simple open/close ratio'),
    ('((close - open) / ((high - low) + .001))', 'price_volume', '#101 intraday range'),
    ('(sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1)))', 'price_volume', '#12 volume-price reversal'),
    ('(-1 * ts_corr(rank(open), rank(volume), 10))', 'price_volume', '#3 open-volume correlation'),
    ('(-1 * ts_rank(rank(low), 9))', 'price_volume', '#4 low rank'),
    ('(-1 * rank(ts_std_dev(high, 10))) * ts_corr(high, volume, 10)', 'price_volume', '#40 vol-weighted high'),
    ('(((high * low)^0.5) - vwap)', 'price_volume', '#41 geometric mean vs vwap'),
    ('rank((vwap - close)) / rank((vwap + close))', 'price_volume', '#42 vwap asymmetry'),
    ('(-1 * ts_corr(high, rank(volume), 5))', 'price_volume', '#44 high-volume corr'),
    ('(-1 * ts_delta((((close - low) - (high - close)) / (close - low)), 9))', 'price_volume', '#53 CLV change'),
    ('((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)))', 'price_volume', '#54 price ratios'),
    ('(-1 * ts_sum(rank(ts_corr(rank(high), rank(volume), 3)), 3))', 'price_volume', '#15 rolling high-vol corr'),
    ('((rank(ts_max((vwap - close), 3)) + rank(ts_min((vwap - close), 3))) * rank(ts_delta(volume, 3)))', 'price_volume', '#11 vwap range + volume delta'),

    # ── Price-Volume (from WQ website — confirmed good) ──
    ('(high + low)/2 - close', 'price_volume', 'WQ#5 midpoint deviation'),
    ('-1/ts_std_dev(returns, 22)', 'price_volume', 'WQ#10 inverse volatility'),
    ('-ts_delta(close, 5)', 'price_volume', 'WQ#15 5-day reversal'),
    ('-sign(close-vwap)', 'price_volume', 'WQ#20 vwap direction'),

    # ── Technical / Mean Reversion ──
    ('-rank(ts_delta(close, 2)) * rank(volume / ts_sum(volume, 30) / 30)', 'price_volume', 'Volume-weighted reversal'),
    ('rank(((0 < ts_min(ts_delta(close, 1), 4)) ? ts_delta(close, 1) : ((ts_max(ts_delta(close, 1), 4) < 0) ? ts_delta(close, 1) : (-1 * ts_delta(close, 1)))))', 'price_volume', '#10 conditional momentum'),
    ('(-1 * rank(((ts_sum(open, 5) * ts_sum(returns, 5)) - ts_delay((ts_sum(open, 5) * ts_sum(returns, 5)), 10))))', 'price_volume', '#8 open-returns momentum delta'),
    ('(((-1 * rank((open - ts_delay(high, 1)))) * rank((open - ts_delay(close, 1)))) * rank((open - ts_delay(low, 1))))', 'price_volume', '#20 triple gap'),
    ('-rank(ts_delta(close, 1))', 'price_volume', 'Simple 1-day reversal'),
    ('-rank(ts_delta(close, 5) / ts_delay(close, 5))', 'price_volume', '5-day pct reversal'),

    # ── Fundamental (verified fields from fields_tracker.csv) ──
    ('rank(sales/assets)', 'fundamental', 'Asset turnover efficiency'),
    ('rank(-ts_delta(debt, 90))', 'fundamental', 'Decreasing debt signal'),
    ('-rank(ebit/capex)', 'fundamental', 'Capital efficiency'),
    ('-ts_rank(retained_earnings, 250)', 'fundamental', 'Retained earnings rank'),
    ('zscore(ts_ir(cashflow_op/debt_st, 1250))', 'fundamental', 'CF/debt info ratio'),
    ('zscore(cash_st/debt_st)', 'fundamental', 'Cash-to-debt ratio'),
    ('rank(ts_rank(cogs/ppent, 240)) * (1 + rank(ts_rank(inventory_turnover, 240)))', 'fundamental', 'Cost efficiency composite'),
    ('-rank(ts_rank(inventory/(assets-goodwill), 60)) * rank(ts_rank(inventory_turnover, 120))', 'fundamental', 'Inventory quality composite'),
    ('group_neutralize(rank(-ts_delta(debt, 60)/assets), sector)', 'fundamental', 'Sector-neutral deleveraging'),
    ('rank(ts_zscore(inventory_turnover, 240))', 'fundamental', 'Inventory turnover zscore'),
    ('-rank(ts_delta(debt/assets, 252))', 'fundamental', 'Leverage change'),
    ('-rank(ts_rank(debt_st/cash_st, 252))', 'fundamental', 'Short-term debt burden'),
    ('rank(ts_rank(sales_ps, 252))', 'fundamental', 'Sales per share trend'),

    # ── Analyst (verified fields) ──
    ('rank(ts_rank(est_eps/close, 40))', 'analyst', 'Earnings yield rank'),
    ('-rank(ts_delta(close/est_eps, 5))', 'analyst', 'PE ratio momentum'),
    ('-rank(ts_zscore(est_eps, 252))', 'analyst', 'EPS estimate zscore'),
    ('rank(ts_rank(est_eps, 126))', 'analyst', 'EPS estimate rank'),

    # ── Options (verified field) ──
    ('-rank(ts_rank(pcr_oi_all, 60))', 'options', 'Put-call ratio rank'),
    ('rank(ts_zscore(pcr_oi_all, 126))', 'options', 'Put-call ratio zscore'),
]

# ─── Category mapping ───────────────────────────────────────────────────────
CATEGORY_MAP = {
    'price_volume': 'Price Volume',
    'fundamental': 'Fundamental',
    'analyst': 'Analyst',
    'sentiment': 'Sentiment',
    'options': 'Options',
    'model': 'Model',
    'technical': 'Price Volume',
}


def get_seeds(category: str = None, count: int = None, shuffle: bool = True) -> list[tuple[str, str, str]]:
    """
    Get seed alphas, optionally filtered by category.
    Returns list of (expression, category, notes) tuples.
    """
    seeds = SEED_ALPHAS
    if category:
        cat_lower = category.lower().replace(' ', '_')
        seeds = [s for s in seeds if s[1] == cat_lower]
    if shuffle:
        seeds = list(seeds)
        random.shuffle(seeds)
    if count:
        seeds = seeds[:count]
    return seeds


def generate_seed_batch(count: int = 30, universe: str = 'TOP3000',
                        category: str = None, decay: int = 6) -> Path:
    """
    Generate a parameters file from seed alphas.
    Returns path to the generated file.
    """
    seeds = get_seeds(category=category, count=count)
    if not seeds:
        print(f"No seeds found for category '{category}'")
        return None

    ts = datetime.now().strftime('%m%d_%H%M')
    cat_label = category.replace(' ', '_').lower() if category else 'mixed'
    filename = BASE_DIR / f'parameters_seed_{cat_label}_{ts}.py'

    univ_var = {
        'TOP3000': 'BASE',
        'TOP500': 'B500',
        'TOP200': 'B200',
    }

    lines = [
        f'# parameters_seed_{cat_label}_{ts}.py',
        f'# Seed alphas from 101 Formulaic Alphas + curated sources',
        f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        f'# Run: cp {filename.name} parameters.py && python3 main.py',
        '',
        'from commands import *',
        f"BATCH_NAME = 'seed_{cat_label}_{ts}'",
        '',
        "BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}",
        "B500 = {**BASE, 'universe': 'TOP500'}",
        "B200 = {**BASE, 'universe': 'TOP200'}",
        '',
        'DATA = [',
    ]

    var = univ_var.get(universe, 'BASE')
    for expr, cat, notes in seeds:
        lines.append(f"    # {notes} [{cat}]")
        lines.append(f"    {{**{var}, 'decay': {decay}, 'code': {repr(expr)}}},")
        # Also test on TOP200 if primary is TOP3000
        if universe == 'TOP3000':
            lines.append(f"    {{**B200, 'decay': {decay}, 'code': {repr(expr)}}},")

    lines += [
        ']',
        '',
        'print(f"Total seed expressions queued: {len(DATA)}")',
        f'print(f"  Estimated runtime: ~{{len(DATA)*1.5:.0f}} min")',
        '',
    ]

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Seed batch written: {filename.name} ({len(seeds)} seeds, {len(seeds) * (2 if universe == 'TOP3000' else 1)} expressions)")
    return filename


def main():
    parser = argparse.ArgumentParser(description='Generate seed alpha batches from curated expressions')
    parser.add_argument('--count', '-n', type=int, default=30, help='Number of seeds to use')
    parser.add_argument('--universe', '-u', default='TOP3000', choices=['TOP3000', 'TOP500', 'TOP200'])
    parser.add_argument('--category', '-c', default=None, help='Filter by category')
    parser.add_argument('--decay', '-d', type=int, default=6, help='Decay setting')
    parser.add_argument('--list', action='store_true', help='List all categories and counts')
    args = parser.parse_args()

    if args.list:
        from collections import Counter
        counts = Counter(cat for _, cat, _ in SEED_ALPHAS)
        print(f"\nSeed alpha database: {len(SEED_ALPHAS)} total")
        for cat, n in counts.most_common():
            print(f"  {cat:<20} {n:>3}")
        return

    generate_seed_batch(args.count, args.universe, args.category, args.decay)


if __name__ == '__main__':
    main()
