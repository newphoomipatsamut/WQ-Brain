# parameters_bvps_tune.py
# book_value_per_share_min_guidance_qtr — Fitness Fix — Session 25
# Generated: 2026-06-04
#
# Near-miss: YPAKoRq6
#   rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5)))
#   TOP3000 | Sharpe=1.36, Fitness=0.76, 6/7, TO=34.81%
#
# Problem: TO=34.81% → fitness ceiling 0.76. Need TO below ~20% for fitness ≥ 1.00.
# Strategy:
#   A) Heavier decay (30/40/60) — primary fix for high-TO decay×mom signals
#   B) hump() wrapper — secondary dampening
#   C) Pure ts_rank (lower structural TO than decay×mom)
#   D) MARKET neutralization — different exposure, may lower TO
#   E) TOP200 with heavier decay — self-corr control
#
# Run: cp parameters_bvps_tune.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'bvps_tune'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}
MKT  = {**BASE, 'neutralization': 'MARKET'}
M200 = {**B200, 'neutralization': 'MARKET'}

DATA = [

    # ── GROUP A: Heavier decay — primary fix ──────────────────────────────────
    # Current decay=21 gives TO=34.8%. Need to roughly halve it.
    {**BASE, 'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 30) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 40) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 60) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 30) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 40) * rank(ts_delta(close, 5)))'},

    # ── GROUP B: hump() wrapper ───────────────────────────────────────────────
    {**BASE, 'code': 'rank(hump(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5))))'},
    {**BASE, 'code': 'rank(hump(ts_decay_linear(book_value_per_share_min_guidance_qtr, 30) * rank(ts_delta(close, 5))))'},
    {**B200, 'code': 'rank(hump(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5))))'},

    # ── GROUP C: Pure ts_rank — structurally lower TO ─────────────────────────
    {**BASE, 'code': 'rank(ts_rank(book_value_per_share_min_guidance_qtr, 252))'},
    {**BASE, 'code': 'rank(ts_rank(book_value_per_share_min_guidance_qtr, 126))'},
    {**BASE, 'code': 'rank(ts_zscore(book_value_per_share_min_guidance_qtr, 252))'},
    {**B200, 'code': 'rank(ts_rank(book_value_per_share_min_guidance_qtr, 252))'},
    {**B200, 'code': 'rank(ts_rank(book_value_per_share_min_guidance_qtr, 126))'},

    # ── GROUP D: MARKET neutralization ────────────────────────────────────────
    {**MKT,  'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5)))'},
    {**MKT,  'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 30) * rank(ts_delta(close, 5)))'},
    {**M200, 'code': 'rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5)))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: bvps_tune | book_value_per_share_min_guidance_qtr fitness fix")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
