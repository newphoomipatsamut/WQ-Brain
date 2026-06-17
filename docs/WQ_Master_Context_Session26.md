# WorldQuant BRAIN — Master Context File
> **Researcher:** Phoomipat | **Last Updated:** 15 Jun 2026 (Session 26) | **Session:** 26
> **Upload this file at the start of every Claude/Gemini session.**

---

## Current Status

| Item | Value |
|------|-------|
| Challenge Score | **28,394** |
| IQC 2026 Stage 1 D1 Score | **10,260** |
| Alphas Submitted (Active) | **21** (no new submissions this session) |
| Competition Phase | **Post-IQC — Next competition prep** |
| Running on | Terminal (local machine) |
| Concurrent Workers | **8** (consultant account; set via `export WQ_CONCURRENCY=8`) |
| Automation | **orchestrator.py** — stopped at batch 46 (session expired), needs restart |

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

> **Note:** Performance Comparison score is only available AFTER submission (`"os"` field is null pre-submission). The orchestrator cannot auto-fetch this — manual check required.

---

## ⚠️ D0 vs D1 — IMPORTANT

**D0 (delay=0) is NOT viable. Do not pursue.**
- D0 thresholds: Sharpe ≥ 2.0, Fitness ≥ 1.30 — far too strict
- All batches use `delay=1` (D1)
- D1 thresholds: Sharpe ≥ 1.25, Fitness ≥ 1.00, Checks ≥ 6/7, Turnover 1–70%, Self-corr < 0.70

---

## 🛑 Alpha Rejection & Signal Rules

1. **Never mark dead from baseline alone** — always flip sign + TOP200 retest first.
2. **Fitness Block fix:** Heavier `ts_decay_linear()` (decay=30/40/60) or `hump()`.
3. **Correlation Block:** Reject if self-corr ≥ 0.70 OR Performance Comparison score negative.
4. **Neutralization:** MARKET neut worth trying for high-TO signals only.
5. **Score > +100 → Tune before submitting.**
6. **Negative sharpe/fitness = valid pass** — `-rank(expr)` with sharpe=-1.5 is identical to `rank(expr)` with sharpe=+1.5. The orchestrator now auto-detects and sign-flips these. Do not manually reject based on negative metrics.

---

## 🚫 Banned Operators (hardcoded — expressions dropped before simulation)

```python
BANNED_OPS = ('ts_decay_linear', 'ts_delta(close')
```

| Operator | Reason |
|----------|--------|
| `ts_decay_linear` | Correlated with Alpha 10 — score change always negative |
| `ts_delta(close` | `rank(ts_delta(close, N))` momentum leg correlated with Alpha 9 — all expressions using this pattern fail self-corr |

**Also banned from Gemini template recommendations:**
- `ts_rank_confirm` — always uses `rank(ts_delta(close, N))` as momentum leg → correlated with Alpha 9
- `ts_rank_confirm_med` — same reason

> ⚠️ **`parameters_bvps_tune.py` near-miss is NOW DEAD** — the expression `rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5)))` uses the banned `ts_delta(close` pattern. It will be dropped automatically. Do not run this batch.

---

## 🔍 WQ Variable Name "Gotchas"

1. **`_alt` suffix:** Often deprecated — try without `_alt` first.
2. **Missing `_2_` prefix:** Many Model 177 fields need `_2_` (e.g., `mdl177_2_deepvaluefactor...`).
3. **"Momemtum" typo:** WQ spells it `pricemomemtummodel` and `earningsmomemtummodel` (double-m).
4. **`adv20` is precomputed:** Use `adv20`, NOT `adv(20)`.
5. **`industryrrelativevaluefactor`:** Double-r — AND confirmed dead.
6. **Not in subscription:** `rau`, `cllev`, `investto_alt`, `curindocta_`, `curindoctp_`.
7. **`anl4_*` EVENT fields:** `anl4_ady_*`, `anl4_*detail*`, `anl4_adxq*` — ALL operators fail. Generator auto-filters. Only working exception: `anl4_adjusted_netincome_ft`.
8. **Categorical/string fields:** Fields ending in `_currency`, `_currency_code`, `_country_code` etc. — generator auto-filters.
9. **`signal_strength` column:** Numeric Sharpe only.

---

## 📊 Field Database Status (Session 26)

| Status | Count |
|--------|-------|
| Untested (blank) | **~6,593** (Fundamental: ~1,571 untested) |
| 🟡 Tested: Baseline Failed | 177 |
| ❌ Abandoned | 97 |
| ❌ Dead | 957 (incl. 928 anl4_* event fields) |
| ✅ In Use | **21** |
| 🟠 Test Soon | 3 |
| ⚪ Backlog | 2 |
| **Total** | **7,850** |

**Tracker columns:** `category, field, status, signal_strength, dataset, description, notes, abandon_reason`
**abandon_reason values:** `neg_sharpe`, `low_sharpe`, `corr_block`, `neg_fitness`, `fitness_ceiling`, `event_type`

