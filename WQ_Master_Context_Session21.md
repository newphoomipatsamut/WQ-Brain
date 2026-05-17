# WorldQuant BRAIN — Master Context File
> **Researcher:** Nutcha | **Last Updated:** 17 May 2026 (Session 21) | **Session:** 21
> **Upload this file at the start of every Claude session.**

---

## Current Status

| Item | Value |
|------|-------|
| IQC 2026 Stage 1 D1 Score | **TBC** (update after each submission) |
| Alphas submitted (IQC Challenge) | 15+ active |
| Last batch | d1v14/15 complete. Flip batch found Golden Alpha +643 (chgacc TOP200). |
| Deadline | May 18, 2026 |
| Days Remaining | **1** |
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

## Submission Calendar — Session 21

> Deadline: **May 18** | 1 slot remaining (May 17)

| Day | Alpha | Score Δ | Universe | Link | Status |
|-----|-------|---------|----------|------|--------|
| ✅ May 9 | NEW-5b | +552 | TOP500 | https://platform.worldquantbrain.com/alpha/6XaA603p | ✅ Done |
| ✅ May 9/10 | VA-1 | +238 | TOP3000 | https://platform.worldquantbrain.com/alpha/mLroERYW | ✅ Done |
| ✅ May 10 | NEW-3b | +340 | TOP500 | https://platform.worldquantbrain.com/alpha/JjgPaA3A | ✅ Done |
| ✅ May 12 | ZY2OXdKQ 🆕 | +238 | TOP500 | https://platform.worldquantbrain.com/alpha/ZY2OXdKQ | ✅ Done |
| ✅ May 13 | npnMdNNz 🆕 | +396 | TOP3000 | https://platform.worldquantbrain.com/alpha/npnMdNNz | ✅ Done |
| ✅ May 14 | 9q90GOld 🔥 | +639 | TOP200 | https://platform.worldquantbrain.com/alpha/9q90GOld | ✅ Done |
| ✅ May 15 | e7nobL6O or better | TBC | TOP3000 | — | Check score |
| ✅ May 16 | chgacc Golden Alpha 🔥 | +643 | TOP200 | — | Check score |
| **May 17** | **RRNLElmo (rvm6)** | **TBC** | **TOP200** | https://platform.worldquantbrain.com/alpha/RRNLElmo | 🔥 Check score — Sharpe 1.47, Fitness 1.50, corr 0.45 |

> ⚠️ Still benched (last resort): T5K-2 (+67), RV-1b (+66), NEW-9b (+50), MPKN7bXr (+37)

---

## 🔥 Golden Alpha Finds — Session 21

| Alpha ID | Variable | Expression | Sharpe | Fitness | Corr | Score | Universe | Status |
|----------|----------|-----------|--------|---------|------|-------|----------|--------|
| chgacc flip | `mdl177_valueanalystmodel_qva_chgacc` | `rank(ts_rank(...,252))` (flipped) | TBC | TBC | 0.20 | **+643** | TOP200 | 🔥 Submit |
| RRNLElmo | `mdl177_fangma_rvm_usa_fangma_rvm6` | `-rank(ts_zscore(...,252))` | 1.47 | 1.50 | 0.45 | **TBC** | TOP200 | Check score |

---

## 🔑 Key Strategy Discoveries — Session 21

### 1. Sign Flip Strategy
- A field with **-1.46 Sharpe** on standard `-rank(ts_rank(...))` became **+643 score** when flipped to `rank(ts_rank(...))`
- **Rule:** Never permanently kill a field based on standard baseline alone. Retry with flip + TOP200.
- Fields to flip-test: any with IS Sharpe > 1.0 but wrong direction signal

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
| `fangma_rvm` | `fangma_rvm6` ✅ | RRNLElmo TOP200 ts_zscore — score TBC |
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

## ⚠️ Important Rule — Baseline ≠ Dead

**Never permanently mark a field dead based on standard baseline alone.**
Standard baseline = TOP3000, `-rank(ts_rank(field,252))`, decay 6.

Before marking dead, also test:
1. **Flip:** `rank(ts_rank(field,252))` — opposite sign
2. **TOP200 universe** — often cleaner corr and better score
3. **ts_zscore** instead of ts_rank
4. If still failing all variants → then mark dead

---

## Run Commands

```bash
# Run a batch
cp parameters_d1_vXX.py parameters.py && python3 main.py

# Run agent on CSV output
python3 agent.py data/d1vXX_YYYYMMDD_HHMMSS.csv

# Enter corr values manually
python3 agent.py --corr

# Reset agent state
python3 agent.py --reset
```

---

## Lessons Learned (Cumulative — Session 21 Additions)

46. **fangma_vmm11 TOP200** → +639. TOP200 consistently outperforms TOP3000 on score.
47. **Sign flip strategy** — -1.46 Sharpe field became +643 when flipped. Always test flip before marking dead.
48. **FCF + working capital regime** — chgacc, si_ratio, uap, pbroeresidual all passing in current regime.
49. **Performance score API:** `/teams/{team_id}/alphas/{id}/before-and-after-performance`
50. **main.py auto-resume:** Timed-out sims retry after 30s automatically.
51. **industryrrelativevaluefactor ALL dead** — confirmed d1v10.
52. **globaldevnorthamerica confirmed dead** — score -228.
53. **Baseline-only failures ≠ dead** — reset to Backlog for flip/TOP200/zscore retry.
54. **rvm6 TOP200 ts_zscore** — Sharpe 1.47, Fitness 1.50, corr 0.45. Strong alpha from "dead" family.
55. **3 concurrent simulations max** — WQ Brain platform limit. main.py uses max_workers=3.

*Update this file at the end of every session.*
