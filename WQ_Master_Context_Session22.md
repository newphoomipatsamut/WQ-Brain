# WorldQuant BRAIN — Master Context File
> **Researcher:** Nutcha | **Last Updated:** 17 May 2026 (Session 22) | **Session:** 22
> **Upload this file at the start of every Claude session.**

---

## Current Status

| Item | Value |
|------|-------|
| IQC 2026 Stage 1 D1 Score | **TBC** (update after each submission) |
| Alphas submitted (IQC Challenge) | 17+ active |
| Last batch | d1v16 ready to run. d1v17a/v17b (full 417-field Model sweep) built. RRNLElmo ✅ submitted May 17. |
| Deadline | May 18, 2026 |
| Days Remaining | **1** (May 18 = final slot) |
| Consultant Status | Conditional Consultant — fees accruing, paid after background check |

---

## ⚡ Key Rule — Performance Comparison Panel

**Always check the Performance Comparison panel before submitting.**

| Score Change | Action |
|-------------|--------|
| > +100 | Submit immediately |
| +10 to +100 | Submit — worthwhile |
| +1 to +10 | Submit last — minimal impact |
| Negative | ❌ REJECT permanently regardless of IS metrics |

**Submit priority = descending score change order.**

---

## ⚠️ D0 vs D1 — IMPORTANT

**D0 (delay=0) is NOT viable. Do not pursue.**
- D0 thresholds confirmed May 12: Sharpe ≥ 2.0, Fitness ≥ 1.30 — far too strict
- All D0 batches (v1–v4) failed. Focus 100% on D1.

---

## Submission Calendar — Session 22

> Deadline: **May 18** | **1 slot remaining (May 18)**

| Day | Alpha | Score Δ | Universe | Link | Status |
|-----|-------|---------|----------|------|--------|
| ✅ May 9 | NEW-5b | +552 | TOP500 | https://platform.worldquantbrain.com/alpha/6XaA603p | ✅ Done |
| ✅ May 9/10 | VA-1 | +238 | TOP3000 | https://platform.worldquantbrain.com/alpha/mLroERYW | ✅ Done |
| ✅ May 10 | NEW-3b | +340 | TOP500 | https://platform.worldquantbrain.com/alpha/JjgPaA3A | ✅ Done |
| ✅ May 12 | ZY2OXdKQ 🆕 | +238 | TOP500 | https://platform.worldquantbrain.com/alpha/ZY2OXdKQ | ✅ Done |
| ✅ May 13 | npnMdNNz 🆕 | +396 | TOP3000 | https://platform.worldquantbrain.com/alpha/npnMdNNz | ✅ Done |
| ✅ May 14 | 9q90GOld 🔥 | +639 | TOP200 | https://platform.worldquantbrain.com/alpha/9q90GOld | ✅ Done |
| ✅ May 15 | e7nobL6O or better | TBC | TOP3000 | — | ✅ Done |
| ✅ May 16 | chgacc Golden Alpha 🔥 | +643 | TOP200 | — | ✅ Done |
| ✅ May 17 | RRNLElmo (rvm6) 🔥 | **TBC — great score** | TOP200 | https://platform.worldquantbrain.com/alpha/RRNLElmo | ✅ Submitted |
| **May 18** | **TBD — best candidate from bench** | **TBC** | — | — | 🔥 Need to pick |

> **May 18 candidates (check score on platform, submit highest):**
> - RV-1b — Sharpe 1.90, Fitness 1.58, corr 0.49 ✅
> - NEW-2 — Sharpe 1.89, Fitness 1.88, corr 0.65 ✅
> - NEW-5b — Sharpe 1.80, Fitness 1.58, corr 0.36 ✅ (already submitted as diff alpha — check if this is duplicate)
> - NEW-3b — Sharpe 1.77, Fitness 1.62, corr 0.55 ✅ (already submitted)
> - E5qJ5qr0 — Sharpe 1.70, Fitness 1.00, corr 0.36 ✅ (days_to_cover)
> - 9q90GOld — Sharpe 1.40, Fitness 1.19, corr 0.24 ✅ (already submitted May 14)
> Open each on BRAIN platform → Performance Comparison panel → pick highest positive score