---

## ⛔ Corr-Failed Fields (cannot be submitted — corr ≥ 0.70 with book)

| Field | Corr Score | Notes |
|-------|-----------|-------|
| `actual_return_on_pension_plan_assets / cap` | 0.75–0.84 | All 4 sign-flip variants failed; field exhausted |

Tracked automatically in `corr_failed_fields.json`. Updated by orchestrator on each corr-fail.

---

## 🏆 Session 26 — Results

### New Automation Features Added

| Feature | Description |
|---------|-------------|
| **Biometric auto-poll** | Polls `POST /persona` every 10s; auto-continues when phone auth complete. No Enter needed. |
| **Negative pass detection** | `abs(sharpe) >= 1.25 and abs(fitness) >= 1.0` — negative metrics treated as pass |
| **Auto corr check** | After each IS pass, polls `GET /alphas/{id}/check` every 15s up to 6 min until `result != 'PENDING'` |
| **Auto grade fetch** | Reads `grade` field from `GET /alphas/{id}` — INFERIOR/AVERAGE/GOOD/EXCELLENT |
| **`--check-passes CSV`** | Re-run corr+grade check on any existing results CSV |
| **Sign-flip** | Detects `-rank(...)` passes, flips to `rank(...)`, re-simulates automatically |
| **Auto knowledge base** | `knowledge bases/auto_findings.md` regenerated after every batch; auto-fed into Gemini |
| **Corr-fail tracking** | `corr_failed_fields.json` — persists fields that fail self-corr across sessions |

### Session 26 Batch Results

| Batch | Passes | Submitted | Notes |
|-------|--------|-----------|-------|
| Sign-flip (actual_return_on_pension_plan_assets / cap) | 4 | 0 | All passed IS (sharpe 1.73–2.05) but failed self-corr (0.75–0.84) |
| Orchestrator batches 1–46 | Unknown | 0 | Session expired at batch 46 — 0/80 completed per batch |

### Corr-Failed This Session
- `actual_return_on_pension_plan_assets / cap` — 4 expressions, all corr 0.75–0.84. Field exhausted.

### No New Submissions
Session was primarily infrastructure/automation improvements. Orchestrator needs restart to resume.

### Confirmed Dead Families (all sessions)
- **devNorthAmerica short sentiment** — days_to_cover, benchmark_fee, act_util, conc_ratio.
- **industryrrelativevaluefactor** — Fitness < 1.00.
- **5yr RelValue** — rel5yocfp, rel5yebitdap, rel5ycfp, rel5yfwdep. Ceiling 0.39–0.58.
- **mdl177_2_deepvaluefactor ttmocfp, ttmfcfev** — corr > 0.70, tapped out.
- **mdl177_deepvaluefactor_pdy_alt** — permanently abandoned.
- **CLV family** — structural fitness ceiling ~0.91–0.97.
- **ADV20 reversion** — structural TO 71%+, fitness ceiling ~0.91.
- **model53 credit curve spreads** — corr_block, score=-191.
- **Implied Volatility (ALL families)** — dead for USA.
- **anl4_* event sub-families** — anl4_ady_*, anl4_*detail*, anl4_adxq* (358 fields).
- **snt_*, scl12_* sentiment** — all dead.
- **pcr_vol_*** — no signal.
- **Options - Analytics / Volatility categories** — skip entirely.
- **book_value_per_share_min_guidance_qtr (bvps near-miss)** — expression used banned `ts_delta(close` — permanently dead.

---

## 🗂️ Local Tools & Scripts

| File | Purpose |
|------|---------|
| `orchestrator.py` | **⭐ MAIN TOOL** — Generates → simulates → corr/grade checks → sign-flip → auto KB update. |
| `main.py` | Simulation engine. max_workers via `WQ_CONCURRENCY` env (default 3, set to 8 for consultant). |
| `llm_alpha_generator.py` | LLM batch generator. Loads all `.md` files from `knowledge bases/` into Gemini system prompt. |
| `template_rl.py` | RL tracker. Learns which (template × frequency) combos work. Check: `python3 template_rl.py` |
| `update_tracker.py` | Updates fields_tracker.csv from a results CSV. Run: `python3 update_tracker.py data/batch.csv` |
| `notify.py` | LINE Messaging API + macOS notifications. |
| `fields_tracker.csv` | 7,850 fields with status, signal_strength, abandon_reason. |
| `template_performance.json` | RL data — (template × frequency) stats. Grows smarter each batch. |
| `corr_failed_fields.json` | Auto-populated list of fields that failed self-corr. Fed into auto KB. |
| `knowledge bases/auto_findings.md` | Auto-generated after each batch. Do NOT manually edit — overwritten every batch. |
| `passes_to_review.txt` | Orchestrator logs passes here. Check each morning. |
| `orchestrator_log.txt` | Full orchestrator session log. |

---

## 🤖 Automation Setup

