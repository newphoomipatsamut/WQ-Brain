# WQ-Brain Alpha AutoTester

An automated simulation and research pipeline for [WorldQuant BRAIN](https://platform.worldquantbrain.com), built for IQC 2026 competition research.

> Forked from [RussellDash332/WQ-Brain](https://github.com/RussellDash332/WQ-Brain), which credits [AbnerTeng/WorldQuant-Brain](https://github.com/AbnerTeng/WorldQuant-Brain).

---

## What This Does

- Submits alpha expressions to the WQ Brain API and records IS metrics
- Runs **3 concurrent simulations** (platform limit)
- Auto-resumes timed-out simulations automatically
- Checks self-correlation and performance score for passing alphas via `agent.py`
- Maintains a variable database (`fields_tracker.csv`, `wq_alpha.db`) tracking 1,700+ fields

---

## Setup

```bash
git clone https://github.com/newphoomipatsamut/WQ-Brain.git
cd WQ-Brain
pip install requests pandas openpyxl
cp credentials.json.example credentials.json
# Edit credentials.json with your WQ Brain email and password
```

---

## Running a Batch

```bash
# 1. Copy a parameters file as the active batch
cp parameters_d1_v11.py parameters.py

# 2. Run simulations
python3 main.py

# 3. When done, run agent to check corr + score
python3 agent.py data/d1v11_YYYYMMDD_HHMMSS.csv

# 4. Enter corr manually if API returns None
python3 agent.py --corr
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Simulation engine — modified with auto-resume + clean logging |
| `agent.py` | Corr checker, score fetcher, tune file generator |
| `parameters_d1_v*.py` | Batch history — each version is a different set of expressions |
| `fields_tracker.csv` | 1,700+ WQ Brain fields with test status and notes |
| `results.csv` | All tested alphas with IS metrics, corr, and score |
| `wq_alpha.db` | SQLite database — queryable version of the above two files |
| `DATABASE.md` | How to query the database |
| `commands.py` | WQ Brain API helpers (from original fork) |
| `credentials.json` | Your login — **gitignored, never commit** |

---

## Alpha Submission Thresholds (D1, delay=1)

| Metric | Pass | Reject |
|--------|------|--------|
| IS Sharpe | ≥ 1.25 | < 1.10 |
| IS Fitness | ≥ 1.00 | < 0.85 |
| Turnover | 1–70% | > 70% or < 1% |
| Checks passed | ≥ 6/7 | < 6 |
| Self-correlation | < 0.70 | ≥ 0.70 |
| **Score change** | **> 0** | **≤ 0** |

> Score change = Performance Comparison panel on the BRAIN platform. A positive IS Sharpe is not enough — the alpha must improve your overall competition score.

---

## Expression Strategies

```python
# Standard baseline
'-rank(ts_rank(FIELD, 252))'

# Z-score variant — often better Sharpe
'-rank(ts_zscore(FIELD, 252))'

# Flipped sign — try when field has strong but wrong-direction signal
'rank(ts_rank(FIELD, 252))'

# TOP200 universe — often cleaner correlation and higher score
{**BASE, 'universe': 'TOP200', 'code': '-rank(ts_zscore(FIELD, 252))'}
```

---

## Variable Database

```bash
# Open the SQLite DB
sqlite3 wq_alpha.db

# Find untested model fields
SELECT field, category FROM v_untested_fields WHERE field LIKE 'mdl177%';

# See all active (submitted/submittable) alphas
SELECT alpha_id, name, sharpe, fitness, max_corr FROM submittable;

# Find dead fields
SELECT field, notes FROM v_dead_fields;
```

---

## Fitness Formula

```
Fitness = sqrt( |Returns%| / max(Turnover%, 12.5%) ) × Sharpe
```

---

## Notes

- **D0 (delay=0) is not viable** for this competition — thresholds are Sharpe ≥ 2.0, Fitness ≥ 1.30
- **Never mark a field dead from standard baseline alone** — always retry with flip sign and TOP200 universe
- **TOP200 universe** consistently produces the best scores in IQC 2026
- **3 concurrent simulations** is the WQ Brain platform limit — do not increase `max_workers`
