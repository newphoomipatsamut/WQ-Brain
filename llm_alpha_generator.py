#!/usr/bin/env python3
"""
llm_alpha_generator.py — LLM-powered alpha expression generator for WQ Brain
=============================================================================
Uses Gemini 3.5 Flash to generate candidate alpha expressions for untested
fields, then writes a ready-to-run parameters_llm_<batch>.py file.

Setup:
  pip install google-generativeai

Usage:
  python3 llm_alpha_generator.py --api-key YOUR_KEY
  python3 llm_alpha_generator.py --api-key YOUR_KEY --category "Model" --count 50
  python3 llm_alpha_generator.py --api-key YOUR_KEY --category "Fundamental" --count 30
  python3 llm_alpha_generator.py --api-key YOUR_KEY --dataset model53 --count 50
  python3 llm_alpha_generator.py --api-key YOUR_KEY --list-categories
  python3 llm_alpha_generator.py --api-key YOUR_KEY --list-datasets

Get a free API key at: https://aistudio.google.com/apikey
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ─── Proven context fed to the LLM ───────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert quantitative researcher generating alpha expressions for the WorldQuant BRAIN platform.

## Platform Rules (STRICT)
- All alphas use delay=1 (D1). Never use D0.
- Region: USA equity market only.
- Neutralization: SUBINDUSTRY (default). MARKET is also valid.
- Universe: TOP3000, TOP500, or TOP200.
- Expression language: FASTEXPR (WorldQuant's own syntax).

## Proven Templates That Work
Use these as your primary building blocks. Vary across templates for each field — do NOT use the same template for every field.

### Basic Templates (validated, always try these)
Template A — Pure rank, annual lookback (low turnover):
  -rank(ts_rank(FIELD, 252))

Template B — Value × price momentum (best Fitness):
  -rank(ts_decay_linear(FIELD, 21) * rank(ts_delta(close, 5)))

Template C — Fitness fix with hump:
  -rank(hump(ts_rank(FIELD, 252)))

Template D — Zscore variant:
  -rank(ts_zscore(FIELD, 252))

Template E — Short lookback (63 days):
  -rank(ts_rank(FIELD, 63))

### Advanced Templates (higher alpha diversity — use at least 1-2 per field)
Template F — Volatility signal (stability of FIELD over time):
  -rank(ts_std_dev(FIELD, 63))
  -rank(ts_rank(ts_std_dev(FIELD, 22), 252))

Template G — Correlation with price (momentum linkage):
  -rank(ts_corr(FIELD, close, 63))
  -rank(ts_rank(ts_corr(FIELD, returns, 22), 126))

Template H — Trend slope extraction (best for slow-moving fundamentals):
  -rank(ts_regression(FIELD, ts_step(1), 252, rettype=2))
  Rettype=2 extracts the slope — captures steady upward/downward trend.

Template I — Group-relative signal (lower self-correlation):
  -rank(group_rank(ts_zscore(FIELD, 252), sector))
  -rank(group_zscore(ts_rank(FIELD, 63), industry))
  Note: Use sector/industry/subindustry for the group argument.

Template J — Preprocessed signal (handles sparse/noisy data better):
  -rank(ts_rank(ts_backfill(FIELD, 120), 252))
  -rank(ts_zscore(winsorize(FIELD, std=4), 252))
  Use ts_backfill when description suggests sparse/quarterly data.
  Use winsorize when field has extreme outliers (e.g. financial statement items).

Template K — Multi-stage composition (wraps one signal inside another):
  -rank(ts_rank(ts_delta(FIELD, 21), 63))
  -rank(ts_decay_linear(ts_zscore(FIELD, 63), 10) * rank(ts_delta(close, 5)))

### Lookback windows to vary
Short: 5, 22 | Medium: 63, 126 | Long: 252, 504
Always try at least two different lookback windows per field.

## Key Gotchas
- Field names with `_alt` suffix are often deprecated — prefer the base name.
- Many Model 177 fields need the `_2_` prefix: mdl177_2_deepvaluefactor_xxx
- `adv20` is precomputed — use `adv20`, NOT `adv(20)`.
- WQ spells momentum as `pricemomemtummodel` and `earningsmomemtummodel` (double-m typo).
- Never use `industryrrelativevaluefactor` family — confirmed dead (Fitness < 1.00).
- For short sentiment fields, use Template E (63-day lookback), not 252.
- Sentiment/social signal families (snt_*, scl12_*) are exhausted — skip them.
- **EVENT-TYPE FIELDS — DO NOT USE:** Fields containing "detail" or "adxq" in their name (e.g. `anl4_ads1detailafv110_*`, `anl4_adxqfv110_*`) are point-in-time event records. Every operator fails with "does not support event inputs". However, `anl4_fs_*`, `anl4_ebit_*`, `anl4_fcf_*`, `anl4_ady_*` and other consensus estimate fields are continuous and work normally.
- **CATEGORICAL / STRING FIELDS — DO NOT USE in any expression:**
  Fields ending in `_currency`, `_currency_code`, `_reporting_currency`, `_country_code`, `_sector_code`, `_exchange_code`, or similar string identifiers are NOT numeric. Using them in ts_rank(), ts_zscore(), ts_decay_linear(), or group_neutralize() will always error with "does not support event inputs". Skip any field whose description says "code", "identifier", "currency", "ticker", or "name".

## ❌ Confirmed Dead Families — DO NOT generate expressions for these
The following families have been exhaustively tested and confirmed dead for USA:
- **Implied Volatility (ALL variants)** — implied_volatility_call_*, implied_volatility_mean_*, implied_volatility_mean_skew_*, iv term structure spreads, iv rate-of-change. All return Sharpe < 0.70. Do not generate.
- **CLV (Close-Low-Value) family** — structural turnover ceiling (fitness < 1.00 regardless of decay). Do not generate.
- **ADV20 reversion** (ts_rank/ts_delta(close)/adv20) — structural turnover 71%+, fitness ceiling ~0.91. Do not generate.
- **model53 credit curve spreads** (jc5/jc6/jm5 5yr-6mo and inversion signals) — passes IS but high book correlation, negative score. Do not generate more.
- **snt_buzz, snt_value, snt_social_*, scl12_buzz, scl12_sentiment** — all dead, fitness ceiling or negative Sharpe.
- **devNorthAmerica short sentiment** (days_to_cover, benchmark_fee, act_util, conc_ratio) — dead for USA.
- **5yr RelValue (rel5yocfp, rel5yebitdap, rel5ycfp, rel5yfwdep)** — fitness ceiling 0.39–0.58.
- **DeepValue ttmocfp, ttmfcfev** — passes IS but corr > 0.70 with existing book. Do not generate.
- **pcr_vol_*** (put-call ratio) — no meaningful signal found.

## Data Frequency Guidance — CRITICAL for lookback selection
Each field will be tagged with its update frequency. Use this to choose lookback windows:
- **DAILY** (Price Volume, News, Sentiment): Use short lookbacks 5–63. Long lookbacks are stale.
- **WEEKLY** (some Model outputs): Use medium lookbacks 22–126.
- **QUARTERLY** (Analyst estimates, most Fundamental): Use long lookbacks 126–504. Short lookbacks (22–63) see almost no signal change — avoid them.
- **ANNUAL** (annual financial statement items): Use very long lookbacks 252–504 only.
- **SLOW** (Credit Risk, Model scores): Use 252–504. Signal evolves slowly.

## Crowdedness Guidance — affects template choice
Each field will be tagged with its crowdedness level based on category:
- **HIGH crowdedness** (Model mdl177_* fields): Many researchers already use these. Use group_rank, group_zscore, TOP200 to reduce self-correlation. Avoid plain ts_rank(252) — likely already in other researchers' books.
- **MEDIUM crowdedness** (Analyst, Model-Analyst): Mix of standard and group templates.
- **LOW crowdedness** (raw Fundamental, Credit Risk Raw, Price-Volume): Less tested — any template works. Standard ts_rank is fine.

## Existing Book Composition — avoid these signal types (already represented)
The researcher's current book of 19 alphas is HEAVILY weighted toward:
- Value signals (book-to-price, earnings yield, FCF yield, EBITDA/EV)
- Quality signals (DeepValue factor variants)
- Credit curve signals (model53 spreads)
AVOID generating more value/quality signals — they will fail self-correlation checks.
PREFER: momentum, growth rate of change, volatility-of-fundamentals, group-relative peer signals, trend slope (ts_regression).

## Signal Direction — always test both
For each field, generate at least one expression with `-rank(...)` (short high = bearish on high values)
AND one with `rank(...)` (long high = bullish on high values). Financial theory doesn't always predict direction correctly — test both.

## Field Diversity — when multiple similar fields are given
If you see fields with similar names (e.g. avg_ebitda_*, avg_capex_*, avg_revenue_*), they are correlated.
Use DIFFERENT templates for each — do not apply the same template to all related fields or they will all fail self-correlation together.

## What Makes a Good Alpha
1. Fitness ≥ 1.00 (turnover 1–70%)
2. Sharpe ≥ 1.25
3. Self-correlation < 0.70 with existing book
4. TOP200 consistently gives lowest self-correlation
5. group_rank / group_zscore gives structurally lower self-corr than plain rank

## Response Format
Return ONLY a valid JSON array. No markdown, no explanation, no code blocks.
Each element must have:
  - "field": exact field name as given
  - "expressions": array of 4–6 alpha expression strings (vary templates AND signs)
  - "rationale": one sentence explaining the economic hypothesis

Example:
[
  {
    "field": "mdl177_2_deepvaluefactor_bp",
    "expressions": [
      "-rank(ts_rank(mdl177_2_deepvaluefactor_bp, 252))",
      "rank(ts_rank(mdl177_2_deepvaluefactor_bp, 252))",
      "-rank(group_rank(ts_zscore(mdl177_2_deepvaluefactor_bp, 252), sector))",
      "-rank(ts_regression(mdl177_2_deepvaluefactor_bp, ts_step(1), 252, rettype=2))",
      "-rank(ts_decay_linear(mdl177_2_deepvaluefactor_bp, 21) * rank(ts_delta(close, 5)))"
    ],
    "rationale": "Book-to-price value signal; slope captures consistent improvement vs. level."
  }
]
"""

