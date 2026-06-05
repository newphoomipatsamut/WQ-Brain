# parameters_neut_sweep.py
# Neutralization Sweep — MARKET + INDUSTRY variants on all near-misses
# Generated: 2026-05-25
#
# WQ Brain tip: try various neutralization
# All prior runs used SUBINDUSTRY. Testing MARKET and INDUSTRY on the
# top near-miss expressions (Fitness 0.85–0.97).
#
# Near-miss targets (confirmed expressions, verified links):
#   CLV decay5   TOP3000  sharpe=1.82 fit=0.96  → N1Ak9G9g
#   CLV×vol/adv  TOP3000  sharpe=1.82 fit=0.97  → 88ngAM3q
#   CLV+Vol/ADV  TOP3000  sharpe=1.65 fit=0.89  → VkOKn775
#   CLV decay10  TOP3000  sharpe=1.56 fit=0.91  → JjbRLO2O
#   ADV20 ts_rank(21)     sharpe=1.93 fit=0.85  → xARXXm8q
#
# Also sweep neutralization on the best 5yr RelValue expressions
# since those are stuck at Fitness 0.70–0.78.
#
# Run: cp parameters_neut_sweep.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'neut_sweep'

BASE  = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500  = {**BASE, 'universe': 'TOP500'}
B200  = {**BASE, 'universe': 'TOP200'}
MKT   = {**BASE, 'neutralization': 'MARKET'}
IND   = {**BASE, 'neutralization': 'INDUSTRY'}
M500  = {**B500, 'neutralization': 'MARKET'}
M200  = {**B200, 'neutralization': 'MARKET'}
I500  = {**B500, 'neutralization': 'INDUSTRY'}
I200  = {**B200, 'neutralization': 'INDUSTRY'}

DATA = [

    # ── CLV decay5 TOP3000 — sharpe=1.82 fit=0.96 ────────────────────────────────
    {**MKT,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**IND,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**M500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**I500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**M200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**I200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},

    # ── CLV×tsrank(vol/adv20,10) decay5 TOP3000 — sharpe=1.82 fit=0.97 ───────────
    {**MKT,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},
    {**IND,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},
    {**M500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},
    {**I500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},
    {**M200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},
    {**I200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},

    # ── CLV+Vol/ADV20 decay5 TOP3000 — sharpe=1.65 fit=0.89 ─────────────────────
    {**MKT,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**IND,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**M500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**I500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**M200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**I200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},

    # ── CLV decay10 TOP3000 — sharpe=1.56 fit=0.91 ───────────────────────────────
    {**MKT,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},
    {**IND,  'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},
    {**M200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},
    {**I200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},

    # ── ADV20 ts_rank(21) TOP3000 — sharpe=1.93 fit=0.85 ────────────────────────
    {**MKT,  'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**IND,  'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**M500, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**I500, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**M200, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**I200, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},

    # ── ADV20 decay10 TOP3000 — sharpe=1.33 fit=0.79 (6 checks passed) ──────────
    {**MKT,  'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},
    {**IND,  'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},
    {**M500, 'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},
    {**I500, 'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},

    # ── 5yr RelValue — MARKET + INDUSTRY on best-performing fields ───────────────
    # rel5yocfp TOP3000 sharpe=1.23 fit=0.76
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},
    {**IND,  'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},
    {**M200, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},
    {**I200, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},

    # rel5yebitdap TOP3000 sharpe=1.16 fit=0.74
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},
    {**IND,  'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},
    {**M200, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},
    {**I200, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},

    # rel5yfcfp×Momentum TOP3000 sharpe=1.38 fit=0.78
    {**MKT,  'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 21) * rank(ts_delta(close, 5)))'},
    {**IND,  'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 21) * rank(ts_delta(close, 5)))'},
    {**M200, 'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 21) * rank(ts_delta(close, 5)))'},

    # rel5ycfp TOP3000 sharpe=1.18 fit=0.76
    {**MKT,  'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 252))'},
    {**IND,  'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 252))'},
    {**M200, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 252))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: neut_sweep | MARKET + INDUSTRY neutralization on all near-misses")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
