# WorldQuant BRAIN: Universe Reference (Knowledge Base)
> **Purpose:** A complete guide to BRAIN's universe options — how they are defined, their trade-offs, and which to use for different alpha strategies.

---

## 1. How Universes Are Defined

All TOP-N universes are defined by **average dollar volume over the past 3 months**:

```
TOP-N = the N stocks with highest liquidity (avg dollar volume) in the USA over the last 3 months
```

This means:
* The composition changes over time as stocks rise or fall in liquidity rank.
* A stock leaving the TOP3000 doesn't mean it's gone — it may re-enter next quarter.
* Dollar volume (price × shares) weights large-cap stocks naturally — AAPL, MSFT, NVDA consistently sit at the top.

---

## 2. Universe Comparison Table

| Universe | Stock Count | Liquidity | Sharpe Potential | Fitness | Self-Corr Risk | Best For |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TOP3000** | ~3,000 | Broad — includes mid/small-cap | Higher (more diversification) | Moderate | Higher (more researchers) | Primary discovery universe |
| **TOP2000** | ~2,000 | Mid-to-large | Moderate | Moderate | Moderate | Intermediate step |
| **TOP1000** | ~1,000 | Large-cap focused | Lower (fewer stocks) | Better | Lower | Sub-universe Sharpe test target |
| **TOP500** | ~500 | High liquidity | Lower | Better | Lower | Liquid alphas; rarely tested |
| **TOPSP500** | ~650 | High + index-defined | Lower but diversified | Better | Lower | Liquid, index-diversified alphas |
| **TOP200** | ~200 | Highest liquidity only | Lowest | Best | Lowest | Self-correlation control |

---

## 3. TOPSP500 — The Index-Aware Universe

**What it is:** TOP500 stocks **plus** any additional S&P 500 constituents not already in TOP500. Results in ~650 stocks total.

**Key difference from TOP500:** S&P 500 membership is determined by a committee based on market cap, liquidity, profitability, and sector representation — not purely by dollar volume. This means TOPSP500 includes some stocks that wouldn't qualify on liquidity alone but are important for sector diversification.

**Notable characteristics:**
* Higher industry diversification than TOP500 (more sector balance due to S&P inclusion criteria)
* Good liquidity — all ~650 stocks are highly tradeable
* Higher tolerable turnover — smaller, liquid universe means each trade is more easily filled
* Sharpe and returns may be lower than TOP3000 (fewer stocks = less diversification of the alpha signal)

**Getting started with TOPSP500:**
1. Re-simulate past TOP3000 alphas that had good sub-universe Sharpe on SP500 — if they already cleared the liquidity test, they are natural candidates
2. Re-simulate TOP500 alphas — the composition difference may produce different Sharpe characteristics
3. Options and Analyst data tend to work well on this universe — these datasets have better coverage for large-cap, actively-traded S&P 500 stocks

**Our pipeline note:** We excluded TOP500 (0 passes from 145 tests). TOPSP500 is different — worth testing for alphas that already pass on TOP3000 with strong sub-universe Sharpe, as the S&P 500 composition may give better industry balance.

---

## 4. The Sub-Universe Sharpe Test

When you submit a TOP3000 alpha, BRAIN secretly tests it on TOP1000 (the next most liquid tier). This is the sub-universe Sharpe check:

```
Sub-Universe Sharpe ≥ 0.75 × sqrt(Sub_Size / Original_Size) × Original_Sharpe
```

For TOP3000 → TOP1000 test: `sqrt(1000/3000) = 0.577`, so sub-universe Sharpe must be ≥ `0.75 × 0.577 × Original_Sharpe ≈ 0.43 × Original_Sharpe`.

**Implication:** An alpha with Sharpe=1.40 on TOP3000 needs sub-universe Sharpe ≥ 0.60 on TOP1000 to pass. If your alpha relies on illiquid micro-cap stocks for most of its PnL, it will fail this test even with strong IS metrics.

**Fix:** Avoid large position sizes in low-liquidity stocks. `rank()` and `Truncation=0.08` help. If the alpha fails sub-universe, try re-simulating directly on TOP1000 or TOPSP500.

---

## 5. Why Single-Stock Alphas Don't Work

BRAIN is a **statistical arbitrage** platform — it requires betting on many stocks simultaneously. Single-stock alphas are not possible.

**The statistical logic:**
* Any single stock's return is dominated by noise — earnings surprises, news events, random sentiment shifts.
* If you are "right" 55% of the time on any one stock, random fluctuations still cause large losses in the remaining 45%.
* Betting on 500+ stocks simultaneously, a 55% accuracy rate produces consistent profits — the law of large numbers smooths out individual errors.

**The practical minimum:**
* Long side: ≥ 10 stocks at any point
* Short side: ≥ 10 stocks at any point
* Total: ≥ 20 stocks with assigned weight
* Fewer than this → CONCENTRATED_WEIGHT check fails

**Implication for alpha construction:** Never write expressions that assign non-zero weight to only one or a handful of stocks (e.g. `close == max(close, market) ? 1 : nan`). Always use `rank()` or `group_rank()` to distribute weights across the full universe.

---

## 6. Universe Size and Information Ratio (IR)

Larger universes generally produce **higher IR** because more stocks = more opportunities to express the alpha signal, and the law of large numbers smooths out individual stock noise. However, this is not always true:

| Situation | IR can be better in smaller universe | Reason |
| :--- | :--- | :--- |
| Fundamental signals | TOP1000 or TOPSP500 may outperform TOP3000 | Large-cap financial data is cleaner, updated more reliably, fewer reporting gaps |
| Price-volume signals | TOP3000 usually wins | More stocks = more trades, more diversification |
| Crowded signals (mdl177_*) | TOP200 often wins | Less researcher competition on the smallest liquid universe |

**Two mechanisms for large stocks being easier to model:**
1. **Cleaner data:** Large-cap companies report on time and with fewer anomalies. Small-cap filings have more gaps, restatements, and outlier values that create noise.
2. **Behavior is more liquid and predictable:** Highly traded stocks react more consistently to signals. Illiquid small-caps have microstructure noise that can overwhelm the signal.

**Practical implication:** If a TOP3000 alpha has mediocre Sharpe (~1.0–1.2) but good sub-universe Sharpe on TOP1000, re-simulating directly on TOP1000 often improves IS Sharpe. The smaller, cleaner universe can sometimes let the true signal shine through.

## 7. Our Pipeline Universe Strategy

| Situation | Universe to Use | Reason |
| :--- | :--- | :--- |
| Primary triage/discovery | TOP3000 | Maximum signal diversification |
| Self-correlation control | TOP200 | Structurally lowest max_corr with existing book |
| Near-miss tuning | Both TOP3000 and TOP200 | Compare IS metrics and self-corr |
| Failed sub-universe Sharpe | TOP1000 or TOPSP500 | Re-simulate on the tier that was tested |
| High-crowdedness fields (mdl177_*) | TOP200 first | Less competition on smaller universe |
| TOP500 | ❌ Excluded | 0 passes from 145 tests |
