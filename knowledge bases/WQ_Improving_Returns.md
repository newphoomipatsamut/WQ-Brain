# WorldQuant BRAIN: How to Improve Returns (Knowledge Base)
> **Purpose:** A focused guide on understanding and improving annualized returns — the core profitability metric that drives Fitness once Sharpe is cleared.

---

## 1. Understanding the Metric

BRAIN defines annualized return as:

```
AnnualReturn = AnnualizedPnL / (0.5 × BookSize)
```

BookSize is fixed at **$20M** on BRAIN. Base capital is assumed as $10M (2× leverage), so the denominator is $10M. A portfolio that earns $1.2M/year annualized has a 12% return.

Returns feed directly into **Fitness**:

```
Fitness = Sharpe × sqrt(abs(Returns) / max(Turnover, 0.125))
```

Low returns = low Fitness, even if Sharpe is high. Returns and Turnover are the two variables you can actually move once Sharpe is stable.

---

## 2. Ways to Increase Returns

### A. Increase Turnover
Higher turnover means more trading activity per day, which compresses the time each dollar is at work and can amplify annualized returns.

* Use **shorter lookback windows** — `ts_rank(FIELD, 63)` trades more actively than `ts_rank(FIELD, 252)`.
* Use **lower Decay** setting — Decay=0 gives raw daily signal; Decay=6 smooths and holds positions longer.
* Use **faster-updating data** — price/volume and news fields update daily; quarterly fundamentals barely move day-to-day.
* ⚠ **Turnover ceiling:** If TO climbs above 70%, the alpha is rejected outright. The sweet spot is 5–40% for Fitness.

### B. Use Lower Decay Values
The `Decay` setting applies a linear rolling average to daily alpha weights over the last N days. Lower decay = less smoothing = more position changes = higher returns (and higher turnover). Start at Decay=6 and step down toward 0 to find the Fitness-optimal point.

### C. Use More Liquid (Smaller) Universes
Counterintuitively, smaller universes like `TOP200` often produce **higher returns** than `TOP3000`:
* Capital concentrates among fewer stocks → each position is larger → absolute PnL per trade is larger.
* Stocks in TOP200 are the most liquid (AAPL, MSFT, etc.) so fills are real and slippage is low.
* Trade-off: self-correlation is harder to clear since other researchers also use TOP200.

### D. Increase Volatility Without Increasing Drawdown
If Sharpe (Return / Volatility) stays constant, you can scale up volatility and returns together:
* Use broader neutralization (`MARKET` instead of `SUBINDUSTRY`) — removes less noise, raises both return and volatility proportionally.
* Remove `rank()` wrapper from intermediate steps — raw signals are noisier but can have larger return swings.
* Use `signed_power(x, 0.5)` instead of raw signal — compresses extremes less aggressively than `rank()`.

### E. Try News and Analyst Datasets
These datasets tend to generate higher-return alphas compared to fundamentals:
* **News** (`anl4_fs_*`, `anl4_ebit_*`, `anl4_fcf_*`): Analyst estimate revisions predict short-term returns strongly. Use Template L (revision rate: `ts_rank(ts_delta(FIELD, 63), 252)`).
* **Analyst consensus** (`snt1_d1_buyrecpercent`): Buy/sell recommendation ratios. Filter by coverage count to avoid single-analyst noise.
* **Sentiment**: High turnover by nature — daily updates drive frequent rebalancing, which compounds returns faster than quarterly data.
* These datasets come with higher turnover natively, solving the low-return / low-TO problem that plagues annual fundamental fields.

---

## 3. The Returns–Fitness–Turnover Triangle

These three variables are locked together by the Fitness formula. Use this table to diagnose:

| Symptom | What's happening | Fix |
| :--- | :--- | :--- |
| High Sharpe, low Fitness | Returns too low OR Turnover too low | Shorten lookback, lower Decay, or try faster data |
| Good Returns, low Fitness | Turnover too HIGH (> 70%) | Add `hump()`, increase Decay, or use `trade_when` |
| Low Returns + low Turnover | Annual/quarterly signal barely moves | Switch to WEEKLY or DAILY data; or use revision rate template |
| Fitness ≥ 1.00 but submittable returns low | Signal is mild but consistent | Stack signals: multiply a value factor by a momentum factor |

---

## 4. Key Principle

> **Focus on returns after clearing the Sharpe and Fitness thresholds.** Once you're above Sharpe ≥ 1.25 and Fitness ≥ 1.00, marginal Sharpe gains matter less than driving returns higher — that's what separates an "Average" alpha from a "Good" or "Excellent" one on BRAIN's fitness scale.

Fitness ratings for reference:
- **Spectacular:** Fitness > 3.25
- **Excellent:** Fitness > 2.60
- **Good:** Fitness > 1.95
- **Average:** Fitness > 1.30
- **Minimum to pass:** Fitness ≥ 1.00
