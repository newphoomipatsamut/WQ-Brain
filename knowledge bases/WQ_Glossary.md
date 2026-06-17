# WorldQuant BRAIN: Research Glossary (Knowledge Base)
> **Purpose:** A-to-Z definitions of every technical term used on the BRAIN platform. Skip to the term you need; cross-references to deeper KB files are included where relevant.

---

## A

**Alpha**
A mathematical model that predicts future price movements of financial instruments. On BRAIN, an Alpha is a Fast Expression that produces daily portfolio weights → simulated on historical data → submitted for live OS trading.

**Alpha List**
A tool to compare multiple Alphas — view overlaid PnL charts and check cross-Alpha correlations. Access via "Alpha to list" on the Alphas or Simulate page.

**ATOM** *(Consultants only)*
An Alpha built on a **single dataset** with relaxed submission checks. Skips the IS Ladder Sharpe tests. Good for proving a dataset has signal without clearing the full 6/7 check gauntlet.

---

## B

**Backfill**
Replacing missing (`NaN`) values in a data field with recent valid values. Operators: `ts_backfill(x, d)`, `group_backfill(x, group, d)`, `kth_element(x, d, k, ignore="NaN")`. See `WQ_Weight_Coverage.md`.

**Backtesting**
Testing a model on historical data. On BRAIN, this is the IS (In-Sample) simulation — the 5-year period you see results for when you simulate. See `WQ_Alpha_Creation_And_Submission_Guide.md`.

**Base Payment**
Daily-accruing compensation for ACTIVE submitted Alphas. Determined by alpha weight in the strategy portfolio. Stops accruing when an Alpha is DECOMMISSIONED.

**Bollinger Bands**
A technical indicator: 20-day SMA (middle band) ± N × daily standard deviation (upper/lower bands). In Fast Expression: `ts_mean(close, 20)` (middle), `ts_mean(close, 20) + ts_std_dev(close, 20)` (upper), etc.

**Booksize**
Fixed at **$20M** per day throughout every BRAIN simulation. Not reinvested — losses are replaced by cash injection. Denominator for Returns = `0.5 × $20M = $10M`. See `WQ_Interpret_Results_Summary.md`.

---

## C

**Capacity**
The maximum capital an Alpha can absorb before marginal profitability falls to zero. Driven by three factors: **high liquidity** (large-cap stocks), **low correlation** (unique signal), **low turnover** (fewer transactions = easier to scale). Of these, low turnover is the biggest contributor. See `WQ_Improving_Fitness.md` Section 4.

**Capitalization (cap)**
Daily market capitalization = outstanding shares × share price. Available as the data field `cap` in Price-Volume dataset. Use `FIELD / cap` to size-normalize dollar-amount fundamentals into yield-style ratios.

**Combination Expression** *(Consultants only)*
The expression used to combine Alphas in a SuperAlpha — outputs daily weights for each constituent Alpha.

**Correlation**
Measures uniqueness of an Alpha relative to the existing book. Must be < 0.70 (self-correlation) to submit. See `WQ_Reducing_Correlation.md`.

**Coverage**
The fraction of universe instruments for which a data field has a defined (non-NaN) value on a given day. Low coverage → weight concentration → CONCENTRATED_WEIGHT check failure. Fix with backfill operators. See `WQ_Weight_Coverage.md`.

---

## D

**Data Field**
A named data series: one value per instrument per day (matrix) or multiple values per instrument per day (vector). E.g. `close`, `revenue`, `nws12_afterhsz_120_min`. See `WQ_Understanding_Data_Summary.md`.

**Dataset**
A collection of related data fields from a single provider/source. E.g. "Price-Volume data" or "Analyst estimate predictions". Each dataset has a category (Fundamental, Analyst, Model, etc.) which determines the appropriate neutralization and lookback.

**Dataset Value Score** *(Consultants only)*
Measures underutilization of a dataset — higher score = fewer researchers using it = less crowded signal. Distinct from Value Factor (which relates to payments). Prioritize high-value-score datasets for lower self-correlation risk.

**Decay**
Post-expression smoothing of alpha output weights using a linearly decreasing weighted average over N days. Formula with Decay=N: `alpha_out = (N×alpha[t] + (N-1)×alpha[t-1] + ... + 1×alpha[t-N+1]) / (N×(N+1)/2)`. Reduces turnover. Our default: Decay=6. See `WQ_Operators_Deep_Reference.md` Section 2.

