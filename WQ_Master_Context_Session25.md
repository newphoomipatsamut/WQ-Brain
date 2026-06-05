# WorldQuant BRAIN — Master Context File
> **Researcher:** Phoomipat | **Last Updated:** 05 Jun 2026 (Session 25 Final) | **Session:** 25
> **Upload this file at the start of every Claude/Gemini session.**

---

## Current Status

| Item | Value |
|------|-------|
| Challenge Score | **28,394** |
| IQC 2026 Stage 1 D1 Score | **10,260** |
| Alphas Submitted (Active) | **21** (+2 submitted this session) |
| Competition Phase | **Post-IQC — Next competition prep** |
| Running on | Terminal (local machine) |
| Concurrent Workers | **8** (consultant account limit confirmed) |
| Automation | **orchestrator.py** — fully automated, running overnight |

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
2. **Fitness Block fix:** Heavier `ts_decay_linear()` (decay=30/40/60) or `hump()`.
3. **Correlation Block:** Reject if max_corr > 0.70 OR Performance Comparison score negative.
4. **Neutralization:** MARKET neut worth trying for high-TO signals only.
5. **Score > +100 → Tune before submitting.**

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
9. **`signal_strength` column:** Numeric Sharpe only. 70 old non-numeric values (`Strong`/`Weak`/`Dead`) cleared Session 25.

---

## 📊 Field Database Status (Session 25 Final)

| Status | Count |
|--------|-------|
| Untested (blank) | **6,593** |
| 🟡 Tested: Baseline Failed | 177 |
| ❌ Abandoned | 97 |
| ❌ Dead | 957 (incl. 928 anl4_* event fields) |
| ✅ In Use | **20** |
| 🟠 Test Soon | 3 |
| ⚪ Backlog | 2 |
| **Total** | **7,850** |

**Tracker columns:** `category, field, status, signal_strength, dataset, description, notes, abandon_reason`
**abandon_reason values:** `neg_sharpe`, `low_sharpe`, `corr_block`, `neg_fitness`, `fitness_ceiling`, `event_type`

---

## 🏆 Session 25 — Results

### Passes Submitted This Session
| Alpha ID | Expression | Universe | Sharpe | Fitness | Score |
|----------|-----------|----------|--------|---------|-------|
| mLXLPa35 | `-rank(ts_rank(acquired_intangible_avg_useful_life, 252))` | TOP200 | 1.33 | 1.38 | +1007 ✅ |
| 78d8kP1Q | `-rank(hump(ts_rank(acquired_intangible_avg_useful_life, 252)))` | TOP200 | 1.25 | 1.22 | +993 ✅ |

### Active Near-Misses
| Expression | Universe | Sharpe | Fitness | Checks | Problem | File |
|-----------|----------|--------|---------|--------|---------|------|
| `rank(ts_decay_linear(book_value_per_share_min_guidance_qtr, 21) * rank(ts_delta(close, 5)))` | TOP3000 | 1.36 | 0.76 | 6/7 | TO=34.8% | `parameters_bvps_tune.py` |

### Batches Completed
| Batch | Passes | Submittable | Notes |
|-------|--------|-------------|-------|
| `llm_fundamental_r1` | 2 | **2** | acquired_intangible_avg_useful_life — submitted ✅ |
| `intangible_tune` | 0 | 0 | decay×mom TOP500 near-miss fit=0.88 |
| `llm_analyst_r1/r2` | 0 | 0 | anl4_* event field errors, fixed |
| `llm_analyst_r3` | 0 | 0 | bvps near-miss found |

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

---

## 🗂️ Local Tools & Scripts

