# WorldQuant BRAIN: Alpha Dashboard & Portfolio Strategy (Knowledge Base)
> **Purpose:** How to navigate the Alphas page, read the diversity visualization, and understand the core mechanics of how BRAIN converts an expression into daily P&L.

---

## 1. The Alphas Page

The Alphas page is the master view of every simulation you have run.

### Stages
Alphas are split into two tabs:
* **Unsubmitted** — simulations not yet sent for correlation/submission review
* **Submitted** — alphas in the submission pipeline (Pending → Active / Rejected)

### Controls

| Control | What it does |
| :--- | :--- |
| **Favorite (★)** | Star an alpha to mark it for later; click again to un-star |
| **Hidden (eye icon)** | Checkbox + eye icon hides an alpha from the default view; click again to restore |
| **Columns** | Add or remove columns from 4 categories: Summary, Settings, Performance, Properties |
| **Filters** | Show a subset — filterable by: Name, Category, Code, Language, Color, Date Created, Decay, Drawdown, Favorite, Fitness, Hidden, Margin, Neutralization, PnL, Region, Returns, Sharpe, Status, Tags, Truncation, Turnover, Universe |
| **Sorting** | Sort by any visible column |
| **Code Preview (</> icon)** | View the expression. Click alpha name → open full info block → Clone Alpha to reopen in simulator |
| **Alpha Lists (list icon)** | Select 2+ alphas → add to list → Performance Comparison view |

**Margin unit note:** Margin is PnL ÷ dollars traded, expressed in **bpm** (basis points of margin). 1 bpm = 1/100th of 1% margin. A margin of 500 bpm = 5% profit per dollar traded.

---

## 2. Distribution of Active Alphas

BRAIN provides a layered donut chart showing the diversity of your submitted alpha book. Navigate by clicking inward:

**Layer 1 → Region** (USA / ASI / EUR / GLB)
**Layer 2 → Delay** (D1 / D0)
**Layer 3 → Data Category** (Price Volume / Fundamental / Analyst / etc.)

Hovering over a segment shows the count and percentage of alphas in that slice.

**Color coding:** Blue = low concentration, Red = high concentration. Red segments are a signal to diversify away.

### Official Diversification Targets

| Rule | Threshold |
| :--- | :--- |
| No single Region | > 50% of submitted alphas |
| Delay-0 minimum | ≥ 5% of submitted alphas |
| No single (Region × Delay × Data Category) intersection | > 30% of submitted alphas |

**Practical implication for our pipeline:** Since we run USA / D1 / Price-Volume and Fundamental heavily, we will likely hit the 30% intersection ceiling on Price-Volume before we reach the 30% ceiling on Fundamental. Diversifying into Analyst, News (nws12_*), and eventually ASI region buys us more capacity.

---

## 3. How an Alpha Expression Becomes P&L

### Step 1 — Output is a weight vector
An alpha expression outputs one value per stock per day. After normalization, these become portfolio weights — fractions of the book to hold long or short.

**Example (3 stocks):**
```
weight_A = 0.2   →   $20M × 0.2 = $4M long in A
weight_B = 0.3   →   $20M × 0.3 = $6M long in B
weight_C = 0.5   →   $20M × 0.5 = $10M long in C
```

### Step 2 — Hold for one day, record the gain/loss
The portfolio is held for one day. If prices change such that the total value moves from $20M to $20.5M, that day's PnL = $0.5M = 2.5 bpm on a $20M book.

### Step 3 — Rebalance daily at constant booksize
BRAIN uses a **constant $20M booksize** every day — it does not compound or shrink based on P&L. The alpha re-runs the expression, generates new weights, and the position differences are the trades (which incur transaction costs).

**Key implication:** BRAIN's simulation does not simulate bankrupt portfolios — it always restarts at $20M regardless of how badly a prior day went. This is correct for the kind of statistical arb BRAIN models (where the strategy is deployed with a fixed capital allocation).

---

