# WorldQuant BRAIN: Error Messages Reference (Knowledge Base)
> **Purpose:** Specific error messages returned during simulation or submission — what they mean and how to fix them.

---

## 1. "Most illiquid 50% instruments after cost Sharpe is above cutoff of original universe"

### What it means
This is a **liquidity robustness test** that runs after submission. BRAIN splits your universe in half by liquidity (dollar volume), takes the bottom 50% (the most illiquid half), and checks whether the alpha still earns an acceptable Sharpe on those stocks after trading costs.

**Threshold formula:**
```
Threshold = 0.525 × AfterCostSharpe(original universe)
```
If the after-cost Sharpe on the illiquid 50% is below ~52.5% of your full-universe after-cost Sharpe, the alpha fails this test.

**Why BRAIN runs this test:** An alpha that only works on the most liquid stocks is hard to scale. If your PnL is entirely driven by the top 50% most liquid names, adding real-world position size would exhaust the liquidity in those names quickly.

### Root causes
* The alpha expression assigns very low or zero weights to illiquid stocks (they are effectively excluded)
* The signal quality or data coverage deteriorates sharply for smaller/less-liquid stocks
* Transaction costs wipe out thin signals on illiquid names faster than on liquid names

### Fixes

**A. Increase weights for illiquid stocks**
Modify the expression to explicitly allocate more capital to lower-liquidity instruments. The key is to make sure illiquid stocks appear meaningfully on both long and short sides:
```
# Example: downweight liquid stocks to let illiquid ones have more relative weight
signal / rank(adv20)   # divides by liquidity rank — boosts illiquid relative weight
```

**B. Conditional decay for illiquid stocks**
Apply a longer (smoother) decay to illiquid stocks to reduce their transaction cost impact:
```python
# Pseudocode — set different decay horizon based on liquidity threshold
adv20 < threshold ? trade_when(condition, signal, -1) : signal
```
Lower-liquidity stocks get held longer (via `trade_when` or higher Decay), reducing their turnover and therefore their after-cost performance penalty.

**C. Neutralize against size and liquidity risk factors**
The illiquid portion is driven by the **size factor** (small-cap) and **liquidity risk factor**. Neutralizing against these inside the expression removes the structural tilt that causes the illiquid half to underperform:
```
group_neutralize(signal, liquidity_bucket)
vector_neut(signal, [size_factor, liquidity_factor])
```
This ensures the alpha is not systematically betting on size or liquidity direction — only on the stock-specific signal within each liquidity tier.

---

## 2. "Alpha better suited for Delay 1"

### What it means
This error appears when you submit or simulate a **Delay-0** alpha, and BRAIN detects that the same expression has **higher Sharpe at Delay-1 than Delay-0**.

### Why it happens
Delay-0 trades at today's market close using signals generated from today's intraday data. The higher transaction costs of D0 execution eat into returns. If the signal does not contain enough intraday-specific information to justify D0, the Sharpe at D1 (next-day open, lower costs) will exceed D0.

### Fix
Simply re-simulate the same expression with **Delay = 1** and submit it from there. You lose nothing — the signal is the same, but the execution is cheaper and the risk bar is lower (Sharpe ≥ 1.25 vs. Sharpe ≥ 2.00 for D0). A D1 alpha with Sharpe 1.40 is more likely to be profitable in live trading than a D0 alpha with Sharpe 1.50, because D1 transaction costs are much lower.

**When to keep trying D0:**
Only pursue D0 if the signal specifically captures intraday information that disappears by the next day — e.g., overnight gaps, after-hours news reactions, or close-auction-specific dynamics. If the signal uses only daily data (`close`, `volume`, fundamentals), there is no information advantage to D0 and you should always use D1.
