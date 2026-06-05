# WorldQuant BRAIN: Alpha Creation & Submission Guide
> **Purpose:** A comprehensive reference for advanced simulation settings, the internal mathematical engine, and the rigorous Out-of-Sample (OS) submission tests required to get an Alpha into production.

---

## 1. The 7-Step Simulation Engine (How BRAIN Works)
When an Alpha expression is simulated, BRAIN translates the raw math into a daily $20M portfolio through these steps:

1. **Evaluate:** Calculates the raw Fast Expression math for every stock in the defined universe.
2. **Neutralize:** Subtracts the group's mean signal from every stock in that group (e.g., forces Sector sum to 0).
3. **Normalize:** Divides each signal by the absolute sum of all signals (forces total absolute weight to 1.0).
4. **Decay (If applicable):** Averages today's weights with previous days' decayed weights to slow down turnover.
5. **Allocate:** Multiplies the normalized weights by the Book Size ($20 Million) to get the dollar allocation per stock.
6. **Calculate PnL:** Multiplies the dollar allocation by the *actual* stock return for that day.
7. **Iterate & Chart:** Repeats for every day in the 5-year In-Sample (IS) period to generate the cumulative PnL chart.

---

## 2. Advanced Simulation Settings

### A. Pasteurize
* **Definition:** Dictates how out-of-universe stocks are handled *before* mathematical operations.
* **Pasteurize = ON (Default):** Replaces out-of-universe stocks with `NaN`. Your stocks are only ranked/compared against other stocks *inside* your selected universe (e.g., TOP500 vs TOP500).
* **Pasteurize = OFF:** Math is calculated against the *entire* market first, and then filtered down to your universe.

### B. NaN Handling
* **Definition:** How missing data is treated by the simulator.
* **NaN Handling = OFF (Recommended):** Preserves `NaN` values. Operators output `NaN` if data is missing, allowing the quant to intelligently handle it (e.g., using `ts_backfill`).
* **NaN Handling = ON:** Replaces `NaN` with `0` (for time series) or Group Means (for cross-sectional). *Warning: This increases coverage but can introduce fake/ambiguous information.*

### C. Core Settings Recap
* **Delay:** Always use `1` (Trades happen the day after the signal).
* **Decay:** Smooths signals linearly to reduce Turnover.
* **Truncation (e.g., 0.08):** Caps the maximum weight of any single stock at 8%.
* **Neutralization (e.g., SUBINDUSTRY):** Protects the portfolio from macro-market/sector crashes.

---

## 3. The Test Period (Beating Overfitting)
To prevent "curve-fitting" (where an Alpha memorizes the past but fails in the future), BRAIN allows splitting the 5-year IS period:
* **Train Period (Blue Line):** Years 1-4. Use this to tweak parameters, adjust decay, and build the Alpha.
* **Test Period (Orange Line):** Year 5. A blind validation zone. If Sharpe is high in Train but crashes in Test, the Alpha is overfitted.
* *Note:* You must click "Show test period" on the UI before you are allowed to submit an Alpha using this feature.

---

## 4. The Submission Tests (OS Hurdles)
After passing baseline IS tests (Fitness > 1.00, Sharpe > 1.25, Turnover 1-70%), an Alpha must pass these structural tests to be submitted:

### A. Weight Concentration Test
* Max weight on a single instrument must be $< 10\%$.
* Fix: Use `Truncation`, `rank()`, or `ts_backfill()` to spread capital wider.

### B. The Sub-Universe Test
* **Objective:** Prevents Alphas from generating all PnL from untradeable micro-caps.
* **Mechanism:** Secretly tests the Alpha on the next most liquid universe (e.g., testing a `TOP3000` Alpha on `TOP1000`).
* **Requirement:** `Sub-Universe Sharpe >= 0.75 * sqrt(Sub_Size / Original_Size) * Original_Sharpe`
* **Fix:** Avoid unbounded size multipliers (like `1 - rank(cap)`).

### C. The Self-Correlation Test
* **Objective:** Forces idea diversification.
* **Mechanism:** The Alpha must have $< 0.70$ correlation with your previously submitted Alphas.
* **The Upgrade Loophole:** If correlation is $\ge 0.70$, it can still pass IF the new Alpha's Sharpe is $\ge 10\%$ higher than the old one.

---

## 5. Special Alpha Classes & Regional Rules

### A. Special Classes
* **ATOM Alphas:** Uses fields from only *one* dataset (e.g., Fundamental only). Skips IS Ladder Sharpe tests.
* **Pyramid Alphas:** Uses fields from max 2 dataset categories.
* **Power Pool Alphas:** Elite tier. Sharpe $\ge 1.0$, $\le 8$ operators, $\le 3$ data fields, and extremely low self-correlation ($< 0.5$).

### B. Regional Robustness
* **GLB (Global) Alphas:** Must maintain Sharpe $> 1.0$ across AMER, APAC, and EMEA individually.
* **ASI (Asia) Alphas:** Must pass the **Japan Robustness Test** (Sharpe $\ge 1.0$ in Japan). Since Japan is the most liquid market in Asia, Alphas that fail here are deemed un-tradeable.
