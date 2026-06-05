# WorldQuant BRAIN: Interpreting Results & Alpha Lifecycle (Knowledge Base)
> **Purpose:** A reference guide detailing how to read the simulation dashboard, the mechanics of the $20M fictional portfolio, and the exact lifecycle of an Alpha from In-Sample testing to Live Trading.

---

## 1. Portfolio Mechanics & Leverage
Every simulated Alpha operates a fictional, self-balancing portfolio.
* **Book Size:** The total amount of capital used to trade is fixed at **$20 Million** every day. 
* **Leverage:** BRAIN assumes you have **$10 Million** in base capital. You are allowed to invest $20M (2x leverage), typically split as $10M Long (buying) and $10M Short (selling borrowed shares).
* **Return Calculation:** Because your base capital is $10M, Return = `Annualized PnL / Half of Book Size`. 
* *Note: Profits are not reinvested, and losses are replaced by cash injections to maintain the $20M constant size.*

---

## 2. The Core Metrics
The "IS Summary" block displays the vital stats of your Alpha over the testing period.

* **Information Ratio (IR):** The ratio of mean daily returns to the volatility of those returns.
* **Sharpe Ratio:** The annualized version of IR. `Sharpe = IR * sqrt(252)` (252 = trading days in a year). Measures the consistency of returns. High Sharpe > High Returns.
* **Fitness:** The ultimate grade. `Fitness = Sharpe * sqrt(abs(Returns) / max(Turnover, 0.125))`. Improving Returns or Sharpe increases Fitness; high Turnover destroys it.
* **Turnover:** Daily Trading Volume / Book Size. How much of the portfolio is flipped daily.
* **Margin:** Profit per dollar traded (`PnL / Total Dollars Traded`). 
* **Drawdown:** The largest peak-to-trough drop in PnL, divided by half of book size. Measures worst-case scenario risk.

---

## 3. The Alpha Timeline (The 3 Phases)
To prevent "overfitting" (creating an algorithm that perfectly predicts the past but fails in the real world), WorldQuant strictly segments time into three periods:

### A. The IS (In-Sample) Period
* **When:** A rolling 5-year window that starts 7 years ago and ends exactly 2 years ago. (Consultants get a 10-year window).
* **What it is:** The testing sandbox. This is the data you see and optimize against.
* **Train/Test Split:** You can optionally split the IS period into "Train" (to build the math) and "Test" (to blindly validate it) to avoid overfitting before submission.

### B. The Semi-OS (Out-of-Sample) Period
* **When:** The most recent 2 years.
* **What it is:** The hidden gauntlet. When you click "Submit", BRAIN secretly tests your Alpha against this unseen data. You cannot view this data to optimize against it. If it fails here, it is rejected.

### C. The OS (Out-of-Sample) Period
* **When:** Today and into the future.
* **What it is:** Live, real-time tracking. Statistics populate day-by-day.

---

## 4. Alpha Statuses & Payouts
What happens to an Alpha after simulation?

* **UNSUBMITTED:** The Alpha passed IS simulation, but you haven't clicked submit. It makes no money.
* **ACTIVE:** The Alpha was submitted and successfully survived the hidden Semi-OS test. It is now trading live in the OS period. **For Consultants, ACTIVE Alphas accrue weight and contribute to quarterly payouts.**
* **DECOMMISSIONED:** If the data source breaks, or the Alpha suffers prolonged underperformance in the live OS period, WorldQuant kills it. It ceases to accrue weight or pay out.

---

## 5. Official Fitness Ratings
BRAIN automatically assigns a rating based on your Delay-1 Fitness score:
* **Spectacular:** $> 3.25$
* **Excellent:** $> 2.60$
* **Good:** $> 1.95$
* **Average:** $> 1.30$
* **Needs Improvement:** $\le 1.30$ (Note: Must be $\ge 1.00$ to pass base submission rules).
