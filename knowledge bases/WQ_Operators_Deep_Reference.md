# WorldQuant BRAIN: Operators & Settings — Deep Reference (Knowledge Base)
> **Purpose:** Detailed explanations of how BRAIN operators and simulation settings work mechanically — beyond the syntax reference in WQ_Operators_Guide.md.

---

## 1. Conditional Logic — The Ternary Operator

```
<condition> ? <expr_if_true> : <expr_if_false>
```

This is BRAIN's equivalent of `if/else`. It evaluates the condition for every stock on every day and returns the appropriate branch.

**Simple example:**
```
close > open ? 0.5*(high - low) : vwap - close
```
If close > open (bullish day): alpha = half the daily range.
Else: alpha = how far the close was below VWAP.

**Nested conditions:** Chain multiple ternary operators for multi-branch logic:
```
close > open ? (high / low > 1.25 ? close - open : 0.5*(high - low)) : vwap - close
```
Equivalent to:
```
if (close > open):
    if (high / low > 1.25):
        alpha = close - open      # strong bullish breakout
    else:
        alpha = 0.5*(high - low)  # moderate bullish
else:
    alpha = vwap - close          # bearish / below average
```

**Single-line nested form (simpler):**
```
close > x ? a : close > y ? b : c
```
Reads: if close > x → a; else if close > y → b; else → c.

**Use case:** Conditional logic is most useful for `trade_when`-style signals where you want to assign different alpha values depending on market regime, data coverage, or signal strength.

---

## 2. Decay — Mechanics and Recommendations

**What Decay does:** Averages today's alpha output weights with the previous N days' outputs, using a linearly decreasing weight schedule:

```
alpha_modified = (N×alpha[t] + (N-1)×alpha[t-1] + ... + 1×alpha[t-N+1]) / (N×(N+1)/2)
```

With Decay=5:
```
alpha_modified = (5×alpha[today] + 4×alpha[today-1] + 3×alpha[today-2] + 2×alpha[today-3] + 1×alpha[today-4]) / 15
```

More recent days have higher weight; the oldest day has weight 1. This is a **weighted moving average of portfolio positions**, not of the raw data.

**Key point:** Decay is applied to the alpha **output** (position weights), not to input data fields. It does not change what signals you're looking at — only how smoothly positions change day to day.

**Decay vs. ts_decay_linear:**
* `Decay` setting: applied to alpha output weights after the expression is evaluated
* `ts_decay_linear(field, N)`: applied to input data inside the expression — **⛔ BANNED** (correlates with submitted alpha)
* Use `hump()` inside the expression instead of `ts_decay_linear`

**Recommendation:** Target final Turnover ≤ 40%. Start at Decay=6 and adjust:
* Too high turnover → increase Decay
* Too low turnover (< 2%) → decrease Decay or switch data frequency
* All smoothing causes some information loss — don't over-decay a strong signal

---

## 3. Delay — Trading Days, Not Calendar Days

**Critical fact:** All delay/lookback parameters in BRAIN are in **trading days**, not calendar days.

* 1 trading day ≈ 1 business day (Mon–Fri, excluding holidays)
* 5 trading days ≈ 1 calendar week
* 21 trading days ≈ 1 calendar month
* 63 trading days ≈ 1 calendar quarter
* 252 trading days ≈ 1 calendar year

**Delay=1 (D1):**
* Positions are taken **at market open** the day after the signal is generated
* Code runs just before the market opens using data up to the **previous day**
* Can use: yesterday's `close`, `high`, `low`, `open`, `volume`, etc.
* Standard mode for all our alphas — lower transaction costs, no microstructure noise