## 4. Alpha in BRAIN vs. Alpha in CAPM

These are different uses of the word "alpha":

| | **BRAIN Alpha** | **CAPM Alpha** |
| :--- | :--- | :--- |
| **Definition** | A mathematical model / expression that assigns weights to stocks | The excess return above what CAPM predicts |
| **Output** | A vector of weights (buy/sell proportions) for each stock each day | A scalar — a single number measuring a portfolio's abnormal return |
| **Usage** | You write, simulate, and submit it for live evaluation | Used in performance attribution after-the-fact |

BRAIN uses "alpha" symbolically — it is the name for a predictive model, not a measure of excess returns.

---

## 5. You Cannot View Per-Stock Weights

BRAIN does not expose which specific stocks the alpha is buying or selling or in what quantities on a given day. You only see **aggregated** statistics:
* Sharpe, Fitness, Turnover, Returns, Margin
* The cumulative PnL chart
* IS Summary (year-by-year breakdown)

**Why:** BRAIN is designed as a statistical arbitrage platform. The value is in the strategy's behavior across 2000–3000 stocks simultaneously, not in the position of any individual stock. Individual weights are transient and would not provide actionable information.

---

## 6. API Access

BRAIN provides an API for **consultants only**. Standard researchers do not have API access.

* **Protocol:** OAuth or similar token-based auth
* **Usage:** Send an alpha expression to the server programmatically, receive JSON results, parse and iterate the search algorithm automatically
* **Rate limit:** Low-intensity communication only — do not hammer the API. The platform is a research environment, not a high-frequency backtesting server.

Our orchestrator (`orchestrator.py`) does exactly this — it uses the BRAIN API to submit simulations and poll results without manual UI interaction. This is the correct usage pattern.

---

## 7. External Research Resources

Alpha research draws from the full breadth of quantitative finance. BRAIN does not restrict what signals you can explore.

| Resource | What it offers |
| :--- | :--- |
| **SSRN (ssrn.com)** | Academic papers on factor research, market anomalies, return predictors — the largest preprint archive for quant finance |
| **Stockcharts.com** | Catalogue of classic technical indicators with explanations and chart examples — a starting point for price-volume signal ideas |
| **WorldQuant tutorials** | BRAIN's own learning courses and Research FAQ (login required) |

**What makes a good idea:** Signals that are **robust across all market years** — they don't only work in bull markets or only in the 2020 COVID period. Consistency across regimes produces lower standard deviation of returns and therefore higher Sharpe. An alpha that works in 2008, 2012, 2017, and 2022 is more trustworthy than one that only shines in a single year.

### Using Academic Papers Correctly
Research papers describe phenomena as they existed at the time of publication — many effects decay or reverse as they become crowded. Use papers as a **starting point**, not a blueprint:

1. **Implement the core idea in its most elementary form first** — no add-ons, no filters
2. **Check if it even works in BRAIN** at the basic level (Sharpe > 0.5 on the first try is encouraging)
3. **Then improve**: filter by a secondary signal, weight by a factor, restrict the universe, tune decay
4. **Do not copy exact parameter values** from the paper — they were calibrated on different data over a different period. Use them as order-of-magnitude guidance only.

If the elementary idea fails entirely, the effect may be arbitraged away or not applicable to BRAIN's universe and timeframe. Move on rather than adding complexity to rescue a dead signal.

## 8. Using Simulation Period Data

BRAIN simulates over **multiple years** (typically 2005–present) even though a live alpha would trade daily. The long history serves to:
* Validate that the signal was not a fluke of one market regime (2008 crisis, 2020 COVID, etc.)
* Build a statistically meaningful Sharpe estimate — more years → more trading days → more reliable mean/std estimate
* Expose the strategy to multiple interest rate cycles, sector rotations, and liquidity conditions

**Use:** If an alpha has great Sharpe in 2020–2023 but negative Sharpe in 2010–2015, it is regime-dependent and not ready for submission.