---

## 🔥 Golden Alpha Finds — Session 22

| Alpha ID | Variable | Expression | Sharpe | Fitness | Corr | Score | Universe | Status |
|----------|----------|-----------|--------|---------|------|-------|----------|--------|
| chgacc flip | `mdl177_valueanalystmodel_qva_chgacc` | `rank(ts_rank(...,252))` (flipped) | TBC | TBC | 0.20 | **+643** | TOP200 | ✅ Submitted |
| 9q90GOld | `mdl177_fangma_vmm_usa_fangma_vmm11` | `-rank(ts_rank(...,252))` | 1.40 | 1.19 | 0.24 | **+639** | TOP200 | ✅ Submitted |
| RRNLElmo | `mdl177_fangma_rvm_usa_fangma_rvm6` | `-rank(ts_zscore(...,252))` | 1.47 | 1.50 | 0.45 | **TBC — great** | TOP200 | ✅ Submitted May 17 |

---

## 🔑 Key Strategy Discoveries — Session 22

### 1. Sign Flip Strategy — UPDATED RULE
- A field with **-1.46 Sharpe** on standard `-rank(ts_rank(...))` became **+643 score** when flipped
- **Rule (refined):** Only flip-test fields with IS Sharpe ≤ **-1.0** after both ts_rank AND ts_zscore have been tried
- Do NOT flip just because ts_rank is negative — try ts_zscore first
- Flip order: ts_rank baseline → ts_zscore → if both still < -1.0 Sharpe → then try flip

### 2. TOP200 Universe is the Sweet Spot
- 9q90GOld (vmm11 TOP200): +639
- chgacc flip TOP200: +643
- rvm6 TOP200 ts_zscore: corr 0.45 (clean), Sharpe 1.47, Fitness 1.50
- **Rule:** After any TOP3000 pass, always test TOP200 with both ts_rank and ts_zscore

### 3. FCF + Working Capital Regime
- `qva_chgacc` (Change in Net Op Working Capital) — strongest field found in IQC
- `si_ratio` (Short Interest Ratio) — +259 score
- `uap` (Unexpected change in accounts payable) — +160 score
- `pbroeresidual` — +160 score
- **Rule:** FCF and working capital fields are working in current market regime

### 4. Variable Names — HARD RULE
- **NEVER guess variable names.** Always verify from `fields_tracker.csv` or the WQ Brain Fields page.
- Wrong names cause silent API errors or test the wrong field entirely.
- When building parameters files: query `wq_alpha.db` → `SELECT field FROM fields WHERE field LIKE 'mdl177%'`

---

## Batch Status — Session 22

| Batch | Status | Fields | Est. Runtime |
|-------|--------|--------|-------------|
| d1v16 | ✅ Complete | 85 results — no full passes. Best: garpanalystmodel_qgp_valuation sharpe=1.30, fitness=0.90 | ~135 min |
| tune_garp_val | ⏳ Ready | 8 expressions — tuning garpanalystmodel_qgp_valuation (TOP200, ts_rank, decay variants) | ~12 min |
| d1v17a | ⏳ Ready to run | 208 fields (full Model sweep part A) | ~312 min |
| d1v17b | ⏳ Ready to run | 209 fields (full Model sweep part B) | ~314 min |

> Run order: tune_garp_val (12 min, might find a passer), then v17a → v17b for post-deadline sweep.
> Note: deadline is May 18 — v17a/v17b results are for post-deadline analysis or future IQC rounds.

