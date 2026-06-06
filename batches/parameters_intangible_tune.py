# parameters_intangible_tune.py
# Intangible Assets — Tuning + Near-Miss Sweep — Session 25
# Generated: 2026-06-03
#
# PASSES (from llm_fundamental batch):
#   mLXLPa35: -rank(ts_rank(acquired_intangible_avg_useful_life, 252)) TOP200
#              Sharpe=1.33, Fit=1.38, 6/7, TO=2.61%, corr=0.153, score=+1007
#   78d8kP1Q: -rank(hump(ts_rank(acquired_intangible_avg_useful_life, 252))) TOP200
#              Sharpe=1.25, Fit=1.22, 6/7, TO=2.32%, corr=0.170, score=+993
#
# Strategy:
#   GROUP A — Tune acquired_intangible_avg_useful_life
#     Score > +100 → tune before submitting
#     Try: different lookbacks (63, 126, 504), TOP500, positive sign, zscore
#     Also: check self-corr between the two passes before submitting both
#
#   GROUP B — Near-miss sweep: goodwill & intangibles family
#     acquired_goodwill_value TOP200: best sharpe=0.93, fit=0.70 → fitness block
#     acquisition_goodwill_amount TOP200: best sharpe=0.89, fit=0.81 → very close
#     acquired_finite_intangible_assets_total TOP200: sharpe=1.19, fit=1.03, 5/7 → checks block
#     acquired_finite_intangible_assets TOP200: sharpe=0.93, fit=0.85 → fitness block
#
#   GROUP C — Related fields not yet tested
#     acquired_intangible_avg_useful_life variants (other templates / normalizations)
#     intangible_assets (raw balance sheet intangibles)
#     intangible_assets_net
#
# Run: cp parameters_intangible_tune.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'intangible_tune'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}
MKT  = {**BASE, 'neutralization': 'MARKET'}
M200 = {**B200, 'neutralization': 'MARKET'}

DATA = [

    # ══════════════════════════════════════════════════════════════════
    # GROUP A — Tune: acquired_intangible_avg_useful_life
    # Both passes are TOP200. Check if TOP500 also passes (more capacity).
    # Check self-corr between mLXLPa35 and 78d8kP1Q — may be > 0.70.
    # ══════════════════════════════════════════════════════════════════

    # Lookback sweep — baseline is 252, try shorter and longer
    {**B200, 'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 126))'},
    {**B200, 'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 504))'},
    {**B200, 'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 63))'},

    # TOP500 — does the signal hold at larger universe?
    {**B500, 'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 252))'},
    {**B500, 'code': '-rank(hump(ts_rank(acquired_intangible_avg_useful_life, 252)))'},
    {**B500, 'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 126))'},

    # Zscore variant (already failed TOP200 checks but try TOP500)
    {**B500, 'code': '-rank(ts_zscore(acquired_intangible_avg_useful_life, 252))'},
    {**B200, 'code': '-rank(ts_zscore(acquired_intangible_avg_useful_life, 126))'},

    # Positive sign (long high useful-life stocks directly)
    {**B200, 'code': 'rank(ts_rank(acquired_intangible_avg_useful_life, 252))'},
    {**B500, 'code': 'rank(ts_rank(acquired_intangible_avg_useful_life, 252))'},

    # Decay×momentum variant
    {**B200, 'code': '-rank(ts_decay_linear(acquired_intangible_avg_useful_life, 21) * rank(ts_delta(close, 5)))'},
    {**B500, 'code': '-rank(ts_decay_linear(acquired_intangible_avg_useful_life, 21) * rank(ts_delta(close, 5)))'},

    # MARKET neutralization — different exposure
    {**M200, 'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 252))'},
    {**MKT,  'code': '-rank(ts_rank(acquired_intangible_avg_useful_life, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP B — Near-miss: acquired_goodwill_value
    # TOP200 best: sharpe=0.93, fit=0.70 — fitness block
    # Strategy: longer lookback to reduce turnover, hump, MARKET neut
    # ══════════════════════════════════════════════════════════════════
    {**B200, 'code': '-rank(ts_rank(acquired_goodwill_value, 504))'},
    {**B200, 'code': '-rank(ts_rank(acquired_goodwill_value, 126))'},
    {**B200, 'code': '-rank(hump(ts_rank(acquired_goodwill_value, 252)))'},
    {**B500, 'code': '-rank(ts_rank(acquired_goodwill_value, 252))'},
    {**B500, 'code': '-rank(ts_rank(acquired_goodwill_value, 504))'},
    {**M200, 'code': '-rank(ts_rank(acquired_goodwill_value, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP C — Near-miss: acquisition_goodwill_amount
    # TOP200 best: sharpe=0.89, fit=0.81 — closest to passing
    # ══════════════════════════════════════════════════════════════════
    {**B200, 'code': '-rank(ts_rank(acquisition_goodwill_amount, 504))'},
    {**B200, 'code': '-rank(ts_rank(acquisition_goodwill_amount, 126))'},
    {**B200, 'code': '-rank(hump(ts_rank(acquisition_goodwill_amount, 252)))'},
    {**B500, 'code': '-rank(ts_rank(acquisition_goodwill_amount, 252))'},
    {**B500, 'code': '-rank(ts_rank(acquisition_goodwill_amount, 504))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP D — Near-miss: acquired_finite_intangible_assets_total
    # TOP200: sharpe=1.19, fit=1.03, but only 5/7 checks — checks block
    # Strategy: try different lookbacks / TOP500 to fix the failing check
    # ══════════════════════════════════════════════════════════════════
    {**B200, 'code': '-rank(ts_rank(acquired_finite_intangible_assets_total, 126))'},
    {**B200, 'code': '-rank(ts_rank(acquired_finite_intangible_assets_total, 504))'},
    {**B500, 'code': '-rank(ts_rank(acquired_finite_intangible_assets_total, 252))'},
    {**B500, 'code': '-rank(ts_zscore(acquired_finite_intangible_assets_total, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP E — Related untested fields (same M&A intangibles family)
    # ══════════════════════════════════════════════════════════════════
    # intangible_assets — raw balance sheet line
    {**B200, 'code': '-rank(ts_rank(intangible_assets, 252))'},
    {**B500, 'code': '-rank(ts_rank(intangible_assets, 252))'},
    {**B200, 'code': '-rank(ts_decay_linear(intangible_assets, 21) * rank(ts_delta(close, 5)))'},

    # intangible_assets_net
    {**B200, 'code': '-rank(ts_rank(intangible_assets_net, 252))'},
    {**B500, 'code': '-rank(ts_rank(intangible_assets_net, 252))'},

    # acquired_intangible_assets (broader: all intangibles from acquisitions)
    {**B200, 'code': '-rank(ts_rank(acquired_intangible_assets, 252))'},
    {**B200, 'code': '-rank(ts_rank(acquired_intangible_assets, 504))'},
    {**B500, 'code': '-rank(ts_rank(acquired_intangible_assets, 252))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: intangible_tune | Tune acquired_intangible_avg_useful_life + goodwill/intangibles near-misses")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
