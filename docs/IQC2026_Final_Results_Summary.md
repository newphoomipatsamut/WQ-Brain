# IQC 2026 — Final Results Summary
> **Researcher:** Phoomipat | **Generated:** May 24, 2026 | **Competition:** IQC 2026 Stage 1

---

## Final Competition Scores

| Metric | Value |
|--------|-------|
| Challenge Score | **28,394** |
| IQC 2026 Stage 1 D1 Score | **10,260** |
| Alphas Submitted (Active) | **16** |
| Total Alphas Tested | **164** |
| Deadline | May 18, 2026 ✅ |

---

## Overall Testing Breakdown

| Status | Count |
|--------|-------|
| ✅ Submitted | 13 |
| ✅ Submittable (not submitted) | 3 |
| ⚠️ Near-Miss | 5 |
| ⚠️ Borderline | 1 |
| ❌ Rejected | 121 |

---

## Submitted Alphas (13 Active)

| Alpha | Universe | Sharpe | Fitness | Max Corr |
|-------|----------|--------|---------|----------|
| Price Reversal × Volume | TOP3000 | 2.01 | 1.00 | — |
| DeepValue ttmfcfp_alt × Momentum | TOP3000 | 1.97 | 1.65 | 0.546 |
| Liquidity Momentum | TOP3000 | 1.93 | 1.31 | — |
| Value Rank ts_rank(252) | TOP3000 | 1.89 | 1.66 | — |
| CashFlow/EV ts_rank(252) | TOP3000 | 1.72 | 1.22 | — |
| P/S Momentum | TOP3000 | 1.71 | 1.37 | — |
| ShortSentiment days_to_cover ts_rank | TOP3000 | 1.70 | 1.00 | 0.359 |
| FANGMA VMM11 ts_rank | TOP3000 | 1.68 | 1.18 | 0.542 |
| FANGMA VMM11 ts_zscore | TOP3000 | 1.65 | 1.17 | 0.577 |
| Norm Earnings Yield ts_rank(252) | TOP3000 | 1.58 | 1.27 | — |
| 5yr RelValue ts_rank(252) | TOP3000 | 1.60 | 1.23 | — |
| DeepValue PDY TOP500 | TOP500 | 1.51 | 1.19 | 0.346 |
| 5yr RelValue rel5ybp TOP500 | TOP500 | 1.43 | 1.18 | 0.547 |

---

## Unsubmitted — Still Viable

These passed IS thresholds but were not submitted before the deadline. Keep for next competition.

| Alpha | Universe | Sharpe | Fitness | Corr | Notes |
|-------|----------|--------|---------|------|-------|
| FANGMA VMM11 ts_rank TOP200 | TOP200 | 1.40 | 1.19 | 0.245 | Low corr, clean signal |
| VMA2 va Naked | TOP3000 | 1.78 | 1.12 | 0.617 | Score +66, submittable |
| RelValue ttmfcfp × Momentum TOP500 | TOP500 | 1.40 | 1.14 | 0.489 | Solid fundamentals combo |

---

## Rejection Breakdown

| Reason | Count |
|--------|-------|
| Dead Signal | 27 |
| 2021–2022 Regime Collapse | 18 |
| Fitness Block (turnover too high) | 11 |
| Self-Correlation > 0.70 | 10 |
| Fitness Below Threshold (< 1.00) | 10 |
| Negative / Marginal Score Change | 6 |
| Train/Test Overfit | 2 |
| Other / Combined | 37 |

---

## Hidden Gems — Best Rejected Alphas

High Sharpe but blocked by fixable issues. Priority targets for next round tuning.

| Alpha | Sharpe | Fitness | Rejection Reason | Fix |
|-------|--------|---------|-----------------|-----|
| CLV Reversion | 2.10 | 0.96 | Fitness Block | Apply `hump()` or `ts_decay_linear()` |
| VWAP Zscore × Volume | 2.10 | 0.81 | Fitness Block | Apply `hump()` or `ts_decay_linear()` |
| ADV20 Reversion | 2.08 | 0.87 | Turnover Too High | Apply `ts_decay_linear()` |
| CLV+Volume/ADV20 | 2.03 | 0.99 | Fitness Block | Minimal fix needed — Fitness 0.99 |
| IV + Current Ratio Filter | 1.96 | 1.46 | Self-Correlation | Try different universe or inner signal |
| IV Regime + A9 Signal | 1.94 | 1.01 | Self-Correlation | Swap inner signal to reduce corr |
| 5yr RelValue TOP1000 ts_rank | 1.92 | 1.75 | Self-Correlation | Already in book — try variant |
| GARP vfpriceratio_2 × Momentum | 1.82 | 1.51 | Self-Corr + Neg Score | Rework momentum component |

---

## Near-Miss Fields (Fitness Just Below 1.00)

These have good Sharpe but Fitness fell just short. Worth a retest with `hump()`.

| Alpha | Sharpe | Fitness | Gap |
|-------|--------|---------|-----|
| indrelcroe_ SUBIND d6 TOP3000 | 1.48 | 0.98 | –0.02 |
| deepvalue pdy_alt d6 TOP3000 | 1.35 | 0.93 | –0.07 |
| deepvalue estep_alt d6 TOP3000 | 1.27 | 0.91 | –0.09 |
| deepvalue fwdep_alt d6 TOP3000 | 1.25 | 0.90 | –0.10 |
| deepvalue fwdep d6 TOP3000 | 1.23 | 0.87 | –0.13 |

---

## Key Takeaways

**What worked:**
- Fundamental value signals combined with momentum (DeepValue × Momentum, P/S Momentum) consistently produced the strongest Sharpe + Fitness combos.
- `ts_rank(252)` was more reliable than `ts_zscore` for Fitness — lower turnover.
- TOP500 and TOP200 universes gave cleaner correlations, helping pass the self-corr check.
- Short sentiment (`days_to_cover`) was a surprisingly effective standalone signal.

**What didn't work:**
- Pure technical signals (CLV, VWAP, ADV20 reversion) had strong Sharpe but consistently failed Fitness due to high turnover.
- `_alt` field variants are largely deprecated — stripped suffix was always correct.
- D0 (delay=0) was not viable — thresholds too strict (Sharpe ≥ 2.0, Fitness ≥ 1.30).
- 2021–2022 was a consistent regime break for 18 signals — any alpha relying on that period's patterns is suspect.

**For next competition:**
- Fix CLV Reversion and CLV+Volume/ADV20 first — they're nearly there.
- Explore `implied_volatility_call_60` with a fresh uncorrelated inner signal.
- Investigate `mdl177_2_liquidityriskfactor_si_ratio` and `mdl177_2_sensitivityfactor400_pbroeresidual` — flagged as manual UI candidates.
- Use TOP200 more aggressively — consistently the cleanest self-correlation results.