### v16 Key Findings
- **No full passes** in 85 tested expressions
- **Best candidate:** `mdl177_garpanalystmodel_qgp_valuation` TOP3000 ts_zscore — Sharpe 1.30, Fitness **0.90** (⚠️ below 1.0), passed 6/7
- **Near-misses:** `qva_earnval` TOP200 (1.11/0.98), `qva_epmodule` TOP200 (1.03/0.91), `fangma_mam16` TOP200 (1.02/1.01 but LOW_SUB_UNIVERSE_SHARPE fail)
- **4 invalid fields found** — marked DEAD: `rau`, `si_ratio` (wrong prefix), `qma_earnxp`, `qga_eps_capex`
- **Families tested:** fangma_mam/emf/dvm, garpanalystmodel, valueanalystmodel siblings, valanalystmodel, earningsquality, liquidityrisk, growth — mostly weak IS metrics

---

## WQ Brain API — Confirmed Endpoints (Do Not Guess)

| Purpose | Endpoint | Parse Path |
|---------|----------|------------|
| Corr | `GET /alphas/{id}/check` | `data['is']['checks']` → `name=='SELF_CORRELATION'` → `.value` |
| Score | `GET /teams/{team_id}/alphas/{id}/before-and-after-performance` | `data['score']['before/after']` |
| Team ID | `GET /users/self/teams?status=ACTIVE&members.self.status=ACCEPTED&order=-dateCreated` | `results[0]['id']` |
| Alpha details | `GET /alphas/{id}` | `data['is']['sharpe/fitness/checks']` |

> ⚠️ Corr returns None until user opens the alpha page on platform UI

---

## Key Thresholds

| Metric | Submit | Borderline | Reject |
|--------|--------|------------|--------|
| IS Sharpe | ≥ 1.25 | 1.10–1.24 | < 1.10 |
| IS Fitness | ≥ 1.00 | 0.85–0.99 | < 0.85 |
| Turnover | 1–70% | — | > 70% or < 1% |
| Passed checks | ≥ 6/7 | — | < 6 |
| Max self-corr | < 0.70 | 0.60–0.69 | ≥ 0.70 |
| **Score change** | **> 0** | **+1 to +50** | **≤ 0** |

---

## Working Families

| Family | Fields | Notes |
|--------|--------|-------|
| `valueanalystmodel` | `qva_chgacc` 🔥 | Golden Alpha +643 flipped TOP200 |
| `fangma_vmm` | `fangma_vmm11` ✅ | npnMdNNz +396, 9q90GOld +639 TOP200 |
| `fangma_rvm` | `fangma_rvm6` ✅ | RRNLElmo TOP200 ts_zscore — submitted May 17 |
| `valanalystmodel` | `qva_incstmt` ✅, `qva_chgacc` ✅ | VA-1 +238, chgacc +278 score |
| `liquidityriskfactor` | `si_ratio` ✅ | +259 score |
| `earningsqualityfactor` | `uap` ✅ | +160 score |
| `sensitivityfactor400` | `pbroeresidual` ✅, `ttmocfev` ✅, `ney` ✅ | Various scores |
| `5shortsentimentfactor` | `days_to_cover` ✅ | E5qJ5qr0 corr 0.36 |
| `5yearrelativevaluefactor` | `rel5yfwdep` ✅, `rel5ybp` ✅ | +385, +238 |

---

## Dead Families — Truly Dead (Do Not Retest)

| Family | Reason |
|--------|--------|
| `industryrrelativevaluefactor` | ALL fitness < 1.00 across all fields |
| `globaldevnorthamerica` | Score -228 confirmed |
| `sensitivityfactor400_ney` | Negative score on all variants |
| `deepvaluefactor_curep` | Neg score -281, corr 0.99 |
| `deepvaluefactor_fcfp` | Neg score -206 |
| `garpanalystmodel_qgp_vfpriceratio` (mdl177_2 prefix) | Neg score -284, corr 0.99 |
| All D0 signals | Sharpe ≥ 2.0 cutoff — not viable |

---

## ⚠️ Important Rules

