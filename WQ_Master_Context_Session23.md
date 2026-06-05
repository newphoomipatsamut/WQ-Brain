# WorldQuant BRAIN — Master Context File
> **Researcher:** Phoomipat | **Last Updated:** 04 Jun 2026 (Session 25) | **Session:** 25
> ⚠️ **SUPERSEDED — Use WQ_Master_Context_Session25.md instead.**

---

## Current Status

| Item | Value |
|------|-------|
| Challenge Score | **28,394** |
| IQC 2026 Stage 1 D1 Score | **10,260** |
| Alphas Submitted (Active) | **19** (one dropped post-deadline) |
| IQC 2026 Stage 1 Deadline | **May 18, 2026 ✅ PASSED** |
| Competition Phase | **Post-IQC — Next competition prep** |
| Running on | Terminal (local machine) |
| Concurrent Workers | **10** (changed Session 24) |

---

## ⚡ Key Rule — Performance Comparison Panel

**Always check the Performance Comparison panel before submitting.**

| Score Change | Action |
|-------------|--------|
| > +100 | Tune — maximize further before Submit |
| +10 to +100 | Log — worthwhile, submit if no better option |
| +1 to +10 | Log or Reject — minimal impact |
| Negative | ❌ REJECT permanently regardless of IS metrics |

**Submit priority = descending score change order.**

---

## ⚠️ D0 vs D1 — IMPORTANT

**D0 (delay=0) is NOT viable. Do not pursue.**
- D0 thresholds: Sharpe ≥ 2.0, Fitness ≥ 1.30 — far too strict
- All batches use `delay=1` (D1)
- D1 thresholds: Sharpe ≥ 1.25, Fitness ≥ 1.00, Checks ≥ 6/7, Turnover 1–70%, Self-corr < 0.70

---

## 🛑 Alpha Rejection & Signal Rules

1. **Never mark dead from baseline alone** — always flip sign + TOP200 retest first.
2. **Fitness Block fix:** Apply `hump()` or `ts_decay_linear()` to reduce turnover.
3. **Correlation Block:** Reject if max_corr > 0.70.
4. **Neutralization:** WQ Brain tip (May 2026) — tried MARKET and INDUSTRY on all near-misses.
   - Result: **neutralization change did NOT help CLV family** — turnover stayed at ~36% regardless.
   - CLV turnover is structural (driven by the expression itself), not neutralization-dependent.
   - MARKET neut still worth trying for other families with genuinely high-TO residuals.

---

## 🔍 WQ Variable Name "Gotchas" (Updated Session 23)

1. **`_alt` suffix:** Often deprecated — try without `_alt` first.
2. **Missing `_2_` prefix:** Many Model 177 fields need `_2_` (e.g., `mdl177_2_deepvaluefactor...`).
3. **"Momemtum" typo:** WQ spells it `pricemomemtummodel` and `earningsmomemtummodel` (double-m).
4. **"Valueanalyst" naming:** `valueanalystmodel` not `valanalystmodel`.
5. **`adv20` is a precomputed field:** Use `adv20`, NOT `adv(20)`.
6. **`industryrrelativevaluefactor`:** Double-r — AND the whole family is confirmed dead (Fitness < 1.00).
7. **Not in subscription:** `rau`, `cllev`, `investto_alt`, `curindocta_`, `curindoctp_` — these exist in tracker but WQ returns "unknown variable".
8. **`niroe` is in growthanalystmodel:** Use `mdl177_2_growthanalystmodel_qga_niroe`, not managementqualityfactor.

---

## 📊 Field Database Status (as of Session 23 — Evening)

| Status | Count |
|--------|-------|
| Untested (blank) | 7,548 (+137 model53) |
| 🟡 Tested: Baseline Failed | 159 (+6 deepvalue) |
| ❌ Abandoned | 104 (+7 deepvalue dead) |
| ❌ Dead | 29 |
| ✅ In Use | 19 |
| 🟡 Backlog: Needs Retest | 0 (pdy_alt → Abandoned) |
| ⚪ Backlog | 2 |
| 🟠 Test Soon | 1 |
| **Total** | **7,850** |

---

## 🏆 Session 24 — Batches Run & Key Findings

