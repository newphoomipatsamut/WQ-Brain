# WorldQuant BRAIN: Core Concepts & Mechanics (Knowledge Base)
> **Purpose:** A distilled summary of the "Discover BRAIN" documentation. Feed this to AI assistants to align their understanding of WorldQuant's simulation engine, metrics, and Fast Expression language.

---

## 1. What is an Alpha? (The Lifecycle)
An Alpha on BRAIN is **not** just a buy/sell signal. It is a mathematical model that transforms raw market data into an **allocation engine**.
* **Expression:** The math (e.g., `rank(sales)`).
* **Weights:** The expression outputs raw signals, which are **normalized** so the sum of their absolute values equals 1 (100%).
* **Long vs. Short:** Positive weights indicate buying (Long). Negative weights indicate selling borrowed shares (Short).
* **Allocation:** The normalized weights are multiplied by the total Book Size (e.g., $20 Million) to determine the exact dollar amount invested in each stock every day.

---

## 2. Fast Expression Language
A proprietary, pseudo-code language used to write Alphas. It lacks classes, loops, or functions, focusing purely on logic.
* **Data Fields (Nouns):** The raw data (e.g., `close`, `volume`, `mdl177_...`).
* **Operators (Verbs):** The mathematical actions (e.g., `rank()`, `ts_zscore()`).
* **Syntax Rules:**
  * Use semicolons (`;`) to end intermediate calculation lines.
  * **CRITICAL:** The very last line of the expression must **NOT** have a semicolon. This final line is the Alpha output vector.
  * Use `/* comments */` for documentation.

---

## 3. The "Big Three" IS (In-Sample) Metrics
BRAIN does not just grade on Returns; it grades on risk-adjusted consistency and tradability.

### A. Sharpe Ratio (Target: > 1.25)
* **Definition:** Measures risk-adjusted return (Mean Daily PnL / Std Dev of Daily PnL).
* **Concept:** A smooth, 45-degree PnL curve yields a high Sharpe. High volatility kills Sharpe.

### B. Turnover (Target: 1% to 70%)
* **Definition:** The ratio of value traded to book size. How much of the portfolio is flipped daily.
* **Concept:** High turnover = high transaction costs. If turnover is too high, the Alpha is rejected regardless of returns.

### C. Fitness (Target: > 1.00)
* **Definition:** WorldQuant's ultimate proprietary metric.
* **Formula:** `Fitness = Sharpe * sqrt(abs(Returns) / Turnover)`
* **Concept:** To increase Fitness, you must increase Sharpe and Returns, while strictly minimizing Turnover.

---

## 4. Crucial Simulation Settings

* **Delay:** Always use `Delay = 1` (D1). It means trading happens one day after the signal is generated. (D0 is functionally unviable due to extreme threshold requirements).
* **Universe:** Limits the pool of stocks. `TOP3000` is safer for passing Sharpe tests due to diversification. `TOP200` yields higher Quality Scores but is harder to pass.
* **Truncation (e.g., 0.08):** Caps the maximum weight of any single stock at 8%. Prevents the Alpha from blowing up due to over-concentration in one asset.
* **Decay (e.g., 6):** Applies a linear rolling average to the final Alpha weights over the last $X$ days. **Highly effective at reducing Turnover.**
* **Neutralization (e.g., SUBINDUSTRY):** Subtracts the group's mean weight from every stock in that group. 
  * *Effect:* Forces the sum of weights in that industry to exactly 0 (Perfectly Market Neutral). Protects the portfolio from macro market crashes.

---

## 5. Troubleshooting Common IS Rejections

| Error / Failure | Root Cause | Solution |
| :--- | :--- | :--- |
| **Low Sharpe / Sub-Universe Sharpe** | High volatility or too few stocks. | Expand Universe to `TOP3000` or apply `rank()` cross-sectionally. |
| **Max weight > 10%** | Alpha concentrated capital in 1-2 stocks. | Add `Truncation = 0.08` to settings and wrap final output in `rank()`. |
| **Too few instruments assigned weight** | Too many `NaN`s (missing data) in the dataset. | Use `ts_backfill()` or `group_backfill()` to fill missing days. |
| **High Turnover (Fitness Block)** | Signal flips from Long to Short too often. | Use `ts_decay_linear()` in the code, or increase the `Decay` setting (e.g., 6). |