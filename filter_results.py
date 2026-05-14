# filter_results.py
import pandas as pd, glob, os, re

# ── UPDATE THIS AFTER EVERY SUBMISSION ────────────────────
SUBMITTED_VARIABLES = [
    'sales_ps',                                              # A4
    'volume',                                                # A9
    'current_ratio',                                         # A10
    'mdl177_garpanalystmodel_qgp_vfpriceratio',              # MC3
    'mdl177_2_sensitivityfactor400_ttmocfev',                # M6 + NEW-3 + NEW-3b
    'mdl177_2_5yearrelativevaluefactor_rel5yfwdep',          # M11 + M10 + NEW-2
    'mdl177_2_sensitivityfactor400_ney',                     # M15b + NEW-9 + NEW-9b
    'mdl177_2_deepvaluefactor_fwdep',                        # DV2c
    'mdl177_2_deepvaluefactor_ttmfcfp',                      # DV5 + NEW-5 + NEW-5b + T1K-3
    'mdl177_2_deepvaluefactor_ttmfcfev',                     # DV3b + T5K-5 (NOTE: ttmfcfev not ttmfcev!)
    'mdl177_2_deepvaluefactor_pdy',                          # DV16 + NEW-7 + NEW-7b
    'mdl177_valanalystmodel_qva_incstmt',                    # VA-1
    'mdl177_2_vma2_vma2_va',                                 # VMA-2 + T5K-4
    'mdl177_relativevaluemodel_ttmfcfp',                     # RV-1b + T5K-2
    'mdl177_2_relativevaluemodel_ttmfcfp',                   # T2K-1 (same alpha as T5K-2, different prefix)
    'mdl177_deepvaluefactor_ttmfcfp_alt',                    # Alt-1
    'mdl177_2_relativevaluemodel_fc_estep',                  # fc_estep (504w benched, 252w dead fitness)
]

# ── THRESHOLDS ─────────────────────────────────────────────
SHARPE_MIN    = 1.25
FITNESS_MIN   = 1.00
TO_MAX        = 70.0
TO_MIN        = 1.0
PASSES_MIN    = 6

SHARPE_BORDER = 1.10
FITNESS_BORDER= 0.85

# ── LOAD LATEST CSV ───────────────────────────────────────
# Support both old format (api_*.csv) and new format (results_*.csv)
all_csvs = sorted(glob.glob('data/results_*.csv') + glob.glob('data/api_*.csv'))
if not all_csvs:
    print('No CSV files found in data/')
    exit()

latest = all_csvs[-1]
print(f'Reading: {latest}\n')
df = pd.read_csv(latest)

# ── EXTRACT VARIABLE NAME FROM CODE ───────────────────────
def extract_var(code):
    m = re.search(r'(mdl177[^\s,)]+)', str(code))
    return m.group(1) if m else str(code)[:40]

# ── CORR FLAG ─────────────────────────────────────────────
def corr_flag(var):
    for sv in SUBMITTED_VARIABLES:
        if sv in var or var in sv:
            return '⚠️  CHECK CORR'
    return '✅ SUBMIT DIRECT'

df['variable'] = df['code'].apply(extract_var)
df['flag']     = df['variable'].apply(corr_flag)

# ── FILTER ────────────────────────────────────────────────
passers = df[
    (df['passed'] >= PASSES_MIN) &
    (df['sharpe'] >= SHARPE_MIN) &
    (df['fitness'] >= FITNESS_MIN) &
    (df['turnover'] <= TO_MAX) &
    (df['turnover'] >= TO_MIN)
].sort_values('sharpe', ascending=False)

borderline = df[
    (df['passed'] >= PASSES_MIN) &
    (df['sharpe'] >= SHARPE_BORDER) &
    (df['fitness'] >= FITNESS_BORDER) &
    (df['sharpe'] < SHARPE_MIN)
].sort_values('sharpe', ascending=False)

errors = df[df['sharpe'] == 0]

# ── PRINT RESULTS ─────────────────────────────────────────
total = len(df)
print(f'Total tested : {total}')
print(f'Errors       : {len(errors)}')
print(f'Passers      : {len(passers)}')
print(f'Borderline   : {len(borderline)}')
print()

if len(passers):
    print('━' * 60)
    print(f'  ✅ PASSERS ({len(passers)})')
    print('━' * 60)
    for _, r in passers.iterrows():
        print(f"\n  {r['flag']}")
        print(f"  Sharpe {r['sharpe']:.2f}  Fitness {r['fitness']:.2f}  TO {r['turnover']:.1f}%  Passed {r['passed']}/7")
        print(f"  Var  : {r['variable']}")
        print(f"  Code : {r['code']}")
        print(f"  Link : {r['link']}")

if len(borderline):
    print()
    print('━' * 60)
    print(f'  🟡 BORDERLINE ({len(borderline)}) — below threshold, check manually')
    print('━' * 60)
    for _, r in borderline.iterrows():
        print(f"\n  {r['flag']}")
        print(f"  Sharpe {r['sharpe']:.2f}  Fitness {r['fitness']:.2f}  TO {r['turnover']:.1f}%  Passed {r['passed']}/7")
        print(f"  Var  : {r['variable']}")
        print(f"  Code : {r['code']}")
        print(f"  Link : {r['link']}")

if len(errors):
    print()
    print('━' * 60)
    print(f'  ❌ ERRORS ({len(errors)}) — unknown variable or API error')
    print('━' * 60)
    for _, r in errors.iterrows():
        print(f"  {r['code']}")

print()
print('Done.')