### Batches Completed
| Batch | Expressions | Passes | Submittable | Best Result |
|-------|-------------|--------|-------------|-------------|
| `miner_clv_fix` | 6 | 0 | 0 | CLV TOP3000 sharpe=2.20 fit=0.96 |
| `all_batches_v1` | 119 | 0 | 0 | CLV decay5 sharpe=1.82 fit=0.96 |
| `all_batches_v2` | 108 | 0 | 0 | CLV×vol/adv decay5 sharpe=1.82 fit=0.97 |
| `neut_sweep` | 46 | 0 | 0 | CLV decay5 MARKET TOP3000 sharpe=1.71 fit=0.95 |
| `deepvalue_sweep` | 48 | 5 | **0** | ttmocfp decay×mom sharpe=1.85 fit=1.41 corr=0.84 ❌ |
| `cleanup_round2` | 35 | 0 | 0 | CLV fit ceiling ~0.91, ADV20 fit ceiling ~0.91 — both abandoned |
| `mdl53_nearmiss` | 29 | 1 | **0** | jc5 inversion sharpe=1.40 fit=1.03 7/7 BUT score=-191 ❌ |
| `iv_sweep` | 44 | 0 | 0 | All IV families dead: levels neg Sharpe, decay×mom ~0.60 fitness ~0.28 |
| `llm_fundamental_r1` | 160 | 2 | **2** | acquired_intangible_avg_useful_life TOP200 sharpe=1.33 fit=1.38 +1007 ✅ |
| `intangible_tune` | 40 | 0 | 0 | decay×mom TOP500 6/7 fit=0.88 near-miss (TO=22%) |
| `llm_analyst_r1` | 68 | 0 | 0 | actual_dividend_value_quarterly promising; anl4_* event fields killed batch |

### Session 24 — deepvalue_sweep Finding
- **5 IS passes, 0 submittable** — all rejected on Performance Comparison panel (corr > 0.70 or negative score).
- `ttmocfp` and `ttmfcfev` have strong IS stats but are **too correlated with existing book** (0.66–0.90).
- Both fields are tapped out — do not retest.
- `pdy_alt` **permanently Abandoned** — persistent near-miss across 10+ expressions, fitness ceiling ~0.99 but checks always fail.
- New near-misses for `cleanup_round2`: `ttmfcfev` ts_rank (sharpe=1.39, fit=0.88), `ttmpiqp` decay (sharpe=1.37, fit=0.88), `bp` decay (sharpe=1.36, fit=0.88).

### Session 24 — New Tools Built
| Tool | Purpose |
|------|---------|
| `llm_alpha_generator.py` | Gemini 3.5 Flash alpha expression generator. Pulls untested fields, generates ready-to-run batch files. |
| `--dataset model53` mode | Specialized prompt for model53 credit risk dataset with curve steepness/inversion/acceleration ideas. |

### Session 24 — New Dataset Added
- **model53** (Creditworthiness Risk) — 137 fields merged into tracker.
  - 41 `mdl53_*` fields: priority targets (jc5, jc6, jm5, ms5 × 10 horizons). High existing alpha count (250–1,855).
  - 96 raw/probability fields: `annualized_pd_*`, `probability_rating_*` etc. — 0 existing alphas, test later.
  - Run: `python3 llm_alpha_generator.py --api-key KEY --dataset model53 --category "Model - Credit Risk"`

### Near-Misses (all active, verified)

⚠️ **All prior near-misses abandoned after cleanup_round2 (fitness ceiling confirmed structural). No active near-misses.**

### Confirmed Dead Families (cumulative)
- **devNorthAmerica short sentiment** — days_to_cover, benchmark_fee, act_util, conc_ratio. All dead for USA.
- **industryrrelativevaluefactor** — confirmed dead, Fitness < 1.00 across all variants.
- **5yr RelValue (rel5yocfp, rel5yebitdap, rel5ycfp)** — fitness ceiling ~0.39–0.58.
- **adverint, fc_rev3y2_alt, navp_alt, indrelrtn5d_, niroe** — sharpe < 0.50.
- **mdl177_2_deepvaluefactor ttmocfp, ttmfcfev** — passes IS but corr > 0.70, tapped out.
- **mdl177_deepvaluefactor_pdy_alt** — permanently abandoned after 10+ attempts.
- **CLV family (all variants)** — fitness ceiling ~0.91–0.97. Structural high-TO, neutralization doesn't help. Abandoned.
- **ADV20 reversion** — fitness ceiling ~0.91, turnover structurally 71%+. Abandoned.
- **model53 credit curve (jc5/jc6/jm5 spreads)** — 1 IS pass but score=-191, book correlation issue. Tapped out.
- **Implied Volatility (ALL families)** — iv_call, iv_mean, iv_mean_skew, iv term structure, iv RoC. All dead for USA. Best Sharpe ~0.60, nowhere near threshold.
- **anl4_* event fields** — 928 fields. anl4_ady_*, anl4_*detail*, anl4_adxq* confirmed event-type. All operators fail. Only confirmed working exception: anl4_adjusted_netincome_ft.

