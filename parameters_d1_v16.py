# parameters_d1_v16.py — D1 batch v16
#
# Strategy: High-priority untested Model fields — ~90 expressions, ~135 min
#
# Priority order:
#   1. fangma siblings — rvm6 TOP200 gave strong IS. rvm1, mam, emf, dvm untested.
#   2. valueanalystmodel siblings — qva_chgacc gave +643. incstmt/finstmt/pegy/earnval/epmodule untested.
#   3. valanalystmodel siblings — qva_incstmt submitted +238. capexdep/epmodule/finstmt/pegy/valuation untested.
#   4. momemtumanalystmodel — fresh family, chgnowc/composite/earnxp/epsgrwth untested.
#   5. vma2 siblings — vma2_va submitted +66. ma/ma_ee/ma_em/ma_pm untested.
#   6. earningsqualityfactor — uap gave +160. chgshare/salerec/wcacc/uar untested.
#   7. liquidityriskfactor siblings — si_ratio gave +259. altmanz/aqi/booklev/cashratio untested.
#   8. growthanalystmodel — completely fresh family.
#
# Skip: globaldev (dead -228), industryrrelativevaluefactor (all fitness<1.0),
#        historicalgrowthfactor (dead), systematicRisk (all negative sharpe),
#        Fundamental Scores (all fitness<0.65 historically)
#
# Run: cp parameters_d1_v16.py parameters.py && python3 main.py
# ~90 expressions, ~135 min runtime

from commands import *

BATCH_NAME = 'd1v16'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
        'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B200 = {**BASE, 'universe': 'TOP200'}

DATA = [
    # ── 1. fangma siblings (rvm6 TOP200 gave strong IS) ──────────────────────
    # rvm1
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_rvm_usa_fangma_rvm1,252))'},
    {**BASE, 'code': '-rank(ts_rank(mdl177_fangma_rvm_usa_fangma_rvm1,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_rvm_usa_fangma_rvm1,252))'},
    # mam siblings
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam16,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam16,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam11,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam11,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam6,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam5,252))'},
    # emf siblings
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf20,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf20,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf15,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf4,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf3,252))'},
    # dvm siblings
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_dvm_usa_fangma_dvm4,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_dvm_usa_fangma_dvm4,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_dvm_usa_fangma_dvm1,252))'},

    # ── 2. valueanalystmodel siblings (qva_chgacc gave +643) ─────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_incstmt,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_incstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_finstmt,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_finstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_pegy,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_pegy,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_earnval,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_earnval,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_epmodule,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_epmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_valuation,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_valuation,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_alertrank,252))'},

    # ── 3. valanalystmodel siblings (qva_incstmt +238) ───────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_capexdep,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_epmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_finstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_pegy,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_valuation,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_invsentiment,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_yoychgdebt,252))'},

    # ── 4. momemtumanalystmodel — fresh family ────────────────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_chgnowc,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_chgnowc,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_epsgrwth,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_epsgrwth,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_rskadj,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_chgnowc,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_epsgrwth,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_earnxp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_rskadj,252))'},

    # ── 5. vma2 siblings (vma2_va +66) ───────────────────────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma_ee,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma_em,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma_pm,252))'},

    # ── 6. earningsqualityfactor siblings (uap gave +160) ────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_chgshare,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_salerec,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_wcacc,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_uar,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_rau,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_saleeps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_opincltd,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_chgshare,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_ttmaccu,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_uinv,252))'},

    # ── 7. liquidityriskfactor siblings (si_ratio gave +259) ─────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_altmanz,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_booklev,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_cashratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_curratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_netcashp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_ocfratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_divcov,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_numest,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_si_ratio,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_si_ratio,252))'},

    # ── 8. growthanalystmodel — fresh family ──────────────────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_eps_capex,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_iarsales,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_niroe,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel2_qga_ltepssurprise,252))'},

    # ── 9. earningmomentumfactor400 fresh picks ───────────────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_rev6,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_epsrm,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_numrevy1,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_salesurp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_stockrating,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_y1aepsg,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_fcfroey1p,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_cvfy1eps,252))'},

    # ── 10. garpanalystmodel fresh variants ───────────────────────────────────
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_relgrowth,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_valuation,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_valuation,252))'},
]

print(f"Total expressions queued: {len(DATA)}")
print("  v16: fangma siblings + valueanalystmodel + valanalystmodel + momemtumanalystmodel")
print("       + vma2 + earningsquality + liquidityrisk + growthanalyst + earningmomentum + garp")
print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")
