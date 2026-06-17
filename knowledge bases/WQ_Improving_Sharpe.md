# WorldQuant BRAIN: How to Improve Sharpe Ratio (Knowledge Base)
> **Purpose:** A focused guide on understanding and improving the Sharpe ratio — the primary IS quality gate for alpha submission.

---

## 1. Understanding the Metric

**Information Ratio (IR)** is the foundation:

```
IR = Return / StdDev(Return)
```

**Sharpe** is simply the annualized IR:

```
Sharpe = IR × sqrt(252)
```

A smooth, steadily rising PnL curve gives high Sharpe. Volatile, choppy PnL gives low Sharpe — even if the average return is the same.

---

## 2. The Two Levers

Since `IR = Return / StdDev(Return)`, there are exactly two ways to improve it:

### A. Increase Returns
* Use better data — slow-moving fundamental signals predict returns over longer horizons; fast price/news signals predict short-term moves.
* Use the right lookback for the data frequency:
    * DAILY: 5–63 days
    * WEEKLY: 22–126 days
    * QUARTERLY: 126–504 days
* Use `ts_regression(FIELD, ts_step(1), 252, rettype=2)` to extract the **slope** of a trend — often more predictive than the raw level.
* Pair signals: spread or residual between two economically related fields carries information neither has alone (`ts_regression(FIELD_A, FIELD_B, 252, rettype=0)`).

### B. Reduce Volatility
* **Neutralization:** Subtracts the group mean from every stock in that group, forcing the sum of group weights to zero. This removes macro/sector shocks that spike volatility.
    * Fundamental / Analyst → `INDUSTRY`
    * News / Sentiment → `SUBINDUSTRY`
    * Price Volume / Options → `MARKET` or `NONE`
* **Group operators:** `group_rank`, `group_zscore`, `group_neutralize` allow multi-level neutralization inside the expression itself — remove both industry and sector effects simultaneously.
* **Expand the universe:** `TOP3000` reduces per-stock weight concentration, smoothing daily PnL swings vs. `TOP200`.
* **Winsorize outliers:** `winsorize(FIELD, std=4)` prevents single extreme data points from causing large one-day PnL spikes that inflate volatility.

---

## 3. Key Principles

> **Don't chase Sharpe by tuning parameters.** Arbitrary lookback adjustments that lift Sharpe without a logical reason are overfitting — the alpha will likely fail Out-of-Sample. Every change should have a mathematical or economic rationale.

> **Once you clear the thresholds (Sharpe ≥ 1.25, Fitness ≥ 1.00), shift focus to returns.** The thresholds exist to filter noise from signal — once you're past them, higher simulated returns matter more than marginal Sharpe gains.

> **Sharpe and Fitness are linked but different.** High Sharpe with ultra-low Turnover (< 2%) still fails Fitness (structural ceiling ~0.88). Fix TO before worrying about Sharpe ceiling.

---

## 4. Practical Checklist

| Problem | Likely Cause | Fix |
| :--- | :--- | :--- |
| Sharpe < 0.5 (no signal) | Wrong data frequency or lookback | Match lookback to update frequency; try shorter/longer |
| Sharpe 0.5–0.9 (weak signal) | Excessive noise in raw field | `winsorize`, `ts_backfill`, or `group_zscore` to clean data |
| Sharpe 0.9–1.2 (near-miss) | Volatility from macro exposure | Tighten neutralization (MARKET → INDUSTRY → SUBINDUSTRY) |
| Sharpe > 1.25 but Fitness < 1.0 (high TO) | Signal flips too fast | Wrap in `hump()`, increase Decay setting, use `trade_when` |
| Sharpe > 1.25 but Fitness < 1.0 (low TO) | Structural ceiling — signal barely moves | Try shorter lookbacks; if signal only exists at annual scale, abandon |
| Sharpe negative | Wrong sign | Add `-` prefix: `-rank(...)` instead of `rank(...)` |
