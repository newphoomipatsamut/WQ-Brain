# WorldQuant BRAIN — Master Context File
> **Researcher:** Nutcha | **Last Updated:** 13 May 2026 (Session 20) | **Session:** 20
> **Upload this file at the start of every Claude session.**

---

## Current Status

| Item | Value |
|------|-------|
| IQC 2026 Stage 1 D1 Score | **8,526** (after npnMdNNz, updated May 13) |
| Alphas submitted (IQC Challenge) | 15+ active |
| Agent | d1v10 complete (industryrrelativevaluefactor — all dead). d1v11 queued (~120 expr, ~180 min). |
| Deadline | May 18, 2026 |
| Days Remaining | **5** |
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

## Submission Calendar — Session 20

> Score baseline: **8,526** | Deadline: **May 18** | Remaining slots: **5** (May 13–17)

| Day | Alpha | Score Δ | Universe | Link | Status |
|-----|-------|---------|----------|------|--------|
| ✅ May 9 | NEW-5b | +552 | TOP500 | https://platform.worldquantbrain.com/alpha/6XaA603p | ✅ Done |
| ✅ May 9/10 | VA-1 | +238 | TOP3000 | https://platform.worldquantbrain.com/alpha/mLroERYW | ✅ Done |
| ✅ May 10 | NEW-3b | +340 | TOP500 | https://platform.worldquantbrain.com/alpha/JjgPaA3A | ✅ Done |
| ✅ May 12 | ZY2OXdKQ 🆕 | +238 | TOP500 | https://platform.worldquantbrain.com/alpha/ZY2OXdKQ | ✅ Done |
| ✅ May 13 | npnMdNNz 🆕 | +396 | TOP3000 | https://platform.worldquantbrain.com/alpha/npnMdNNz | ✅ Done |
| **May 14** | **9q90GOld 🔥** | **+639** | TOP200 | https://platform.worldquantbrain.com/alpha/9q90GOld | 🔥 BEST SCORE EVER — submit immediately |
| **May 15** | **e7nobL6O 🆕** | **TBC** | TOP3000 | https://platform.worldquantbrain.com/alpha/e7nobL6O | Check score on platform first |
| **May 16** | **E5qJ5qr0 🆕** | **TBC** | TOP3000 | https://platform.worldquantbrain.com/alpha/E5qJ5qr0 | Check score on platform first |
| **May 17** | **MPKN7bXr 🆕** | **+37** | TOP500 | https://platform.worldquantbrain.com/alpha/MPKN7bXr | Fallback — swap if d1v11 finds better |

> 🆕 = found by automated agent.py
> ⚠️ Still benched (last resort): T5K-2 (+67), RV-1b (+66), NEW-9b (+50), Alt-1 (+27), DV3b (+4)
> **Priority swap rule:** If d1v11 results find score > 66, swap into May 15–17 slots.
> **IMPORTANT:** Always check score on platform before submitting.

---

## New Agent Finds — Session 19/20 (d1v9 batch)

| Alpha ID | Variable | Sharpe | Fitness | Corr | Score | Universe | Status |
|----------|----------|--------|---------|------|-------|----------|--------|
| npnMdNNz | `mdl177_fangma_vmm_usa_fangma_vmm11` ts_zscore | 1.65 | 1.17 | 0.5772 | **+396** | TOP3000 | ✅ Submitted May 13 |
| **9q90GOld** | **`mdl177_fangma_vmm_usa_fangma_vmm11` ts_rank** | **1.40** | **1.19** | **0.2451** | **🔥 +639** | **TOP200** | **✅ Submit May 14** |
| e7nobL6O | `mdl177_fangma_vmm_usa_fangma_vmm11` ts_rank | 1.68 | 1.18 | 0.5423 | TBC | TOP3000 | ✅ Submit May 15 |
| E5qJ5qr0 | `mdl177_5shortsentimentfactor_days_to_cover` ts_rank | 1.70 | 1.00 | 0.3589 | TBC | TOP3000 | ✅ Submit May 16 |

---

## Session 20 — d1v11 Batch Plan

**Run:** `cp parameters_d1_v11.py parameters.py && python3 main.py`
**~120 expressions, ~180 min runtime**

