# WorldQuant BRAIN: Price-Volume Data Reference (Knowledge Base)
> **Purpose:** A practical reference for price-volume fields — their definitions, correct usage, and alpha construction patterns. Price-volume data is DAILY frequency and the foundation of short-term momentum and reversion signals.

---

## 1. Core Field Definitions

### Volume
The number of shares traded for a stock on a given day. Measures market participation and interest.

**Alpha uses:**
* High volume on a price move = conviction (momentum signal)
* High volume without price move = absorption (potential reversion signal)
* `ts_rank(volume, 20)` = how active is this stock relative to its recent history
* `volume / adv20` = today's volume relative to average — detects unusual activity

### VWAP (Volume-Weighted Average Price)
```
VWAP = Total Dollar Value Traded / Total Shares Traded
```
The average price a stock traded at over the day, weighted by volume. Heavier weighting goes to price levels where more shares changed hands.

**Alpha uses:**
* `close - vwap` = where did the stock close relative to the intraday average? Positive = closed above average (bullish intraday), negative = below (bearish).
* `ts_rank(close / vwap, 20)` = is the stock consistently closing above its intraday average?
* VWAP is a cleaner price signal than `close` alone because it reflects actual transaction prices rather than just the final print.

### Liquidity
Liquidity = the ease with which a stock can be bought or sold without moving the price. In BRAIN, liquidity is proxied by volume:
* High volume = high liquidity = large position can be entered/exited without market impact.
* Low volume stocks have wide bid-ask spreads and large price impact — alphas relying on illiquid stocks tend to fail the sub-universe Sharpe test.
* **Why TOP200 exists:** The 200 most liquid stocks (by volume/market cap) are highly tradeable. Alphas on TOP200 are more realistic in live trading.

### adv20 (Average Daily Volume, 20-day)
Pre-computed field available directly in BRAIN expressions:
```
adv20 = ts_delay(ts_mean(volume, 20), 1)
```
The 1-day delay (`ts_delay(..., 1)`) ensures today's volume is not included — adv20 reflects yesterday's 20-day average.

**Critical syntax note:** Use `adv20` directly as a field name — **do NOT write `adv(20)`** (that syntax does not exist in FASTEXPR).

**Alpha uses:**
* `volume / adv20` — volume surprise ratio. Stocks trading 3× their average are experiencing unusual attention.
* `-rank(ts_rank(adv20, 252))` — rank stocks by their average liquidity (avoid illiquid micro-caps in a signal)
* `cap / adv20` — days-to-trade metric: how many days of average volume it takes to trade the full market cap

---

## 2. Price Field Relationships

### Close vs. Open — They Are NOT the Same
Today's opening price is **not** equal to yesterday's closing price. The gap between them (the "overnight gap") is a tradeable signal:

**Why the gap exists:**
* After-hours trading (earnings releases, macro news after the bell)
* Investor sentiment changes that accumulate overnight
* Market makers resetting prices based on overnight order flow (Nasdaq uses an "opening cross" algorithm to determine the best opening price given accumulated overnight orders)

**Alpha uses:**
* `open - ts_delay(close, 1)` = overnight gap — positive means gap up (bullish overnight news)
* `close - open` = intraday move — positive means the stock gained from open to close
* `ts_rank(open - ts_delay(close, 1), 20)` = is this stock consistently gapping up or down?

### The Standard OHLCV Fields
| Field | Description | Update Frequency |
| :--- | :--- | :--- |
| `open` | First trade price of the day | Daily |
| `high` | Highest trade price of the day | Daily |
| `low` | Lowest trade price of the day | Daily |
| `close` | Last trade price of the day | Daily |
| `volume` | Shares traded | Daily |
| `vwap` | Volume-weighted average price | Daily |
| `returns` | Daily return: `close / ts_delay(close, 1) - 1` | Daily |
| `adv20` | 20-day average daily volume (pre-computed) | Daily |
| `cap` | Market capitalization | Daily |

---

## 3. Aggregating Volume Across Groups

Volume is a per-stock scalar — to get group-level totals:

```
group_sum(volume, market)      # total market volume on that day
group_sum(volume, sector)      # total volume for each sector
group_sum(volume, industry)    # total volume for each industry
```

**Relative volume signal:**
```
-rank(volume / group_sum(volume, industry))
```
Each stock's share of its industry's total volume — detects which stocks are capturing unusual attention within their peer group.

---

## 4. Price-Volume Alpha Patterns

### Momentum / Trend
```
-rank(ts_rank(returns, 20))              # short-term return momentum
-rank(ts_mean(returns, 5))               # 5-day average return
-rank(ts_rank(close / ts_delay(close, 252), 20))  # 52-week high proximity
```

### Reversion
```
rank(ts_rank(returns, 5))                # short-term reversion (opposite sign)
rank(close - ts_mean(close, 20))         # distance from moving average
```

### Volume-Price Interaction
```
-rank(ts_rank(returns * volume / adv20, 20))   # volume-confirmed momentum
-rank(ts_corr(volume, returns, 20))             # how correlated is volume with price moves?
```

### VWAP-Based
```
-rank(ts_rank(close - vwap, 20))         # intraday close vs. average position
-rank(ts_rank((close - vwap) / vwap, 20)) # normalized intraday premium/discount
```

---

## 5. Key Rules for Price-Volume Alphas

> **Use MARKET or NONE neutralization for price-volume signals.** Price moves and volume patterns are meaningful at the whole-market level — neutralizing by SUBINDUSTRY removes the signal. See `WQ_Neutralization_Strategy.md`.

> **Use SHORT lookbacks (5–63 days).** Price-volume data is daily and fast-moving. A 252-day `ts_rank` of `returns` is a medium-term momentum signal; a 5-day version is a short-term reversion signal. Lookbacks > 63 days tend to oversmooth the signal.

> **`ts_delta(close, N)` is BANNED.** The pattern `rank(ts_delta(close, N))` correlates with Alpha 9 (price momentum already in our book). Any expression containing `ts_delta(close` is dropped before simulation. Use `returns` or `ts_rank(close, N)` instead.

> **Price-volume fields are HEAVILY researched.** Most simple patterns (momentum, reversion, RSI-style) are already in other researchers' books. Prefer using price-volume as a *conditioning* variable rather than the primary signal — e.g., `trade_when(volume > 2 * adv20, fundamental_signal, -1)` only trades a fundamental signal on high-volume days.