**Human intervention only needed for:**
1. **Biometric auth** — LINE notification sent. Complete on phone. Script polls `POST /persona` every 10s, auto-continues. No Enter needed.
2. **Performance Comparison panel** — LINE notification on pass. Check score manually (can't auto-fetch pre-submission). Orchestrator auto-continues after 30 min if no input.
3. **Alpha submission** — Manual click after verifying score is positive.

### Running

```bash
# Full loop (Fundamental → Analyst → Model → ...)
python3 orchestrator.py

# Resume after session expired (restart — re-authenticates automatically)
python3 orchestrator.py

# Re-run corr+grade on an existing results CSV
python3 orchestrator.py --check-passes data/batch_name.csv

# Combine best expressions from different field families
python3 orchestrator.py --combine

# Re-tune near-misses
python3 orchestrator.py --retune

# Check RL leaderboard
python3 template_rl.py
```

### credentials.json
```json
{
  "email": "...",
  "password": "...",
  "line_channel_token": "YOUR_CHANNEL_ACCESS_TOKEN",
  "line_user_id": "Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

### Category priority order
Fundamental → Analyst → Model → Model-Analyst → Model-Fundamental Scores → Price Volume → Model-Systematic Risk → Sentiment/Analyst → Credit Risk families
*(Options + Social Media skipped — IV and snt confirmed dead)*

---

## 🧠 LLM Generator — What Gemini Knows

Templates injected into system prompt (active — ts_rank_confirm REMOVED):
- **Basic (A-E):** ts_rank(252), decay×momentum, hump, ts_zscore, ts_rank(63)
- **Advanced (F-K):** ts_std_dev, ts_corr, ts_regression(rettype=2), group_rank/group_zscore, ts_backfill+winsorize, multi-stage composition
- ~~ts_rank_confirm~~ — BANNED (rank(ts_delta(close,N)) correlated with Alpha 9)

Per-field context injected:
- **Frequency hint** (DAILY/WEEKLY/QUARTERLY/SLOW) → drives lookback selection
- **Crowdedness hint** (HIGH/MEDIUM/LOW) → drives group_rank vs plain ts_rank
- **RL recommendations** → ranked template performance from `template_performance.json`
- **Both signs** → always generates rank() and -rank() variants (sign-flip catches negative passes)

Knowledge bases loaded each run (ALL `.md` files in `knowledge bases/` folder):
- Alpha_Examples.md, WQ_Operators_Guide.md, WQ_Advanced_Topics.md, WQ_Alpha_Creation_And_Submission_Guide.md
- WQ_Discover_BRAIN.md, WQ_Interpret_Results_Summary.md, WQ_Understanding_Data_Summary.md
- **auto_findings.md** ← new: auto-generated summary of banned ops, submitted alphas, corr-failed fields, template leaderboard

### Template Performance (from template_performance.json, as of Session 26)
| Template × Frequency | Pass Rate | Notes |
|---------------------|-----------|-------|
| ts_rank × QUARTERLY | 0.6% | Best for Fundamental fields |
| ts_rank × WEEKLY | 4.3% | Best for Model fields |
| Model category | 8.3% overall yield | Highest of any category |
| Analyst category | 0.0% overall yield | Lowest — avoid spending batches here |

---

## 📋 Immediate Actions for Next Session

1. **Restart orchestrator** — stopped at batch 46 due to WQ session expiry:
   ```bash
   cd ~/Downloads/WQ-Brain-main
   python3 orchestrator.py
   ```
2. **Do NOT run `parameters_bvps_tune.py`** — expression uses banned `ts_delta(close` and will be dropped
3. **Check passes_to_review.txt** after orchestrator runs overnight
4. **Look for passes from new field families** — `actual_return_on_pension_plan_assets` is exhausted; need fields not already in book

---

## 🔑 Key Principles

1. **Score change > everything.** Check Performance Comparison panel always. Cannot auto-fetch — manual only.
2. **TOP200 for self-corr bypass.** Consistently gives lowest max_corr.
3. **Fitness fix = heavier decay (30/40/60) or hump().** Try heavier decay first.
4. **Neutralization only helps if TO is neutralization-driven.**
5. **Never mark dead from baseline alone.** Flip + TOP200 required first.
6. **D1 only.** All batches use `delay=1`.
7. **8 concurrent workers** (`export WQ_CONCURRENCY=8`), 0.8s stagger, 2-attempt cap.
8. **Orchestrator is fully hands-free.** Biometric auto-polls POST /persona, passes auto-continue after 30 min.
9. **RL improves over time.** After ~10 runs per (template × frequency) bucket, recommendations kick in.
10. **Both signs always tested.** Generator produces rank() and -rank(); sign-flip catches negative-sharpe passes automatically.
11. **Self-corr is async — must poll.** WQ API returns PENDING initially; orchestrator polls every 15s up to 6 min.
12. **Corr-failed fields persist.** `corr_failed_fields.json` + `auto_findings.md` ensure Gemini avoids exhausted fields.