USER_PROMPT_TEMPLATE = """Generate alpha expressions for the following {n} untested fields from the WorldQuant BRAIN platform.

Fields to generate expressions for (format: field_name | category | update_frequency | crowdedness | description):
{field_list}

For each field:
1. Use the update_frequency tag to choose appropriate lookback windows (QUARTERLY → 126-504, DAILY → 5-63)
2. Use the crowdedness tag to choose templates (HIGH → prefer group_rank/TOP200, LOW → any template ok)
3. Generate both -rank(...) and rank(...) sign variants to cover both directions
4. Vary templates across fields — if adjacent fields are similar, use different templates for each
5. Prefer momentum/growth/trend templates over value — the existing book is value-heavy
6. Include at least one group_rank or group_zscore expression per field for self-corr diversity

Return ONLY the JSON array."""

# ─── Dataset-specific prompt extensions ──────────────────────────────────────

DATASET_PROMPTS = {
    'model53': """
## Dataset: model53 — Creditworthiness Risk Measure Model

This dataset provides default probability measures and credit risk indicators across multiple time horizons.
Fields follow the pattern: mdl53_<model>_<horizon>  (e.g. mdl53_jc5_1year, mdl53_jc5_5year, mdl53_jc6_1year)

### Proven Alpha Ideas for This Dataset

**Idea 1 — Default Curve Steepness** (spread between long and short horizon):
  -rank(ts_rank(mdl53_jc5_5year - mdl53_jc5_1year, 252))
  Logic: Long stocks where long-term risk is falling relative to short-term (improving outlook).
  Short stocks where the curve is steeply steepening (deteriorating future).

**Idea 2 — Curve Inversion Signal** (short > long = acute distress, mean-reverts):
  rank(ts_rank(mdl53_jc5_1year - mdl53_jc5_5year, 63))
  Logic: An inverted curve (short risk > long risk) signals temporary distress.
  Go LONG on fundamentally sound companies with inverted curves — tends to mean-revert.

**Idea 3 — Rate-of-Change / Acceleration** (second derivative of default prob):
  -rank(ts_delta(ts_delta(FIELD, 21), 21))
  Logic: Capture acceleration in credit quality changes. Long = deceleration after spike.
  Short = accelerating deterioration. Markets underreact to inflection points.

**Idea 4 — ts_delta momentum on single horizon field**:
  -rank(ts_rank(ts_delta(FIELD, 21), 252))
  Logic: Rate of change of default probability is more predictive than level.

**Idea 5 — Cross-horizon spread with decay**:
  -rank(ts_decay_linear(mdl53_jc5_5year - mdl53_jc5_1year, 21) * rank(ts_delta(close, 5)))
  Logic: Combine credit curve signal with price momentum.

### Additional Guidelines for model53
- For SINGLE-HORIZON fields (e.g. mdl53_jc6_1year): use ts_delta, ts_rank, or zscore templates
- For PAIRS of fields (1year + 5year from same model): also generate spread expressions (5yr - 1yr)
- Short lookbacks (21–63 days) work better than 252 for credit signals — they react faster
- TOP3000 and TOP200 both worth testing; credit signals tend to be less correlated than value signals
- sign() and ts_delta() combinations capture acceleration as described in Idea 3
"""
}


