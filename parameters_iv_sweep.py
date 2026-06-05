# parameters_iv_sweep.py
# Implied Volatility Expiry Sweep — Session 24
# Generated: 2026-05-29
#
# Background:
#   iv_call_60 had Sharpe 1.94–1.96 in prior sessions but was always
#   self-corr blocked (0.94 vs A9/A10 in the book). Strategy: test
#   different expirations and the mean/skew families which should be
#   structurally less correlated.
#
# Field families tested:
#   A) IV Call — expirations 30, 90, 120, 270 (skip 60 — corr blocked)
#   B) IV Mean (call+put avg) — 60, 90, 120, 270
#   C) IV Mean Skew — 30, 60, 90, 120 (NEW — 90% vs 110% moneyness spread)
#      Skew = fear gauge. High skew = expensive puts = bearish sentiment.
#   D) IV Term Structure Spreads — short minus long expiration
#      Contango: short IV < long IV (normal). Backwardation: short > long (fear).
#
# Universe: TOP500 (recommended in strategy doc for IV signals)
# Also testing TOP200 for self-corr control
#
# Run: cp parameters_iv_sweep.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'iv_sweep'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}
MKT  = {**BASE, 'neutralization': 'MARKET'}

DATA = [

    # ══════════════════════════════════════════════════════════════════
    # GROUP A — IV Call (non-60 expirations)
    # Avoid iv_call_60 — confirmed corr-blocked with A9/A10
    # ══════════════════════════════════════════════════════════════════
    {**B500, 'code': '-rank(ts_rank(implied_volatility_call_30, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_call_30, 252))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_call_30, 21) * rank(ts_delta(close, 5)))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_call_90, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_call_90, 252))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_call_90, 21) * rank(ts_delta(close, 5)))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_call_120, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_call_120, 252))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_call_120, 21) * rank(ts_delta(close, 5)))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_call_270, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_call_270, 252))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_call_270, 21) * rank(ts_delta(close, 5)))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP B — IV Mean (call + put average)
    # More balanced signal — may have lower overlap with call-only book alphas
    # ══════════════════════════════════════════════════════════════════
    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_60, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_60, 252))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_mean_60, 21) * rank(ts_delta(close, 5)))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_90, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_90, 252))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_120, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_120, 252))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_270, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP C — IV Mean Skew (brand new — untested family)
    # Skew = IV(90% moneyness) - IV(110% moneyness)
    # High skew = puts expensive relative to calls = bearish fear signal
    # Going short high-skew stocks (fear premium) often mean-reverts
    # ══════════════════════════════════════════════════════════════════
    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_skew_30, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_skew_30, 252))'},
    {**B500, 'code': '-rank(ts_zscore(implied_volatility_mean_skew_30, 252))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_skew_60, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_skew_60, 252))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_mean_skew_60, 21) * rank(ts_delta(close, 5)))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_skew_90, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_skew_90, 252))'},

    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_skew_120, 252))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_skew_120, 252))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP D — IV Term Structure Spreads
    # Short - Long expiration spread = volatility curve shape
    # Backwardation (short > long): near-term fear, potential mean-reversion
    # Contango (short < long): normal vol curve
    # ══════════════════════════════════════════════════════════════════
    # Call term structure
    {**B500, 'code': '-rank(ts_rank(implied_volatility_call_30 - implied_volatility_call_270, 63))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_call_30 - implied_volatility_call_270, 63))'},
    {**B500, 'code': '-rank(ts_rank(implied_volatility_call_30 - implied_volatility_call_120, 63))'},
    {**B500, 'code': '-rank(ts_decay_linear(implied_volatility_call_30 - implied_volatility_call_270, 21) * rank(ts_delta(close, 5)))'},

    # Mean term structure
    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_30 - implied_volatility_mean_270, 63))'},
    {**B200, 'code': '-rank(ts_rank(implied_volatility_mean_30 - implied_volatility_mean_270, 63))'},
    {**B500, 'code': '-rank(ts_rank(implied_volatility_mean_60 - implied_volatility_mean_270, 63))'},

    # ══════════════════════════════════════════════════════════════════
    # GROUP E — IV Rate of Change
    # Rising IV predicts volatility; sharp IV spikes often mean-revert
    # ══════════════════════════════════════════════════════════════════
    {**B500, 'code': '-rank(ts_rank(ts_delta(implied_volatility_call_30, 21), 63))'},
    {**B500, 'code': '-rank(ts_rank(ts_delta(implied_volatility_mean_60, 21), 63))'},
    {**B200, 'code': '-rank(ts_rank(ts_delta(implied_volatility_mean_60, 21), 63))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batch: iv_sweep | Call(30/90/120/270) + Mean(60/90/120/270) + Skew(30/60/90/120) + Spreads + RoC")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
