# WQ-Brain Auto-Generated Research Findings
_Auto-updated after each batch. Last update: 2026-06-17 21:40_
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
- `interest_expense` (Fundamental)
- `ppent` (Fundamental)
- `revenue` (Fundamental)
- `sales_ps` (Fundamental)
- `mdl177_2_sensitivityfactor400_ttmocfev` (Model)
- `mdl177_garpanalystmodel_qgp_vfpriceratio` (Model)
- `mdl177_2_relativevaluemodel_ttmfcfp` (Model - Analyst)
- `mdl177_2_sensitivityfactor400_pbroeresidual` (Model - Analyst)
- `mdl177_2_valueanalystmodel_qva_chgacc` (Model - Analyst)
- `mdl177_2_vma2_vma2_va` (Model - Analyst)
- `mdl177_5shortsentimentfactor_days_to_cover` (Model - Analyst)
- `mdl177_fangma_vmm_usa_fangma_vmm11` (Model - Analyst)
- `mdl177_valanalystmodel_qva_chgacc` (Model - Analyst)
- `mdl177_valanalystmodel_qva_incstmt` (Model - Analyst)
- `mdl177_valueanalystmodel_qva_chgacc` (Model - Analyst)
- `mdl177_earningsqualityfactor_uap` (Model - Analyst)
- `close` (Price-Volume)
- `high` (Price-Volume)
- `low` (Price-Volume)
- `returns` (Price-Volume)
- `volume` (Price-Volume)

## Template Performance Summary

### QUARTERLY
- `ts_rank`: pass_rate=0.6% (3/522 runs), avg_sharpe=0.04
- `hump_ts_rank`: pass_rate=0.2% (1/578 runs), avg_sharpe=0.04
- `group_zscore`: pass_rate=0.0% (0/108 runs), avg_sharpe=0.11
- `ts_corr`: pass_rate=0.0% (0/50 runs), avg_sharpe=0.06
- `revision_rate`: pass_rate=0.0% (0/322 runs), avg_sharpe=0.06
- `ts_zscore`: pass_rate=0.0% (0/209 runs), avg_sharpe=0.04
- `group_rank`: pass_rate=0.0% (0/138 runs), avg_sharpe=0.03
- `ts_regression`: pass_rate=0.0% (0/206 runs), avg_sharpe=0.02
- `ts_std_dev`: pass_rate=0.0% (0/96 runs), avg_sharpe=-0.02
- `other`: pass_rate=0.0% (0/23 runs), avg_sharpe=-0.22
→ **Best for QUARTERLY: `ts_rank`**

### WEEKLY
- `ts_rank`: pass_rate=4.3% (3/70 runs), avg_sharpe=0.43
- `ts_zscore`: pass_rate=0.0% (0/20 runs), avg_sharpe=0.30
→ **Best for WEEKLY: `ts_rank`**

### SLOW
- `ts_zscore`: pass_rate=0.0% (0/11 runs), avg_sharpe=-0.23
- `ts_rank`: pass_rate=0.0% (0/25 runs), avg_sharpe=-0.39
→ **Best for SLOW: `ts_zscore`**

## Category Yield (Historical)

- **Model**: 2 passes / 24 tested (8.3%) | 2696 fields remaining
- **Fundamental**: 7 passes / 277 tested (2.5%) | 1381 fields remaining
- **Model - Analyst**: 10 passes / 261 tested (3.8%) | 340 fields remaining
- **Sentiment / Analyst**: 0 passes / 1 tested (0.0%) | 16 fields remaining
- **Analyst**: 0 passes / 1324 tested (0.0%) | 0 fields remaining
