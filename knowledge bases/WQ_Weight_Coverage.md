# WorldQuant BRAIN: Weight Coverage — Common Issues & Fixes (Knowledge Base)
> **Purpose:** A focused guide on diagnosing and fixing the CONCENTRATED_WEIGHT check — one of the most common reasons a high-Sharpe alpha fails to submit.

---

## 1. What the Weight Test Checks

BRAIN enforces a hard limit: **no single stock can hold more than 10% of the total book size ($20M) at any point in the simulation.**

```
Max single-stock weight < 10%  ($2M out of $20M book)
```

This exists to limit drawdown risk in Out-of-Sample trading — if one over-concentrated stock gaps down, the portfolio suffers disproportionately.

**In our simulation setup:** `Truncation = 0.08` (8%) is set in the BASE dict. This provides a safety buffer below the 10% hard limit and is the first line of defense.

---

## 2. Root Cause 1: Low Coverage (Most Common)

The weight test fails most often when the alpha has too few stocks with valid (non-NaN) weights:
* **< 10 stocks on either the long or short side** at any point in the simulation.
* **Total < 20 stocks** with assigned weight.
* **Unbalanced long/short count** — one side dramatically outnumbers the other.

When coverage is low, the remaining stocks each receive a proportionally larger weight — eventually exceeding the 10% cap.

### How to Detect
Use visualization (BRAIN's chart tool) to plot the Long/Short count over time. Watch for:
* **Dips at the start of the simulation** — early data is sparse; coverage may be below 60% of final count for the first 1–2 years.
* **Regular spikes** at quarterly intervals — a sign of low-coverage fundamental fields dropping data periodically.
* **A sudden drop to near-zero** — a data gap causing total coverage collapse for one or more days.

### How to Fix Low Coverage

**1. Backfill missing data:**

For fields missing for just one day:
```
ts_backfill(FIELD, 2)
```

For quarterly-updated fundamental fields (data valid ~63 days between updates):
```
ts_backfill(FIELD, 120)
```
120 trading days (~6 months) safely bridges a full quarter gap with buffer.

For fields where the company's own history is too sparse (use peer group to impute):
```
group_backfill(FIELD, subindustry, 60)
```

**2. Detect abnormal coverage drops in real time:**

Filter the alpha to only trade on days when enough stocks have data:
```
group_count(is_nan(ALPHA), market) > 40 ? ALPHA : nan
```
This returns the alpha value when more than 40 stocks have data; otherwise returns `nan` — preventing the alpha from concentrating capital on the few remaining stocks on bad-data days.

**3. Remove the sparse early period:**
If coverage is below 60% of final count at the start of the IS period, trim the alpha: use `ts_delay` or restrict the IS start date in settings. BRAIN's IS period starts 7 years ago — early fundamental data may be genuinely sparse.

**4. Build your own backfill logic:**
```
is_nan(FIELD) ? last_diff_value(FIELD, 252) : FIELD
```
Uses `is_nan()` to detect gaps and `last_diff_value()` to retrieve the most recent valid reading within 252 days. Combine with `days_from_last_change()` to detect how stale the backfilled value is — and potentially down-weight very stale readings.

⚠ **Don't overuse backfill with a large back-day.** Backfilling too far back (e.g. 504 days) can introduce stale data that hurts performance — the signal you're trading may no longer be valid. Match the lookback to the data's update frequency.

---

## 3. Root Cause 2: Alpha Magnitude Distribution (Outliers)

Not all weight failures are coverage problems. Some alpha ideas produce extreme outlier values in the raw signal — a few stocks get extreme scores and absorb most of the portfolio weight even when coverage is fine.

**Signs of this problem:**
* Coverage looks fine (50+ stocks on each side), but one or two stocks consistently hit the truncation cap.
* The alpha uses raw dollar values (revenue, assets, debt) that vary by orders of magnitude across large-cap and small-cap stocks.

### How to Fix Outlier Concentration

**1. `rank()` — the primary fix:**
`rank()` transforms any distribution into a uniform [0, 1] range. Every stock gets a proportional weight regardless of how extreme its raw value is. This is the most effective single fix:
```
-rank(FIELD)
```
`rank()` also passes the rank robustness test (part of BRAIN's submission checks) — alphas using `rank()` are more likely to pass the rank test.

**2. `winsorize(FIELD, std=4)` — clip extreme outliers before ranking:**
Caps values at ±4 standard deviations from the mean before applying any operator. Useful when outliers are so extreme they distort the `ts_rank` or `ts_zscore` even before the final `rank()`:
```
-rank(ts_rank(winsorize(FIELD, std=4), 252))
```

**3. `log(FIELD)` — compress multiplicative distributions:**
For fields spanning multiple orders of magnitude (revenue: $10M to $500B), `log()` compresses the scale:
```
-rank(ts_rank(log(FIELD), 252))
```
⚠ Only valid for strictly positive fields. Returns `NaN` for zero or negative values.

**4. `group_rank(FIELD, group)` — normalize within peers:**
Ranks each stock only against its industry/subindustry peers. Removes between-group scale differences (e.g. financial companies have inherently different revenue scales than tech companies):
```
-rank(group_rank(ts_rank(FIELD, 252), industry))
```

**5. `zscore(FIELD)` / `normalize(FIELD, useStd=true)` — cross-sectional z-score:**
Subtracts the market mean and divides by market std dev. Forces a roughly standard normal distribution across the universe.

**General rule:** Always normalize data range before using raw values in any weight-bearing expression. Rank → most robust. Log → good for multiplicative fields. Zscore → good for additive fields with heavy tails.

---

## 4. Quick Reference Table

| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| Weight failure at IS start only | Sparse early data | Trim early period or `ts_backfill(FIELD, 120)` |
| Regular quarterly weight spikes | Quarterly field data gaps | `ts_backfill(FIELD, 120)` or `group_backfill` |
| Sudden one-day coverage collapse | Missing data for one day | `ts_backfill(FIELD, 2)` |
| Weight failure throughout IS | Outlier stocks dominating | Wrap in `rank()`, add `winsorize`, or use `group_rank` |
| Long/short count severely unbalanced | Distribution skewed | `rank()` forces a balanced uniform distribution |
| Weight failure + turnover spike together | Low-coverage field dropping data | `ts_backfill` + `group_count` guard clause |

---

## 5. Key Principle

> **If the weight test still fails after applying truncation, backfill, and rank normalization, move on.** Some alpha ideas are structurally incompatible with the 10% weight cap — the data is too sparse or too concentrated by nature. This is not a failure of your technique; it's a property of the dataset. Opportunities to create new alphas with passing weight tests always exist.
>
> `rank()` is your best all-purpose tool — it balances long/short counts, normalizes outliers, and passes the rank robustness test simultaneously.