# ─── Category metadata — frequency + crowdedness hints ───────────────────────

CATEGORY_HINTS = {
    # (update_frequency, crowdedness)
    'Price Volume':              ('DAILY',      'LOW'),
    'Price-Volume':              ('DAILY',      'LOW'),
    'News':                      ('DAILY',      'MEDIUM'),
    'Sentiment':                 ('DAILY',      'MEDIUM'),
    'Sentiment / Analyst':       ('DAILY',      'MEDIUM'),
    'Social Media':              ('DAILY',      'MEDIUM'),
    'Analyst':                   ('QUARTERLY',  'MEDIUM'),
    'Model - Analyst':           ('QUARTERLY',  'HIGH'),
    'Fundamental':               ('QUARTERLY',  'LOW'),
    'Model':                     ('WEEKLY',     'HIGH'),
    'Model - Fundamental Scores':('QUARTERLY',  'MEDIUM'),
    'Model - Systematic Risk':   ('WEEKLY',     'MEDIUM'),
    'Options - Analytics':       ('DAILY',      'LOW'),
    'Options - Volatility':      ('DAILY',      'LOW'),
    'Credit Risk':               ('SLOW',       'LOW'),
    'Credit Risk - Raw':         ('SLOW',       'LOW'),
    'Credit Risk - Rating Prob': ('SLOW',       'LOW'),
    'Credit Risk - Rating Dist': ('SLOW',       'LOW'),
    'Model - Credit Risk':       ('SLOW',       'MEDIUM'),
}
DEFAULT_HINT = ('QUARTERLY', 'MEDIUM')