| Priority | Family | Fields | Why |
|----------|--------|--------|-----|
| 🔥 1 | `fangma` siblings | gpam (11/10/5), rvm (6/1), mam (16/11/6/5), emf (25/20/15/4), dvm (4/1) | vmm11 gave +396/+639 — siblings untested |
| 2 | `valanalystmodel` siblings | qva_fwdep/bp/revs/divy/epssurp/valuation | VA-1 qva_incstmt +238 — siblings untested |
| 3 | `valueanalystmodel` | qva_incstmt/finstmt/epmodule/pegy/earnval | DIFFERENT model from valanalystmodel — untested |
| 4 | `vma2` siblings | vma2_ma/ma_ee/ma_em/ma_pm | VMA-2 vma2_va +66 — siblings untested |
| 5 | `5yearrelativevaluefactor` siblings | rel5yep/ocfp/fcfp/sp/coreepsp | rel5yfwdep +385, rel5ybp +238 — more untested |
| 6 | `earningmomentumfactor400` | rev6/numrevy1/numrevq1/epsrm/fqsurs_std/salesurp/stockrating/y1aepsg/cvfy1eps/fcfroey1p | Completely fresh analyst momentum family |

---

## Dead Confirmed (Session 19/20)

| Family | Reason |
|--------|--------|
| `industryrrelativevaluefactor` | ALL fields fitness < 1.00 — dead (d1v10 confirmed) |
| `globaldevnorthamerica` | Score -228 (gJmzoEWM) — dead regardless of IS metrics |

---

## Session 19/20 — Key Technical Work

### main.py — Auto-Resume Fix
- **Bug:** Timed-out simulations were silently added to `rows_processed` → never retried
- **Fix:** Timed-out sims go to `self._timed_out`, returned for retry. While loop retries with 30s delay.
- **Logging:** Cleaned up — ▶/⏳/✔ symbols, progress % only on change, no thread names

### agent.py — Performance Score Added
- **Endpoint:** `GET /teams/{team_id}/alphas/{id}/before-and-after-performance`
- **Parse:** `data['score']['before']` and `data['score']['after']`
- **team_id:** Fetched via `GET /users/self/teams?status=ACTIVE&...` → `results[0]['id']`
- **Throttle wait removed** from corr check — now retries=3, wait=3.0, no throttle handling
- **Negative score logic:** Alphas with score < 0 are permanently rejected (not counted as submittable)
- **Note:** `/alphas/{id}` has `competitions: null` — wrong endpoint, don't use for score

### Batches This Session
| Batch | Status | Results |
|-------|--------|---------|
| d1v9 (fangma_vmm + globaldev) | ✅ Complete | 3 submittables found |
| d1v9b (5shortsentimentfactor) | ✅ Complete | 1 submittable (days_to_cover), 2 dead |
| tune_d1v9 (vmm11 variants) | ✅ Complete | npnMdNNz + e7nobL6O confirmed best |
| d1v10 (industryrrelativevaluefactor) | ✅ Complete | ALL dead — fitness < 1.00 across all fields |
| **d1v11** | 🔄 **Queued** | ~120 expr — fangma siblings + 5 other families |

---

## WQ Brain API — Confirmed Endpoints (Do Not Guess)

| Purpose | Endpoint | Parse Path |
|---------|----------|------------|
| Corr | `GET /alphas/{id}/check` | `data['is']['checks']` → `name=='SELF_CORRELATION'` → `.value` |
| Score | `GET /teams/{team_id}/alphas/{id}/before-and-after-performance` | `data['score']['before/after']` |
| Team ID | `GET /users/self/teams?status=ACTIVE&members.self.status=ACCEPTED&order=-dateCreated` | `results[0]['id']` |
| Alpha details | `GET /alphas/{id}` | `data['is']['sharpe/fitness/checks']` |

> ⚠️ Corr returns None until user opens the alpha page on platform UI — enter manually via `python3 agent.py --corr`

---

## Active Alphas (15+ Currently ACTIVE)

| Name | Submitted | Universe | Notes |
|------|-----------|----------|-------|
| REL5-2 | May 11 | TOP500 | Active |
| ZY2OXdKQ (rel5ybp) | May 12 | TOP500 | Agent find +238 |
| VA-1 | May 10 | TOP3000 | +238 submitted |
| New-3b | May 10 | TOP500 | Active |
| New-5b | May 9 | TOP500 | Active |
| Submit New-2 #1 | May 8 | TOP500 | Active |
| Submit dv5 | May 7 | TOP3000 | Active |
| Submit Dv2c | May 6 | TOP3000 | Active |
| Submit m10 (5yr relative value naked) | May 5 | TOP3000 | Active |
| Submit M15b | May 5 | TOP3000 | Active |
| Submit M11 | May 4 | TOP3000 | Active |
| M6 ts_rank(ttmocfev) | May 3 | TOP3000 | Active |
| MC3 ts_rank(252) | May 3 | TOP3000 | Sharpe 1.89, Fitness 1.66 |
| Alpha 10 Current Ratio | May 2 | TOP3000 | Active |
| Alpha 9 1-day reversal × volume | Apr 30 | TOP3000 | Sharpe 2.01, Fitness 1.00 |

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