**Delay=0 (D0):**
* Positions are taken **at market close** on the same day the signal is generated
* Code runs just before market close using data up to **today** (including today's `open`, `high`, `low`)
* Higher transaction costs — you're trading into the closing auction
* Requires Sharpe ≥ 2.0 (vs 1.25 for D1) — the bar is much higher because intraday signals are noisier
* Captures overnight gaps and after-hours news reactions that D1 misses

**Why D1 even when D0 has better IS performance:**
D0's higher IS Sharpe comes with a cost: higher transaction costs that the simulation doesn't account for. A D1 alpha with Sharpe=1.40 can produce equal or greater real-world PnL than a D0 alpha with Sharpe=1.80, because the D1 alpha's lower transaction costs make up the difference. Only use D0 if you deeply understand market microstructure and specifically need intraday signal execution.

**Delay example:**
```
# alpha = -returns (reversion)
# Delay=1: bets against yesterday's return (trade at today's open)
# Delay=0: bets against today's return (trade at today's close — you need to know today's return!)
```

---

## 4. Rank — Mechanics and Why It Works

`rank(x)` sorts all stocks in the universe by their value of `x` on that day and assigns uniform percentile scores from 0.0 (worst) to 1.0 (best).

**Why this matters:**
* The resulting weight distribution is **uniform** — every stock gets a distinct, proportional weight
* No outliers — a stock with revenue = $1 trillion and one with revenue = $1 billion don't dominate the portfolio; they're placed at their percentile rank
* Automatically balances long and short sides — stocks above the median (rank > 0.5) are long; below are short
* After neutralization, the neutral point shifts but the uniform distribution property remains

**`rank()` vs `group_rank()`:**
* `rank(x)`: ranks each stock against the **entire universe** (3000 stocks)
* `group_rank(x, group)`: ranks each stock against **its group peers only** (e.g. within its industry)
* `group_rank` produces a structurally lower self-correlation because the ranking is industry-relative, not market-wide

**Rank is a robustness test:** BRAIN's submission process includes a "rank test" — changing your raw signal to `rank(signal)`. If performance collapses, the alpha was relying on extreme outlier values. Alphas using `rank()` pass this test by construction.

---

## 5. Pasteurize — What It Actually Does

`Pasteurize = ON` (default) does **two things**:

1. **Replaces `INF` values with `NaN`:** When a calculation produces infinity (e.g. `1/returns` when returns=0), pasteurize converts it to NaN so no weight is assigned to that stock.

2. **Removes out-of-universe stocks:** If a stock is in TOP2000 but NOT in your TOP1000 universe, pasteurize sets its alpha value to NaN — the stock gets zero weight. Without pasteurization, group operators might accidentally include out-of-universe stocks in their calculations.

**NaN vs 0 — critical distinction:**
* `alpha = NaN`: stock gets **no weight** and is excluded from all subsequent operations (decay, neutralization, etc.)
* `alpha = 0`: stock gets **zero weight but is still included** — decay can make it non-zero, neutralization shifts it based on group mean

**When to use `pasteurize()` manually:**
```
pasteurize(1 / returns)   # prevents INF from dominating weights when returns=0
```

Use it any time division or other operations could produce infinite values.

---

## 6. Truncation — The Weight Cap

Truncation is a simulation setting (we use `0.08` by default) that caps the maximum weight of any single stock at the specified fraction of book size:

* `Truncation = 0.08`: max 8% of $20M = $1.6M per stock
* `Truncation = 0.10`: max 10% = $2M per stock (BRAIN's hard limit for submission)

Truncation is applied **after** the alpha expression and decay — it clips any weights that exceed the cap and redistributes the excess across other positions.

**Use when:**
* Low-coverage data causes 1–2 stocks to absorb all weight
* A single stock has an extreme alpha value that `rank()` didn't normalize away
* As a baseline safety net in all simulations (already in our BASE dict)

---

## 7. min(x, y) and max(x, y) — Parallel Operations

`min(x, y)` computes the **parallel minimum** — it compares `x[i]` and `y[i]` for each stock `i` independently and returns the smaller of the two:

```
min(0.5*(open + close), high)
# For each stock: returns whichever is smaller — the midpoint or the high
```

This is equivalent to R's `pmin()` or Python's `np.minimum()` — NOT the minimum across all stocks (that would be a cross-sectional operation).

`max(x, y)` works identically but returns the larger of the two values per stock.

---

## 8. Exponentiation — The ^ Operator

BRAIN supports the `^` operator for exponentiation:

```
x ^ y     # x to the power y
```

**Euler's number (e^x):**
```
2.71828 ^ x    # approximation of e^x
```

**More useful operators for financial data:**

* `signed_power(x, 0.5)` — square root that preserves sign: `sign(x) * abs(x)^0.5`. Better than `sqrt()` for signed signals because `sqrt()` returns NaN for negative values.
* `power(x, 0.5)` — standard square root (returns NaN if x < 0)
* `log(x)` — natural logarithm for compressing multiplicative distributions (revenue, assets). Only valid for x > 0.

**When to use exponential transforms:**
* `log()`: normalize fields that span orders of magnitude (revenue $10M to $500B)
* `signed_power(x, 0.5)`: soften outlier signals while preserving direction
* `x ^ 2`: amplify differences between strong and weak signals (rarely useful — prefer `rank()`)

---

## 9. Skewness and ts_moment

**Skewness** measures the asymmetry of a distribution:
* `skewness > 0`: distribution has a longer right tail (more extreme positive outliers)
* `skewness < 0`: longer left tail (more extreme negative outliers)
* `skewness = 0`: symmetric (like a normal distribution)

**In BRAIN:** `ts_moment(x, d, k)` computes the kth central moment of `x` over `d` days:

```
m = ts_mean(x, d)
ts_moment(x, d, k) = mean((x - m)^k, d)
```

| k | What it computes |
| :--- | :--- |
| 1 | Mean deviation (≈ 0 by definition) |
| 2 | Variance |
| 3 | Skewness (unnormalized) |
| 4 | Kurtosis (unnormalized — measures tail heaviness) |

**Alpha use:** High skewness in returns can indicate a stock is prone to sudden jumps (lottery-like behavior). Stocks with high positive skewness tend to be overpriced (investors overpay for upside lottery tickets):
```
rank(ts_moment(returns, 252, 3))   # skewness of annual returns — high = lottery stock = overpriced
```

---

## 10. Quick Reference: Settings Summary

| Setting | What it does | Our default | Notes |
| :--- | :--- | :--- | :--- |
| **Delay** | When positions are taken (1=next open, 0=today's close) | 1 | Always D1 |
| **Decay** | Smooths output weights over N days (linear weighted avg) | 6 | Adjust ±2 to tune turnover |
| **Truncation** | Max weight per stock as fraction of book | 0.08 | Hard limit is 0.10 |
| **Universe** | Which stocks are eligible | TOP3000 / TOP200 | See `WQ_Universe_Reference.md` |
| **Neutralization** | Removes group-mean exposure | INDUSTRY (Fund/Analyst) / SUBINDUSTRY (others) | See `WQ_Neutralization_Strategy.md` |
| **Pasteurization** | Replaces INF→NaN + enforces universe | ON | Always ON |
| **NaN Handling** | Replaces NaN with 0 or group mean | OFF | OFF preserves real gaps |