**Delay**
When positions are taken. Always in **trading days** (not calendar days).
- `Delay=1`: trade at next morning's open using yesterday's data (our standard)
- `Delay=0`: trade at today's close using today's data (requires Sharpe ≥ 2.0, high transaction costs)
See `WQ_Operators_Deep_Reference.md` Section 3.

**Dividend**
Distribution of company earnings to shareholders. Field: `dividend_yield = dividend / close`. Value signal — high yield relative to industry peers often signals undervaluation. See `WQ_Fundamental_Data_Reference.md`.

**Drawdown**
Largest peak-to-trough drop in PnL during the IS period, expressed as a percentage of half-booksize ($10M). High drawdown = fragile alpha. Related to but distinct from Sharpe — an alpha can have high Sharpe but large drawdown if there's one bad year. See `WQ_Smoothing_PnL.md`.

---

## F

**Fast Expression (FASTEXPR)**
BRAIN's proprietary expression language for writing Alphas. No loops, classes, or functions — purely mathematical operators applied to data fields. Uses semicolons to separate intermediate lines; the final line (no semicolon) is the alpha output. See `WQ_Discover_BRAIN.md`.

**Financial Ratio**
Metrics derived from financial statements (balance sheet, income statement, cash flow) to assess company quality. Key categories: liquidity (current ratio), leverage (debt/equity), profitability (ROE, ROA), valuation (P/E, EV/EBITDA). These are the inputs for fundamental alpha signals. See `WQ_Fundamental_Data_Reference.md`.

**Fitness**
`Fitness = Sharpe × sqrt(abs(Returns) / max(Turnover, 0.125))`. The primary IS submission gate (must be ≥ 1.00). Rating scale: Spectacular (>3.25), Excellent (>2.60), Good (>1.95), Average (>1.30), Needs Improvement (≤1.30). See `WQ_Improving_Fitness.md`.

**Fundamental Analysis**
Evaluating a security by examining economic and financial factors — earnings, revenue, debt, management quality. Contrasts with technical analysis (price/volume patterns). Fundamental data fields update quarterly or annually. See `WQ_Fundamental_Data_Reference.md`.

---

## G

**Genius** *(Consultants only)*
Leveled system: Gold → Expert → Master → Grandmaster. Higher levels unlock more data, tools, and opportunities. Tracks pyramid completion, alpha submission volume, and diversity.

**Group**
A categorical field classifying instruments into buckets. Standard groups: `market`, `sector`, `industry`, `subindustry`. Used as input to group operators (`group_rank`, `group_neutralize`, `group_zscore`). Custom groups can be created with `bucket()`.

**Grouping Field**
Fields that categorize instruments: `country`, `exchange`, `currency`, `market`, `sector`, `industry`, `subindustry`. These can be used in expressions without counting against Genius pyramid or Power Pool field limits.

---

## I

**Information Ratio (IR)**
`IR = mean(daily PnL) / std_dev(daily PnL)`. The daily version of Sharpe. `Sharpe = IR × sqrt(252)`. See `WQ_Improving_Sharpe.md`.

**In-Sample (IS)**
The 5-year historical simulation period (7 years ago to 2 years ago). All IS metrics (Sharpe, Fitness, Turnover, Checks) are what you see when simulating. See `WQ_Alpha_Creation_And_Submission_Guide.md`.

**Investability** *(Consultants only)*
Position-size limits based on a fraction of `adv20`. Ensures the alpha doesn't try to trade more than the market can absorb in liquid instruments. Improves sub-universe Sharpe by avoiding illiquid micro-cap positions.

**IS Ladder** *(Consultants only)*
Checks that Sharpe over each of the most recent IS years stays above a minimum threshold — not just the 5-year average. Catches alphas that had one great year covering for three bad years. A key overfitting guard.

---

## K

**Kurtosis**
Fourth central standardized moment — measures tail heaviness. High kurtosis = fat tails = more extreme events than a normal distribution would predict. Operator: `ts_kurtosis(x, d)`. Useful for risk-aware signal construction. Related to `ts_moment(x, d, 4)`.

---

## L

**Liquidity**
Ease of buying/selling without moving the price. Proxied by trading volume on BRAIN. Smaller universes (TOP200, TOP1000) are more liquid — positions can be filled without market impact. See `WQ_Universe_Reference.md`.

