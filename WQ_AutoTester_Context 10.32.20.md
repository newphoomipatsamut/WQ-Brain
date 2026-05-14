# WQ-Brain Auto-Tester Context
> **Purpose:** Context file for Claude to set up, modify, and extend the WQ-Brain automated testing pipeline.
> **Repo:** https://github.com/RussellDash332/WQ-Brain
> **Upload alongside WQ_Master_Context_Session_XX.md at session start.**
> **Last Updated:** Session 20, May 13 2026

---

## What This System Does

- Submits alpha expressions to WorldQuant BRAIN API automatically
- Runs up to 10 simulations concurrently via threading
- Saves all results to timestamped CSV files in `data/`
- Does **NOT** submit alphas to the BRAIN book — testing only
- Passing candidates must be manually reviewed and submitted via BRAIN UI

---

## Folder Structure

```
WQ-Brain/
├── credentials.json           ← Your BRAIN login (never commit to GitHub)
├── parameters.py              ← YOUR FILE — edit this every batch
├── parameters_top500.py       ← TOP500 batch file (copy into parameters.py to run)
├── filter_results.py          ← YOUR FILE — reads CSV, prints passing alphas with corr flags
├── main.py                    ← Engine — do not modify
├── commands.py                ← Helper — do not modify
├── database.py                ← Helper — do not modify
└── data/
    └── results_YYYYMMDD_HHMMSS.csv  ← Results auto-saved here (human-readable name)
    └── results_YYYYMMDD_HHMMSS.log  ← Per-run log (visible in BOTH terminal and file)
```

---

## How to Run

```bash
# Standard run
python3 main.py

# Run in background (Terminal can be closed)
nohup python3 main.py > output.log 2>&1 &

# Watch live progress (log goes to data/*.log NOT output.log)
tail -f data/$(ls -t data/*.log | head -1 | xargs basename)

# Filter results after run completes
python3 filter_results.py
```

> ✅ Logging now writes to BOTH terminal and `data/results_YYYYMMDD_HHMMSS.log` simultaneously. You will see live progress in the terminal.

---

## Full Workflow

```
parameters.py → main.py → filter_results.py → BRAIN UI checks → submit
```

1. Edit `parameters.py`
2. Run `main.py`
3. Run `filter_results.py` — results split into SUBMIT DIRECT / CHECK CORR / BORDERLINE
4. For each passer, open BRAIN link and check in this order:
   - **Yearly Sharpe** — 2021 and 2022 must both be positive
   - **Corr panel** — max corr < 0.70 vs all submitted
   - **Performance Comparison score change** — must be positive; submit highest first
5. Submit in descending score-change order (1 per day)
6. Update `SUBMITTED_VARIABLES` in `filter_results.py` after each submission

---

## parameters.py — Full Template

```python
# parameters.py
from commands import *

BASE = {
    'neutralization': 'SUBINDUSTRY',
    'decay':          4,
    'truncation':     0.08,
    'delay':          1,
    'universe':       'TOP3000',
    'region':         'USA',
}

BASE_TOP1000 = {**BASE, 'universe': 'TOP1000'}
BASE_TOP500  = {**BASE, 'universe': 'TOP500'}

VARIABLES = [
    # Add variables here
]

TEMPLATES = [
    # Tier 1 — Confirmed working
    "-rank(ts_rank({v},252))",
    "-rank(ts_rank({v},252)*rank(ts_delta(close,21)))",

    # Tier 2 — Window variants (uncomment if Tier 1 borderline)
    # "-rank(ts_rank({v},126))",
    # "-rank(ts_rank({v},63))",
]

DATA = [
    {**BASE, 'code': t.format(v=v)}
    for v in VARIABLES
    for t in TEMPLATES
]

print(f"Total expressions queued: {len(DATA)}")
```

---

## filter_results.py — Current Template (Session 16)