### Baseline ≠ Dead
**Never permanently mark a field dead based on standard baseline alone.**
Standard baseline = TOP3000, `-rank(ts_zscore(field,252))`, decay 6.

Before marking dead, also test:
1. **ts_zscore** instead of ts_rank (always try this first)
2. **TOP200 universe** — often cleaner corr and better score
3. **Flip:** `rank(ts_zscore(field,252))` — ONLY if IS Sharpe ≤ -1.0 after both ts_rank AND ts_zscore
4. If still failing all variants → then mark dead

### Never Guess Variable Names
**HARD RULE:** Never guess or construct variable names from memory. Always verify from:
- `fields_tracker.csv` — master list of 1,731+ confirmed field names
- `wq_alpha.db` — `SELECT field FROM fields WHERE field LIKE 'mdl177%'`
- WQ Brain Fields page on platform UI
Wrong names = silent failures or wrong field tested.

---

## Run Commands

```bash
# Run a batch
cp parameters_d1_vXX.py parameters.py && python3 main.py

# Run in background (recommended for long batches)
nohup python3 main.py > output.log 2>&1 &
tail -f output.log

# Run agent on CSV output
python3 agent.py data/d1vXX_YYYYMMDD_HHMMSS.csv

# Enter corr values manually
python3 agent.py --corr

# Reset agent state
python3 agent.py --reset
```

---

## Lessons Learned (Cumulative — Session 22 Additions)

46. **fangma_vmm11 TOP200** → +639. TOP200 consistently outperforms TOP3000 on score.
47. **Sign flip strategy** — only flip fields with IS Sharpe ≤ -1.0 AFTER both ts_rank and ts_zscore have been tried.
48. **FCF + working capital regime** — chgacc, si_ratio, uap, pbroeresidual all passing in current regime.
49. **Performance score API:** `/teams/{team_id}/alphas/{id}/before-and-after-performance`
50. **main.py auto-resume:** Timed-out sims retry after 30s automatically.
51. **industryrrelativevaluefactor ALL dead** — confirmed d1v10.
52. **globaldevnorthamerica confirmed dead** — score -228.
53. **Baseline-only failures ≠ dead** — reset to Backlog for flip/TOP200/zscore retry.
54. **rvm6 TOP200 ts_zscore** — Sharpe 1.47, Fitness 1.50, corr 0.45. Submitted May 17.
55. **3 concurrent simulations max** — WQ Brain platform limit. main.py uses max_workers=3.
56. **NEVER guess variable names** — always verify from fields_tracker.csv or wq_alpha.db. Wrong names = silent failures.
57. **v17a/v17b built** — full 417-field Model sweep split into two ~5hr batches. Built from wq_alpha.db untested fields query.
58. **Biometric auth** — log in via browser first, then start main.py immediately. Session persists for full batch run without re-auth.

59. **scrape_fields.py** — scrapes all fields from WQ Brain API, 7,750 total (1,612 mdl177). PAGE_SIZE=20, SLEEP_BETWEEN=3.0. Resume from offset: `python3 scrape_fields.py model77 400`.
60. **Full DB built** — wq_alpha.db now has 7,750 fields. Views: submittable (16), v_untested_fields (7,631), v_dead_fields (96+), v_in_use (20).
61. **agent.py flip threshold** — SHARPE_FLIP_MAX = -1.00. Only flip AFTER both ts_rank AND ts_zscore tried and both ≤ -1.0.
62. **v16 — no full passes** — 85 expressions tested. Best: garpanalystmodel_qgp_valuation (sharpe=1.30, fitness=0.90, passed=6). 4 invalid fields found (bad field IDs in scraper output).
63. **Invalid field IDs** — some fields in fields_tracker have IDs not recognized by the platform. These return "unknown variable" errors. Mark DEAD after first failure; don't retry.
64. **tune_garp_valuation** — built 8-expression tune file for best v16 candidate. Try TOP200 and ts_rank to push fitness over 1.0 threshold.

*Update this file at the end of every session.*
