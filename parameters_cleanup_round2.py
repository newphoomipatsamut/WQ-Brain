# parameters_cleanup_round2.py
# Near-Miss Fitness Fix Sweep — Session 24
# Generated: 2026-05-28
#
# Targets all active near-misses with fitness < 1.00:
#
# GROUP 1 — CLV family (structural high-TO, needs heavier decay)
#   Best so far: decay=5 → fit=0.96/0.97. Try decay=10/15/20.
#   Also try longer outer ts_rank to reduce flip frequency.
#
# GROUP 2 — ADV20 reversion (ts_rank(21) → turnover 71.7%, checks=5)
#   High TO is structural. Try hump(), decay wrappers, shorter ts_rank.
#
# GROUP 3 — New DeepValue near-misses (fit=0.88 across the board)
#   ttmfcfev ts_rank TOP3000: fit=0.88 → try hump + TOP200 + MARKET
#   ttmpiqp decay×mom TOP3000: fit=0.88 → try hump + TOP200
#   bp decay×mom TOP3000: fit=0.88 → try hump + TOP200
#
# Run: cp parameters_cleanup_round2.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'cleanup_round2'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}
MKT  = {**BASE, 'neutralization': 'MARKET'}
M200 = {**B200, 'neutralization': 'MARKET'}

DATA = [

    # ══════════════════════════════════════════════════════════════════
    # GROUP 1 — CLV × ts_rank(volume/adv20) — best: sharpe=1.82, fit=0.97
    # Strategy: heavier decay to reduce turnover below fitness threshold
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 10))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 15))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 20))'},
    {**B200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 10))'},
    {**B200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 15))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP 1B — CLV × ts_rank(volume) — best: sharpe=1.82, fit=0.96
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 15))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 20))'},
    {**B200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},
    {**B200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 15))'},
    # hump variant — wrap inner signal to reduce turnover differently
    {**BASE, 'code': '-rank(ts_decay_linear(hump(((2*close-high-low)/(high-low))*ts_rank(volume,5)), 5))'},
    {**BASE, 'code': '-rank(ts_decay_linear(hump(((2*close-high-low)/(high-low))*ts_rank(volume,5)), 10))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP 1C — CLV × volume/adv20 — best: sharpe=1.65, fit=0.89
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 10))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 15))'},
    {**B200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 10))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP 2 — ADV20 reversion — sharpe=1.93, fit=0.85, checks=5
    # Problem: turnover=71.7% kills fitness. Need heavy damping.
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(hump(ts_rank(ts_delta(close,1)/adv20, 21)))'},
    {**BASE, 'code': '-rank(ts_decay_linear(ts_rank(ts_delta(close,1)/adv20, 21), 5))'},
    {**BASE, 'code': '-rank(ts_decay_linear(ts_rank(ts_delta(close,1)/adv20, 21), 10))'},
    {**B200, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**B200, 'code': '-rank(hump(ts_rank(ts_delta(close,1)/adv20, 21)))'},
    # Shorter ts_rank lookback to reduce turnover
    {**BASE, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 10))'},
    {**BASE, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 63))'},
    {**B200, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 10))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP 3 — ttmfcfev ts_rank TOP3000 — sharpe=1.39, fit=0.88
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252)))'},
    {**B200, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252)))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252))'},
    {**M200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP 4 — ttmpiqp decay×momentum TOP3000 — sharpe=1.37, fit=0.88
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_ttmpiqp, 252)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmpiqp, 21) * rank(ts_delta(close, 5)))'},
    {**MKT,  'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmpiqp, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmpiqp, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP 5 — bp decay×momentum TOP3000 — sharpe=1.36, fit=0.88
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_bp, 252)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_bp, 21) * rank(ts_delta(close, 5)))'},
    {**MKT,  'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_bp, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_bp, 252))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: cleanup_round2 | CLV heavier decay + ADV20 + DeepValue fitness fixes")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
