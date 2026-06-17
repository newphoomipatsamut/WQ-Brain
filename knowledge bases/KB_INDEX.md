# WQ Brain Knowledge Base — Master Index
> Navigation guide for all KB files. Files are grouped by topic. `auto_findings.md` is machine-generated — do not edit manually.

---

## 🏛️ 1. Platform Foundations
*What BRAIN is, how to read results, how submission works.*

| File | Contents |
| :--- | :--- |
| `WQ_Discover_BRAIN.md` | Core BRAIN concepts: what an alpha is, Fast Expression syntax, the 3 IS metrics, simulation settings, troubleshooting table |
| `WQ_Interpret_Results_Summary.md` | Portfolio mechanics ($20M booksize, leverage), core metrics, IS/Semi-OS/OS lifecycle, alpha statuses, Fitness rating scale |
| `WQ_Alpha_Creation_And_Submission_Guide.md` | 7-step simulation engine, advanced settings (Pasteurize, NaN handling), the 3 submission tests (Weight, Sub-Universe, Self-Correlation), special alpha classes (ATOM, Power Pool, Pyramid) |
| `WQ_Alpha_Dashboard_And_Portfolio_Strategy.md` | Alphas page controls (stages, filter params, columns), Distribution donut chart, diversification targets (<50% region, ≥5% D0, <30% per intersection), weights→PnL mechanics, Alpha vs CAPM alpha, per-stock visibility limits, API access |
| `WQ_Glossary.md` | A-to-Z definitions of every BRAIN term — with cross-references and Fast Expression code for technical indicators |

---

## 🔬 2. Alpha Research Strategy
*How to build, evaluate, and diversify alpha ideas.*

| File | Contents |
| :--- | :--- |
| `Alpha_Examples.md` | Template library (A–M), validated expression patterns, BANNED templates, empirical warnings (ts_std_dev dead for QUARTERLY), frequency yield rankings |
| `WQ_Advanced_Topics_And_D0_Summary.md` | Low/high Sharpe fixes, ultra-low turnover fitness ceiling, overfitting tests (Train/Test, Rank, Sub-Universe), advanced neutralization, D0 alpha requirements |
| `WQ_Reducing_Correlation.md` | 4 decorrelation approaches (swap field / operator / grouping / think outside box), empirical book insights, Performance Comparison vs. Self-Correlation distinction |

---

## 📈 3. Metric Optimization
*How to improve each IS metric when it's blocking submission.*

| File | Fixes for... |
| :--- | :--- |
| `WQ_Improving_Sharpe.md` | Low Sharpe — IR formula, two levers (increase returns / reduce volatility), practical checklist |
| `WQ_Improving_Returns.md` | Low returns — turnover, decay, universe, volatility scaling, news/analyst datasets |
| `WQ_Improving_Turnover.md` | Turnover too high or too low — Decay, hump(), trade_when, shorter lookbacks, frequency |
| `WQ_Improving_Fitness.md` | Low Fitness — the Fitness formula, all three levers (Sharpe + Returns + Turnover), 6-step checklist, capacity |
| `WQ_Improving_Margin.md` | Low Margin — PnL per dollar traded, better signals vs. wasteful turnover |
| `WQ_Smoothing_PnL.md` | Choppy PnL / year-by-year dips — NaN flicker, signal noise, concentration, quarterly turnover spikes, macro exposure |
| `WQ_Weight_Coverage.md` | CONCENTRATED_WEIGHT failures — low coverage root cause, outlier distribution root cause, all fix operators |

---

## 📦 4. Data References
*How each data category behaves and how to construct alphas from it.*

| File | Covers... |
| :--- | :--- |
| `WQ_Understanding_Data_Summary.md` | Matrix vs. vector vs. group data, 6 data probes, Event data pitfalls (anl4_ady_* dead), model77 dataset, sentiment1 dataset |
| `WQ_Fundamental_Data_Reference.md` | Field hierarchy (debt ⊂ liabilities, cashflow_sales ⊂ cashflow_operations), how to use slow-moving data, empirical pass rate table, INDUSTRY neutralization rationale |
| `WQ_Price_Volume_Data_Reference.md` | OHLCV fields, VWAP, adv20 formula & syntax, overnight gap signal, volume aggregation, BANNED ts_delta(close) pattern, alpha patterns |
| `WQ_Vector_Data_And_Datasets.md` | Vector-to-matrix operators (vec_count/avg/sum/median), turnover problem with raw vectors, nws12_afterhsz_* family, dataset decommissioning |

---

## ⚙️ 5. Operators & Settings
*Syntax, mechanics, and configuration of BRAIN's expression engine.*

| File | Covers... |
| :--- | :--- |
| `WQ_Operators_Guide.md` | Full operator syntax reference — Arithmetic, Logical, Time Series, Cross-Sectional, Vector, Transformational, Group operators. ts_decay_linear marked ⛔ BANNED |
| `WQ_Operators_Deep_Reference.md` | How operators work mechanically: conditional/ternary logic, Decay formula, Delay (trading vs. calendar days), D0 vs D1 trade-off, Rank mechanics, Pasteurize's two functions, NaN vs 0 distinction, exponentiation, skewness/ts_moment, settings summary table |
| `WQ_Neutralization_Strategy.md` | Mechanics (mean subtraction example, dollar-neutral), Setting vs group_neutralize() (equivalence + when to use each), Neutralization=None risks (Sharpe 2.04→0.92 example, consultant penalties), "alpha=1 returns NaN" diagnostic, strategy by data category, universe combinations |
| `WQ_Universe_Reference.md` | TOP-N definition (dollar volume), full universe comparison table, TOPSP500 characteristics, sub-universe and super-universe test formulas, our pipeline universe strategy |
| `WQ_Error_Messages.md` | "Most illiquid 50% instruments" error (threshold formula, 3 fixes: weight illiquid names, conditional decay, vector_neut against size/liquidity), "Alpha better suited for Delay 1" error (cause + fix) |

---

## 🤖 6. Auto-Generated (Do Not Edit)
| File | Contents |
| :--- | :--- |
| `auto_findings.md` | Live pipeline findings: banned operators, submitted alpha fields, template pass rates by frequency, category yield scores |

---

## 🕳️ Known Gaps

These topics are **not yet covered** by any KB file:

| Gap | Why it matters |
| :--- | :--- |
| **Analyst Data Reference** | We have Fundamental, Price-Volume, and Vector KB files but no dedicated guide for Analyst (anl4_fs_*, anl4_ebit_*, etc.) and Model (mdl177_*) data patterns |
| **Submission Pre-Check Checklist** | A quick "before you click Submit" checklist tying together all 7 checks, the correlation check, and Performance Comparison — currently scattered across multiple files |
| **Regional Alphas (ASI/EUR/GLB)** | Consultant-only; robustness requirements differ by region. Not relevant until consultant tier is reached |
