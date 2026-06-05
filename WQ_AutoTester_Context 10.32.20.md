# WQ-Brain Auto-Tester Context
> **Purpose:** Context file for Claude to set up, modify, and extend the WQ-Brain automated testing pipeline.
> **Repo:** https://github.com/newphoomipatsamut/WQ-Brain
> **Upload alongside WQ_Master_Context_Session_XX.md at session start.**
> **Last Updated:** Session 21, May 17 2026

---

## What This System Does

- Submits alpha expressions to WorldQuant BRAIN API automatically
- Runs **3 concurrent simulations** (WQ Brain platform limit — do NOT increase)
- Saves all results to timestamped CSV files in `data/`
- Does **NOT** submit alphas to the BRAIN book — simulation/testing only
- Passing candidates must be manually reviewed and submitted via BRAIN UI

---

## Actual Files in Repo

```
WQ-Brain/
├── credentials.json        ← Your BRAIN login (gitignored — never commit)
├── parameters.py           ← Active batch — copy from parameters_d1_vXX.py to run
├── parameters_d1_v*.py     ← Batch history — named by version
├── main.py                 ← Simulation engine (modified — auto-resume fix)
├── agent.py                ← Corr checker + score fetcher + tune file generator
├── scrape_fields.py        ← Scrapes all fields from WQ Brain API → fields_tracker.csv
├── check_alphas.py         ← Standalone alpha checker (corr + score)
├── commands.py             ← Expression generators from fork (reference only)
├── database.py             ← Dependency of commands.py (reference only)
├── scrape_alphas.py        ← Scrapes unsubmitted passing alphas with links (optional)
├── submit_alphas.py        ← Auto-submits from scrape CSV (use with caution)
├── fields_tracker.csv      ← Master variable database (7,750 fields — scraped May 17)
├── results.csv             ← All tested alphas with sharpe/fitness/corr/score
├── wq_alpha.db             ← SQLite version of above — queryable
├── DATABASE.md             ← How to query the DB
├── WQ_Master_Context_*.md  ← Session context files
└── data/
    ├── d1vXX_YYYYMMDD_HHMMSS.csv       ← Batch results (gitignored)
    └── fields_raw_model77_*.csv         ← Raw field scrape output
```

> **Not used:** `filter_results.py` — replaced by `agent.py`. Kept in repo for reference only.

---

## How to Run

```bash
# Standard run
cp parameters_d1_vXX.py parameters.py && python3 main.py

# Run agent on completed batch CSV
python3 agent.py data/d1vXX_YYYYMMDD_HHMMSS.csv

# Enter corr values manually (when API returns None)
python3 agent.py --corr

# Reset agent state between batches
python3 agent.py --reset

# Run in background
nohup python3 main.py > output.log 2>&1 &
```

---

## Full Workflow

```
parameters_d1_vXX.py → main.py → agent.py → platform UI checks → submit
```

1. Build `parameters_d1_vXX.py` with expressions to test
2. `cp parameters_d1_vXX.py parameters.py && python3 main.py`
3. When done, run `python3 agent.py data/BATCH_CSV.csv`
4. Agent fetches corr + score for passing alphas, generates tune file
5. For each passer, open BRAIN link and verify in this order:
   - **Yearly Sharpe** — 2021 and 2022 must both be positive
   - **Corr panel** — max corr < 0.70 vs all submitted
   - **Performance Comparison score** — must be positive; submit highest first
6. Submit in descending score-change order (1 per day max)

---

## parameters_d1_vXX.py — Template

```python
# parameters_d1_vXX.py
from commands import *

BATCH_NAME = 'd1vXX'  # prefixes output CSV filename

BASE  = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
         'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B200  = {**BASE, 'universe': 'TOP200'}
B500  = {**BASE, 'universe': 'TOP500'}

DATA = [
    {**BASE, 'code': '-rank(ts_rank(FIELD,252))'},
    {**BASE, 'code': '-rank(ts_zscore(FIELD,252))'},
    {**B200, 'code': '-rank(ts_zscore(FIELD,252))'},
    # Flip variants:
    {**B200, 'code': 'rank(ts_rank(FIELD,252))'},
]

print(f"Total expressions queued: {len(DATA)}")
print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")
```

---

## Expression Strategies

