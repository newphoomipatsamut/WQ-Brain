#!/usr/bin/env python3
"""
template_rl.py — Reinforcement Learning template performance tracker
=====================================================================
Tracks which (template_type × data_frequency) combinations produce
the highest Sharpe ratios over time. After each batch, updates a
JSON file with running stats. Before each new batch, injects
top-performer recommendations into Gemini's prompt.

No ML framework needed — this is a lightweight multi-armed bandit.
The key insight: after 50+ tests per (template × frequency) bucket,
the avg_sharpe stabilises and gives a reliable signal about what works.

Usage:
  from template_rl import update_from_results, get_recommendations
"""

import csv
import json
import re
from pathlib import Path

BASE_DIR   = Path(__file__).parent
PERF_FILE  = BASE_DIR / 'template_performance.json'
TRACKER_CSV = BASE_DIR / 'fields_tracker.csv'

# ─── Template type detection ──────────────────────────────────────────────────
# Order matters — more specific patterns first

TEMPLATE_PATTERNS = [
    ('ts_regression',   r'ts_regression\('),
    # group_neutralize must precede group_rank — double-neutral contains both
    ('group_neutralize',r'group_neutralize\('),
    ('group_rank',      r'group_rank\('),
    ('group_zscore',    r'group_zscore\('),
    ('ts_std_dev',      r'ts_std_dev\('),
    ('ts_corr',         r'ts_corr\('),
    ('hump_ts_rank',    r'hump\(ts_rank\('),
    ('ts_decay_linear', r'ts_decay_linear\('),
    # New templates — must precede generic ts_rank to get their own RL buckets
    ('ts_rank_confirm', r'\*\s*rank\(ts_delta\('),   # -rank(ts_rank(f,N) * rank(ts_delta(close,M)))
    ('revision_rate',   r'ts_rank\(ts_delta\('),      # -rank(ts_rank(ts_delta(f, N), M))
    ('ts_zscore',       r'ts_zscore\('),
    ('ts_rank',         r'ts_rank\('),
]

FREQUENCY_MAP = {
    'Price Volume':               'DAILY',
    'Price-Volume':               'DAILY',
    'News':                       'DAILY',
    'Sentiment':                  'DAILY',
    'Sentiment / Analyst':        'DAILY',
    'Social Media':               'DAILY',
    'Analyst':                    'QUARTERLY',
    'Model - Analyst':            'QUARTERLY',
    'Fundamental':                'QUARTERLY',
    'Model':                      'WEEKLY',
    'Model - Fundamental Scores': 'QUARTERLY',
    'Model - Systematic Risk':    'WEEKLY',
    'Credit Risk':                'SLOW',
    'Credit Risk - Raw':          'SLOW',
    'Credit Risk - Rating Prob':  'SLOW',
    'Credit Risk - Rating Dist':  'SLOW',
    'Model - Credit Risk':        'SLOW',
}

# Minimum runs before a template is considered statistically reliable
MIN_RUNS_FOR_RECOMMENDATION = 10

# Templates banned from recommendations regardless of stats.
# ts_decay_linear: correlated with Alpha 10 (score change consistently negative)
# ts_rank_confirm / ts_rank_confirm_med: use rank(ts_delta(close,N)) as price-momentum
#   leg — all expressions correlated with Alpha 9
BANNED_TEMPLATES = {'ts_decay_linear', 'ts_rank_confirm', 'ts_rank_confirm_med'}


# ─── Core helpers ─────────────────────────────────────────────────────────────

def extract_template_type(code: str) -> str:
    """Identify which template family an expression uses."""
    for name, pattern in TEMPLATE_PATTERNS:
        if re.search(pattern, str(code)):
            return name
    return 'other'


def _extract_field(code: str) -> str | None:
    """Extract field name — delegates to canonical alpha_utils.extract_field."""
    from alpha_utils import extract_field
    return extract_field(code)