```python
# filter_results.py
import pandas as pd, glob, os, re

# ── UPDATE THIS AFTER EVERY SUBMISSION ────────────────────
SUBMITTED_VARIABLES = [
    'sales_ps',                                              # A4
    'volume',                                                # A9
    'current_ratio',                                         # A10
    'mdl177_garpanalystmodel_qgp_vfpriceratio',              # MC3
    'mdl177_2_sensitivityfactor400_ttmocfev',                # M6 + NEW-3 + NEW-3b
    'mdl177_2_5yearrelativevaluefactor_rel5yfwdep',          # M11 + M10 + NEW-2
    'mdl177_2_sensitivityfactor400_ney',                     # M15b + NEW-9 + NEW-9b
    'mdl177_2_deepvaluefactor_fwdep',                        # DV2c
    'mdl177_2_deepvaluefactor_ttmfcfp',                      # DV5 + NEW-5 + NEW-5b + T1K-3
    'mdl177_2_deepvaluefactor_ttmfcfev',                     # DV3b + T5K-5 (NOTE: ttmfcfev not ttmfcev!)
    'mdl177_2_deepvaluefactor_pdy',                          # DV16 + NEW-7 + NEW-7b
    'mdl177_valanalystmodel_qva_incstmt',                    # VA-1
    'mdl177_2_vma2_vma2_va',                                 # VMA-2 + T5K-4
    'mdl177_relativevaluemodel_ttmfcfp',                     # RV-1b + T5K-2
    'mdl177_2_relativevaluemodel_ttmfcfp',                   # T2K-1 (same alpha as T5K-2)
    'mdl177_deepvaluefactor_ttmfcfp_alt',                    # Alt-1
]
```

The full `filter_results.py` with corr flagging logic outputs three sections:
- **✅ SUBMIT DIRECT** — new variable family, corr safe
- **⚠️ CHECK CORR FIRST** — same/related variable in book
- **🟡 BORDERLINE** — below main threshold

---

## CSV Output — Column Reference

| Column | Meaning | Good Value |
|--------|---------|------------|
| `passed` | IS checks passed (out of 6) | ≥ 5 |
| `sharpe` | IS Sharpe | ≥ 1.25 |
| `fitness` | IS Fitness | ≥ 1.00 |
| `turnover` | Turnover % | 1–70% |
| `weight` | Concentrated weight check | PASS |
| `subsharpe` | Sub-universe Sharpe | > 0 |
| `link` | Direct URL to alpha in BRAIN | Click to open |
| `code` | The expression tested | — |

---

## What CSV Does NOT Give You

Before submitting any passing candidate, manually check in BRAIN UI:

1. **Yearly Sharpe** — 2021 and 2022 must both be positive
2. **Corr panel** — max corr < 0.70 vs all submitted
3. **Performance Comparison score change** — must be positive

---

## Confirmed Working Variable Families

| Family Prefix | Signal Type | Hit Rate | Notes |
|--------------|-------------|----------|-------|
| `mdl177_2_deepvaluefactor_*` | Value | ~40% | Fully exhausted |
| `mdl177_garpanalystmodel_*` | GARP Value | partial | MC3 (vfpriceratio) submitted; capeff/roefcf corr-toxic |
| `mdl177_2_sensitivityfactor400_*` | Earnings | ~33% | M6 (ttmocfev), M15b (ney) + TOP500 variants submitted |
| `mdl177_2_5yearrelativevaluefactor_*` | Relative Value | 2/? tested | rel5yfwdep +385 (NEW-2), **rel5ybp +238 (ZY2OXdKQ, agent)**. ep/ocfp/fcfp/sp/coreepsp in d1v11. |
| `mdl177_valanalystmodel_*` | Value Analyst | 1/7 tested | `qva_incstmt` working — VA-1 +238. Siblings (fwdep/bp/revs/divy/epssurp/valuation) in d1v11. |
| `mdl177_valueanalystmodel_*` | Value Analyst II | 0/5 tested | DIFFERENT from valanalystmodel. qva_incstmt/finstmt/epmodule/pegy/earnval in d1v11. |
| `mdl177_2_vma2_*` | Value Model II | 1/5 tested | `vma2_va` working — VMA-2 +66. Siblings (ma/ma_ee/ma_em/ma_pm) in d1v11. |
| `mdl177_2_earningmomentumfactor400_*` | Analyst Momentum | 0/10 tested | Fresh family — rev6/numrevy1/numrevq1/epsrm/fqsurs_std/salesurp/stockrating/y1aepsg/cvfy1eps/fcfroey1p in d1v11. |
| `mdl177_relativevaluemodel_*` | Relative Value | 1/2 tested | `ttmfcfp` × momentum works (RV-1b +66). Naked version dead (corr DV5). |
| `mdl177_2_deepvaluefactor_pdy` | Value | 2 variants | DV16 TOP3000 submitted. **pdy TOP500 +37 (MPKN7bXr, agent)** |

