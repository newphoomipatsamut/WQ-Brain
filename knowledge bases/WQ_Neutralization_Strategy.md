# WorldQuant BRAIN: Neutralization — Mechanics & Strategy Guide

---

## 1. What Neutralization Does (Layman)

Neutralization forces your portfolio to be **dollar-neutral** — the same dollar amount on the long side (buying) and the short side (selling). If your expression says "buy $100 of AAPL and buy $50 of MSFT," market neutralization subtracts the group mean from each:

```
mean = ($100 + $50) / 2 = $75
AAPL: $100 - $75 = +$25   (long)
MSFT: $50  - $75 = -$25   (short)
```

Result: you are now long $25 AAPL and short $25 MSFT — net zero market exposure. You only profit if AAPL outperforms MSFT, not from the market going up.

**Industry neutralization** does the same operation but within each industry independently — every industry's weight sums to zero. Sub-industry does it at an even finer granularity.

**Why this matters:** A non-neutralized alpha has directional market exposure. If the market drops 5% on Monday, your alpha drops roughly 5% too, regardless of whether your signal was correct. Neutralization removes this "free" market risk from the PnL.

---

## 2. Neutralization Setting vs. group_neutralize() — Critical Difference

These two use identical math but operate at different points in the simulation pipeline:

| | **Neutralization Setting (UI)** | **group_neutralize(x, group)** |
| :--- | :--- | :--- |
| When applied | **Last step** after all other operations (evaluate → neutralize → normalize → decay → allocate) | Wherever you place it in the expression |
| Scope | Entire alpha output | Only the sub-expression passed as `x` |
| Use case | Single neutralization, all at once | Multiple neutralizations, or mid-expression neutralization |

**They are interchangeable when applied to the full expression:**
```python
# Equivalent:
# Alpha: ts_returns(close, 5)  +  Neutralization: INDUSTRY  +  Decay: 0  +  Truncation: 0
# is the same as:
# Alpha: group_neutralize(ts_returns(close, 5), industry)  +  Neutralization: NONE  +  Decay: 0  +  Truncation: 0
```

**When to use group_neutralize() inside the expression:**
* You want to apply different neutralizations to different parts of the alpha (e.g. neutralize signal A by industry, signal B by market, then combine them)
* You want to apply neutralization *before* other operators (e.g. rank the already-neutralized signal)
* You want to use decay/truncation operators inside the expression rather than in settings

**Settings when using group_neutralize() manually:**
* Set Neutralization = `None` in simulation settings
* Set Decay = `0` (apply decay inside the expression if needed)
* Set Truncation = `0` (apply truncation inside the expression if needed)

---

## 3. Neutralization = None — Risks and When to Avoid

**"Neutralization = None" makes the alpha long-only** (or directional). Without neutralization, the alpha does not subtract the market/group mean, so the sum of weights may be entirely positive — you are effectively just buying stocks, not running a balanced long-short portfolio.

### Consequences of submitting a Neutralization=None alpha without manual group_neutralize:
* **Sub-optimal WQ Challenge Score** — BRAIN penalizes directional market exposure
* **Higher self-correlation** — all directional alphas share a common beta component
* **Worse merged performance score** in IS and OS (market risk bleeds into the signal)
* **OS test failures** at consultant tier — BRAIN screens out unbalanced alphas more aggressively
* **Lower payouts** if active as a consultant

### Concrete example (same expression, different neutralization):

```
Expression: rank(-ts_delta(close, 2))
Settings: USA / TOP3000 / D1 / Decay=8 / Truncation=0.08
```

| | Neutralization = SECTOR | Neutralization = NONE |
| :--- | :--- | :--- |
| **Sharpe** | **2.04** | 0.92 |
| **Returns** | 14.69% | 35.80% |
| **Drawdown** | **3.53%** | 31.96% |

Returns appear higher without neutralization, but Sharpe collapses and drawdown explodes. The extra "return" is just market beta — it will evaporate in a down market.

**When Neutralization=None is acceptable:** Exploring a dataset in isolation to understand its raw signal, before deciding on a neutralization strategy. Never submit with None unless you manually balance long/short inside the expression using `group_neutralize`.

### Diagnostic: alpha expression "1" returns NaN
If you enter the expression `1` with the default SUBINDUSTRY neutralization, you get all NaN (no weights). This is correct: neutralization subtracts the group mean from each stock's value. For `1` (constant), every stock has value 1, the mean is 1, and `1 - 1 = 0` → weights become zero → NaN in results. To verify neutralization is off and see raw results, temporarily set Neutralization = None.

---

