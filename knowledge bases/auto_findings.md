# WQ-Brain Auto-Generated Research Findings
_Auto-updated after each batch. Last update: 2026-06-22 21:58_
_Do not edit — regenerated automatically by orchestrator.py._

## Banned Operators / Patterns
NEVER use these in any expression — they are dropped before simulation:

- `ts_decay_linear(field, N)` — correlated with submitted Alpha 10; Performance Comparison score always negative regardless of IS metrics.
- `ts_delta(close, N)` / `rank(ts_delta(close, N))` — correlated with Alpha 9 (price momentum). Self-corr 0.75–0.84 on every combination tested.

## Submitted Alphas Already In Book
These fields are already submitted — generating expressions using them risks high self-correlation:

- `acquired_intangible_avg_useful_life` (Fundamental)
- `current_ratio` (Fundamental)
- `eps` (Fundamental)

## Template Performance Summary

### QUARTERLY
- `ts_rank`: pass_rate=0.5% (3/603 runs), avg_sharpe=0.02
- `hump_ts_rank`: pass_rate=0.1% (1/942 runs), avg_sharpe=0.01
- `group_zscore`: pass_rate=0.0% (0/144 runs), avg_sharpe=0.08
- `ts_regression`: pass_rate=0.0% (0/246 runs), avg_sharpe=0.04
- `ts_corr`: pass_rate=0.0% (0/54 runs), avg_sharpe=0.04
- `ts_zscore`: pass_rate=0.0% (0/221 runs), avg_sharpe=0.02
- `group_rank`: pass_rate=0.0% (0/176 runs), avg_sharpe=0.02
- `revision_rate`: pass_rate=0.0% (0/697 runs), avg_sharpe=0.00
- `ts_std_dev`: pass_rate=0.0% (0/98 runs), avg_sharpe=-0.03
- `other`: pass_rate=0.0% (0/23 runs), avg_sharpe=-0.22
- `group_neutralize`: pass_rate=0.0% (0/15 runs), avg_sharpe=-0.31
→ **Best for QUARTERLY: `ts_rank`**

### WEEKLY
- `ts_rank`: pass_rate=2.2% (3/136 runs), avg_sharpe=0.20
- `ts_zscore`: pass_rate=0.0% (0/60 runs), avg_sharpe=0.09
- `group_rank`: pass_rate=0.0% (0/26 runs), avg_sharpe=-0.03
- `group_neutralize`: pass_rate=0.0% (0/48 runs), avg_sharpe=-0.07
- `ts_regression`: pass_rate=0.0% (0/22 runs), avg_sharpe=-0.14
- `revision_rate`: pass_rate=0.0% (0/26 runs), avg_sharpe=-0.19
- `hump_ts_rank`: pass_rate=0.0% (0/16 runs), avg_sharpe=-0.19
→ **Best for WEEKLY: `ts_rank`**

### SLOW
- `ts_zscore`: pass_rate=0.0% (0/11 runs), avg_sharpe=-0.23
- `ts_rank`: pass_rate=0.0% (0/34 runs), avg_sharpe=-0.32
→ **Best for SLOW: `ts_zscore`**

## Category Yield (Historical)

- **Fundamental**: 3 passes / 448 tested (0.7%) | 14 fields remaining
- **Analyst**: 0 passes / 1324 tested (0.0%) | 0 fields remaining