---

## Dead Variable Families — Do Not Retest

| Family | Reason |
|--------|--------|
| `mdl177_fangma_*` (most) | Corr ~0.99 vs MC3 — EXCEPTION: fangma_vmm_usa_fangma_vmm11 corr 0.54–0.58, submittable. Siblings (gpam/rvm/mam/emf/dvm) untested — in d1v11. |
| `mdl177_2_liquidityriskfactor_*` | Negative IS |
| `mdl177_2_earningsqualityfactor_*` | 2022 structural reversal |
| `beta_last_*`, `systematic_risk_*`, `unsystematic_risk_*` | Risk factors dead |
| All `snt_*`, `scl12_*`, `snt_buzz_ret` | Sentiment family dead for D1 |
| All `implied_volatility_*`, `pcr_*`, `forward_price_*` | Options dead |
| All Analyst (`anl4_*`, `snt1_d1_*`) | 2021 structural failure |
| `deepvaluefactor` all 32 fields | Fully exhausted |
| `sensitivityfactor400` siblings | All IS < 1.0 except ttmocfev/ney |
| `managementqualityfactor_*` | All IS < 1.0 |
| `shortsentimentfactor_*` | Mostly dead — EXCEPTION: days_to_cover corr 0.36, sharpe 1.70 (E5qJ5qr0 submittable). onloan_conc + sht_int confirmed dead. |
| `surpriseanalystmodel_*` | Dead |
| `historicalgrowthfactor_*` | Dead |
| `industryrrelativevaluefactor_*` | ALL fitness < 1.00 — d1v10 confirmed dead across all 8 tested fields |
| `globaldevnorthamerica_*` | Score -228 (confirmed) — dead regardless of IS metrics. Do not test. |
| All derivative score fields | All Fitness < 0.65 |
| `garpanalystmodel_qgp_capeff_*` | Corr-toxic |
| `garpanalystmodel_qgp_roefcf` | Corr 0.77 vs DV2c, score -27 |
| `fa_fc_fwdep`, `fa_fc_fcfp`, `fa_totalcov` | Corr ~1.0 vs DV2c |
| `deepvaluefactor_estep` | Corr 0.997 vs DV2c |
| Naked `relativevaluemodel_ttmfcfp` (both prefixes) | Corr 0.96 vs DV5 |
| TOP1000 universe (most variables) | Corr 0.73–0.83 — exception: ttmfcfp TOP1000 at 0.58 |
| VA-2 `qva_incstmt` × momentum | Corr 0.74 vs DV2c AND score -77 |
| VMA-1 `vma2_va` × momentum | Score change -84 |
| `deepvaluefactor_*_alt` all variants | Corr 0.90–1.00 vs submitted DV alphas. Exception: `ttmfcfp_alt` × momentum corr 0.55 vs M6, score +27 (Alt-1, submitted) |
| `mdl177_2_garpanalystmodel_qgp_vfpriceratio` | Corr 0.91 vs MC3 (`mdl177_` prefix version) — same variable family, different prefix |

---

## Operator Logic — What Works and What Doesn't

