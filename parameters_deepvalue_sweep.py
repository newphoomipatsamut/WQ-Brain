# parameters_deepvalue_sweep.py
# DeepValue Sweep — untested mdl177_2_deepvaluefactor fields
# Generated: 2026-05-25
#
# Strategy: DeepValue family had Fitness up to 1.65 in IQC2026.
# Testing the 7 untested mdl177_2_ fields + pdy_alt retest.
#
# Templates:
#   A: -rank(ts_rank(field, 252))                       — pure rank momentum
#   B: -rank(ts_decay_linear(field, 21) * rank(ts_delta(close, 5)))  — value × price momentum
#   C: -rank(hump(ts_rank(field, 252)))                 — fitness fix variant
#
# Untested mdl177_2_ fields:
#   acqmul   — invested capital / trailing EBITDA
#   bp       — book-to-price
#   cashp    — cash per share / price
#   proformaep — pro forma earnings-to-price (excl. special items)
#   ttmfcfev — TTM free cash flow / enterprise value
#   ttmocfp  — TTM operating cash flow per share / price
#   ttmpiqp  — TTM price-implied quality premium
#
# Also: pdy_alt retest (sharpe=1.19, fit=0.99, failed checks=4 — near miss!)
#
# Run: cp parameters_deepvalue_sweep.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'deepvalue_sweep'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}
MKT  = {**BASE, 'neutralization': 'MARKET'}
M200 = {**B200, 'neutralization': 'MARKET'}

DATA = [

    # ══════════════════════════════════════════════════════════════════
    # pdy_alt — RETEST (sharpe=1.19, fit=0.99, checks=4 — near miss!)
    # Previously: -rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt,252)))
    # Fitness is fine (0.99), problem is checks count. Try more universes.
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},
    {**B200,  'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},
    {**MKT,   'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},
    {**M200,  'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},
    {**BASE,  'code': '-rank(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252))'},
    {**B200,  'code': '-rank(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # acqmul — invested capital / EBITDA (acquisition multiple)
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_acqmul, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_acqmul, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_acqmul, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_acqmul, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_acqmul, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_acqmul, 252)))'},

    # ══════════════════════════════════════════════════════════════════
    # bp — book-to-price
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_bp, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_bp, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_bp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_bp, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_bp, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_bp, 252)))'},

    # ══════════════════════════════════════════════════════════════════
    # cashp — cash per share / price
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_cashp, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_cashp, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_cashp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_cashp, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_cashp, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_cashp, 252)))'},

    # ══════════════════════════════════════════════════════════════════
    # proformaep — pro forma earnings-to-price (excl. special items)
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_proformaep, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_proformaep, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_proformaep, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_proformaep, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_proformaep, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_proformaep, 252)))'},

    # ══════════════════════════════════════════════════════════════════
    # ttmfcfev — TTM free cash flow / enterprise value
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmfcfev, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmfcfev, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_ttmfcfev, 252)))'},

    # ══════════════════════════════════════════════════════════════════
    # ttmocfp — TTM operating cash flow per share / price
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmocfp, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmocfp, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmocfp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmocfp, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmocfp, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_ttmocfp, 252)))'},

    # ══════════════════════════════════════════════════════════════════
    # ttmpiqp — TTM price-implied quality premium
    # ══════════════════════════════════════════════════════════════════
    {**BASE, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmpiqp, 252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmpiqp, 252))'},
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_deepvaluefactor_ttmpiqp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmpiqp, 21) * rank(ts_delta(close, 5)))'},
    {**B200, 'code': '-rank(ts_decay_linear(mdl177_2_deepvaluefactor_ttmpiqp, 21) * rank(ts_delta(close, 5)))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_deepvaluefactor_ttmpiqp, 252)))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: deepvalue_sweep | 7 untested fields + pdy_alt retest")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