## Variable Name Gotchas

| Wrong | Correct | Context |
|-------|---------|---------|
| `ttmfcev` | `ttmfcfev` | deepvaluefactor TTM FCF/EV |
| `industryrelativevaluefactor` | `industryrrelativevaluefactor` | Double-r in dataset name |
| `curindocta_` | `curindocfta_` | Added f |
| `curindoctp_` | `curindocfp_` | Added f, dropped t |

---

## Working Families

| Family | Fields | Notes |
|--------|--------|-------|
| `fangma_vmm` | `fangma_vmm11` ✅ | npnMdNNz +396 (TOP3000), 9q90GOld +639 (TOP200). Siblings in v11. |
| `5shortsentimentfactor` | `days_to_cover` ✅ | E5qJ5qr0 corr 0.36 clean. onloan_conc + sht_int dead. |
| `valanalystmodel` | `qva_incstmt` ✅ | VA-1 +238. Siblings (fwdep/bp/revs/divy/epssurp/valuation) in v11. |
| `vma2` | `vma2_va` ✅ | VMA-2 +66. Siblings (ma/ma_ee/ma_em/ma_pm) in v11. |
| `relativevaluemodel` | `ttmfcfp` ✅ (momentum only) | RV-1b +66, T5K-2 +67 |
| `5yearrelativevaluefactor` | `rel5yfwdep` ✅, `rel5ybp` ✅ | Best +385 (NEW-2), +238 (ZY2OXdKQ). More siblings in v11. |
| `deepvaluefactor` | `pdy` ✅ | MPKN7bXr TOP500 +37 |
| `sensitivityfactor400` | `ttmocfev`, `ney` ✅ | TOP500 variants working |

---

## Dead Families — Do Not Retest

| Family | Reason |
|--------|--------|
| `industryrrelativevaluefactor` | ALL fitness < 1.00 — d1v10 confirmed dead |
| `globaldevnorthamerica` | Score -228 — dead regardless of IS metrics |
| `5shortsentimentfactor_onloan_conc` | Negative sharpe — dead |
| `5shortsentimentfactor_sht_int` | Sharpe 0.54 — dead |
| `sensitivityfactor400` siblings | All IS < 1.0 except ttmocfev/ney |
| `managementqualityfactor` (most) | All IS < 1.0 except indrelcroe_ (near-miss) |
| `surpriseanalystmodel` | Dead |
| `historicalgrowthfactor` | Dead |
| All D0 signals | Sharpe ≥ 2.0 cutoff — not viable |

---

## Pending Actions (Session 20)

1. **Submit 9q90GOld on May 14** — +639 best score ever. Do not miss this slot.
2. **Check score on platform for e7nobL6O** before May 15 submission
3. **Check score on platform for E5qJ5qr0** before May 16 submission
4. **Run d1v11** — `cp parameters_d1_v11.py parameters.py && python3 main.py`
5. **Run agent.py on d1v11 CSV** when done — check corr + generate tune file
6. **Swap May 15–17 slots** if d1v11 finds anything with score > 66

---

## Run Commands

```bash
# Run d1v11 batch
cp parameters_d1_v11.py parameters.py && python3 main.py

# Run agent on a specific CSV
python3 agent.py data/d1v11_YYYYMMDD_HHMMSS.csv

# Enter corr values manually
python3 agent.py --corr

# Reset agent state
python3 agent.py --reset
```

---

## Lessons Learned (Cumulative — Session 20 Additions)

46. **fangma_vmm11 is a strong signal** — ts_zscore (npnMdNNz) scores +396, ts_rank TOP200 (9q90GOld) scores +639
47. **5shortsentimentfactor family has mixed results** — days_to_cover works, onloan_conc and sht_int dead
48. **Performance score API:** Use `/teams/{team_id}/alphas/{id}/before-and-after-performance`, parse `data['score']['before/after']`. NOT `/alphas/{id}` (competitions field is null).
49. **main.py auto-resume:** Timed-out sims now retry automatically — while loop with 30s delay between attempts
50. **industryrrelativevaluefactor:** Double-r in name. Fixed field spellings: curindocfta_, curindocfp_ (not curindocta_, curindoctp_). ALL fitness < 1.00 — entire family dead.
51. **globaldevnorthamerica confirmed dead** — score -228. IS metrics don't matter if score is negative.
52. **agent.py negative score filter:** Alphas with score < 0 now permanently rejected — not counted as submittable.
53. **TOP200 universe is powerful** — 9q90GOld (vmm11 ts_rank TOP200) scored +639 vs +396 for TOP3000. Always test TOP200 for top candidates.

*Update this file at the end of every session.*