| Strategy | Expression | When to Use |
|----------|-----------|-------------|
| Standard | `-rank(ts_zscore(field,252))` | Default baseline — test first |
| ts_rank | `-rank(ts_rank(field,252))` | Also test alongside ts_zscore |
| TOP200 | Same expr + `'universe':'TOP200'` | After any TOP3000 pass — often cleaner corr + better score |
| TOP500 | Same expr + `'universe':'TOP500'` | Mid-tier universe — corr usually 0.28–0.65 vs TOP3000 |
| Flipped | `rank(ts_zscore(field,252))` | **ONLY** when IS Sharpe ≤ -1.0 after BOTH ts_rank AND ts_zscore have been tried |

> ⚠️ **Never mark a field dead from standard baseline alone.** Retry order: ts_zscore → TOP200 → flip (only if Sharpe ≤ -1.0 on both) → then mark dead.

---

## 🚫 HARD RULE — Never Guess Variable Names

**Never construct or guess variable names from memory or pattern-matching.**

Always verify field names from one of:
1. `fields_tracker.csv` — master list of 1,731+ confirmed field names
2. `wq_alpha.db` — `SELECT field FROM fields WHERE field LIKE 'mdl177%' AND status = ''`
3. WQ Brain Fields page on the platform UI

Wrong variable names cause silent API failures or test the wrong field entirely. This rule has no exceptions — even if a name "looks right" based on family patterns.

---

## main.py — Key Modifications (vs original fork)

### Auto-Resume Fix
- **Bug fixed:** Timed-out simulations were silently dropped (added to rows_processed)
- **Fix:** `self._timed_out` list — timed-out sims returned to main loop, retried after 30s
- **max_workers = 3** — WQ Brain platform concurrent simulation limit

### Logging Cleanup
- ▶/⏳/✔ symbols for start/timeout/complete
- Progress % only shown on change
- `[N/total] done` counter
- No thread names in log

---

## agent.py — What It Does

- Reads a batch CSV from `data/`
- Fetches **self-correlation** for passing alphas via `/alphas/{id}/check`
- Fetches **performance score** via `/teams/{team_id}/alphas/{id}/before-and-after-performance`
- Rejects alphas with negative score (logs `❌ NEGATIVE SCORE`)
- Generates `parameters_tune_*.py` with tuning variants of strong candidates
- State saved in `agent_state.json` — use `--reset` between batches

### Score API (confirmed working)
```python
# Get team_id first
GET /users/self/teams?status=ACTIVE&members.self.status=ACCEPTED&order=-dateCreated
→ results[0]['id']

# Get score
GET /teams/{team_id}/alphas/{alpha_id}/before-and-after-performance
→ data['score']['before'], data['score']['after']
→ change = round(after - before)
```

> ⚠️ `/alphas/{id}` has `competitions: null` — wrong endpoint for score. Always use the team endpoint above.

> ⚠️ Corr returns None until the alpha page has been opened in the platform UI. Enter manually: `python3 agent.py --corr`

---

## CSV Output — Column Reference

| Column | Meaning | Good Value |
|--------|---------|------------|
| `passed` | IS checks passed (out of 7) | ≥ 6 |
| `sharpe` | IS Sharpe | ≥ 1.25 |
| `fitness` | IS Fitness | ≥ 1.00 |
| `turnover` | Turnover % | 1–70% |
| `weight` | Concentrated weight check | PASS |
| `subsharpe` | Sub-universe Sharpe | > 0 |
| `link` | Direct URL to alpha in BRAIN | Click to open |
| `code` | The expression tested | — |

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

## Confirmed Working Variable Families

| Family | Fields | Score | Notes |
|--------|--------|-------|-------|
| `fangma_vmm` | `vmm11` | +396/+639 | TOP200 ts_rank best |
| `fangma_rvm` | `rvm6` | TBC | TOP200 ts_zscore — Sharpe 1.47, Fit 1.50, corr 0.45 |
| `valueanalystmodel` | `qva_chgacc` | +643 🔥 | Flipped sign, TOP200 |
| `valanalystmodel` | `qva_incstmt`, `qva_chgacc` | +238/+278 | Working family |
| `liquidityriskfactor` | `si_ratio` | +259 | High corr but positive score |
| `earningsqualityfactor` | `uap` | +160 | Working |
| `sensitivityfactor400` | `ttmocfev`, `pbroeresidual` | +160+ | Tested variants working |
| `5yearrelativevaluefactor` | `rel5yfwdep`, `rel5ybp` | +385/+238 | Strong family |
| `5shortsentimentfactor` | `days_to_cover` | TBC | Corr 0.36, sharpe 1.70 |