| File | Purpose |
|------|---------|
| `orchestrator.py` | **⭐ MAIN TOOL** — Fully automated loop. Generates → runs → analyzes → tunes → notifies. |
| `main.py` | Simulation engine. max_workers=8, 0.8s stagger, 2-attempt cap, hands-free biometric. |
| `llm_alpha_generator.py` | LLM batch generator. 11 templates, frequency/crowdedness hints, RL recommendations, deduplication, auto-TOP200 pairs. |
| `template_rl.py` | **RL tracker.** Learns which (template × frequency) combos work best. Updates `template_performance.json` after each batch. Check leaderboard: `python3 template_rl.py` |
| `update_tracker.py` | Updates fields_tracker.csv + RL tracker from a results CSV. Run manually: `python3 update_tracker.py data/batch.csv` |
| `notify.py` | LINE Messaging API + macOS notifications. |
| `fields_tracker.csv` | 7,850 fields with status, signal_strength, abandon_reason. |
| `template_performance.json` | RL data — (template × frequency) avg Sharpe. Grows smarter each batch. |
| `parameters_bvps_tune.py` | ⏳ PENDING — book_value_per_share_min_guidance_qtr fitness fix (16 expressions). |
| `passes_to_review.txt` | Orchestrator logs passes here. Check each morning. |
| `orchestrator_log.txt` | Full orchestrator session log. |
| `knowledge bases/` | 7 MD files loaded into Gemini context: Operators Guide, Alpha Examples, Advanced Topics, etc. |

---

## 🤖 Automation Setup

**Human intervention only needed for:**
1. **Biometric auth** — LINE notification sent. Complete on phone. Script auto-detects (polls 20× × 30s = 10 min), auto-refreshes expired link. No Enter needed.
2. **Performance Comparison panel** — LINE notification on pass. Check score + corr. Orchestrator auto-continues after 30 min if no input.
3. **Alpha submission** — Manual click after verifying.

### Running
```bash
# Full loop (Fundamental → Analyst → Model → ...)
python3 orchestrator.py --api-key YOUR_GEMINI_KEY

# Resume from specific category (rotates list, skipped categories move to end)
python3 orchestrator.py --api-key YOUR_GEMINI_KEY --start-category "Analyst"

# Dry run
python3 orchestrator.py --api-key YOUR_GEMINI_KEY --dry-run

# Check RL leaderboard
python3 template_rl.py

# Manually update RL from a results CSV
python3 template_rl.py data/batch_name.csv
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

Templates injected into system prompt (11 total):
- **Basic (A-E):** ts_rank(252), decay×momentum, hump, ts_zscore, ts_rank(63)
- **Advanced (F-K):** ts_std_dev, ts_corr, ts_regression(rettype=2), group_rank/group_zscore, ts_backfill+winsorize, multi-stage composition

Per-field context injected:
- **Frequency hint** (DAILY/WEEKLY/QUARTERLY/SLOW) → drives lookback selection
- **Crowdedness hint** (HIGH/MEDIUM/LOW) → drives group_rank vs plain ts_rank
- **Book composition warning** → book is value-heavy, prefer momentum/trend/volatility signals
- **Past results feedback** → tested fields in same category, avg Sharpe by status
- **RL recommendations** → ranked template performance from `template_performance.json`
- **Both signs** → always generates rank() and -rank() variants
- **Field diversity** → different templates for similar fields in same chunk

Knowledge bases loaded each run (from `knowledge bases/` folder):
Alpha_Examples.md, WQ_Operators_Guide.md, WQ_Advanced_Topics.md, WQ_Alpha_Creation_And_Submission_Guide.md, WQ_Discover_BRAIN.md, WQ_Interpret_Results_Summary.md, WQ_Understanding_Data_Summary.md

---

## 📋 Immediate Actions for Next Session

1. **Check passes_to_review.txt** — any overnight passes need Performance Comparison check
2. **Run bvps_tune batch** if orchestrator hasn't handled it:
   ```bash
   cp parameters_bvps_tune.py parameters.py && python3 main.py
   python3 update_tracker.py data/bvps_tune_*.csv
   ```
3. **Check orchestrator_log.txt** — categories covered, any errors
4. **Check template_rl.py** — view leaderboard as it builds up data

---

## 🔑 Key Principles

1. **Score change > everything.** Check Performance Comparison panel always.
2. **TOP200 for self-corr bypass.** Consistently gives lowest max_corr.
3. **Fitness fix = heavier decay (30/40/60) or hump().** Try heavier decay first.
4. **Neutralization only helps if TO is neutralization-driven.**
5. **Never mark dead from baseline alone.** Flip + TOP200 required first.
6. **D1 only.** All batches use `delay=1`.
7. **8 concurrent workers, 0.8s stagger, 2-attempt cap.**
8. **Orchestrator is fully hands-free.** Biometric auto-detects, passes auto-continue after 30 min.
9. **RL improves over time.** After ~10 runs per (template × frequency) bucket, recommendations kick in.
10. **Both signs always tested.** Generator produces rank() and -rank() for every field.
