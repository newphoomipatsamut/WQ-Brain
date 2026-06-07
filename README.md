# WQ-Brain Alpha Research Pipeline

An automated alpha discovery and simulation pipeline for [WorldQuant BRAIN](https://platform.worldquantbrain.com), built for IQC 2026 competition research.

> Forked from [RussellDash332/WQ-Brain](https://github.com/RussellDash332/WQ-Brain), which credits [AbnerTeng/WorldQuant-Brain](https://github.com/AbnerTeng/WorldQuant-Brain).

---

## What This Does

- **LLM-powered alpha generation** — Gemini 3.5 Flash with automatic Groq fallback (llama-3.3-70b) on rate limits
- **Reinforcement learning** — multi-armed bandit tracks which templates work per data frequency and steers LLM toward them
- **Fully automated orchestrator** — cycles through categories, generates batches, runs simulations, tunes near-misses, updates tracker
- **Concurrent simulation** — parallel simulations with auto-resume on timeout
- **Biometric auth** — sends LINE notification with auth link, waits for user completion
- **Near-miss tuning** — automatically builds parameter sweeps for expressions close to passing thresholds
- **Field tracking** — 6,500+ fields across 19 categories with emoji-coded status tracking

---

## Setup

```bash
git clone https://github.com/newphoomipatsamut/WQ-Brain.git
cd WQ-Brain
pip install requests pandas openpyxl google-genai groq
cp credentials.json.example credentials.json
# Edit credentials.json with your WQ Brain email and password
```

---

## Quick Start

### Fully automated (recommended)
```bash
# Run the orchestrator — generates, simulates, tunes, repeats
python3 orchestrator.py --api-key YOUR_GEMINI_KEY

# With Groq fallback (auto-switches when Gemini hits rate limits)
python3 orchestrator.py --api-key YOUR_GEMINI_KEY --groq-key YOUR_GROQ_KEY

# Start from a specific category
python3 orchestrator.py --api-key YOUR_GEMINI_KEY --start-category "Analyst"

# Plan only — see what would run
python3 orchestrator.py --api-key YOUR_GEMINI_KEY --dry-run

# Retune historical near-misses (no API key needed)
python3 orchestrator.py --retune

# Run curated seed alphas (101 Formulaic + research)
python3 orchestrator.py --seed
python3 orchestrator.py --seed --seed-category price_volume

# Mutate passing alphas (genetic evolution)
python3 orchestrator.py --mutate --mutate-count 50

# Portfolio correlation check
python3 agent.py --portfolio
```

### Manual workflow
```bash
# 1. Generate expressions with Gemini
python3 llm_alpha_generator.py --api-key YOUR_GEMINI_KEY --category "Fundamental" --count 30

# 2. Run simulations
cp parameters_llm_fundamental_*.py parameters.py
python3 main.py

# 3. Check results — corr + score
python3 agent.py data/<output>.csv

# 4. Baseline sweep (no LLM needed)
python3 generate_batch.py --category "Model" --smart
```

---

## Key Files

| File | Purpose |
|------|---------|
| `orchestrator.py` | Fully automated research loop — generate, simulate, tune, repeat |
| `llm_alpha_generator.py` | LLM-powered expression generator (Gemini + Groq fallback) with RL recommendations |
| `template_rl.py` | Multi-armed bandit tracking template performance by frequency |
| `main.py` | Simulation engine — concurrent workers, auto-resume, biometric auth |
| `agent.py` | Post-simulation analysis — corr check, score fetch, tuning |
| `generate_batch.py` | Baseline sweep generator (no LLM, cross-product of templates) |
| `alpha_miner.py` | Enumerate all template variants for a specific field |
| `alpha_utils.py` | Shared utilities — field extraction, expression validation |
| `scrape_alphas.py` | Scrape passing alphas from your WQ account |
| `submit_alphas.py` | Submit passing alphas to competition |
| `scrape_fields.py` | Scrape all available fields from WQ API |
| `update_tracker.py` | Sync fields_tracker.csv with latest results |
| `notify.py` | LINE + macOS notification system |
| `database.py` | SQLite database management |
| `seed_alphas.py` | 50+ curated seed expressions from 101 Formulaic Alphas + research |
| `mutator.py` | Genetic mutation engine — operator swaps, crossover, lookback mutations |
| `fields_tracker.csv` | 6,500+ fields with status, category, signal strength |
| `wq_alpha.db` | SQLite database — queryable version of results |
| `credentials.json` | Login credentials — **gitignored, never commit** |

---

## Alpha Submission Thresholds (D1)

| Metric | Pass | Near-Miss | Reject |
|--------|------|-----------|--------|
| IS Sharpe | >= 1.25 | >= 0.90 | < 0.90 |
| IS Fitness | >= 1.00 | >= 0.70 | < 0.70 |
| Checks | >= 6/7 | >= 5/7 | < 5 |
| Self-correlation | < 0.70 | — | >= 0.70 |
| Score change | > 0 | — | <= 0 |

---

## Status Labels

| Emoji | Status | Meaning |
|-------|--------|---------|
| (empty) | Untested | Not yet simulated |
| ⚪ | Backlog | Untested, queued for testing |
| 🟡 | Tested: Baseline Failed | Tested, didn't pass |
| 🟠 | Test Soon | Near-miss, worth tuning |
| ✅ | In Use | Passed IS, in competition book |
| ❌ | Dead | Confirmed no signal |
| ❌ | Abandoned | Manually marked, skip |

---

## Template RL System

The reinforcement learning system (`template_rl.py`) tracks pass rates by template type and data frequency:

```bash
# View current recommendations
python3 -c "from template_rl import print_summary; print_summary()"
```

Templates are ranked by composite score: (pass_rate, near_miss_rate, avg_sharpe). The top template for each frequency gets "STRONGLY PREFER" status and is injected into Gemini's system prompt.

---

## Near-Miss Tuning

When the orchestrator finds expressions with sharpe 0.90-1.24, it automatically builds tuning batches. The tuning strategy depends on what's blocking the pass:

- **Fitness < 1.00** (turnover too high) — adds `hump()` wrapper, increases decay, tries TOP200, replaces ts_decay_linear with ts_rank
- **Checks < 6** — universe flips and lookback sweeps
- **Sharpe < 1.25** — standard lookback/universe parameter sweep

Run `python3 orchestrator.py --retune` to retune all historical near-misses.

---

## Seed Alphas & Genetic Mutation

**Seed Alphas** (`seed_alphas.py`): A curated database of 50+ alpha expressions from the "101 Formulaic Alphas" paper and WorldQuant training materials. Run `python3 orchestrator.py --seed` to generate a batch. These are starting points that need tuning (decay, neutralization, universe) before passing IS thresholds.

**Genetic Mutation** (`mutator.py`): Takes passing or near-miss alphas and generates variants through operator swaps (ts_rank to ts_zscore), lookback mutations, wrapper additions (hump, log), group argument swaps, and arithmetic crossover between two alphas. Run `python3 orchestrator.py --mutate` to generate mutations from your best-performing alphas.

**Portfolio Check** (`agent.py --portfolio`): Analyzes your submittable alphas for pairwise correlation risk. Flags when multiple alphas use the same base field (likely high self-correlation) and checks universe/wrapper diversity.

---

## Notes

- **D0 (delay=0) is not viable** for IQC 2026 — thresholds are Sharpe >= 2.0, Fitness >= 1.30
- **TOP200 universe** consistently produces the lowest self-correlation
- **2-3 concurrent simulations** is the WQ Brain platform limit (server-side)
- **Score change** requires manual check on the Performance Comparison panel
- Knowledge bases in `knowledge bases/` are fed to the LLM for domain-specific guidance
- **Groq free tier** — 14,400 req/day vs Gemini's 20/day; get a key at [console.groq.com](https://console.groq.com)
- **Environment variables** — set `GEMINI_API_KEY` and/or `GROQ_API_KEY` to avoid passing keys on CLI
