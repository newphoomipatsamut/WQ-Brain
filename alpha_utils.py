#!/usr/bin/env python3
"""
alpha_utils.py — Shared utilities for WQ-Brain pipeline
========================================================
Single source of truth for field extraction, expression validation,
and book dedup logic used across orchestrator, update_tracker, template_rl, etc.
"""

import csv
import re
from pathlib import Path

# ─── Field extraction ────────────────────────────────────────────────────────
# Ordered most-specific to least-specific. Extracts the innermost data field
# from a FASTEXPR alpha expression.

_FIELD_PATTERNS = [
    # Group operators wrapping time-series operators
    r'group_(?:rank|zscore|neutralize|mean|scale)\((?:ts_\w+|rank|hump)\(([^,)]+)',
    # Group operators with direct field
    r'group_(?:rank|zscore|neutralize|mean|scale)\(([^,)]+)',
    # ts_regression — field is first arg
    r'ts_regression\(([^,)]+)',
    # ts_corr — field is first arg
    r'ts_corr\(([^,)]+)',
    # Standard time-series operators
    r'(?:ts_rank|ts_zscore|ts_decay_linear|ts_std_dev|ts_mean|ts_delta|ts_backfill|hump)\(([^,)]+)',
    # Fallback: rank(FIELD) or -rank(FIELD)
    r'rank\(([^,)]+)',
]


def extract_field(code: str) -> str | None:
    """Extract the data field name from an alpha expression string."""
    code = str(code)
    for pat in _FIELD_PATTERNS:
        m = re.search(pat, code)
        if m:
            field = m.group(1).strip()
            if not re.match(r'^[\d\-]', field) and '(' not in field:
                return field
    return None


# ─── Expression validation ───────────────────────────────────────────────────

# Known FASTEXPR operators
_KNOWN_OPS = {
    'rank', 'sigmoid', 'exp', 'fraction', 'log', 'log_diff', 'scale', 'zscore',
    'sign', 'abs', 'sqrt', 'hump', 'winsorize',
    'ts_rank', 'ts_zscore', 'ts_decay_linear', 'ts_std_dev', 'ts_mean',
    'ts_delta', 'ts_backfill', 'ts_sum', 'ts_product', 'ts_entropy',
    'ts_av_diff', 'ts_arg_max', 'ts_delay', 'ts_ir', 'ts_max', 'ts_max_diff',
    'ts_median', 'ts_min', 'ts_min_diff', 'ts_skewness', 'ts_kurtosis',
    'ts_corr', 'ts_regression', 'ts_step',
    'group_rank', 'group_zscore', 'group_neutralize', 'group_mean',
    'group_scale', 'group_std_dev', 'group_sum', 'group_max', 'group_median',
}

# Known group arguments and price/volume fields (not data fields)
_KNOWN_ARGS = {
    'market', 'sector', 'industry', 'subindustry',
    'open', 'high', 'low', 'close', 'vwap', 'returns', 'volume', 'adv20', 'cap',
}


def validate_expression(expr: str, known_fields: set[str] = None) -> tuple[bool, str]:
    """
    Validate a FASTEXPR expression. Returns (is_valid, error_message).
    If known_fields is provided, also checks that the extracted field exists.
    """
    expr = expr.strip()
    if not expr:
        return False, "Empty expression"

    # Check parentheses balance
    depth = 0
    for ch in expr:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if depth < 0:
            return False, "Unbalanced parentheses: extra closing ')'"
    if depth != 0:
        return False, f"Unbalanced parentheses: {depth} unclosed '('"

    # Check that all function calls use known operators
    for m in re.finditer(r'([a-z_]+)\(', expr):
        op = m.group(1)
        if op not in _KNOWN_OPS:
            return False, f"Unknown operator: {op}"

    # Check field exists (if known_fields provided)
    if known_fields is not None:
        field = extract_field(expr)
        if field and field not in known_fields and field not in _KNOWN_ARGS:
            return False, f"Unknown field: {field}"

    return True, ""


def load_known_fields(tracker_csv: Path) -> set[str]:
    """Load all field names from fields_tracker.csv."""
    fields = set()
    try:
        with open(tracker_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                field = row.get('field', '').strip()
                if field:
                    fields.add(field)
    except Exception:
        pass
    return fields


# ─── Book dedup ──────────────────────────────────────────────────────────────

def load_submitted_alphas(tracker_csv: Path) -> list[dict]:
    """Load all passing/in-use alphas from the tracker for dedup and prompt context."""
    alphas = []
    try:
        with open(tracker_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                status = row.get('status', '')
                if '✅' in status:  # ✅ In Use
                    alphas.append({
                        'field': row.get('field', '').strip(),
                        'signal_strength': row.get('signal_strength', ''),
                        'category': row.get('category', ''),
                    })
    except Exception:
        pass
    return alphas


def load_passing_expressions(data_dir: Path) -> list[dict]:
    """
    Scan all result CSVs in data/ for expressions that passed IS thresholds.
    Returns list of dicts with field, code, sharpe, fitness, universe.
    """
    passes = []
    seen_codes = set()
    try:
        for csv_file in sorted(data_dir.glob('*.csv'), key=lambda p: p.stat().st_mtime, reverse=True):
            if csv_file.name.startswith('evaluated_'):
                continue
            with open(csv_file, newline='', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    try:
                        sharpe = float(row.get('sharpe', 0) or 0)
                        fitness = float(row.get('fitness', 0) or 0)
                        passed = int(row.get('passed', 0) or 0)
                        code = row.get('code', '').strip()
                        if not code or code in seen_codes:
                            continue
                        if sharpe >= 1.25 and fitness >= 1.0 and passed >= 6:
                            seen_codes.add(code)
                            passes.append({
                                'field': extract_field(code) or '?',
                                'code': code,
                                'sharpe': sharpe,
                                'fitness': fitness,
                                'universe': row.get('universe', ''),
                            })
                    except (ValueError, TypeError):
                        continue
    except Exception:
        pass
    # Sort by sharpe descending
    passes.sort(key=lambda x: x['sharpe'], reverse=True)
    return passes