# ─── Knowledge base loader ───────────────────────────────────────────────────

def load_knowledge_bases(base_dir: Path) -> str:
    """Load all .md files from the 'knowledge bases' folder and return combined text."""
    kb_dir = base_dir / 'knowledge bases'
    if not kb_dir.exists():
        return ''
    combined = []
    for md_file in sorted(kb_dir.glob('*.md')):
        try:
            content = md_file.read_text(encoding='utf-8').strip()
            combined.append(f'## [{md_file.stem}]\n{content}')
        except Exception:
            pass
    if combined:
        return '\n\n---\n\n'.join(combined)
    return ''


# ─── Field loader ─────────────────────────────────────────────────────────────

_CATEGORICAL_SUFFIXES = (
    '_currency', '_currency_code', '_reporting_currency', '_country_code',
    '_sector_code', '_exchange_code', '_iso_code', '_ticker', '_identifier',
)
# Event-type field prefixes — entire families confirmed as point-in-time records.
# Standard operators all fail: "does not support event inputs".
# anl4_ady_*, anl4_detail*, anl4_adxq* all confirmed broken.
# Only known working exception: anl4_adjusted_netincome_ft (already In Use).
# Safest: exclude all anl4_* until sub-families are individually verified.
_EVENT_FIELD_PREFIXES = ('anl4_',)
_CATEGORICAL_DESC_KEYWORDS = ('currency code', 'country code', 'identifier', 'iso code', 'ticker symbol')


