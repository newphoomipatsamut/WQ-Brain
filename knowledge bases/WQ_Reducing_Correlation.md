# WorldQuant BRAIN: How to Reduce Self-Correlation (Knowledge Base)
> **Purpose:** A focused guide on understanding and reducing the self-correlation check — the final gate between a passing alpha and a submittable one.

---

## 1. Understanding the Self-Correlation Check

After passing IS metrics (Sharpe ≥ 1.25, Fitness ≥ 1.00, Checks ≥ 6/7), your alpha is tested against every alpha already in your submitted book:

```
max_corr = max(correlation(new_alpha, existing_alpha_i))  for all i
```

* **Must be < 0.70** to submit.
* **The Upgrade Loophole:** If max_corr ≥ 0.70, you can still submit IF the new alpha's Sharpe is ≥ 10% higher than the correlated one. Rare in practice.

High correlation does **not** mean the alpha is bad — it means your core idea is already represented in your book. The signal is real; the expression is too similar.

**What correlation measures:** Correlation is computed on **PnL graphs** (the daily returns sequence), not on code or formula similarity. Two completely different expressions can be highly correlated if they react to the same market events on the same days. Conversely, the same expression with Delay-0 vs. Delay-1 may or may not be correlated — compare their PnL charts directly to find out.

**Correlation scope by researcher tier:**
* **Standard researcher (pre-consultant):** Your new alpha is only tested against **your own submitted alphas**. The correlation bar is lower because your book is small.
* **Consultant:** Your new alpha is tested against the **entire BRAIN alpha pool** — all alphas submitted by all researchers worldwide. The effective correlation threshold is much harder to clear because the pool is large and many ideas are already represented. This is why Consultants benefit more from exotic data and unusual approaches.

---

## 2. Four Approaches to Reduce Correlation

### A. Different Data Fields
The easiest starting point — swap the underlying data while keeping the same mathematical logic:
* Replace `close` with `open`, `high`, `low`, or `vwap` — these carry the same price signal but with different intraday timing.
* Replace a fundamental field with an economically equivalent one (e.g. `net_income` → `operating_income` → `ebit`).
* Add a scaling denominator: `FIELD / cap` (yield-style) vs. raw `FIELD` — the cap-normalized version is structurally less correlated with level-based alphas.
* For analyst fields: switch from estimate level (`anl4_fs_eps`) to revision (`ts_delta(anl4_fs_eps, 63)`) — different economic signal, usually lower correlation.

### B. Different Operators
Swap the mathematical transformation while keeping the same underlying data:
* `ts_rank` → `ts_zscore` → `ts_regression(rettype=2)` → `ts_corr(FIELD, returns, 63)`
* `rank()` → `group_rank()` → `group_zscore()` — each normalizes differently and produces a distinct weight distribution
* `ts_mean` → `ts_median` — median is more robust to outliers and produces different rankings
* `ts_std_dev` → `ts_corr(FIELD, close, 63)` — measures a different property of the same field

These swaps change what the math *extracts* from the data, not just how it's scaled.

### C. Different Groupings and Neutralizations
This is the most powerful structural lever — changing how the portfolio is balanced fundamentally alters the cross-sectional weight distribution:
* `SUBINDUSTRY` → `INDUSTRY` → `SECTOR` → `MARKET` — each level changes which stocks are long/short relative to each other.
* `group_rank(signal, subindustry)` vs. `group_rank(signal, sector)` — ranking within smaller vs. larger peer groups produces different orderings.
* **Double neutralization:** `-rank(group_neutralize(group_rank(ts_rank(FIELD, 252), subindustry), sector))` — strips both industry and sector effects simultaneously. Structurally lowest self-correlation of any template.
* ⚠ Do not create arbitrary groups (e.g. random `bucket()` splits) purely to bypass the correlation test. The grouping must have an economic rationale — it must make sense to compare companies within that group.

### D. Think Outside the Box
The strategies above are adjustments to an existing idea. True decorrelation comes from a different economic hypothesis:
* **Pair expressions:** Spread or residual between two related fields carries information neither has alone and cannot correlate with single-field alphas built on either field.
    * Spread: `-rank(ts_rank(FIELD_A - FIELD_B, 252))`
    * Residual: `-rank(ts_regression(FIELD_A, FIELD_B, 252, rettype=0))` — the part of A unexplained by B
* **Different data category entirely:** If your correlated alpha is Fundamental, try the same economic hypothesis using a Model or Analyst field.
* **Time-frame shift:** The correlated alpha uses a 252-day lookback — try 504 (2-year) or 126 (6-month). Different holding periods capture different parts of the return distribution.
* **Conditional logic:** `trade_when(condition, signal, -1)` only takes positions when a specific event occurs — structurally different from an always-on alpha even with the same underlying signal.

---

## 3. Empirical Notes from This Book

Based on actual self-correlation results across 19+ submitted alphas:

* **`ts_decay_linear` patterns always correlate** with existing book entries — banned entirely. Use `hump()` or Decay setting instead.
* **`rank(ts_delta(close, N))` always correlates** with Alpha 9 (price momentum) — banned. Sharpe 0.75–0.84 on every combination tested.
* **TOP200 consistently gives lower max_corr than TOP3000** for the same expression. When an alpha is borderline correlated (0.65–0.72), switching universe to TOP200 often clears it.
* **`group_rank` and `group_zscore` are structurally lower-correlation** than plain `rank()` — use them as the first retry when a `ts_rank`-based alpha fails the correlation check.
* **Double neutralization** (`group_neutralize(group_rank(..., subindustry), sector)`) is the most aggressive structural decorrelator — use it specifically for high-crowdedness fields (mdl177_*) where plain ts_rank almost certainly correlates with other researchers' books.

---

## 4. How to Check Correlation Before and After Submitting

### Before submitting — Generate Self Correlation
On the **Simulate page** (upper right corner) and the **Alphas page**, use the **"Generate Self Correlation"** button. This shows the top 5 alphas you have already submitted that correlate most with the expression currently open in the simulator. Use this immediately after a simulation passes IS metrics — if any of the top 5 have correlation > 0.60, start decorrelating before wasting a submission attempt.

### After submitting — Inner Correlation between submitted alphas
To see how correlated your submitted alphas are *with each other*:
1. Go to the **Alphas page** → select the alphas you want to compare
2. Click **"Add Alphas to List"**
3. Open the **Alpha Lists** view
4. Scroll to the bottom of the list — **Inner Correlation** is displayed there

Inner Correlation shows the correlation matrix across your selected alphas. Clusters of high inner correlation (> 0.70) indicate you are over-indexing on the same idea and leaving capacity on the table.

### D0 vs D1 of the same expression — are they correlated?
Yes, possibly. Correlation is computed on PnL graphs, not expressions. If a D0 and D1 version of the same expression react to the same market events on the same days (just offset by one day), their PnL series may be highly correlated. The only way to know is to add both to an Alpha List and check Inner Correlation.

## 5. Correlation Check vs. Performance Comparison

These are two separate checks in the submission process — do not confuse them:

| Check | What it measures | Threshold | Fix |
| :--- | :--- | :--- | :--- |
| **Self-Correlation** | Correlation with *your* submitted alphas | < 0.70 | Change operators, grouping, or data field |
| **Performance Comparison** | Score change vs. the correlated alpha (if any) | Positive score change | New alpha must have ≥ 10% higher Sharpe than the one it correlates with |

A new alpha can fail Performance Comparison even with max_corr < 0.70 if the platform judges it not to add value over existing submissions. Focus on genuine signal diversity, not just arithmetic decorrelation.
