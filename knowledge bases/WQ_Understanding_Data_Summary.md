# WorldQuant BRAIN: Understanding Data (Knowledge Base)
> **Purpose:** A guide on how to navigate, analyze, and implement datasets within BRAIN, focusing on data types, exploration strategies, and specific insights for Analyst (model77) and Sentiment (sentiment1) datasets.

---

## 1. Data Fundamentals
Before trading a field, you must understand its structure:

* **Matrix Data:** One value per instrument per day (e.g., closing price). Can be used directly in Alpha expressions.
* **Vector Data:** Multiple values per instrument per day (e.g., 5 news articles published on AAPL today).
    * *Rule:* You **must** convert Vector data into Matrix data using aggregation operators (e.g., `vec_avg()`, `vec_count()`) before applying math.
    * *Warning:* Aggregated vectors (like daily news counts) have incredibly high turnover. You must wrap them in `ts_decay` or `ts_rank` to stabilize the signal.
* **Group Data:** Categorical matrices (e.g., Industry, Sector) used to neutralize signals across peers.
    * *Custom Groups:* You can build your own groups using `bucket(signal, range)`. Always wrap custom groups in `densify()` to prevent the simulator from crashing on empty buckets.
* **Event Data (⚠️ CONFIRMED Session 25):** Point-in-time event records — NOT continuous daily series. Standard operators ALL fail with "does not support event inputs":
    * Affected families: `anl4_ady_*`, `anl4_*detail*`, `anl4_adxq*` (358 confirmed dead fields).
    * Safe `anl4_*` families (continuous consensus estimates): `anl4_fs_*`, `anl4_ebit_*`, `anl4_fcf_*`, `anl4_adjusted_*` — these work normally.
    * Workaround (untested): `trade_when(event_field, alpha_signal, -1)` — only rebalances on event days.
* **Categorical/String Fields:** Fields ending in `_currency`, `_currency_code`, `_reporting_currency`, `_country_code` etc. are string identifiers. Cannot be used in any numeric operator. Generator auto-filters these.

---

## 2. The 6 Data Probes (Data Driven Research)
When exploring an unknown data field, run these Fast Expressions (with `Decay = 0`, `Neutralization = NONE`) and check the "Long/Short Count" in the IS Summary to deduce its properties:

1. **Coverage:** `datafield` (What % of the Universe does it cover?)
2. **Sparsity:** `datafield != 0 ? 1 : 0` (Is the data mostly zeros?)
3. **Update Frequency:** `ts_std_dev(datafield, 5) != 0 ? 1 : 0` (If zero, the data does not update weekly; it may be quarterly).
4. **Bounds:** `abs(datafield) > X` (Are values normalized between -1 and 1?)
5. **Averages:** `ts_median(datafield, 1000) > X` (What is the 5-year baseline?)
6. **Distribution:** `X < scale_down(datafield) && scale_down(datafield) < Y` (Is the data skewed to the upside or downside?)

---

## 3. The Data Explorer
BRAIN's AI-powered search engine allows you to hunt for specific data rather than browsing blindly.

* **NLP Search:** Search using natural language (e.g., "trade by people inside company").
* **Filter by Criteria:** Search for datasets with high coverage but low "Alpha Count" or "User Count" to find uncrowded signals (essential for passing the Correlation Test).
* **Search Strategy (3Ss):** Keep searches Short, Simple, and Straightforward. Always include abbreviations (e.g., "Earnings Per Share" AND "EPS").

---

## 4. Key Dataset Highlights

### A. The 'model77' Dataset (Analysts' Factor Model)
* **What it is:** Pre-calculated institutional factor metrics (Value, Momentum, Quality, Risk).
* **Coverage Strategy:** If coverage is <70%, explicitly set your simulation Universe to `TOP1000` or `TOPSP500`. Do not force it on `TOP3000`.
* **Pro-Trades:**
    * **Value:** `mdl77_fa_ebitdaev` (EBITDA to EV yield).
    * **PEAD (Post-Earnings Drift):** `mdl77_400_sue` (Standardized Unexpected Earnings).
    * **Risk:** `mdl77_altmanz` (Bankruptcy risk score).

### B. The 'sentiment1' Dataset (Research Sentiment & Earnings)
* **What it is:** A hybrid dataset tracking market mood (news/socials) and Analyst behavior (Estimates/Surprises).
* **The "Two-Speed" Problem:**
    * *Sentiment Scores:* Very fast-moving and noisy. High turnover. Requires heavy `ts_decay` smoothing.
    * *Analyst Estimates:* Slow-moving. Do not use lookbacks >63 days, as older estimates become irrelevant.
* **Pro-Trades:**
    * **Sentiment Extremes:** Trade `snt1_cored1_score` explicitly when it breaches +/- 5.
    * **Analyst Consensus:** `snt1_d1_buyrecpercent` (Ratio of Buy to Sell recommendations). Always filter by `snt1_d1_analystcoverage` to ignore stocks with only 1 analyst rating.
