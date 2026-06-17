# WorldQuant BRAIN: How to Improve Margin (Knowledge Base)
> **Purpose:** A focused guide on understanding and improving Margin — the efficiency metric that measures how much profit each dollar of trading actually generates.

---

## 1. Understanding Margin

```
Margin = PnL / Total Dollars Traded
```

Where Total Dollars Traded = `Turnover × BookSize × TradingDays`.

Margin measures the **quality of each trade** rather than the quantity. A high-Margin alpha generates good PnL without needing to trade excessively. Low Margin means many trades are happening but generating little net profit — a sign that transaction costs are eating the signal.

**Relationship to other metrics:**

```
Returns = Margin × Turnover × sqrt(252)  (approximate)
```

This means Returns can be high from either:
* High Margin + moderate Turnover (efficient, high-quality signal)
* Low Margin + very high Turnover (brute-force trading — risky, cost-sensitive)

High-Margin alphas are more robust in live trading where real transaction costs apply.

---

## 2. Two Levers for Improving Margin

### A. Increase Returns
Higher PnL from the same amount of trading directly raises Margin. All the strategies in `WQ_Improving_Returns.md` apply:
* Use better-quality signals (ts_regression slope, revision rate) that predict larger return moves.
* Use longer-horizon signals for fundamentals — larger price moves at longer timescales mean more PnL per trade.
* Combine signals: a value signal multiplied by a momentum signal often picks better entry points, raising PnL per unit traded.
* Use `trade_when` to only execute when the signal is strong — filtering to high-conviction moments raises average PnL per trade.

### B. Manage Turnover
Since `Margin = PnL / Total Dollars Traded`, reducing unnecessary trades (trades that generate little PnL) raises Margin directly:

* **Cut wasteful turnover with `hump()`:** Position changes below the threshold are held — these small changes contribute near-zero PnL but still count as trading volume. Removing them raises Margin:
  ```
  -rank(hump(ts_rank(FIELD, 252)))
  ```
* **Increase Decay:** Smooths daily weight changes, reducing the total dollars traded while roughly preserving PnL (the signal still earns, just with fewer rebalances).
* **Use `trade_when` to trade only on high-signal days:** Concentrates trading on days where the expected PnL per dollar is highest.
* **Avoid ultra-high Turnover (> 40%):** Above this level, each additional dollar of trading is likely generating diminishing returns — Margin compresses and real-world transaction costs become unmanageable.

---

## 3. Margin vs. Returns vs. Fitness

These three are related but measure different things:

| Metric | Measures | Optimization Target |
| :--- | :--- | :--- |
| **Margin** | PnL per dollar traded — trade efficiency | Increase with better signals + cut wasteful TO |
| **Returns** | Total annual PnL / base capital — absolute profit | Increase with higher TO or larger signals |
| **Fitness** | Sharpe × sqrt(Returns / TO) — submission gate | All three metrics working together |

A common trap: increasing Turnover raises Returns but crushes Margin. The best alphas have both — moderate Turnover with high Margin, so Returns are solid and the signal survives real transaction costs.

---

## 4. Key Principle

> **Margin is the real-world sanity check.** In simulation, transaction costs are ignored — but in live trading, every dollar traded has a cost. A high-Margin alpha earns well per trade and can absorb those costs. A low-Margin, high-Turnover alpha looks fine in simulation but deteriorates badly once real friction is applied.
>
> When optimizing, prioritize alpha ideas where each trade has a clear economic reason to be profitable — don't add turnover just to inflate Returns. Margin rewards you for trading purposefully.