**Long-Short Neutral**
BRAIN's portfolio structure: equal dollar amounts on long (positive weight) and short (negative weight) sides. Profits come from the spread between longs and shorts — not from the market going up or down. `rank()` naturally creates a balanced long-short weight distribution.

---

## M

**Margin**
`Margin = PnL / Total Dollars Traded`. Profit per dollar of trading activity. High margin = each trade earns well. Low margin + high turnover = simulation looks OK but live trading deteriorates due to real transaction costs. See `WQ_Improving_Margin.md`.

**Matrix**
A data field with exactly one value per instrument per day. Standard format for all Fast Expression inputs and outputs. Examples: `close`, `returns`, `cap`, `eps`. See `WQ_Understanding_Data_Summary.md`.

**Max Trade** *(Consultants only)*
Limits daily position changes to a fraction of `adv20`. Reduces turnover in illiquid instruments, improving sub-universe Sharpe.

**Mean Reversion**
The observation that extreme price moves tend to reverse toward the historical mean. Short-term reversion (1–5 days): use `rank(ts_rank(returns, 5))`. Long-term reversion (21–63 days): use `rank(ts_mean(returns, 21))`.

**Momentum**
The empirical observation that recent price trends continue. Short-term: `ts_rank(returns, 20)`. Long-term: `ts_rank(close / ts_delay(close, 252), 20)` (52-week high proximity). Contrasts with reversion.

---

## N

**NaN (Not a Number)**
Indicates missing data or invalid computation (e.g. division by zero). A stock with `alpha = NaN` gets zero weight AND is excluded from all subsequent operations (decay, neutralization). Different from `alpha = 0`, which is included in calculations and can become non-zero after decay. See `WQ_Operators_Deep_Reference.md` Section 5.

**Neutralization**
Subtracts the group mean from every stock in that group — forces the sum of weights within each group to zero. Removes exposure to group-wide market moves. Settings: MARKET, SECTOR, INDUSTRY, SUBINDUSTRY, NONE. Our defaults: INDUSTRY for Fundamental/Analyst; SUBINDUSTRY for everything else. See `WQ_Neutralization_Strategy.md`.

---

## O

**Out-of-Sample (OS)**
Live performance after the alpha is submitted. BRAIN tests against the 2-year Semi-OS period secretly during submission. If it passes, the alpha goes ACTIVE and begins accruing in the live OS period. See `WQ_Interpret_Results_Summary.md`.

**Overfitting**
Tuning alpha parameters to maximize IS Sharpe without economic justification (e.g. changing exponent from 2 to 2.3, flipping signs for specific sectors). Overfitted alphas pass IS but fail Semi-OS or deteriorate in live OS. See `WQ_Advanced_Topics_And_D0_Summary.md`.

---

## P

**Pasteurization**
`Pasteurize = ON` (our default) does two things: (1) replaces `INF` values with `NaN`, (2) sets out-of-universe stocks to `NaN`. See `WQ_Operators_Deep_Reference.md` Section 5.

**PnL (Profit and Loss)**
`daily_PnL = Σ (position_size_i × daily_return_i)` for all instruments. Cumulative PnL chart is what you see in the simulation. Annualized PnL / $10M = Returns (%). See `WQ_Interpret_Results_Summary.md`.

**Power Pool Alpha** *(Consultants only)*
High-quality alpha: Sharpe ≥ 1.0, ≤ 8 unique operators, ≤ 3 data fields, self-correlation < 0.5. Monthly cap of 10 submissions after 3-month initial period.

**Prod Correlation**
Maximum Pearson correlation between a given alpha and ALL alphas submitted by ALL BRAIN consultants globally. Distinct from self-correlation (which only compares within your own book).

**Pyramid** *(Consultants only)*
A combination of region + delay + dataset category (e.g. USA-D1-Fundamental). Building 3+ alphas in a pyramid counts toward Genius tier progression.

---

## R

**Rank**
`rank(x)`: assigns each stock a uniform percentile score [0.0, 1.0] relative to all stocks in the universe on that day. 0 = worst, 1 = best. Removes outliers, balances long/short, passes the rank robustness test. The standard outer wrapper for most alpha expressions (`-rank(...)`). See `WQ_Operators_Deep_Reference.md` Section 4.

