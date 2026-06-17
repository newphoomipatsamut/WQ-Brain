# WorldQuant BRAIN: How to Improve Fitness (Knowledge Base)
> **Purpose:** A focused guide on understanding and improving the Fitness score — the ultimate IS submission gate that combines Sharpe, Returns, and Turnover into one number.

---

## 1. The Formula

```
Fitness = Sharpe × sqrt(abs(Returns) / max(Turnover, 0.125))
```

The `max(Turnover, 0.125)` floor means Turnover below 12.5% no longer helps Fitness — extremely low TO doesn't keep compounding the benefit. The three levers are:

| Lever | Effect on Fitness | Cross-reference |
| :--- | :--- | :--- |
| ↑ Sharpe | Direct multiplier — most powerful single lever | `WQ_Improving_Sharpe.md` |
| ↑ Returns | Increases the numerator inside the sqrt | `WQ_Improving_Returns.md` |
| ↓ Turnover | Decreases the denominator inside the sqrt | `WQ_Improving_Turnover.md` |

All three must be optimized together — high Sharpe with near-zero Turnover still hits a structural Fitness ceiling.

---

## 2. Structural Fitness Ceiling from Ultra-Low Turnover

If Turnover < ~2%, even a strong Sharpe (e.g. 1.32) can only reach Fitness ~0.88 — structurally unable to clear 1.00.

**Why:** At TO = 1.61%, `sqrt(Returns / 0.0161)` is small regardless of Returns. The formula is not linear — doubling Returns only improves Fitness by `sqrt(2)` ≈ 41%, which may not be enough.

**Fix:** Shorten lookback windows to raise TO. If the signal only exists at annual timescales (252+ days) and shorter lookbacks destroy it, the field has a structural fitness ceiling. Mark it abandoned and move on. See `WQ_Improving_Turnover.md` Section 3C.

---

## 3. Reducing Turnover to Improve Fitness (Most Common Fix)

### A. Decay Simulation Setting
The `Decay = N` setting applies a linear weighted average over the last N days to the alpha's output weights:
* Day `t` weight = weighted average of weights from `t-N` to `t`, with more weight on recent days.
* This does **not** change the input data — it smooths the *output* position weights only.
* Default `Decay = 6` is a good starting point. The default was historically 4; 6 gives slightly more smoothing without sacrificing much signal.
* Increasing Decay → lower TO → higher Fitness, BUT also lower Returns. Test at Decay = 6, 8, 10 and pick the value that maximizes Fitness (not just lowest TO).

### B. `hump()` Operator — The Preferred Turnover Reducer
`hump()` defines a percentage-change threshold below which positions are held unchanged. A trade is only simulated when the alpha value changes by more than the threshold:

```
-rank(hump(ts_rank(FIELD, 252)))
```

**Why `hump()` is better than just increasing Decay for quarterly data:**
* Decay averages uniformly — it blurs large meaningful signals along with small noise.
* `hump()` is selective — it holds positions when the daily change is noise, but allows full rebalancing when the change is real.
* More advanced uses: variable threshold based on market conditions, per-stock thresholds based on liquidity or volatility, group-level thresholds (one threshold for each subindustry).

⚠ Never use `ts_decay_linear()` — it is banned (correlates with a submitted alpha).

### C. `trade_when()` — Event-Driven Execution
Only rebalances when a specific condition triggers; holds the previous alpha value (`-1` means "hold") on all other days:

```
trade_when(Event_condition, Alpha_expression, -1)
```

**Practical pattern:**
```
trade_when(abs(ts_delta(returns, 1)) > 0.05, signal, -1)
```
Trades only when a stock's daily return spike exceeds 5% — all other days hold position.

**When to use:**
* Event-driven signals: earnings releases, analyst rating changes, insider filings.
* Any signal where the alpha idea is only valid during certain conditions.
* As a last resort for reducing TO when Decay and `hump()` aren't enough.