| Operator Pattern | Works? | Notes |
|-----------------|--------|-------|
| `ts_rank(VAR, 252)` | ✅ Yes | Core template — naked version |
| `ts_rank(VAR, 252) * rank(ts_delta(close, 21))` | ⚠️ Sometimes | Momentum can hurt (VA-2, VMA-1 both went negative) |
| `ts_rank(VAR, 126)` | ⚠️ Sometimes | pdy jumped 1.34→1.61 with 126w |
| `ts_decay_linear(VAR, 21) * rank(ts_delta(close, 5))` | ⚠️ Sometimes | A4/A10 template only |
| `ts_delta(VAR, 63)` | ❌ No | 2021 always fails |
| `ts_rank(ts_delta(VAR, 63), 252)` | ❌ No | Noise not signal |

---

## Universe Variant Rules

| Universe | Corr vs TOP3000 | Use When |
|----------|----------------|----------|
| TOP500 | Usually 0.28–0.65 | Test first — often passes cleanly |
| TOP1000 | Usually 0.73–0.83 | Skip unless variable family is very different. Exception: ttmfcfp TOP1000 = 0.58. |

---

## Batch Strategy

### Standard batch — new variables
```python
TEMPLATES = ["-rank(ts_rank({v},252))", "-rank(ts_rank({v},252)*rank(ts_delta(close,21)))"]
# 20 vars × 2 = 40 expressions, ~10 min
```

### Universe variants batch
```python
BASE_TOP500 = {**BASE, 'universe': 'TOP500'}
DATA = [{**BASE_TOP500, 'code': e} for e in PASSING_EXPRESSIONS]
# Test TOP500 first — usually cleaner corr than TOP1000
```

### Session 16 batches (complete)
- Main batch (100 expressions): relativevaluemodel siblings, 5yr relative value new fields, vma2 siblings, valanalystmodel siblings, growthanalystmodel
- Mop-up batch (6 expressions): deepvaluefactor_alt family + garpanalystmodel_2
- TOP500 batch (7 expressions): VMA-2, VA-1, RV variants, DV3b, DV2c, MC3 in TOP500

### Session 19 — agent.py Redesign (complete)
- **New role:** Corr-checker + tuning file generator (no longer runs main.py itself)
- **Flow:** Watch data/ for CSVs → fetch corr → diagnose weak metrics → write parameters_tune_*.py → you run it
- **Score fetching added:** `GET /teams/{team_id}/alphas/{id}/before-and-after-performance` → `data['score']['before/after']`
- **team_id:** Fetched at login via `GET /users/self/teams` → `results[0]['id']`
- **Corr entry:** `python3 agent.py --corr` for manual entry when API returns None
- **State:** `agent_state.json` — tracks processed_csvs, corr_checked, tune_candidates, submittable
- **Finds:** npnMdNNz (vmm11 zscore TOP3000 +396), e7nobL6O (vmm11 ts_rank TOP3000), E5qJ5qr0 (days_to_cover +TBC)

### Session 19 — main.py Auto-Resume Fix (applied)
- **Bug fixed:** Timed-out simulations were silently dropped (added to rows_processed)
- **Fix:** `self._timed_out` list — timed-out sims returned to main loop, retried after 30s
- **Logging:** Cleaned up — ▶/⏳/✔ symbols, progress % only on change, `[N/total] done` counter

### Session 19/20 — Batch d1v9 / d1v9b / d1v10 / d1v11
- **d1v9:** fangma_vmm_usa_fangma_vmm11 + globaldev fields. TOP3000 only. Found 3 submittables.
- **d1v9b:** 5shortsentimentfactor. days_to_cover passes; onloan_conc + sht_int dead.
- **d1v10:** industryrrelativevaluefactor (double-r). 16 expressions. **ALL DEAD — fitness < 1.00 across all fields.** Entire family confirmed dead.
  - Fixed spellings: `curindocfta_` (not curindocta_), `curindocfp_` (not curindoctp_)
  - Fields tested: curindfcfp_, curindcfp_, curindfwdep_, curindep_, curindbp_, curindsp_, curindocfta_, curindocfp_
