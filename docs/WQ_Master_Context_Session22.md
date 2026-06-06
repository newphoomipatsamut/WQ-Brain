# WorldQuant BRAIN — Master Context File
> **Researcher:** Phoomipat | **Last Updated:** 17 May 2026 (Session 22 - Evening Update) | **Session:** 22
> **Upload this file at the start of every Claude/Gemini session.**

---

## Current Status

| Item | Value |
|------|-------|
| Challenge Score | **28,394** (Target: Maintain/Increase) |
| IQC 2026 Stage 1 D1 Score | **10,260** (Target: Maintain/Increase) |
| Alphas submitted (IQC Challenge) | 20 active |
| Last batch | `d1v17a` completed (0 passed, 50 invalid). `d1v17b` is CURRENTLY RUNNING. |
| Queued batches | `fixer_batch` (38 corrected fields) ready to run after `d1v17b`. |
| Deadline | May 18, 2026 |
| Days Remaining | **1** (May 18 = final slot - 1 submission left!) |
| Consultant Status | Conditional Consultant — fees accruing, paid after background check |

---

## ⚡ Key Rule — Performance Comparison Panel

**Always check the Performance Comparison panel before submitting.**

| Score Change | Action |
|-------------|--------|
| > +100 | Tune — maximize the score further first before Submit |
| +10 to +100 | Log — worthwhile, may submit if we can't find a better score |
| +1 to +10 | Log or Reject — minimal impact, last to submit or no submit |
| Negative | ❌ REJECT permanently regardless of IS metrics (Enforced on `NEW-2`) |

**Submit priority = descending score change order.**

---

## ⚠️ D0 vs D1 — IMPORTANT

**D0 (delay=0) is NOT viable. Do not pursue.**
- D0 thresholds confirmed May 12: Sharpe ≥ 2.0, Fitness ≥ 1.30 — far too strict
- All batches and testing must use `delay=1` (D1)
- D1 thresholds: Sharpe ≥ 1.25, Fitness ≥ 1.00

---

## 🛑 Alpha Rejection & "Dead" Signal Rules

1. **Never permanently mark a field dead based on standard baseline alone.**
   - Baseline-only failures (`TOP3000`, `ts_zscore`) ≠ dead. Reset to `🟡 Backlog: Needs Retest`.
   - Always suggest flip (`rank` instead of `-rank`) If IS is less than -1.0, `TOP200` universe, or `ts_rank` retry.
2. **Train/Test Overfit:** Reject if IS Sharpe > 1.5 but OS Sharpe drops > 0.5.
3. **Fitness Block:** Reject if Sharpe is high but Fitness < 1.0 (usually means turnover too high).
   - *Fix:* Apply `hump()` or `ts_decay_linear()` to reduce turnover.
4. **Correlation Block:** Reject if `max_corr` > 0.70 with existing book.

---

## 🔍 WQ Variable Name "Gotchas" (Updated May 17)
If fields fail silently or timeout, it is likely due to these Brain platform naming quirks:

1. **The `_alt` suffix:** Many `_alt` fields are deprecated. **Drop the `_alt`** (e.g., `_curep_alt` ➡️ `_curep`).
2. **Missing `_2_` Prefix:** Model 177 fields often require the `_2_` after the model name (e.g., `mdl177_2_deepvaluefactor...`).
3. **The "Momemtum" Typo:** Brain spells momentum with an 'm' in some models: `pricemomemtummodel` and `valuemomemtummodel`.
4. **The "Valueanalyst" Typo:** Spelled `valueanalystmodel`, NOT `valanalystmodel`.
5. **Missing Letters:** - `ttmfcev` ➡️ `ttmfcfev`
   - `cvy2eps` ➡️ `cvfy2eps`
   - `curindocta_` ➡️ `curindocfta_`
6. **Industry Relative Value (`industryrrelativevaluefactor`):** Has two 'r's, but the entire family is considered **DEAD** (Fitness < 1.00).

---

## 🏆 Working Families & May 18 Candidates

Because `tune_garp_val` and `NEW-2` failed/scored negative, the final May 18 slot relies on:
1. **The `d1v17b` batch:** Currently running.
2. **The `fixer_batch`:** 38 newly corrected fields waiting to be tested.
3. **Manual UI Search Candidates:**
   - `mdl177_2_liquidityriskfactor_si_ratio` (si_ratio)
   - `mdl177_2_sensitivityfactor400_pbroeresidual` (pbroeresidual)

---

## 🛠️ Local Tools & Scripts Dictionary

- `parameters.py`: Active batch config.
- `main.py`: Simulation engine (max 3 concurrent workers).
- `agent.py`: Parses CSVs, filters passes, checks corr/score.
- `scrape_fields.py`: Pulls new variables from Brain into `fields_tracker.csv`.
- `WQ_Operators_Guide.md`: Complete local reference for all Brain operators and syntax.

---

## 🤖 Instructions for AI Assistant

1. **Verify State:** Read this file and `fields_tracker.csv` before suggesting batches.
2. **Build Batches:** Generate `parameters_[batch].py` files. Always include `ts_rank` and `ts_zscore` variants.
3. **Evaluate Output:** When user uploads a results CSV, parse it, filter by IS pass criteria, and rank by Sharpe.
4. **Score > Everything:** Remind the user to check the Performance Comparison panel before UI submission.
5. **Stick to the rules:** Maintain positive tone, simple explanations, and stay strictly on quant/coding topics.