**Pros:** Good coverage, flexible event definition, naturally low transaction costs.

**Cons:** Hard to get high Sharpe (signal is on only some days). Hard to get high Returns (fewer trading days = less total PnL). Use when the event itself carries the alpha, not as a generic TO reducer.

**Note:** The hold expression (`-1`) can be replaced with a decaying version of the previous alpha — this allows positions to gently unwind during the hold period rather than staying static.

---

## 4. Increasing Alpha Capacity (Long-Term Fitness via Scalability)

High-capacity alphas share three properties: **high liquidity, low correlation, low turnover**. Of these, low turnover is the biggest contributor to capacity — fewer transactions means more capital can be deployed without moving the market.

**Capacity is related to Fitness** because:
* Low TO → lower transaction costs → higher real-world PnL → more submittable alphas.
* High-capacity alphas survive longer in the live OS period before being decommissioned.

**Practical steps to increase capacity:**
1. Apply `hump()` to reduce wasteful turnover (position changes that generate negligible PnL but real transaction costs).
2. Use `trade_when` for event signals — only trade when the signal is strong enough to cover costs.
3. Use `TOP200` or `TOP3000` (most liquid universes) — avoids capacity constraints from illiquid micro-caps.
4. Target low self-correlation — diversified book has higher combined capacity than a book of correlated alphas.

---

## 5. Increasing Sharpe and Returns Together

Since `Fitness = Sharpe × sqrt(Returns / TO)`, raising both Sharpe and Returns simultaneously compounds Fitness multiplicatively. Key techniques:

**Predict better:**
* Short-term (< 63 days): Use price-volume, news, or sentiment data — fast signals, higher TO, higher Returns.
* Long-term (126–504 days): Use fundamental or analyst estimate data — slow signals, lower TO, smoother Sharpe.
* Complex models generate higher Returns but risk overfitting. Simple models (e.g. plain `ts_rank`) are more robust but modest.

**Reduce volatility without reducing Returns:**
* Neutralization removes market/sector exposure that adds volatility without adding signal.
* `group_rank` and `group_zscore` normalize within peer groups — removes between-group noise while preserving within-group signal.
* `winsorize(FIELD, std=4)` clips extreme outliers before ranking — prevents single data spikes from creating one-day PnL swings.

---

## 6. Fitness Optimization Checklist

Work through these in order — each step is faster than the next:

1. **Check Turnover first.** If TO > 40%, increase Decay or add `hump()` before touching anything else.
2. **Check for NaN flicker.** If PnL is choppy with spikes, add `ts_backfill(FIELD, 120)` — fixes both Sharpe and TO simultaneously.
3. **Check Sharpe.** If Sharpe < 1.0, the signal is weak — change template or field before tuning parameters.
4. **Check Returns.** If Sharpe ≥ 1.25 but Fitness < 1.00 and TO is healthy (5–40%), Returns are too low. Lower Decay or try a faster data frequency.
5. **Check for structural TO ceiling.** If TO < 2% and Sharpe is already > 1.25, the field may be unpassable — see Section 2.
6. **Try `hump()` + TOP200.** If the above don't help, `hump()` cuts wasteful TO and TOP200 often gives lower self-corr and sometimes better Fitness.

---

## 7. Key Principle

> **Fitness is the hardest metric to game because it requires Sharpe, Returns, and Turnover all pointing in the right direction simultaneously.** Don't chase Fitness by arbitrary parameter tuning — changing the lookback from 252 to 200 to get 0.03 more Fitness is overfitting. Every change should have a mathematical or economic rationale.
>
> **Target Fitness ≥ 1.30 ("Average" rating).** Getting above 1.00 clears the submission gate; getting above 1.30 starts building real payout weight. The difference between 1.00 and 2.60 ("Excellent") is mostly Returns — Sharpe and TO are gating conditions, Returns is what separates good alphas from great ones.