**Region**
Geographic market. USA is available to all users. EUR and ASI are consultant-only. Each region is tested independently for regional robustness (GLB Alphas must maintain Sharpe > 1.0 in each region).

**Regression**
Statistical measure of relationship between variables. In Fast Expression: `ts_regression(y, x, d, rettype=0)`. `rettype=2` (slope) is our primary use — extracts the trend direction of a fundamental field. See `WQ_Operators_Guide.md`.

**Relative Strength Index (RSI)**
Technical momentum oscillator [0–100]. Measures magnitude of recent price changes: RSI > 70 = overbought, RSI < 30 = oversold. In Fast Expression: `ts_mean(max(returns,0), 14) / ts_mean(abs(returns), 14) * 100` (approximate).

**Returns**
`AnnualReturn = AnnualizedPnL / (0.5 × BookSize)`. Expressed as %. Key component of Fitness — high Sharpe with low returns still gives low Fitness. See `WQ_Improving_Returns.md`.

**Reversion** → see Mean Reversion.

**Risk Factors** *(Consultants only)*
Systematic variables (market, industry, style) that influence returns independently of the alpha signal. BRAIN offers risk-factor neutralization in 3 modes: Slow Factors, Fast Factors, Slow+Fast Factors. Risk-neutralized alphas show returns orthogonal to common factor exposures.

**Robustness**
An alpha is robust if it maintains good performance across different scenarios: sub-universe test (TOP3000 → TOP1000), rank test (raw signal → `rank(signal)`), region portability, time-period consistency (no single bad year dominating). See `WQ_Advanced_Topics_And_D0_Summary.md`.

---

## S

**Sector**
Large grouping of companies by business activity (e.g. Technology, Healthcare, Energy). Broader than Industry, narrower than Market. Group operator: `group_rank(x, sector)`.

**Self-Correlation**
Maximum Pearson correlation between your new alpha and any of your own previously submitted alphas. Must be < 0.70 to submit. See `WQ_Reducing_Correlation.md`.

**Semi Out-of-Sample (Semi-OS)**
The 2-year period between the end of IS and today. Tested secretly when you click Submit — you cannot see or optimize against this data. If the alpha fails here, it is rejected.

**Sharpe Ratio**
`Sharpe = IR × sqrt(252)`. Minimum 1.25 for D1 submission, 2.0 for D0. Target > 1.25 to pass; focus on Returns once above threshold. See `WQ_Improving_Sharpe.md`.

**Signal**
An informal term for an elementary model that shows potential as an alpha. Any expression with positive IS Sharpe is a "signal."

**Simulation**
Running a Fast Expression through BRAIN's backtesting engine to produce IS metrics. Covers a rolling 5-year window (7 years ago to 2 years ago). See `WQ_Alpha_Creation_And_Submission_Guide.md`.

**Skewness**
Third central standardized moment — measures distribution asymmetry. Positive skewness = long right tail (lottery stocks). Operator: `ts_moment(x, d, 3)` (unnormalized). High-skewness stocks tend to be overpriced. See `WQ_Operators_Deep_Reference.md` Section 9.

**Standard Deviation**
Measures spread of values around the mean. Low std = stable/consistent. High std = volatile. Operator: `ts_std_dev(x, d)`. Note: `ts_std_dev` for QUARTERLY fields has near-zero pass rate (0/96 runs) — avoid for fundamental data. See `WQ_Improving_Sharpe.md`.

**Statistical Arbitrage (StatArb)**
The methodology underlying all BRAIN alphas: bet on many stocks simultaneously using mean-reversion signals. One stock's noise is cancelled out across hundreds of positions. The law of large numbers converts marginal predictive accuracy into consistent profits. Single-stock alphas are not possible on BRAIN.

**Stochastic Oscillator**
Technical mean-reversion indicator. `%K = (close - lowest_low) / (highest_high - lowest_low) × 100`. Values near 0 = oversold; near 100 = overbought. In Fast Expression: `-rank(ts_rank(close - ts_min(low, 14), 20) / ts_rank(ts_max(high, 14) - ts_min(low, 14), 20))` (approximate).

