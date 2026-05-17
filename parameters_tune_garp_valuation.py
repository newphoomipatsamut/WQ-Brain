# parameters_tune_garp_valuation.py
# Best candidate from v16: mdl177_garpanalystmodel_qgp_valuation
# v16 result: sharpe=1.30, fitness=0.90, passed=6 (TOP3000 ts_zscore) — fitness just below 1.0
# Goal: find variant where fitness ≥ 1.00
# Field verified: mdl177_garpanalystmodel_qgp_valuation

BATCH_NAME = 'tune_garp_val'

BASE  = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
         'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B200  = {**BASE, 'universe': 'TOP200'}
B500  = {**BASE, 'universe': 'TOP500'}

FIELD = 'mdl177_garpanalystmodel_qgp_valuation'

DATA = [
    # Already tested — baseline (here for reference, will re-confirm)
    {**BASE, 'code': f'-rank(ts_zscore({FIELD},252))'},
    # ts_rank variant
    {**BASE, 'code': f'-rank(ts_rank({FIELD},252))'},
    # TOP200 — often cleaner corr + better fitness
    {**B200, 'code': f'-rank(ts_zscore({FIELD},252))'},
    {**B200, 'code': f'-rank(ts_rank({FIELD},252))'},
    # TOP500 — mid-tier
    {**B500, 'code': f'-rank(ts_zscore({FIELD},252))'},
    {**B500, 'code': f'-rank(ts_rank({FIELD},252))'},
    # Decay variants — try shorter decay for cleaner signal
    {**BASE, 'decay': 3, 'code': f'-rank(ts_zscore({FIELD},252))'},
    {**B200, 'decay': 3, 'code': f'-rank(ts_zscore({FIELD},252))'},
]

print(f"Total expressions queued: {len(DATA)}")
print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")