---

## Dead Families — Truly Dead (Do Not Retest Any Variant)

| Family | Reason |
|--------|--------|
| `industryrrelativevaluefactor` | ALL fitness < 1.00 — d1v10 confirmed |
| `globaldevnorthamerica` | Score -228 — dead regardless of IS metrics |
| `sensitivityfactor400_ney` (all variants) | Negative score confirmed |
| `deepvaluefactor_curep` | Score -281, corr 0.99 |
| `deepvaluefactor_fcfp` | Score -206 |
| `garpanalystmodel_qgp_vfpriceratio` (mdl177_2) | Score -284, corr 0.99 |
| All D0 signals | Sharpe ≥ 2.0 cutoff — not viable |

---

## Variable Name Gotchas

| Wrong | Correct | Context |
|-------|---------|---------|
| `ttmfcev` | `ttmfcfev` | deepvaluefactor TTM FCF/EV |
| `industryrelativevaluefactor` | `industryrrelativevaluefactor` | Double-r |
| `curindocta_` | `curindocfta_` | Added f |
| `curindoctp_` | `curindocfp_` | Added f, dropped t |
| `valanalystmodel` | `valueanalystmodel` | Two different models — mdl177_val... vs mdl177_value... |

**Rule:** Never guess variable names. Always verify from `fields_tracker.csv` or the WQ Brain Fields page.

---

## scrape_fields.py — Field Database Scraper

Scrapes all fields from a WQ Brain dataset via API and merges into `fields_tracker.csv`.

```bash
# Scrape Model 77 (default)
python3 scrape_fields.py

# Resume from a specific offset (if interrupted)
python3 scrape_fields.py model77 400

# Scrape a different dataset
python3 scrape_fields.py fundamental26
```

- Paginates 20 fields per request with 3s sleep (rate limit safe)
- Saves raw output to `data/fields_raw_DATASET_TIMESTAMP.csv`
- Merges new fields into `fields_tracker.csv` — **never overwrites existing status/notes**
- Also run after any WQ Brain dataset update to catch newly added fields
- Full model77 scrape: ~19 min, 7,642 fields

**Last run:** May 17, 2026 — 7,750 total fields (1,612 mdl177, 2,738 Model, 1,658 Fundamental, 1,324 Analyst, 996 News)

---

## Batch History

| Batch | Status | Key Finds |
|-------|--------|-----------|
| d1v1–v4 | ❌ D0 — all failed | D0 confirmed not viable |
| d1v9 | ✅ Complete | fangma_vmm11 → npnMdNNz +396, 9q90GOld +639 |
| d1v9b | ✅ Complete | days_to_cover passes; onloan_conc + sht_int dead |
| d1v10 | ✅ Complete | industryrrelativevaluefactor — ALL dead |
| d1v11 | ✅ Complete | ~120 expressions, fangma siblings + 5 families |
| d1v12/13 | ✅ Complete | See tune/flip results |
| d1v14/15 | ✅ Complete | chgacc Golden Alpha +643, rvm6 TOP200 strong |
| d1v16 | ⏳ Ready | ~90 expressions — high priority untested Model families |
| d1v17a | ⏳ Ready | 208 fields — full Model sweep part A |
| d1v17b | ⏳ Ready | 209 fields — full Model sweep part B |

---

## Instructions for Claude

When the researcher uploads this file:

1. **Check Master Context** for current score, submitted book, and pending queue
2. **Check fields_tracker.csv** for untested fields — query `wq_alpha.db` if available
3. **Build parameters file** ready to run — include flip + TOP200 variants for candidates
4. **After CSV results:** Run through agent.py logic — filter by IS pass → corr → score
5. **Never mark a field dead** from standard baseline alone — always suggest flip/TOP200 retry
6. **Score check first** before finalizing any submit decision
7. **3 concurrent sims max** — do not set max_workers > 3 in main.py

When building parameters files:
- Always include both ts_rank and ts_zscore variants
- Always include TOP200 for any field that looks promising on TOP3000
- Always include flip variant (`rank(...)` not `-rank(...)`) for any field with IS < 0
- Print total expression count and estimated runtime (~1.5 min per expression)
- Use BATCH_NAME = 'd1vXX' to prefix output files

*Keep this file updated as new strategies are discovered.*
