# WorldQuant BRAIN: How to Smooth the PnL Curve (Knowledge Base)
> **Purpose:** A focused guide on diagnosing and fixing sudden PnL jumps, year-by-year dips, and turnover spikes — the patterns that lower Sharpe and signal fragility in Out-of-Sample trading.

---

## 1. Root Causes of Sudden PnL Jumps

### A. NaN Flicker (Data Gaps)
When a field flickers between a real value and `NaN`, the alpha weight for that stock jumps between its signal value and 0. If a large position suddenly disappears for one day, the PnL spikes.

**Fix: `ts_backfill(FIELD, lookback)`**
Replaces `NaN` with the most recent valid value from the lookback window, bridging the gap cleanly:
```
-rank(ts_rank(ts_backfill(FIELD, 120), 252))
```

**Fix: `group_backfill(FIELD, group, d)`**
Fills `NaN`s using a winsorized mean of peer stocks in the same group — better than simple backfill for fundamental data where the company's own history is too sparse:
```
-rank(ts_rank(group_backfill(FIELD, subindustry, 60), 252))
```

Use `ts_backfill` for fields with occasional gaps. Use `group_backfill` for fields with structural sparsity (quarterly data with many `NaN` days between updates).

### B. Signal Changes Too Rapidly
When the underlying signal oscillates quickly, portfolio weights flip frequently and PnL becomes choppy.

**Fix: Decay simulation setting**
`Decay = N` averages the alpha's daily output weights over the last N days linearly — the fastest, broadest lever:
* Our default `Decay = 6` gives moderate smoothing.
* Increase to 10–15 for high-frequency data (news, sentiment).

**Fix: `hump()` operator**
Suppresses small day-to-day weight changes below the threshold (default 1%). Only updates position when the change is large enough to matter:
```
-rank(hump(ts_rank(FIELD, 252)))
```
Unlike Decay, `hump()` selectively dampens noise without averaging out large meaningful moves.

**Fix: `ts_mean()` / `ts_rank()` wrapper**
Wrap the raw signal in a time-series smoother before ranking:
* `ts_rank(FIELD, 252)` maps the raw value into its 252-day historical percentile — inherently more stable than the raw value.
* `ts_mean(FIELD, 22)` replaces point-in-time values with a 22-day moving average.

### C. Over-Concentration in a Single Stock
If one stock holds too large a weight and that stock has a sudden price move, the PnL spike is amplified. One stock going from +20% to -20% on earnings can cause a visible kink in an otherwise smooth curve.

**Fix: Truncation setting**
Set `Truncation = 0.08` in simulation settings — caps any single stock at 8% of the book ($1.6M in a $20M portfolio). No single position can cause a catastrophic single-day jump.

**Fix: `rank()` wrapper**
Outer `rank()` compresses all weights to a uniform [0, 1] distribution — inherently limits concentration compared to using raw values.

---

## 2. Year-by-Year Dips (Structural Fragility)

Checking the **Aggregate Data** section in the BRAIN UI (year-by-year breakdown) is critical — the IS summary hides multi-year deterioration behind an average.

### Why Dips Happen
* **Random noise / overfitting:** The alpha memorised specific years in the IS period. Use the Train/Test split — if Sharpe is high in Train (years 1–4) but collapses in Test (year 5), it's curve-fitted.
* **Crowded signal:** Other quants discovered the same idea. Excess competition erodes the signal over time.
* **Macro events:** COVID-19 (2020), GFC (2008–2009), or industry shocks can affect alphas that have concentrated sector exposure. An alpha heavily long tech stocks will show a 2022 dip regardless of signal quality.
* **Industry exposure drift:** If your alpha idea (e.g. "buy high-ROE stocks") has different cross-industry implications over time — internet companies had high ROE in 2015; manufacturing companies had it in 2018 — the alpha will produce dips when the industry mix shifts.

### How to Fix Dips

**Neutralize the risk, not the signal:**
Remove macro exposure without destroying the underlying idea. If the alpha bets on ROE ranking but ROE differs by industry, neutralize by industry so you're only trading the *within-industry* ROE spread:
```
-rank(group_rank(ts_rank(roe, 252), industry))
```

**Neutralization levels to try (in order):**
1. Simulation setting: MARKET → INDUSTRY → SUBINDUSTRY
2. In-expression: `group_neutralize(signal, sector)` removes sector-wide exposure
3. Double neutralization: `group_neutralize(group_rank(signal, subindustry), sector)` strips both industry and market effects

**Other neutralization operators:**
* `group_zscore(FIELD, group)` — z-score within peer group, removes between-group level differences
* `regression_neut` / `ts_vector_neut` — advanced tools for removing factor exposure statistically (use when standard group operators aren't enough)

**Check for regime sensitivity:**
If a dip coincides with a known macro event (2020 COVID, 2022 rate hikes), the alpha has macro exposure that neutralization can help reduce. If the dip is idiosyncratic and random-looking, it may be noise — check if the same dip appears in sub-universe tests (`TOP1000` vs `TOP3000`).

---

## 3. Turnover Spikes (Low-Coverage Fields)

Short-period spikes in the turnover chart — regular vertical lines repeating at fixed intervals (e.g. quarterly) — are a specific pattern caused by **low-coverage data fields**.

**Why it happens:**
When a quarterly field has no data on certain days, all stocks holding that field go to zero weight simultaneously on those days. The portfolio completely reshuffles → Turnover spikes → CONCENTRATED_WEIGHT check fails.

**Pattern to recognize:** If the turnover spike chart shows regular spikes at quarterly intervals (every ~63 trading days), the field has sparse quarterly coverage.

**Fix: `ts_backfill(FIELD, 120)`**
Fills the no-data days with the most recent quarterly reading, so the portfolio doesn't rebalance every time data drops out:
```
-rank(ts_rank(ts_backfill(FIELD, 120), 252))
```
120 trading days (~6 months) covers a full quarter gap with buffer.

**Fix: `group_backfill(FIELD, group, 60)`**
For fields where even the company's own prior reading is missing, use peer-group imputation.

---

## 4. Diagnostic Summary

| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| Single-day PnL spike | NaN flicker on a large position | `ts_backfill()` or `group_backfill()` |
| General choppiness throughout IS | Signal changes too fast | Increase Decay, add `hump()`, or wrap in `ts_rank()` |
| One stock dominates drawdown | Over-concentration | Set `Truncation = 0.08`, use outer `rank()` |
| Multi-year dip or late-IS decline | Macro exposure, crowding, or overfitting | Neutralize by industry/sector; check Train/Test split |
| Regular turnover spikes at quarterly intervals | Low-coverage field losing data | `ts_backfill(FIELD, 120)` before the rank operator |
| Turnover spike causes CONCENTRATED_WEIGHT fail | Same as above — coverage drops → few stocks hold all weight | `ts_backfill` or `group_backfill` to maintain coverage |

---

## 5. Key Principle

> A smooth PnL curve is not just aesthetically better — it directly increases Sharpe (lower daily return volatility) and reduces drawdown. Every fix above also tends to improve IS metrics, not just visual smoothness.
>
> If an alpha shows a consistent multi-year decline in the IS period, treat it as a red flag regardless of the overall Sharpe. BRAIN's IS-ladder test (year-by-year Sharpe) is a submission gate for exactly this reason — an alpha that degrades over time is unlikely to perform well Out-of-Sample.
