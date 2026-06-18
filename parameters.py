# parameters_tune_fn_comp_industry_neut.py
# Re-test best fn_comp_* expressions with INDUSTRY neutralization (correct for Fundamental category)
# Prior batch (auto_tune_0617_2148) used SUBINDUSTRY — wrong for Fundamental fields.
# That likely caused passed=4 consistently. INDUSTRY neut may push passed to 6+.
#
# Targets:
#   fn_comp_non_opt_vested_a          — sign-flipped: sh=+1.33, fit=+1.05, p=4 (SUBINDUSTRY)
#   fn_comp_number_of_shares_authorized_q — sh=1.26, fit=0.76, p=5 (ts_regression, SUBINDUSTRY)

from commands import *
BATCH_NAME = 'tune_fn_comp_industry_neut'

# Correct neutralization for Fundamental category
BASE = {'neutralization': 'INDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B200 = {**BASE, 'universe': 'TOP200'}

F1 = 'fn_comp_number_of_shares_authorized_q'
F2 = 'fn_comp_non_opt_vested_a'

DATA = [
    # ── fn_comp_non_opt_vested_a ── sign-flipped (rank instead of -rank) ──────
    # TOP200 with INDUSTRY neut — prior SUBINDUSTRY run: sh=-1.33, fit=-1.05, p=4
    {**B200,  'code': f'rank(hump(group_zscore(ts_rank({F2}, 504), subindustry)))'},
    {**BASE,  'code': f'rank(hump(group_zscore(ts_rank({F2}, 504), subindustry)))'},

    # Also test -rank versions to confirm sign direction with INDUSTRY neut
    {**B200,  'code': f'-rank(hump(group_zscore(ts_rank({F2}, 504), subindustry)))'},
    {**BASE,  'code': f'-rank(hump(group_zscore(ts_rank({F2}, 504), subindustry)))'},

    # group_zscore variants (shorter lookback to push check count)
    {**B200,  'code': f'rank(group_zscore(ts_rank({F2}, 252), subindustry))'},
    {**BASE,  'code': f'rank(group_zscore(ts_rank({F2}, 252), subindustry))'},

    # ts_regression — INDUSTRY neut (prior run: sh=-1.09, fit=-0.82, p=4)
    {**B200,  'code': f'rank(ts_regression({F2}, ts_step(1), 504, rettype=2))'},
    {**BASE,  'code': f'rank(ts_regression({F2}, ts_step(1), 504, rettype=2))'},

    # Regression with shorter lookback (more data coverage → more checks pass)
    {**B200,  'code': f'rank(ts_regression({F2}, ts_step(1), 252, rettype=2))'},
    {**BASE,  'code': f'rank(ts_regression({F2}, ts_step(1), 252, rettype=2))'},

    # ── fn_comp_number_of_shares_authorized_q ────────────────────────────────
    # ts_regression TOP3000 SUBINDUSTRY: sh=1.26, fit=0.76, p=5 — near-miss
    # Try INDUSTRY neut to see if checks improve
    {**BASE,  'code': f'-rank(ts_regression({F1}, ts_step(1), 252, rettype=2))'},
    {**B200,  'code': f'-rank(ts_regression({F1}, ts_step(1), 252, rettype=2))'},

    # rettype=1 (slope) may give higher fitness than R-squared (rettype=2)
    {**BASE,  'code': f'-rank(ts_regression({F1}, ts_step(1), 252, rettype=1))'},
    {**B200,  'code': f'-rank(ts_regression({F1}, ts_step(1), 252, rettype=1))'},

    # hump+ts_rank INDUSTRY neut — prior SUBINDUSTRY: sh=1.21, fit=2.27, p=4
    {**B200,  'code': f'-rank(hump(ts_rank({F1}, 252)))'},
    {**BASE,  'code': f'-rank(hump(ts_rank({F1}, 252)))'},

    # ts_backfill + INDUSTRY neut (prior: sh=1.23, fit=2.22, p=4 with SUBINDUSTRY)
    {**B200,  'code': f'-rank(hump(ts_rank(ts_backfill({F1}, 120), 252)))'},
    {**BASE,  'code': f'-rank(hump(ts_rank(ts_backfill({F1}, 120), 252)))'},
]

print(f"Total expressions queued: {len(DATA)}")
print(f"  F1: {F1}")
print(f"  F2: {F2}")
print(f"  Neutralization: INDUSTRY (corrected from prior SUBINDUSTRY batch)")