def _is_categorical_field(field: str, description: str) -> bool:
    """Return True if a field is categorical/string or event-type — unusable in numeric expressions."""
    field_l = field.lower()
    if any(field_l.endswith(s) for s in _CATEGORICAL_SUFFIXES):
        return True
    # Exclude all anl4_* — entire family is event-type until sub-families are individually verified
    if any(field_l.startswith(p) for p in _EVENT_FIELD_PREFIXES):
        return True
    desc_l = description.lower()
    if any(kw in desc_l for kw in _CATEGORICAL_DESC_KEYWORDS):
        return True
    return False


def load_untested_fields(csv_path: Path, category_filter: str = None, count: int = 50) -> list[dict]:
    """Load untested fields from fields_tracker.csv, enriched with frequency/crowdedness hints."""
    fields = []
    skipped_categorical = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get('status', '').strip()
            if status:  # skip anything with a status
                continue
            category = row.get('category', '').strip()
            field = row.get('field', '').strip()
            description = row.get('description', '').strip()
            if not field:
                continue
            if category_filter and category_filter.lower() not in category.lower():
                continue
            # Skip categorical/string fields — they error in all numeric expressions
            if _is_categorical_field(field, description):
                skipped_categorical += 1
                continue
            freq, crowd = CATEGORY_HINTS.get(category, DEFAULT_HINT)
            fields.append({
                'category': category,
                'field': field,
                'description': description,
                'frequency': freq,
                'crowdedness': crowd,
            })
            if len(fields) >= count:
                break
    if skipped_categorical:
        print(f"  Skipped {skipped_categorical} categorical/string fields (not numeric)")
    return fields


