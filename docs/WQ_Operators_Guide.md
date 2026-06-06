# 📘 WorldQuant BRAIN: Master Operators Guide

A complete, clean reference guide for WorldQuant BRAIN Alpha operators, including practical examples, edge-case handling (like NaNs), and syntax.

---

## 📑 Table of Contents
1. [Arithmetic Operators](#1-arithmetic-operators)
2. [Logical Operators](#2-logical-operators)
3. [Time Series Operators](#3-time-series-operators)
4. [Cross Sectional Operators](#4-cross-sectional-operators)
5. [Vector Operators](#5-vector-operators)
6. [Transformational Operators](#6-transformational-operators)
7. [Group Operators](#7-group-operators)

---

## 🧮 1. Arithmetic Operators

- **`abs(x)`**
  Returns the absolute value, removing any negative sign. Ensures only magnitude is considered. 
  > *Example:* `abs(close - open)`

- **`add(x, y, filter=false)`** / **`x + y`**
  Adds inputs element-wise. 
  > *Pro-Tip:* Use `filter=true` to treat `NaN`s as `0` before summing to improve coverage without backfilling. Example: `add([1, NaN], [4, 5], filter=true)` = `[5, 5]`.

- **`densify(x)`**
  Converts a grouping field of many buckets into a lesser number of only available buckets. Makes working with grouping fields computationally efficient. 

- **`divide(x, y)`** / **`x / y`**
  Divides `x` by `y`.

- **`inverse(x)`**
  Returns `1 / x`.

- **`log(x)`**
  Calculates the natural logarithm (base e). Used to normalize data, reduce skewness, or convert multiplicative relationships to additive ones. *(Input must be > 0)*.

- **`max(x, y, ...)`** / **`min(x, y, ...)`**
  Returns the maximum or minimum value of all inputs.

- **`multiply(x, y, ..., filter=false)`** / **`x * y`**
  Multiplies inputs. If `filter=true`, `NaN`s are replaced with `1` before multiplication.

- **`power(x, y)`**
  Raises `x` to the power of `y` (`x ^ y`). 

- **`reverse(x)`**
  Returns `-x`.

- **`sign(x)`**
  Returns `1` for positive, `-1` for negative, `0` for zero, and `NaN` for `NaN`.

- **`signed_power(x, y)`**
  Raises `x` to the power of `y` while preserving the sign of `x`. 
  > *Formula:* `sign(x) * (abs(x) ^ y)`

- **`sqrt(x)`**
  Non-negative square root. Equivalent to `power(x, 0.5)`. Returns `NaN` for negative numbers.

- **`subtract(x, y, filter=false)`** / **`x - y`**
  Subtracts left to right. If `filter=true`, `NaN`s are treated as `0`.

---

## 🧠 2. Logical Operators

- **`and(x, y)`** / **`or(x, y)`**
  Returns `1` if both/either are true (1), else `0`.

- **`not(x)`**
  Returns `0` if `x` is 1, and `1` if `x` is 0.

- **`if_else(condition, true_expr, false_expr)`**
  Returns the first expression if the condition is true, otherwise the second.
  > *Example:* `if_else(volume > adv20, ts_delta(close,3)*2, ts_delta(close,3))`

- **`is_nan(x)`**
  Returns `1` if input is `NaN`, else `0`. Excellent for creating fallback logic.

- **Comparators:** `x < y`, `x <= y`, `x == y`, `x > y`, `x >= y`, `x != y`
  Returns `1` if true, `0` if false.

---

## 📈 3. Time Series Operators

- **`days_from_last_change(x)`**
  Days since the value last changed. Great for tracking data "age" or event staleness.

- **`hump(x, hump=0.01)`**
  Limits magnitude of changes to reduce turnover. If change is < hump limit, it keeps yesterday's value.

- **`kth_element(x, d, k, ignore="NaN")`**
  Looks back `d` days and returns the `k`-th value, ignoring specified inputs.
  > *Pro-Tip:* Setting `k=1` and `ignore="NaN"` is a highly efficient way to backfill.

- **`last_diff_value(x, d)`**
  Returns the most recent value in the past `d` days that is *different* from today's value.

- **`ts_arg_max(x, d)`** / **`ts_arg_min(x, d)`**
  Returns the number of days ago (index) the maximum/minimum value occurred in the last `d` days. (Today = 0).

- **`ts_av_diff(x, d)`**
  Returns `x - ts_mean(x, d)` while ignoring `NaN`s in the mean calculation.

- **`ts_backfill(x, lookback=d, k=1)`**
  Replaces `NaN`s with the `k`-th most recent valid value from the lookback window.

- **`ts_corr(x, y, d)`**
  Pearson correlation between `x` and `y` over `d` days (-1 to 1).

- **`ts_count_nans(x, d)`**
  Counts how many `NaN`s exist in the last `d` days.

- **`ts_covariance(y, x, d)`**
  Covariance between `x` and `y` over `d` days.

- **`ts_decay_linear(x, d, dense=false)`**
  Averages recent values giving linear higher weight to recent days. Smooths data and reduces turnover. 
  > *Pro-Tip:* Best used in intermediate steps, e.g., `rank(ts_decay_linear(x, 5))`.

- **`ts_delay(x, d)`**
  Returns the value of `x` from exactly `d` days ago.

- **`ts_delta(x, d)`**
  `x - ts_delay(x, d)`. Measures absolute momentum/change.

- **`ts_mean(x, d)`**
  Simple moving average over `d` days.

- **`ts_product(x, d)`**
  Multiplies all values over `d` days. 
  > *Example:* `power(ts_product(returns, 10), 1/10)` gives geometric mean.

- **`ts_quantile(x, d, driver="gaussian")`**
  Computes `ts_rank` and maps it to a statistical distribution (`gaussian`, `uniform`, `cauchy`). Highly effective for normalizing skewed data histories.

- **`ts_rank(x, d, constant=0)`**
  Ranks current value against its own `d`-day history (0.0 to 1.0).

- **`ts_regression(y, x, d, lag=0, rettype=0)`**
  Runs an OLS Linear Regression over `d` days. `rettype` selects output: 
  `0` = Error Term | `1` = Alpha (Intercept) | `2` = Beta (Slope) | `6` = R-Square.

- **`ts_scale(x, d, constant=0)`**
  Min-max scaling of `x` over `d` days to a `[0, 1]` range. *(Sensitive to outliers).*

- **`ts_std_dev(x, d)`**
  1-Standard deviation of `x` over `d` days (Volatility).

- **`ts_step(1)`**
  An incrementing counter. Often used as the `x` (independent variable) in `ts_regression`.

- **`ts_sum(x, d)`**
  Sum of values over `d` days.

- **`ts_zscore(x, d)`**
  Standardizes data to its historical mean. Formula: `(x - mean) / std_dev`.

---

## 🌐 4. Cross Sectional Operators 
*(Operates across the daily universe of stocks)*

- **`normalize(x, useStd=false, limit=0.0)`**
  Subtracts the daily market mean from `x`. If `useStd=true`, divides by std (essentially a z-score). `limit` acts as a symmetric cap/winsorize bound.

- **`quantile(x, driver="gaussian", sigma=1.0)`**
  Ranks cross-sectionally, shifts, and maps to a distribution to strictly enforce an outlier-free shape.

- **`rank(x, rate=2)`**
  Uniformly distributes cross-sectional values between `0.0` (worst) and `1.0` (best). The standard normalizer for Alphas.

- **`scale(x, scale=1, longscale=1, shortscale=1)`**
  Adjusts values so the sum of their absolute values equals a target book size (default 1).

- **`winsorize(x, std=4)`**
  Clamps extreme outliers to ±`std` deviations from the mean.

- **`zscore(x)`**
  Cross-sectional Z-score: `(x - mean) / std`.

---

## 🧮 5. Vector Operators

- **`vec_avg(x)`**
  Averages all elements in a vector field for each stock on that day.

- **`vec_sum(x)`**
  Sums all elements in a vector field. Excellent for aggregating intraday "buzz" or sentiment vectors.

---

## 🔄 6. Transformational Operators

- **`bucket(rank(x), range="...", buckets="...")`**
  Divides ranked data into categorical buckets. Essential for creating custom groups before passing them to Group Operators. 
  > *Pro-Tip:* Wrap the result in `densify()` to dramatically speed up simulation times!

- **`trade_when(trigger_cond, new_alpha, exit_cond)`**
  - If `trigger` is true → Alpha = `new_alpha`
  - If `exit` is true → Alpha = `NaN` (closes position)
  - If neither → Alpha holds its previous value.
  > *Pro-Tip:* This is a massive turnover reducer.

---

## 🏢 7. Group Operators 
*(For Industry, Sector, Country, or Custom Buckets)*

- **`group_backfill(x, group, d, std=4.0)`**
  Fills `NaN`s using a winsorized mean of other stocks *in the same group* over `d` days. Extremely powerful for patching spotty fundamental data.

- **`group_mean(x, weight, group)`**
  Harmonic mean within a group. Perfect for averaging P/E or valuation ratios.

- **`group_neutralize(x, group)`**
  Subtracts the group's mean from `x`. Removes sector-wide market movements so you only trade the intra-group differences.

- **`group_rank(x, group)`**
  Ranks `[0.0 to 1.0]` solely against peers in the same group.

- **`group_scale(x, group)`**
  Min-max scaling `[0.0 to 1.0]` within the group.

- **`group_zscore(x, group)`**
  Calculates how many standard deviations a stock is from its *group's* average, rather than the whole market average.