---

## 🗂️ Local Tools & Scripts

| File | Purpose |
|------|---------|
| `parameters.py` | Active batch config (copy target file here to run) |
| `main.py` | Simulation engine (max_workers=10) |
| `alpha_miner.py` | Parameter sweep generator — takes any expression and outputs batch file |
| `parameters_deepvalue_sweep.py` | ✅ Done — 48 expressions, 5 IS passes, 0 submittable (corr > 0.70) |
| `parameters_neut_sweep.py` | ✅ Done — MARKET+INDUSTRY neut on all near-misses (0 passes) |
| `parameters_cleanup_round2.py` | ✅ Done — 35 expressions, 0 passes, CLV/ADV20/DeepValue all abandoned |
| `llm_alpha_generator.py` | LLM batch generator — Gemini 3.5 Flash. Reads knowledge bases, filters event/categorical fields, auto-adds TOP200 pairs. |
| `orchestrator.py` | **Fully automated research loop.** Generates → runs → analyzes → tunes → notifies. Run overnight. |
| `notify.py` | LINE Messaging API + macOS notifications. Alerts on biometric auth, passes found, waiting for input. |
| `wq_alpha.db` | SQLite field database (7,850 fields) |
| `fields_tracker.csv` | CSV mirror of DB (updated Session 24 — model53 added) |
| `IQC2026_Final_Results_Summary.md` | Full IQC2026 results |
| `Next_Competition_Strategy.md` | Phase 1/2/3 plan for next competition |

---

## 📋 What's Next (Priority Order)

### Immediate — Session 25 Queue

1. **Run orchestrator overnight** ← NEXT — fully automated from here
   ```bash
   python3 orchestrator.py --api-key YOUR_GEMINI_KEY
   ```
   Covers: Fundamental → Analyst → Model → Model-Analyst → ...
   Notifies via LINE when passes found or auth needed.

2. **Submit mLXLPa35** — acquired_intangible_avg_useful_life TOP200, score=+1007, corr=0.153
   - Check self-corr with 78d8kP1Q before submitting both

3. **Former next (now handled by orchestrator):**
   - Run `llm_alpha_generator.py` on high-alpha-count categories (e.g., Fundamental, Analyst, Growth)
   - These have thousands of untested fields — highest probability of finding new signals
   - Command: `python3 llm_alpha_generator.py --api-key KEY --category "Fundamental" --count 40`

2. **GARP variants** — `valuation`, `qgp_*` fields
   - Run LLM generator or manual sweep on growth-at-reasonable-price metrics

3. **Price Momentum** — selective, TOP200 only
   - `pricemomemtummodel` fields (note double-m typo)
   - TOP200 universe to minimize book correlation

4. **model53 raw/probability fields** — `annualized_pd_*`, `probability_rating_*`
   - Currently 0 existing alphas — completely fresh territory
   - Use LLM generator: `--dataset model53 --category "Credit Risk - Raw"`

---

## 🔑 Key Principles (Carried Forward)

1. **Score change > everything.** Check Performance Comparison panel always.
2. **TOP200 for self-corr bypass.** Consistently gives lowest max_corr.
3. **Fitness fix = `hump()` or `ts_decay_linear()`.** Fitness block → apply one of these.
4. **Neutralization only helps if turnover is neutralization-driven.** CLV family proved neut change does nothing — turnover is structural.
5. **Never mark dead from baseline alone.** Flip + TOP200 required first.
6. **D1 only.** All batches use `delay=1`.
7. **10 concurrent workers.** `max_workers=10` in `main.py` (changed Session 24).
8. **Run on Terminal (local).** Use `cp parameters_X.py parameters.py && python3 main.py`.