def list_categories(csv_path: Path) -> dict:
    """Count untested fields per category."""
    counts = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('status', '').strip():
                continue
            cat = row.get('category', 'Unknown').strip()
            counts[cat] = counts.get(cat, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ─── Gemini caller ────────────────────────────────────────────────────────────

CHUNK_SIZE = 8  # fields per API call — reduced from 15 to handle expanded template set (11 templates × auto-TOP200)


def _parse_json_response(raw: str) -> list[dict]:
    """Parse JSON from Gemini response, stripping markdown fences if present."""
    raw = raw.strip()
    if raw.startswith('```'):
        lines = raw.split('\n')
        raw = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try extracting just the array portion
        start = raw.find('[')
        end = raw.rfind(']') + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
        raise


def _call_chunk(generate_fn, fields: list[dict]) -> list[dict]:
    """Send one chunk of fields and return parsed results."""
    field_lines = [
        f"- {f['field']} | {f['category']} | {f.get('frequency','QUARTERLY')} | {f.get('crowdedness','MEDIUM')} | {f['description'] or 'No description'}"
        for f in fields
    ]
    prompt = USER_PROMPT_TEMPLATE.format(
        n=len(fields),
        field_list='\n'.join(field_lines)
    )
    return _parse_json_response(generate_fn(prompt))


def _build_past_feedback(csv_path: Path, fields: list[dict]) -> str:
    """Read tested fields from same category and summarise what worked/failed."""
    if not csv_path.exists() or not fields:
        return ''
    category = fields[0].get('category', '')
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            rows = [r for r in csv.DictReader(f)
                    if r.get('category') == category and r.get('status') and r.get('signal_strength')]
    except Exception:
        return ''
    if not rows:
        return ''

    passing  = [r for r in rows if '✅' in r['status']]
    nearmiss = [r for r in rows if '🟠' in r['status']]
    failed   = [r for r in rows if '🟡' in r['status'] or '❌' in r['status']]

    lines = [f"From {len(rows)} previously tested fields in category '{category}':"]
    if passing:
        sharpes = []
        for r in passing:
            try:
                sharpes.append(float(r['signal_strength']))
            except (ValueError, TypeError):
                pass
        avg = f"{sum(sharpes)/len(sharpes):.2f}" if sharpes else 'N/A'
        lines.append(f"- {len(passing)} passed IS (avg Sharpe {avg}) — these fields and templates WORK in this category.")
        for r in passing[:3]:
            lines.append(f"  ✅ {r['field']} (sharpe={r['signal_strength']})")
    if nearmiss:
        lines.append(f"- {len(nearmiss)} near-misses — signals exist but fitness/checks blocking.")
    if failed:
        avg_s = []
        for r in failed:
            try:
                avg_s.append(float(r['signal_strength']))
            except (ValueError, TypeError):
                pass
        avg = f"{sum(avg_s)/len(avg_s):.2f}" if avg_s else 'N/A'
        lines.append(f"- {len(failed)} failed (avg signal_strength={avg}) — standard templates underperform here. Try advanced templates (group_rank, ts_regression, ts_std_dev).")
    return '\n'.join(lines)


def call_gemini(api_key: str, fields: list[dict], dataset: str = None) -> list[dict]:
    """Send fields to Gemini 3.5 Flash in chunks and return combined alpha expressions."""
    try:
        from google import genai
        from google.genai import types as genai_types
        NEW_SDK = True
    except ImportError:
        try:
            import google.generativeai as genai
            NEW_SDK = False
        except ImportError:
            print("ERROR: Gemini SDK not installed.")
            print("Run: pip install google-genai")
            sys.exit(1)

    # Build past-results feedback for this category
    past_feedback = _build_past_feedback(Path(__file__).parent / 'fields_tracker.csv', fields)

    # Build RL template recommendations
    rl_recs = ''
    try:
        from template_rl import get_all_recommendations
        frequencies = list(set(f.get('frequency', 'QUARTERLY') for f in fields))
        rl_recs = get_all_recommendations(frequencies)
    except Exception:
        pass

    # Build system prompt — inject knowledge bases + RL recs + dataset-specific section
    system_prompt = SYSTEM_PROMPT
    if rl_recs:
        system_prompt += f'\n\n{rl_recs}'
    if past_feedback:
        system_prompt += f'\n\n## Past Results Feedback for This Category\n{past_feedback}'
    kb_text = load_knowledge_bases(Path(__file__).parent)
    if kb_text:
        system_prompt += f'\n\n## WorldQuant BRAIN Reference Documentation\nUse the following official WQ documentation to inform your alpha ideas:\n\n{kb_text}'
    if dataset and dataset.lower() in DATASET_PROMPTS:
        system_prompt += DATASET_PROMPTS[dataset.lower()]
        print(f"  Using dataset-specific prompt for: {dataset}")

    if NEW_SDK:
        client = genai.Client(api_key=api_key)
        def _generate(prompt):
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=16384,
                )
            )
            return response.text
    else:
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel(
            model_name='gemini-3.5-flash',
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=16384,
            )
        )
        def _generate(prompt):
            return _model.generate_content(prompt).text

    # Split into chunks to avoid token limit truncation
    chunks = [fields[i:i + CHUNK_SIZE] for i in range(0, len(fields), CHUNK_SIZE)]
    total_chunks = len(chunks)
    all_results = []

    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}/{total_chunks}: sending {len(chunk)} fields...")
        try:
            results = _call_chunk(_generate, chunk)
            all_results.extend(results)
            print(f"  Chunk {i}/{total_chunks}: ✓ got {len(results)} responses")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"  Chunk {i}/{total_chunks}: ✗ JSON parse failed — {e}")
            print(f"  Skipping chunk {i} and continuing...")

    return all_results


# ─── Parameter file writer ────────────────────────────────────────────────────