- **tune_d1v9:** Tuning variants of vmm11. npnMdNNz (zscore TOP3000 +396) + 9q90GOld (ts_rank TOP200 +639) confirmed best.
- **d1v11:** ~120 expressions, ~180 min. 6 families: fangma siblings (gpam/rvm/mam/emf/dvm), valanalystmodel siblings, valueanalystmodel, vma2 siblings, 5yr relvalue siblings, earningmomentumfactor400. **Queued to run.**

### D0 Batches — ALL FAILED, DO NOT RETRY
- D0 thresholds confirmed May 12: Sharpe ≥ 2.0, Fitness ≥ 1.30 — too strict
- 4 batches (v1–v4) all failed. Best achieved: sharpe 1.22, fitness 0.47
- **Decision: Focus 100% on D1**

---

## Key Thresholds

| Metric | Submit | Borderline | Reject |
|--------|--------|------------|--------|
| IS Sharpe | ≥ 1.25 | 1.10–1.24 | < 1.10 |
| IS Fitness | ≥ 1.00 | 0.85–0.99 | < 0.85 |
| Turnover | 1–70% | — | > 70% or < 1% |
| 2021 Yearly Sharpe | > 0 | — | ≤ 0 |
| 2022 Yearly Sharpe | > 0 | — | ≤ 0 |
| Max self-corr | < 0.70 | 0.60–0.69 | ≥ 0.70 |
| **Score change** | **> 0** | **+1 to +50** | **≤ 0** |

---

## Variable Name Gotchas — Confirmed Typos

| Wrong | Correct | Context |
|-------|---------|---------|
| `ttmfcev` | `ttmfcfev` | deepvaluefactor TTM FCF/EV — always verify from Fields Tracker tab |
| `industryrelativevaluefactor` | `industryrrelativevaluefactor` | Double-r — confirmed May 13 |
| `curindocta_` | `curindocfta_` | industryrrelativevaluefactor field — added f |
| `curindoctp_` | `curindocfp_` | industryrrelativevaluefactor field — added f, dropped t |

**Rule:** Never guess variable names. Always verify from the Fields Tracker tab in the Excel tracker before batching. Mass "unknown variable" errors (32/36 in Batch 16) happened from guessing.

**mdl177 vs mdl177_2 prefix:** Different prefixes of the same variable family produce near-identical alphas — corr 0.91 or higher. Do NOT test both prefixes as if they're independent signals.

---

## Fitness Formula

```
Fitness = sqrt( |Returns%| / max(Turnover%, 12.5%) ) × Sharpe
```

---

## Setup Commands (Mac)

```bash
git clone https://github.com/RussellDash332/WQ-Brain.git
cd WQ-Brain
pip3 install requests pandas
cp credentials.json.example credentials.json
# Edit credentials.json with BRAIN email and password
python3 main.py
python3 filter_results.py
```

---

## Instructions for Claude

When the researcher uploads this file, Claude should:

1. **Check Master Context** for current submitted book and pending queue
2. **Ask which batch to build** — new Fields Tracker variables, window variants, universe variants
3. **Generate `parameters.py`** ready to copy-paste
4. **After CSV results pasted:** Filter and rank by: IS pass → corr risk flag → recommend score-change check order
5. **When corr/score data provided:** Give final verdict and update submit priority queue
6. **Never suggest modifying `main.py`**
7. **Remind researcher** to check Performance Comparison score change before every submission

When building `parameters.py`:
- Print total expression count and estimated runtime
- Organize by family with comments
- Tier 1 templates first, Tier 2/3 commented out
- Include both TOP3000 and TOP500 sections for confirmed passers

When analyzing results:
- Flag SUBMIT DIRECT vs CHECK CORR based on variable family
- Always ask for Performance Comparison data before finalizing submit order
- Reject any alpha with negative score change permanently
- **Momentum template (× ts_delta close,21) can hurt** — if naked passes but momentum doesn't, the naked version is the keeper

---

*Keep this file updated as new operators are discovered or new variable families are confirmed working.*