## 4. Does Neutralization Improve Sharpe?

Neutralization is a **risk control mechanism** — it reduces standard deviation of returns by removing the group's directional exposure. Lower std dev → higher Sharpe (assuming returns don't drop proportionally).

* **SUBINDUSTRY neutralization** tends to give the best Sharpe in most cases because it removes the most granular sector exposure while still allowing signals to trade across the widest range of relative bets.
* **MARKET neutralization** has lower Sharpe than SUBINDUSTRY but lower turnover — useful for Fitness optimization when TO is too high.
* **NONE** has the highest raw returns but highest volatility — Sharpe is usually lower despite the higher returns.

---

## 5. Rules by Category (Strategy Guide)

### Price Volume
- **Neutralize by: MARKET or NONE**
- Price volume ideas work for all instruments — do NOT neutralize by industry or subindustry
- No neutralization is extremely strong for price reversion (you can long/short the whole market)
- Neutralizing by MARKET instead of SUBINDUSTRY can reduce Sharpe but greatly increases fitness
- For mean reversion alphas specifically, try NONE first

### Fundamental
- **Neutralize by: INDUSTRY**
- Fundamentals affect price differently in different industries
- Compare companies to industry peers, not the whole market
- Examples: sales/assets, debt/equity, inventory_turnover, retained_earnings

### Analyst / Estimates
- **Neutralize by: INDUSTRY**
- Analyst data estimates future fundamental data
- Consensus estimates are most meaningful within the same industry
- Examples: est_eps, mdf_pec, mdf_eg3, fam_est_eps_rank

### Model (mdf_*, mdl_*, fam_*)
- **Neutralize by: varies — experiment with SECTOR and INDUSTRY**
- Model datasets vary wildly with subcategory
- Start with SECTOR, then try INDUSTRY
- For model scores that are already cross-sectional (like fam_roe_rank), SUBINDUSTRY works

### News
- **Neutralize by: SUBINDUSTRY**
- News impacts companies differently based on their subindustry
- High-count news = momentum signal, low-count = reversion signal
- Use ts_rank or ts_decay to smooth high turnover from news data

### Social Media / Sentiment
- **Neutralize by: SUBINDUSTRY or INDUSTRY**
- Social media impact is company-dependent
- Sentiment scores (snt_*, scl12_*) should be neutralized granularly
- Volume-weighted sentiment is more robust than raw sentiment

### Options
- **Neutralize by: MARKET or SECTOR**
- Options have consistent impact across industries
- Put-call ratio, implied volatility work at a broad level
- Don't over-neutralize — market-level captures the signal best

### Short Interest
- **Neutralize by: INDUSTRY**
- Short interest is relative to sector norms
- Experiment with SUBINDUSTRY as well

### Insider / Institutional
- **Neutralize by: SECTOR or INDUSTRY**
- Institution data depends on type and provider
- Insider news is company-dependent — try INDUSTRY or SUBINDUSTRY

### Earnings
- **Neutralize by: INDUSTRY**
- Earnings is like fundamentals — compare within industry
- Earnings surprise signals work best with MARKET neutralization
- Post-earnings drift: momentum for 2 days, then reversal for 5 days

### Credit Risk
- **Neutralize by: SECTOR**
- Credit risk varies by sector (financial vs. tech vs. energy)
- Rating probabilities are meaningful within the same sector

### Macro / Sector / Industry data
- **Neutralize by: MARKET**
- These are already macro-level signals
- Don't neutralize by subindustry — it removes the signal

## General Tips

1. **Smaller universe (TOP200) + broader neutralization (MARKET)** = lower turnover
2. **Larger universe (TOP3000) + tighter neutralization (SUBINDUSTRY)** = more signal but higher turnover
3. When in doubt, test SUBINDUSTRY first (it's the WQ default) then try INDUSTRY and MARKET
4. `group_neutralize(alpha, group)` can be used inside expressions for fine-grained control
5. No neutralization is sometimes the best choice for pure price reversion
6. Fitness problems (turnover too high) can often be fixed by switching from SUBINDUSTRY to MARKET

## Neutralization + Universe Combinations That Work

| Category | TOP3000 | TOP200 |
|----------|---------|--------|
| Price Volume | MARKET or NONE | MARKET or NONE |
| Fundamental | INDUSTRY | INDUSTRY |
| Analyst | INDUSTRY | INDUSTRY |
| Model | SECTOR | INDUSTRY |
| Sentiment | SUBINDUSTRY | INDUSTRY |
| Options | MARKET | MARKET |
| Credit Risk | SECTOR | SECTOR |