def write_parameters_file(results: list[dict], batch_name: str, output_path: Path) -> Path:
    """Write a ready-to-run parameters_llm_<batch>.py file."""
    filename = f'parameters_llm_{batch_name}.py'
    filepath = output_path / filename
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Flatten all expressions into DATA list
    # For every TOP3000 expression, automatically add a TOP200 counterpart (self-corr control)
    entries = []
    for item in results:
        field = item.get('field', '')
        expressions = item.get('expressions', [])
        rationale = item.get('rationale', '')
        seen_exprs = set()
        for expr in expressions:
            if expr in seen_exprs:
                continue
            seen_exprs.add(expr)
            # Determine universe — keep what the LLM picked, default TOP3000
            if 'TOP200' in expr.upper():
                univ = 'TOP200'
            elif 'TOP500' in expr.upper():
                univ = 'TOP500'
            else:
                univ = 'TOP3000'
            entries.append((field, expr, univ, rationale))
            # Auto-add TOP200 counterpart for every TOP3000 expression (self-corr control)
            if univ == 'TOP3000':
                entries.append((field, expr, 'TOP200', rationale))

    # Deduplicate — remove identical (code, universe) pairs
    seen = set()
    deduped = []
    for item in entries:
        key = (item[1], item[2])  # (expr, universe)
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    removed = len(entries) - len(deduped)
    if removed:
        print(f'  Deduplication: removed {removed} duplicate expressions')
    entries = deduped

    lines = [
        f'# {filename}',
        f'# Auto-generated by llm_alpha_generator.py — {ts}',
        f'# Model: gemini-3.5-flash | Fields: {len(results)} | Expressions: {len(entries)} (incl. auto-TOP200 pairs)',
        f'# Run: cp {filename} parameters.py && python3 main.py',
        '',
        'from commands import *',
        f"BATCH_NAME = 'llm_{batch_name}'",
        '',
        "BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}",
        "B500 = {**BASE, 'universe': 'TOP500'}",
        "B200 = {**BASE, 'universe': 'TOP200'}",
        "UNIV = {'TOP3000': BASE, 'TOP500': B500, 'TOP200': B200}",
        '',
        'DATA = [',
    ]

    prev_field = None
    for field, expr, univ, rationale in entries:
        if field != prev_field:
            lines.append(f'    # {field}')
            if rationale:
                lines.append(f'    # {rationale}')
            prev_field = field
        lines.append(f"    {{**UNIV['{univ}'], 'code': {repr(expr)}}},")

    lines += [
        ']',
        '',
        'print(f"Total expressions queued: {len(DATA)}")',
        f'print("  Batch: llm_{batch_name} | {len(results)} fields")',
        'print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min")',
        '',
    ]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return filepath


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Generate WQ Brain alpha expressions for untested fields using Gemini 3.5 Flash.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available categories and untested counts
  python3 llm_alpha_generator.py --api-key YOUR_KEY --list-categories

  # Generate 50 expressions from Model category
  python3 llm_alpha_generator.py --api-key YOUR_KEY --category "Model" --count 50

  # Generate from Fundamental fields, custom batch name
  python3 llm_alpha_generator.py --api-key YOUR_KEY --category "Fundamental" --count 30 --batch-name fund_r1

  # Generate from all untested fields (mixed)
  python3 llm_alpha_generator.py --api-key YOUR_KEY --count 40

