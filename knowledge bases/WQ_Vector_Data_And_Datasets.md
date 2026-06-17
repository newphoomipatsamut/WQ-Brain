# WorldQuant BRAIN: Vector Data Fields & Dataset Reference (Knowledge Base)
> **Purpose:** A guide to vector data fields — how they differ from matrix data, how to convert them for use in expressions, and platform-level dataset facts.

---

## 1. Vector vs. Matrix Data

All BRAIN alpha expressions must output a **matrix** — one value per instrument per day. Most data fields are already matrices. Vector fields are not.

| Type | Shape | Example |
| :--- | :--- | :--- |
| **Matrix** | 1 value per instrument per day | `close`, `revenue`, `eps` |
| **Vector** | N values per instrument per day (N varies) | `nws12_afterhsz_1_minute`, `scl15_d1_sentiment` |

**Why vectors exist:** News data is a natural vector — AAPL might have 0 news items on Monday and 7 on Tuesday. Forcing this into a matrix would either discard events or fill with NaN. Vectors capture the full event count.

**The rule:** Every BRAIN operator (`ts_rank`, `rank`, `group_zscore`, etc.) expects **matrix input**. You **must** convert vector fields to matrix first using `vec_` operators before applying any other operator.

```
# WRONG — ts_rank cannot accept a vector field directly
ts_rank(nws12_afterhsz_120_min, 20)

# CORRECT — convert to matrix first, then apply ts_rank
ts_rank(vec_count(nws12_afterhsz_120_min), 20)
```

---

## 2. Vector-to-Matrix Conversion Operators

| Operator | What it produces | Best for |
| :--- | :--- | :--- |
| `vec_count(x)` | Number of events in the vector | News count, event frequency |
| `vec_avg(x)` | Mean of all values in the vector | Average sentiment score, average price move |
| `vec_sum(x)` | Sum of all values in the vector | Total volume from intraday events |
| `vec_median(x)` | Median of all values in the vector | Robust central tendency (outlier-resistant) |
| `vec_min(x)` | Minimum value in the vector | Worst-case event in a day |
| `vec_max(x)` | Maximum value in the vector | Peak event intensity in a day |

**Choosing between avg and median:**
* `vec_avg`: sensitive to extreme values — one massive news event inflates the average.
* `vec_median`: more robust — better when events have highly variable magnitudes and you want typical sentiment, not total sentiment.

---

## 3. The Turnover Problem with Vector Fields

Raw vector-derived signals have **extremely high turnover** — often 130–200%. This is because event counts and sentiment scores change dramatically day to day.

**Always reduce turnover after converting:**

```
# News count momentum (high count = high intensity = momentum signal)
-rank(ts_rank(vec_count(nws12_afterhsz_120_min), 20))

# Sentiment average with smoothing
-rank(ts_rank(vec_avg(scl15_d1_sentiment), 10))
```

`ts_rank` maps the daily count/score into its recent historical percentile, dramatically reducing the day-to-day swings. Alternatively, increase the `Decay` setting (10–15 recommended for news/sentiment) or use `hump()`.

---

## 4. Alpha Patterns Using Vector Fields

### News Count as Momentum/Reversion Signal
A general observation:
* **High news intensity** (many events, high `vec_count`) → stock follows **momentum** — the news confirms a trend
* **Low news intensity** → stock follows **reversion** — quiet periods precede mean-reversion moves

```
# News intensity momentum
-rank(ts_rank(vec_count(nws12_afterhsz_120_min), 20))

# Or use vec_count of ANY nws12_afterhsz_* field — the field choice matters
# less than the count; all fields in this family measure event frequency
```

### Sentiment Aggregation
For sentiment vector fields, aggregate first then rank within history:
```
-rank(ts_rank(vec_avg(scl15_d1_sentiment), 10))    # mean sentiment
-rank(ts_rank(vec_median(scl15_d1_sentiment), 10)) # median (outlier-robust)
```

### Volume Aggregation
```
group_sum(vec_sum(intraday_volume_field), market)  # total market intraday volume
```

---

## 5. Practical Notes

* **`nws12_afterhsz_*` family:** Each variant (`1_minute`, `10_min`, `120_min`) measures the percentage price change within that window after news release. Use `vec_count` to get event frequency; use `vec_avg` to get average post-news price impact.
* **High turnover is expected and must be handled.** Raw `vec_count` or `vec_avg` can exceed 200% turnover — always wrap in `ts_rank(x, 10–20)` or use `Decay = 10–15`.
* **Consultant-only fields:** Some vector fields (`scl15_*`) are only available to consultant-tier researchers. Standard researchers should use `nws12_*` family fields instead.

---

## 6. You Cannot Download the Underlying Data

BRAIN does not provide access to raw day-by-day instrument-level data. You can only:
* Run simulations and view aggregated results (Sharpe, Fitness, Turnover, PnL chart)
* View the IS Summary statistics
* Export simulation results (not raw field data)

You cannot export field values to work on externally in Python, Matlab, R, or any other tool. All alpha development must happen inside BRAIN's expression engine.

---

## 7. Decommissioned Datasets

If a dataset you previously used no longer appears in the Data Explorer:
* The dataset provider **ceased publication**, OR
* WorldQuant **suspended access** for operational reasons.

**What happens to your alphas:**
* Alphas using the decommissioned dataset are also marked **DECOMMISSIONED** on the Alphas page.
* They will have already accrued their base payment up to the decommission date.
* If the dataset returns to the platform, those alphas **may be reinstated** to active status automatically.

**Practical implication for our pipeline:** If a field disappears from `fields_tracker.csv` or the LLM generator can't find it, check whether its dataset has been decommissioned before assuming a naming error. Decommissioned fields should be marked `❌ Abandoned (dataset_decommissioned)` in the tracker.
