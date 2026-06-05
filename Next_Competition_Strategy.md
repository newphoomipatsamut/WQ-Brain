# Next Competition Strategy
> **Researcher:** Phoomipat | **Prepared:** May 24, 2026 | **Based on:** IQC 2026 Stage 1 learnings

---

## Starting Position

| Asset | Count |
|-------|-------|
| Active alpha book (✅ In Use) | 20 fields |
| Backlog — priority retests | 17 fields |
| Tested baseline failed — retry candidates | 152 fields |
| Untested mdl177 fields | ~1,356 |
| Untested non-model fields | ~6,073 |
| Fields to avoid (Abandoned / Dead) | 96 fields |

Your book is already well-established. The next competition is primarily an **expansion** problem — find new uncorrelated signals from the thousands of untested fields.

---

## Phase 1 — Quick Wins (First Week)

These are the highest-confidence items. Do these before building any new batches.

### 1A — Fix the Fitness Blocks (Immediate)
Four high-Sharpe alphas failed only because of turnover. Apply `hump()` or `ts_decay_linear()` to reduce turnover and retest.

| Alpha | Sharpe | Fitness | Fix |
|-------|--------|---------|-----|
| CLV Reversion | 2.10 | 0.96 | `rank(hump(((2*close-high-low)/(high-low))*ts_rank(volume,5)))` |
| CLV+Volume/ADV20 | 2.03 | 0.99 | Wrap outer signal in `ts_decay_linear(..., 5)` |
| ADV20 Reversion | 2.08 | 0.87 | `rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))` |
| VWAP Zscore × Volume | 2.10 | 0.81 | Reduce lookback or add `ts_decay_linear` |

> **CLV+Volume/ADV20 at Fitness 0.99 is the single easiest win** — it only needs a marginal turnover reduction.

### 1B — Backlog: Needs Retest (17 Fields)
These were near-misses — Fitness just below 1.00, or revived fields that need a proper TOP200 / ts_rank / flip test. Build a single batch covering all 17.

**Priority within this group:**
- `mdl177_2_managementqualityfactor_indrelcroe_` — Sharpe 1.48, Fitness 0.98 (2 basis points from passing)
- `mdl177_deepvaluefactor_pdy_alt` — Sharpe 1.35, Fitness 0.93
- `mdl177_liquidityriskfactor_si_ratio` — manually flagged as UI candidate
- `mdl177_2_industryrelativevaluefactor_*` — note: entire family previously flagged DEAD (Fitness < 1.00) — test but expect failure

**Suggested expressions for retest batch:**
```python
# For each field F in backlog:
'-rank(hump(ts_rank(F, 252)))'               # reduced-turnover baseline
'-rank(ts_zscore(F, 252))'                   # zscore variant
{**BASE, 'universe': 'TOP200', 'code': '-rank(ts_zscore(F, 252))'}  # TOP200
```

### 1C — Unsubmitted Submittable Alphas
Three alphas passed all thresholds but weren't submitted before May 18. Submit immediately if the competition window reopens:
- FANGMA VMM11 ts_rank TOP200 (Sharpe 1.40, Fitness 1.19, Corr 0.245 — lowest corr in the book)
- VMA2 va Naked (Sharpe 1.78, Fitness 1.12, Score +66)
- RelValue ttmfcfp × Momentum TOP500 (Sharpe 1.40, Fitness 1.14)

---

## Phase 2 — Systematic New Field Exploration

### Priority Order by Family

| Priority | Family | Untested | Why |
|----------|--------|----------|-----|
| 🔴 High | **5yr RelValue** (new variants) | 5 | Proven family — `rel5ybp`, `rel5yfwdep` both submitted. Try `rel5ycfp`, `rel5yocfp`, `rel5yebitdap` |
| 🔴 High | **DeepValue** (untested variants) | 24 | `ttmfcfp` and `ttmocfev` both work. Try `ttmfcev`, `bp`, `cashp`, `proformaep`, `ttmocfp` |
| 🔴 High | **Short Sentiment (devNA)** | 15 | `days_to_cover` worked (Sharpe 1.70). Test the full `devnorthamerica` family |
| 🟡 Med | **Implied Volatility** | 20+ | `iv_call_60` had Sharpe 1.94–1.96 but self-corr blocked. Test other expirations (30, 90, 120, 270) as the inner signal filter |
| 🟡 Med | **Earnings Quality** | 59 | Largely untested mdl177 family. `uap` is in use — find uncorrelated siblings |
| 🟡 Med | **GARP** (new variants) | 13 | `vfpriceratio` worked. Try `valuation`, `qgp_*` variants |
| 🟢 Low | **Price Momentum** | 216 | Large family but regime-sensitive. Test selectively with TOP200 |
| 🟢 Low | **Surprise/Earnings Momentum** | 88+11 | Test a sample — unpredictable family |

### 5yr RelValue — Highest Priority New Batch
Your `5yr RelValue` alphas consistently had the best Fitness (up to 1.88) and clean self-correlation. These untested variants are the most promising next batch:

```python
FIELDS_5YR_RELVALUE = [
    'mdl177_2_5yearrelativevaluefactor_rel5ycfp',    # Cash flow / price
    'mdl177_2_5yearrelativevaluefactor_rel5yocfp',   # Operating CF / price
    'mdl177_2_5yearrelativevaluefactor_rel5yebitdap', # EBITDA / price
    'mdl177_2_5yearrelativevaluefactor_rel5yfcfp',   # Free CF / price
    'mdl177_2_5yearrelativevaluefactor_rel5ydivp',   # Dividend yield
]
```

### Short Sentiment — devNorthAmerica Family
`days_to_cover` (Sharpe 1.70, Fitness 1.00, Corr 0.36) was one of your cleanest alphas. The `devnorthamerica` variants are likely to be cleaner than the base model. Priority fields:
- `mdl177_devnorthamericashortsentimentfactor_days_to_cover`
- `mdl177_devnorthamericashortsentimentfactor_benchmark_fee`
- `mdl177_devnorthamericashortsentimentfactor_act_util`
- `mdl177_devnorthamericashortsentimentfactor_conc_ratio`

### Implied Volatility — Expiration Sweep
`iv_call_60` was your best non-model signal (Sharpe 1.94) but always correlated with A9/A10. Strategy: use different IV expirations as a regime filter rather than a primary signal, or test in TOP500 universe to reduce overlap.

```python
# Test as standalone (different expirations)
'implied_volatility_call_30', 'implied_volatility_call_90',
'implied_volatility_call_120', 'implied_volatility_call_270',
'implied_volatility_put_60', 'implied_volatility_mean_120'
```

---

## Phase 3 — Combination Strategies

Based on what worked in IQC 2026, these combination templates reliably produce Fitness > 1.00:

### Template A — DeepValue × Momentum (best template)
```python
'-rank(ts_decay_linear(FIELD, 21) * rank(ts_delta(close, 5)))'
```
Works for: DeepValue fields, 5yr RelValue fields, any fundamental yield metric

### Template B — ts_rank with decay (low turnover)
```python
'-rank(hump(ts_rank(FIELD, 252)))'
```
Works for: Any field where baseline `ts_rank(252)` shows signal but Fitness < 1.00

### Template C — TOP200 zscore (cleanest self-corr)
```python
{**BASE, 'universe': 'TOP200', 'code': '-rank(ts_zscore(FIELD, 252))'}
```
Works for: Any signal that passes TOP3000 — TOP200 consistently gives the lowest max_corr

### Template D — Short Sentiment pure rank
```python
'-rank(ts_rank(FIELD, 63))'   # shorter lookback for sentiment signals
```
Works for: Short sentiment family — 252 lookback is too long for borrow signals

---

## What to Avoid

| Signal Type | Reason |
|-------------|--------|
| D0 (delay=0) | Thresholds too strict: Sharpe ≥ 2.0, Fitness ≥ 1.30 |
| `_alt` field suffixes | Deprecated — drop the `_alt` |
| `industryrrelativevaluefactor` family | Confirmed DEAD — Fitness < 1.00 across all variants |
| Pure technical reversal (CLV, VWAP naked) | High Sharpe but Fitness fails — only viable with decay wrapper |
| 2021–2022 regime-dependent signals | 18 alphas collapsed in this period — avoid signals whose IS strength depends on it |
| `debt`, `assets`, `return_assets`, `ebit`, `capex` (raw) | COVID-distorted, confirmed negative IS Sharpe |
| Sentiment/social signals (`snt_*`, `scl12_*`) | 10+ variants all exhausted — abandoned family |

---

## Recommended Batch Schedule

| Batch | Contents | Expected |
|-------|----------|---------|
| `fix_fitness` | CLV Reversion, CLV+ADV20, ADV20 Rev, VWAP (with hump/decay) | 2–3 passes |
| `backlog_retest` | 17 Backlog: Needs Retest fields (TOP200 + ts_rank + hump variants) | 3–5 passes |
| `5yr_rv_new` | 5 untested 5yr RelValue fields × 3 expressions | 3–5 passes |
| `short_snt_devna` | 4 devNorthAmerica short sentiment fields × 3 expressions | 2–3 passes |
| `deepvalue_sweep` | 10 untested DeepValue fields × 2 expressions | 3–6 passes |
| `iv_expiry_sweep` | 6 IV expiration variants × 2 expressions (TOP3000 + TOP200) | 1–3 passes |

---

## Key Principles Carried Forward

1. **Score change > everything.** Always check the Performance Comparison panel. Positive IS Sharpe is not enough.
2. **TOP200 for self-corr.** When a TOP3000 alpha is blocked by correlation, retest in TOP200 — corr drops significantly.
3. **Fitness fix = `hump()` or `ts_decay_linear()`.** Any Fitness Block rejection can be retried with these.
4. **Never mark dead from baseline alone.** Flip sign and TOP200 retest required first.
5. **D1 only.** All batches use `delay=1`. D0 is not viable.
6. **3 concurrent workers max.** Do not increase `max_workers` in `main.py`.
