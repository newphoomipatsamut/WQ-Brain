# WorldQuant BRAIN: Alpha Examples & Strategy Recipes (Knowledge Base)
> **Purpose:** A categorized reference guide of official WorldQuant Alpha examples. This document illustrates how to translate real-world economic hypotheses into Fast Expression code, scaling from basic historical comparisons to advanced statistical models.

---

## 1. Beginner Tier: Historical Comparisons & Ratios
*Focus: Looking backward to compare a company against its own history or using simple financial ratios.*

* **The "Beat Your Own History" Trade (Operating Earnings Yield)**
    * **Concept:** If a company's operating income is currently higher than its historical average, it is outperforming expectations. Buy it.
    * **Implementation:** `ts_rank(operating_income, 252)`
    * **Pro-Tip:** Always scale absolute numbers (like income) by a size metric (like assets or market cap) to ensure the growth is efficient.
* **The "Debt Trap" Trade (Appreciation of Liabilities)**
    * **Concept:** Rapidly increasing debt/liabilities signals financial distress. Short it.
    * **Implementation:** `-ts_delta(liabilities, 63)`
* **The "Avoid the Hype" Trade (Short-Term Sentiment Stability)**
    * **Concept:** High variance in internet chatter/sentiment usually precedes a "pump and dump" crash. Short unstable hype.
    * **Implementation:** `-ts_std_dev(scl12_buzz, 10)`

---

## 2. Bronze Tier: Expectations vs. Reality & Cross-Sectional Ranking
*Focus: Comparing market estimates against reality, or blending time-series analysis with cross-sectional peer ranking.*

* **The "Valuation Squeeze" (Cash Flow Multiples)**
    * **Concept:** If Enterprise Value to Cash Flow (EV/CF) drops, the stock is getting cheap relative to its cash generation.
    * **Implementation:** `-group_rank(ts_zscore(EV / CF, 252), industry)`
    * **Pro-Tip:** Wrapping `ts_zscore` (historical weirdness) inside a `group_rank` (peer comparison) creates a highly robust, low-turnover signal.
* **The "Priced In" Trade (Overpriced Stocks)**
    * **Concept:** If analyst Price Targets and Free Cash Flow estimates are moving in perfect lockstep (high correlation), the market perfectly understands the stock. No positive surprises remain. Short it.
    * **Implementation:** `-ts_corr(est_ptp, est_fcf, 20)`
* **The "Options Secret" (Volatility Arbitrage)**
    * **Concept:** The options market predicts the future (Implied Volatility), while price charts show the past (Historical Volatility). If IV > HV, the smart money is pricing in a massive move.
    * **Implementation:** `implied_volatility - historical_volatility`
    * **Pro-Tip:** Use `ts_backfill(implied_volatility, 5)` to handle missing daily options data.

---

## 3. Silver Tier: Advanced Stats, Trends, & Conditional Logic
*Focus: Multi-line expressions, extracting statistical slopes, and conditional trading execution.*

* **The "Trend Extraction" Trade (Investing for the Future)**
    * **Concept:** Finding companies with a smooth, consistent upward trajectory in long-term investments, ignoring daily noise.
    * **Implementation:** `ts_regression(long_term_investment, ts_step(1), 756, rettype=2)`
    * **Pro-Tip:** Using `ts_regression` with `rettype=2` extracts the mathematical **slope** of the trendline. This is the ultimate tool for finding steady momentum.
* **The "News Fade / Bull Trap" Trade**
    * **Concept:** If a stock spikes on open due to news, but its historical slope of news reactions has been deteriorating, it's a trap. Short it.
    * **Implementation:** Extract slope of `news_pct_1min` using `ts_regression`, multiply by upside return, and `winsorize(std=4)`.
    * **Pro-Tip:** Always `winsorize` high-frequency/minute data to prevent extreme outliers from destroying your regression models.
* **The "Mean Reversion Laggard" (Peer vs. Stock Gap)**
    * **Concept:** If an industry rallies 5% but one stock stays flat, that stock will likely snap upward to catch up.
    * **Implementation:** `trade_when(abs(peer_return - stock_return) > 0.05, signal, -1)`
    * **Pro-Tip:** Use the `trade_when` operator to ensure you only execute trades when the signal/gap is large enough to overcome transaction fees (reducing turnover).

