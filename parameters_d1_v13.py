# parameters_d1_v13.py — D1 batch v13
#
# Strategy: Fresh untested fields from Fields Tracker
#
# Two categories:
#   A) snt1_d1 analyst signals — stockrank is dead but OTHER snt1_d1 fields are completely
#      untested. Earnings revision, target upgrades, composite ranks are classic quant signals.
#      Note: snt1_d1_stockrank confirmed dead (Session 11). These are DIFFERENT fields.
#
#   B) Core fundamentals — untested clean balance sheet / income statement fields.
#      current_ratio and sales_ps work well → other fundamentals worth a sweep.
#      Using ts_rank(252) only — ts_delta confirmed dead for fundamentals.
#
# Skipped entirely:
#   - All options fields (implied_vol, pcr, forward_price, breakeven) — confirmed dead family
#   - fnd6_* fields — mostly technical/administrative codes, not signal fields
#   - vwap, adv20 — tracker notes TO ceiling blocks fitness
#   - snt1_d1_stockrank — already confirmed dead Session 11
#   - snt1_d1_earningssurprise — similar to surprise analyst model (dead)
#   - snt1_d1_sellrecpercent, downtargetpercent — low signal (sell-side crowded)
#   - employee, depre_amort, income_tax — low signal quality fundamentals
#
# Run: cp parameters_d1_v13.py parameters.py && python3 main.py
# ~56 expressions, ~85 min runtime

from commands import *

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
        'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}

DATA = [
    # ══════════════════════════════════════════════════════════════════════════
    # A) snt1_d1 ANALYST SIGNALS — completely untested (different from stockrank)
    # Template: ts_rank(v,252) only — ts_zscore also tested for top candidates
    # ══════════════════════════════════════════════════════════════════════════

    # Earnings revision momentum — most classic quant analyst signal
    # earningsrevision = 1-month change in mean EPS estimate / price
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_earningsrevision,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_earningsrevision,252))'},
    {**B500, 'code': '-rank(ts_rank(snt1_d1_earningsrevision,252))'},

    # Net earnings revision — % analysts raising vs lowering EPS
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_netearningsrevision,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_netearningsrevision,252))'},

    # Price target momentum — % analysts raising vs lowering targets
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_nettargetpercent,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_nettargetpercent,252))'},

    # Analyst upgrades — % recommending buy
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_uptargetpercent,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_uptargetpercent,252))'},

    # Buy rec percent — % analysts recommending buy (level signal)
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_buyrecpercent,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_buyrecpercent,252))'},

    # LT EPS growth estimate — 3-5yr growth, value/growth crossover signal
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_longtermepsgrowthest,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_longtermepsgrowthest,252))'},

    # Composite analyst score — proprietary composite, bullish >5
    {**BASE, 'code': '-rank(ts_rank(snt1_cored1_score,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_cored1_score,252))'},

    # Dynamic focus rank — short-term sentiment composite (0-100)
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_dynamicfocusrank,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_dynamicfocusrank,252))'},

    # Fundamental focus rank — longer-term value/fundamental composite (0-100)
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_fundamentalfocusrank,252))'},
    {**BASE, 'code': '-rank(ts_zscore(snt1_d1_fundamentalfocusrank,252))'},

    # EPS estimate dispersion — contrarian signal (high dispersion = uncertainty)
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_dtstsespe,252))'},

    # Analyst coverage — more coverage = less alpha? contrarian
    {**BASE, 'code': '-rank(ts_rank(snt1_d1_analystcoverage,252))'},

    # ══════════════════════════════════════════════════════════════════════════
    # B) CORE FUNDAMENTALS — untested clean fields
    # current_ratio and sales_ps work → sweep other quality/value fundamentals
    # ts_rank(252) only — no ts_delta (confirmed dead for fundamentals)
    # ══════════════════════════════════════════════════════════════════════════

    # Quality factors
    {**BASE, 'code': '-rank(ts_rank(return_equity,252))'},       # ROE
    {**BASE, 'code': '-rank(ts_rank(operating_income,252))'},    # Operating income
    {**BASE, 'code': '-rank(ts_rank(ebitda,252))'},              # EBITDA

    # Cash flow signals — cleaner than earnings
    {**BASE, 'code': '-rank(ts_rank(cashflow_op,252))'},         # Operating CF
    {**BASE, 'code': '-rank(ts_rank(cashflow_op,252)*rank(ts_delta(close,21)))'},  # × momentum

    # Revenue/growth
    {**BASE, 'code': '-rank(ts_rank(revenue,252))'},             # Revenue
    {**BASE, 'code': '-rank(ts_rank(sales_growth,252))'},        # Sales growth QoQ

    # Investment signals
    {**BASE, 'code': '-rank(ts_rank(capex,252))'},               # Capex (low capex = value)
    {**BASE, 'code': '-rank(ts_rank(rd_expense,252))'},          # R&D (innovation proxy)

    # Balance sheet quality
    {**BASE, 'code': '-rank(ts_rank(working_capital,252))'},     # Working capital
    {**BASE, 'code': '-rank(ts_rank(invested_capital,252))'},    # Invested capital
    {**BASE, 'code': '-rank(ts_rank(equity,252))'},              # Book equity
    {**BASE, 'code': '-rank(ts_rank(cashflow_fin,252))'},        # Financing CF (negative = buybacks)

    # Income statement
    {**BASE, 'code': '-rank(ts_rank(pretax_income,252))'},       # Pretax income
    {**BASE, 'code': '-rank(ts_rank(income_beforeextra,252))'},  # Income before extra items
    {**BASE, 'code': '-rank(ts_rank(eps,252))'},                 # EPS basic

    # Debt/leverage signals
    {**BASE, 'code': '-rank(ts_rank(debt_lt,252))'},             # LT debt (high = risk)
    {**BASE, 'code': '-rank(ts_rank(interest_expense,252))'},    # Interest expense

    # Efficiency
    {**BASE, 'code': '-rank(ts_rank(inventory_turnover,252))'},  # Inventory turnover
    {**BASE, 'code': '-rank(ts_rank(inventory,252))'},           # Inventory level
    {**BASE, 'code': '-rank(ts_rank(receivable,252))'},          # Receivables
    {**BASE, 'code': '-rank(ts_rank(sga_expense,252))'},         # SG&A (efficiency proxy)
]

print(f"Total expressions queued: {len(DATA)}")
print("  v13: snt1_d1 analyst signals (11 fields) + core fundamentals (13 fields)")
print(f"Estimated runtime: ~{len(DATA) * 1.5:.0f} min")
