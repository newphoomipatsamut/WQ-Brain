# WorldQuant BRAIN: How to Improve Turnover (Knowledge Base)
> **Purpose:** A focused guide on understanding, diagnosing, and tuning Turnover — the metric that connects Sharpe to Fitness and determines real-world tradability.

---

## 1. Understanding Turnover

```
Daily Turnover = Dollar Trading Volume / BookSize
```

BookSize is fixed at $20M on BRAIN. A Turnover of 10% means the portfolio rebalances ~$2M worth of positions each day.

**Turnover feeds directly into Fitness:**

```
Fitness = Sharpe × sqrt(abs(Returns) / max(Turnover, 0.125))
```

* Too high (> 70%): **Alpha is rejected** — transaction costs would make it unprofitable in the real world.
* Too low (< 1%): **Structural Fitness ceiling** — even Sharpe of 1.32 can only achieve Fitness ~0.88 at TO = 1.61%.
* Sweet spot: **5–40%** for strong Fitness. Below 40% is advisable; below 70% is the hard limit.

Good alphas tend to have **lower turnover** — lower transaction costs mean more PnL survives to live trading.

---

## 2. Reducing Turnover (Too High → Fitness or Tradability Problem)

### A. Decay Simulation Setting
Setting `Decay = N` averages the alpha's daily output weights over the last N days linearly, slowing how fast positions change. This is the most effective single lever:
* `Decay = 0`: Raw daily signal, maximum turnover.
* `Decay = 6` (our default): Moderate smoothing — typical Turnover reduction of 30–50%.
* `Decay = 10–15`: Aggressive smoothing — use when signal is inherently high-frequency (news, sentiment).
* ⚠ Increasing Decay can change performance substantially — always re-check Sharpe and Returns after adjusting.

### B. `rank()` Wrapper
Wrapping raw signals in `rank()` compresses extreme values to a uniform [0, 1] distribution, reducing the magnitude of daily weight changes:
* `rank(ts_zscore(FIELD, 252))` turns a volatile zscore into a smooth rank — Turnover drops significantly.
* This is why nearly all our templates use `-rank(...)` as the outer layer.

### C. `trade_when` Operator
Only rebalances when a specific condition triggers; holds the previous position on all other days:
```
trade_when(abs(peer_return - stock_return) > 0.05, signal, -1)
```
* Ideal for event-driven signals — trades only when the signal is strong enough to overcome transaction costs.
* Practically eliminates turnover on quiet days.

### D. `hump()` Operator
Suppresses small daily changes below a threshold (default 1%), keeping yesterday's weight if the change is too small to matter:
```
-rank(hump(ts_rank(FIELD, 252)))
```
* Our preferred fitness fix for quarterly-data alphas. Use instead of `ts_decay_linear` (banned).
* Particularly effective when the signal updates slowly (quarterly/annual data) but small NaN-flicker creates fake daily turnover.

---

## 3. Increasing Turnover (Too Low → Fitness Ceiling Problem)

### A. Lower Decay Value
Reduce `Decay` from 6 toward 0 to let the daily signal pass through with less averaging. Step down in increments of 2 and check Fitness at each step.

### B. Smaller Universe
`TOP200` trades fewer stocks with larger individual weights — each position change represents a larger fraction of the book, pushing Turnover up. Counterintuitively, a smaller universe often has *higher* Turnover than `TOP3000` for the same expression.

### C. Shorter Lookback Windows
Shorter time-series windows make the signal react faster to new data, generating more frequent position changes:
* `ts_rank(FIELD, 63)` → higher TO than `ts_rank(FIELD, 252)`
* `ts_rank(FIELD, 22)` → higher TO again, but signal quality may degrade
* ⚠ For quarterly/annual fields, shorter lookbacks often destroy the signal entirely — the data doesn't update frequently enough to have meaningful 22-day variation.

### D. Use Frequently-Updated Datasets
Datasets that update daily naturally produce higher Turnover:
* **News** (`anl4_fs_*`, `anl4_ebit_*`): Analyst estimate revisions trigger daily signals.
* **Sentiment** (`snt1_*`, `scl12_*`): Score changes every day — inherently high-TO. Wrap in `ts_rank` or `ts_decay` to prevent TO from exceeding 70%.
* **Price-Volume** (`returns`, `volume`, `vwap`): Fastest-moving data — use short lookbacks (5–22 days).

---

## 4. Diagnosing Your Turnover Problem

| Turnover | Likely Cause | Fix |
| :--- | :--- | :--- |
| > 70% (rejected) | Signal too reactive / no smoothing | Add `hump()`, increase Decay, use `rank()`, or switch to `trade_when` |
| 40–70% (risky) | Moderate over-activity | Increase Decay by 2–4, or add `hump()` |
| 5–40% (healthy) | — | No action needed |
| 1–5% (low but passing) | Slow-moving signal | Check Fitness — if > 1.00, acceptable. If not, try shorter lookbacks |
| < 1% (structural ceiling) | Annual/quarterly signal barely moves day-to-day | Shorter lookbacks (may destroy signal); switch to revision-rate template (`ts_delta`); or abandon if signal only exists at annual timescale |

---

## 5. Key Principle

> **Turnover below 40% is advisable; below 70% is mandatory.** If a high-Sharpe alpha can't clear Fitness because TO is too high, use `hump()` or increase Decay before adding complexity. If TO is too low, switch to faster data or shorter lookbacks before assuming the signal is dead.
>
> The hardest case is ultra-low TO (< 2%) on annual fundamental fields — no amount of tuning rescues these from the Fitness ceiling. Identify them early and move on.

**Development target:** During alpha exploration, aim for **TO < 30%** (not just < 40%). The stricter target leaves headroom for real-world transaction costs — a simulated alpha at 35% TO may be marginal in live trading, but one at 25% TO has clear capacity. Use 30% as your internal bar; 40% as the absolute wall.
