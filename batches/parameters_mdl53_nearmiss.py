# parameters_mdl53_nearmiss.py
# mdl53 Credit Curve Near-Miss Sweep — Session 24
# Generated: 2026-05-28
#
# Target: -rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5)))
#   sharpe=1.31, fit=0.99, checks=6/7, TO=15.06% — ONE tick from passing
#
# Strategy:
#   - Fitness=0.99 means turnover is right at the edge — very small nudge needed
#   - Try hump() wrapper, different universes, different decay periods, MARKET neut
#   - Also sweep other promising jc5/jm5 spread pairs that showed signal
#   - Try jm5_4year - jm5_1year (fit=0.89) with same fixes
#
# Run: cp parameters_mdl53_nearmiss.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'mdl53_nearmiss'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}
MKT  = {**BASE, 'neutralization': 'MARKET'}
M200 = {**B200, 'neutralization': 'MARKET'}

DATA = [

    # ══════════════════════════════════════════════════════════════════
    # PRIMARY TARGET — jc5_5year - jc5_6month × Momentum
    # sharpe=1.31, fit=0.99, TO=15% — tiny nudge needed
    # ══════════════════════════════════════════════════════════════════
    # Base expression — different universes
    {**B200, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5)))'},
    {**MKT,  'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5)))'},
    {**M200, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5)))'},
    {**B500, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5)))'},
    # hump() wrapper to slightly reduce turnover
    {**BASE, 'code': '-rank(hump(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5))))'},
    {**B200, 'code': '-rank(hump(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 21) * rank(ts_delta(close, 5))))'},
    # Different decay periods
    {**BASE, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 10) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 15) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 30) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_6month, 15) * rank(ts_delta(close, 5)))'},
    # Pure ts_rank variant (no momentum)
    {**BASE, 'code': '-rank(ts_rank(mdl53_jc5_5year - mdl53_jc5_6month, 63))'},
    {**B200, 'code': '-rank(ts_rank(mdl53_jc5_5year - mdl53_jc5_6month, 63))'},
    {**BASE, 'code': '-rank(ts_rank(mdl53_jc5_5year - mdl53_jc5_6month, 126))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl53_jc5_5year - mdl53_jc5_6month, 63)))'},

    # ══════════════════════════════════════════════════════════════════
    # jc5 curve inversion — sharpe=1.31, fit=0.71 (TO block)
    # rank(ts_rank(jc5_1year - jc5_10year, 63)) — inversion signal
    # TO=17% but fitness block — try hump to reduce further
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': 'rank(hump(ts_rank(mdl53_jc5_1year - mdl53_jc5_10year, 63)))'},
    {**B200, 'code': 'rank(ts_rank(mdl53_jc5_1year - mdl53_jc5_10year, 63))'},
    {**MKT,  'code': 'rank(ts_rank(mdl53_jc5_1year - mdl53_jc5_10year, 63))'},
    {**BASE, 'code': 'rank(ts_decay_linear(mdl53_jc5_1year - mdl53_jc5_10year, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': 'rank(ts_decay_linear(mdl53_jc5_1year - mdl53_jc5_10year, 21) * rank(ts_delta(close, 5)))'},

    # ══════════════════════════════════════════════════════════════════
    # jm5 spread — sharpe=1.27, fit=0.89 (jm5_4year - jm5_1year)
    # ══════════════════════════════════════════════════════════════════
    {**B200, 'code': '-rank(ts_decay_linear(mdl53_jm5_4year - mdl53_jm5_1year, 21) * rank(ts_delta(close, 5)))'},
    {**MKT,  'code': '-rank(ts_decay_linear(mdl53_jm5_4year - mdl53_jm5_1year, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl53_jm5_4year - mdl53_jm5_1year, 63)))'},
    {**B200, 'code': '-rank(ts_rank(mdl53_jm5_4year - mdl53_jm5_1year, 63))'},
    # Try jm5 5year spread
    {**BASE, 'code': '-rank(ts_decay_linear(mdl53_jm5_5year - mdl53_jm5_6month, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl53_jm5_5year - mdl53_jm5_6month, 21) * rank(ts_delta(close, 5)))'},

    # ══════════════════════════════════════════════════════════════════
    # jc6 spread — untested, same model family as jc5
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_decay_linear(mdl53_jc6_5year - mdl53_jc6_6month, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl53_jc6_5year - mdl53_jc6_6month, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(ts_rank(mdl53_jc6_5year - mdl53_jc6_6month, 63))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl53_jc6_4year - mdl53_jc6_1year, 21) * rank(ts_delta(close, 5)))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: mdl53_nearmiss | jc5 5yr-6mo spread + inversion + jm5/jc6 variants")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