---

---

## 4. Session 25 — Advanced Templates (Validated Research Findings)
*These templates expand beyond the basic ts_rank/ts_zscore set. Use them when basic templates fail to pass fitness or produce negative Sharpe.*

* **Volatility of a Field as a Signal**
    * **Concept:** The variability of a fundamental signal (e.g. earnings) is itself informative — low volatility = quality/consistency.
    * **Implementation:** `-rank(ts_std_dev(FIELD, 63))` or `-rank(ts_rank(ts_std_dev(FIELD, 22), 252))`
    * **⚠ Empirical warning (96 runs, 0 passes, avg_sharpe = -0.02 for QUARTERLY fields):** ts_std_dev has near-zero yield for quarterly-updated fundamental data. When it produces signal, TO is typically < 2% → structural fitness ceiling at ~0.88. Use only as a last resort for fundamentals; prioritize ts_rank/ts_regression instead.

* **Correlation Between Field and Price**
    * **Concept:** How closely a fundamental moves with price reveals whether it's already "priced in". High correlation = crowded, low = undiscovered.
    * **Implementation:** `-rank(ts_corr(FIELD, close, 63))` or `-rank(ts_rank(ts_corr(FIELD, returns, 22), 126))`

* **Trend Slope of a Fundamental**
    * **Concept:** The direction (slope) of improvement matters more than the level. A company consistently growing FCF beats one with high but flat FCF.
    * **Implementation:** `-rank(ts_regression(FIELD, ts_step(1), 252, rettype=2))`
    * **Pro-Tip:** rettype=2 returns the slope only. Use 252 for annual trend, 63 for quarterly.

* **Group-Relative Signal (lower self-corr)**
    * **Concept:** Normalise within peers before ranking cross-sectionally. Removes sector/industry bias. Structurally less correlated with existing book.
    * **Implementation:** `-rank(group_rank(ts_zscore(FIELD, 252), sector))` or `-rank(group_zscore(ts_rank(FIELD, 63), industry))`
    * **Pro-Tip:** group_rank inside rank = cross-sectional rank of a peer-relative score. Very powerful for fundamental value signals.

* **Preprocessing Sparse/Noisy Data**
    * **Concept:** Quarterly-updated fields have many NaN days. ts_backfill bridges the gaps. Outlier-heavy financials need winsorize first.
    * **Implementation (sparse):** `-rank(ts_rank(ts_backfill(FIELD, 120), 252))`
    * **Implementation (outliers):** `-rank(ts_zscore(winsorize(FIELD, std=4), 252))`

* **Multi-Stage Composition**
    * **Concept:** Wrap one transform inside another to create second-order signals.
    * **Implementation:** `-rank(ts_rank(ts_delta(FIELD, 21), 63))` — rate-of-change ranked over time
    * **⚠ BANNED patterns — DO NOT USE:** `ts_decay_linear(...)` and `rank(ts_delta(close, N))` are both banned. They correlate with existing submitted alphas and always fail self-correlation or Performance Comparison. These have been removed from all active templates.

---

## 5. Key Takeaways for Alpha Engineering
1.  **Level Up Your Math:** Raw field → ts_zscore/ts_rank → group_rank → ts_regression slope → multi-stage composition.
2.  **Combine Signals (Multi-Factor):** Multiply value signal × momentum signal to amplify.
3.  **Control Execution:** Use `trade_when` to force longer holds — reduces TO and improves Fitness. (`ts_decay_linear` is banned — use `hump()` for fitness fixes instead.)
4.  **Preprocess first:** `ts_backfill(FIELD, 120)` for sparse data, `winsorize(FIELD, std=4)` for outlier-heavy financials.
5.  **Use group operators for diversification:** `group_rank` and `group_zscore` give structurally lower self-corr than plain `rank`.
6.  **Prioritize WEEKLY fields over QUARTERLY:** WEEKLY ts_rank has a 4.3% pass rate vs QUARTERLY's 0.6% — nearly 7x more fertile. SLOW frequency fields (credit risk, slow model scores) have negative average Sharpe — avoid them.
7.  **QUARTERLY ts_std_dev is a trap:** 0 passes from 96 runs. The signal occasionally exists but always hits a fitness ceiling from ultra-low TO. Use ts_rank or ts_regression slope instead for quarterly data.