Get a free API key at: https://aistudio.google.com/apikey
        """
    )
    parser.add_argument('--api-key', '-k', type=str, default=None,
                        help='Google AI Studio API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--category', '-c', type=str, default=None,
                        help='Category filter (e.g. "Model", "Fundamental", "Analyst")')
    parser.add_argument('--count', '-n', type=int, default=30,
                        help='Number of fields to generate expressions for (default: 30)')
    parser.add_argument('--batch-name', '-b', type=str, default=None,
                        help='Batch name suffix for output file (default: auto-generated)')
    parser.add_argument('--dataset', '-d', type=str, default=None,
                        help='Dataset ID for specialized prompt (e.g. model53). Adds dataset-specific alpha ideas.')
    parser.add_argument('--list-categories', action='store_true',
                        help='List available categories and untested field counts, then exit')
    parser.add_argument('--list-datasets', action='store_true',
                        help='List datasets that have specialized prompts built in, then exit')
    parser.add_argument('--tracker', type=str, default='fields_tracker.csv',
                        help='Path to fields_tracker.csv (default: fields_tracker.csv)')
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    tracker_path = base_dir / args.tracker

    if not tracker_path.exists():
        print(f"ERROR: fields_tracker.csv not found at {tracker_path}")
        sys.exit(1)

    # ── List datasets mode ────────────────────────────────────────────────────
    if args.list_datasets:
        print("\nDatasets with specialized prompts:")
        for ds in DATASET_PROMPTS:
            print(f"  --dataset {ds}")
        print("\nUsage: python3 llm_alpha_generator.py --api-key KEY --dataset model53")
        return

    # ── List categories mode ──────────────────────────────────────────────────
    if args.list_categories:
        counts = list_categories(tracker_path)
        print(f"\n{'Category':<35} {'Untested':>8}")
        print('-' * 45)
        total = 0
        for cat, n in counts.items():
            print(f"  {cat:<33} {n:>8}")
            total += n
        print('-' * 45)
        print(f"  {'TOTAL':<33} {total:>8}")
        return

    # ── API key ───────────────────────────────────────────────────────────────
    api_key = args.api_key or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: No API key provided.")
        print("  Pass --api-key YOUR_KEY  or  set GEMINI_API_KEY environment variable")
        print("  Get a free key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    # ── Load fields ───────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  WQ Brain LLM Alpha Generator — gemini-3.5-flash")
    print(f"{'='*60}")

    fields = load_untested_fields(tracker_path, args.category, args.count)
    if not fields:
        print(f"ERROR: No untested fields found for category='{args.category}'")
        print("Use --list-categories to see available options.")
        sys.exit(1)

    cat_label = args.category or 'All categories'
    print(f"\n  Category : {cat_label}")
    if args.dataset:
        ds_label = args.dataset + (' (specialized prompt ✓)' if args.dataset.lower() in DATASET_PROMPTS else ' (no specialized prompt — using generic)')
        print(f"  Dataset  : {ds_label}")
    print(f"  Fields   : {len(fields)} untested fields loaded")

    # ── Call Gemini ───────────────────────────────────────────────────────────
    print(f"\n  Calling Gemini 3.5 Flash...")
    results = call_gemini(api_key, fields, dataset=args.dataset)
    total_exprs = sum(len(r.get('expressions', [])) for r in results)
    print(f"  ✓ Received {len(results)} field responses, {total_exprs} expressions (x2 with auto-TOP200 = {total_exprs*2})")

    # ── Write parameters file ─────────────────────────────────────────────────
    if args.batch_name:
        batch_name = args.batch_name
    else:
        ts = datetime.now().strftime('%m%d_%H%M')
        cat_slug = (args.category or 'mixed').lower().replace(' ', '_').replace('-', '_')
        # Collapse multiple underscores (e.g. "model___credit" → "model_credit")
        import re as _re
        cat_slug = _re.sub(r'_+', '_', cat_slug).strip('_')
        ds_slug = (f'_{args.dataset}' if args.dataset else '')
        batch_name = f'{cat_slug}{ds_slug}_{ts}'

    filepath = write_parameters_file(results, batch_name, base_dir)
    total_data = sum(len(r.get('expressions', [])) for r in results)

    print(f"\n  ✅ Written: {filepath.name}")
    print(f"  Expressions: {total_data} (incl. auto-TOP200) | Est. runtime: ~{total_data * 1.5:.0f} min (~{total_data * 1.5 / 60:.1f} hours)")
    print(f"\n  To run:")
    print(f"    cp {filepath.name} parameters.py && python3 main.py")
    print()

    # ── Preview ───────────────────────────────────────────────────────────────
    print("  Preview (first 3 fields):")
    for item in results[:3]:
        print(f"\n  [{item.get('field', '?')}]")
        print(f"    {item.get('rationale', '')}")
        for expr in item.get('expressions', [])[:3]:
            print(f"    → {expr}")


if __name__ == '__main__':
    main()