def _load_field_frequencies(tracker_csv: Path) -> dict[str, str]:
    """Build field → frequency lookup from the tracker."""
    mapping = {}
    try:
        with open(tracker_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                cat = row.get('category', '')
                field = row.get('field', '').strip()
                if field:
                    mapping[field] = FREQUENCY_MAP.get(cat, 'QUARTERLY')
    except Exception:
        pass
    return mapping


def load_performance() -> dict:
    """Load template_performance.json, or return empty dict."""
    if PERF_FILE.exists():
        with open(PERF_FILE) as f:
            return json.load(f)
    return {}


def save_performance(perf: dict):
    """Save template_performance.json."""
    with open(PERF_FILE, 'w') as f:
        json.dump(perf, f, indent=2, sort_keys=True)


# ─── Update from results ──────────────────────────────────────────────────────

def update_from_results(results_csv: Path, tracker_csv: Path = TRACKER_CSV):
    """
    Parse a results CSV and update template_performance.json.
    Call this after every batch completes.
    """
    field_freq = _load_field_frequencies(tracker_csv)
    perf = load_performance()
    count = 0

    try:
        with open(results_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                try:
                    sharpe = float(row.get('sharpe', 0) or 0)
                    fitness = float(row.get('fitness', 0) or 0)
                    passed  = int(row.get('passed', 0) or 0)
                    code    = row.get('code', '').strip()
                    if not code:
                        continue

                    tmpl  = extract_template_type(code)
                    field = _extract_field(code)
                    freq  = field_freq.get(field, 'QUARTERLY') if field else 'QUARTERLY'
                    key   = f'{tmpl}_{freq}'

                    if key not in perf:
                        perf[key] = {
                            'runs': 0, 'sharpe_sum': 0.0,
                            'passes': 0, 'near_misses': 0
                        }

                    perf[key]['runs']      += 1
                    perf[key]['sharpe_sum'] += sharpe
                    if abs(sharpe) >= 1.25 and abs(fitness) >= 1.0 and passed >= 6:
                        perf[key]['passes'] += 1
                    elif abs(sharpe) >= 0.90 and abs(fitness) >= 0.70 and passed >= 5:
                        perf[key]['near_misses'] += 1
                    count += 1
                except Exception:
                    pass
    except Exception as e:
        print(f'[rl] Could not parse {results_csv.name}: {e}')
        return

    # Recompute avg_sharpe
    for v in perf.values():
        if v['runs'] > 0:
            v['avg_sharpe'] = round(v['sharpe_sum'] / v['runs'], 3)

    save_performance(perf)
    print(f'[rl] Updated template_performance.json — {count} expressions processed')
    _print_summary(perf)


def record_corr_fail(code: str, tracker_csv: Path = TRACKER_CSV):
    """A pass failed self-correlation (≥0.70) — it can never be submitted.
    Penalize its (template × frequency) bucket so the RL stops favoring it.
    This is how ts_decay_linear-style traps get caught automatically."""
    field_freq = _load_field_frequencies(tracker_csv)
    field = _extract_field(code)
    freq = field_freq.get(field, 'QUARTERLY') if field else 'QUARTERLY'
    key = f'{extract_template_type(code)}_{freq}'
    perf = load_performance()
    perf.setdefault(key, {'runs': 0, 'sharpe_sum': 0.0,
                          'passes': 0, 'near_misses': 0})
    perf[key]['corr_fails'] = perf[key].get('corr_fails', 0) + 1
    save_performance(perf)
    print(f'[rl] Recorded corr-fail for {key} '
          f'(total: {perf[key]["corr_fails"]})')


def effective_passes(v: dict) -> int:
    """Passes that actually count — corr-fails subtract, since an
    unsubmittable pass is worth nothing."""
    return max(v.get('passes', 0) - v.get('corr_fails', 0), 0)


def _print_summary(perf: dict):
    """Print a quick leaderboard to terminal."""
    qualified = {k: v for k, v in perf.items() if v.get('runs', 0) >= MIN_RUNS_FOR_RECOMMENDATION}
    if not qualified:
        return
    def _score(item):
        v = item[1]
        runs = v.get('runs', 1)
        pass_rate = effective_passes(v) / runs
        near_miss_rate = (effective_passes(v) + v.get('near_misses', 0)) / runs
        return (pass_rate, near_miss_rate, v.get('avg_sharpe', 0))
    ranked = sorted(qualified.items(), key=_score, reverse=True)
    print('[rl] Template leaderboard (≥10 runs, ranked by pass rate):')
    for key, v in ranked[:8]:
        runs = v.get('runs', 1)
        pr = v.get('passes', 0) / runs * 100
        print(f"  {key:<30} pass={pr:.1f}%  passes={v['passes']}/{v['runs']}  avg={v['avg_sharpe']:.2f}")


# ─── Recommendations for Gemini ───────────────────────────────────────────────

def get_recommendations(frequency: str) -> str:
    """
    Return a prompt snippet with ranked template recommendations for this frequency.
    Returns empty string if not enough data yet.
    """
    perf = load_performance()
    relevant = {
        k: v for k, v in perf.items()
        if k.endswith(f'_{frequency}') and v.get('runs', 0) >= MIN_RUNS_FOR_RECOMMENDATION
        and k[: -len(frequency) - 1] not in BANNED_TEMPLATES
    }
    if not relevant:
        return ''

    # Rank by EFFECTIVE pass_rate (passes minus corr-fails), then near_miss_rate,
    # then avg_sharpe as tiebreaker
    def _score(item):
        v = item[1]
        runs = v.get('runs', 1)
        pass_rate = effective_passes(v) / runs
        near_miss_rate = (effective_passes(v) + v.get('near_misses', 0)) / runs
        return (pass_rate, near_miss_rate, v.get('avg_sharpe', 0))

    ranked = sorted(relevant.items(), key=_score, reverse=True)
    total_runs = sum(v['runs'] for _, v in ranked)

    lines = [
        f'## RL Template Recommendations for {frequency} fields ({total_runs} historical tests)',
        'Ranked by PASS RATE (passes/runs) — use top templates, avoid bottom ones:',
    ]
    for key, v in ranked:
        tmpl = key.replace(f'_{frequency}', '')
        runs = v.get('runs', 1)
        pass_rate = v.get('passes', 0) / runs * 100
        bar  = '★' * min(5, max(1, int(pass_rate * 5 + 0.5))) if pass_rate > 0 else '☆'
        lines.append(
            f"  {bar} {tmpl:<22} pass_rate={pass_rate:.1f}%  "
            f"passes={v['passes']}/{v['runs']}  avg_sharpe={v.get('avg_sharpe', 0):.2f}"
        )

    if ranked:
        best  = ranked[0][0].replace(f'_{frequency}', '')
        worst = ranked[-1][0].replace(f'_{frequency}', '')
        lines.append(f'→ STRONGLY PREFER: {best.upper()}')
        if len(ranked) > 1:
            lines.append(f'→ AVOID (low pass rate): {worst.upper()}')

    return '\n'.join(lines)


def get_all_recommendations(frequencies: list[str]) -> str:
    """Get recommendations for multiple frequencies, combined."""
    parts = [get_recommendations(f) for f in set(frequencies)]
    parts = [p for p in parts if p]
    return '\n\n'.join(parts)


# ─── CLI for inspection ───────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        # Update from a results CSV
        results_path = Path(sys.argv[1])
        if results_path.exists():
            update_from_results(results_path)
        else:
            print(f'File not found: {results_path}')
    else:
        # Print current leaderboard
        perf = load_performance()
        if not perf:
            print('No performance data yet. Run batches and call update_from_results().')
        else:
            print(f'Template performance ({PERF_FILE.name}):')
            _print_summary(perf)
            print()
            for freq in ['DAILY', 'WEEKLY', 'QUARTERLY', 'SLOW']:
                rec = get_recommendations(freq)
                if rec:
                    print(rec)
                    print()