**Sub-Universe Test**
Submission check: the alpha must maintain adequate Sharpe when tested on the next-lower universe (e.g. TOP3000 → TOP1000). Threshold: `sqrt(252) × max(0.065, sqrt(sub_size/orig_size) × 0.15)` for D1. Fails when the alpha relies on illiquid micro-caps for most of its PnL. Fix: `rank()`, `Truncation=0.08`, or re-simulate directly on TOP1000/TOPSP500. See `WQ_Universe_Reference.md`.

**Super-Universe Test**
Checks that alpha Sharpe on the next-larger universe is > 0.7 × current Sharpe. An alpha on TOP1000 must still work on TOP3000 at 70% of its Sharpe.

**SuperAlpha** *(Consultants only)*
A meta-alpha that combines multiple individual alphas using a selection expression and combination expression. More robust than any single alpha.

---

## T

**Technical Analysis**
Evaluating investments using price and volume patterns. Contrasts with fundamental analysis. Tools: moving averages, RSI, Bollinger Bands, stochastic oscillator. See `WQ_Price_Volume_Data_Reference.md`.

**Test Period**
A simulation setting that hides a subset of the IS period for blind validation — the "orange line" in IS results. Use to detect overfitting before submission: build on Train (years 1–4), validate on Test (year 5).

**Truncation**
Caps the maximum weight of any single stock as a fraction of booksize. Our default: `0.08` (8% = $1.6M per stock). BRAIN's hard limit is 0.10 (10%). Applied after expression evaluation and decay. See `WQ_Operators_Deep_Reference.md` Section 6 and `WQ_Weight_Coverage.md`.

**ts-Zscore**
`ts_zscore(x, n) = (x - ts_mean(x, n)) / ts_std_dev(x, n)`. Standardizes a field to its N-day historical mean and volatility. Unlike `rank()`, preserves magnitude differences. More sensitive to outliers than `rank()`.

**Turnover**
`Daily Turnover = Dollar Trading Volume / Booksize`. Target: 1–40% (advisable), hard limit 70%. Too low (<2%) → structural Fitness ceiling. Too high (>70%) → submission rejected. See `WQ_Improving_Turnover.md`.

---

## U

**Universe**
The pool of eligible trading instruments. Defined by TOP-N (N most liquid stocks by dollar volume over 3 months). Available to all users: TOP3000, TOP2000, TOP1000, TOP500, TOP200. Consultant-only: TOPSP500, ASI/EUR universes. Our pipeline uses TOP3000 (discovery) and TOP200 (self-correlation control). See `WQ_Universe_Reference.md`.

---

## V

**Value Factor** *(Consultants only)*
Payment-related metric for consultants: combines individual alpha performance, submission diversity, and uniqueness vs. other consultants. Distinct from Dataset Value Score.

**Vector**
A data field with N values per instrument per day (N varies). Must be converted to matrix using `vec_count()`, `vec_avg()`, `vec_sum()`, `vec_median()` etc. before use in any other operator. See `WQ_Vector_Data_And_Datasets.md`.

**Visualization**
An optional simulation mode that computes advanced metrics and charts (coverage over time, PnL year-by-year, turnover chart). Increases simulation time. Use to diagnose NaN spikes, coverage drops, and turnover patterns.

**Volume**
Shares traded in a day. Proxy for liquidity and market participation. Pre-computed average: `adv20 = ts_delay(ts_mean(volume, 20), 1)`. See `WQ_Price_Volume_Data_Reference.md`.

**VWAP**
`VWAP = Total Dollar Value Traded / Total Shares Traded`. Average execution price weighted by volume. `close - vwap > 0` means stock closed above the day's average trade price (intraday bullish). See `WQ_Price_Volume_Data_Reference.md`.

---

## W

**Weight**
The alpha output for each stock — a value that, after neutralization and normalization, determines the dollar long or short allocation. Positive = long; negative = short. The sum of absolute weights = 1 (100% of booksize = $20M total exposure). `rank()` distributes weights uniformly.

**Winsorize**
`winsorize(x, std=4)`: clips values beyond ±4 standard deviations from the cross-sectional mean. Prevents extreme outliers from dominating weights. Our default `std=3` for outlier-heavy fields (e.g. `fn_comp_*`).

---

## Z

**Z-Score**
`(x - mean(x)) / std_dev(x)`. Measures how many standard deviations a value is from the mean. Cross-sectional: `zscore(x)`. Time-series: `ts_zscore(x, n)`. Group-relative: `group_zscore(x, group)`. Strong normalization tool — comparable across fields with different scales.
