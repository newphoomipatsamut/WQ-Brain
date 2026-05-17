# parameters_d1_v17b.py — D1 batch v17b
#
# Strategy: Full sweep of ALL untested Model fields (part B of 2)
# Fields: 209 | Estimated runtime: ~314 min
#
# Skipped families (confirmed dead):
#   - globaldevnorthamerica (score -228)
#   - industryrrelativevaluefactor (ALL fitness<1.0)
#
# Run: cp parameters_d1_v17b.py parameters.py && python3 main.py

from commands import *

BATCH_NAME = 'd1v17b'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
        'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B200 = {**BASE, 'universe': 'TOP200'}

DATA = [

    # ── earningmomentumfactor_egp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_egp_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_fcfroey1p,252))'},

    # ── earningmomentumfactor_fcfroey1p (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_fcfroey1p_alt,252))'},

    # ── earningmomentumfactor_fqsurs (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_fqsurs_std,252))'},

    # ── earningmomentumfactor_fqsurs_std (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_fqsurs_std_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_numrevy1,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_perg,252))'},

    # ── earningmomentumfactor_perg (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_perg_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_qepsferr,252))'},

    # ── earningmomentumfactor_rev1q1 (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_rev1q1_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_rev3y1,252))'},

    # ── earningmomentumfactor_rev3y1 (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_rev3y1_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_rev6,252))'},

    # ── earningmomentumfactor_rev6 (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_rev6_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_salesurp,252))'},

    # ── earningmomentumfactor_salesurp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_salesurp_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_stockrating,252))'},

    # ── earningmomentumfactor_stockrating (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_stockrating_alt,252))'},

    # ── earningmomentumfactor_sucf (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_sucf_alt,252))'},

    # ── earningmomentumfactor_sue (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_sue_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_surp,252))'},

    # ── earningmomentumfactor_surp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_surp_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_y2repsg,252))'},

    # ── earningmomentumfactor_y2repsg (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_y2repsg_alt,252))'},

    # ── earningsmomentummodel_fc_egp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsmomentummodel_fc_egp_alt,252))'},

    # ── earningsmomentummodel_fc_fqsurstd (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsmomentummodel_fc_fqsurstd_alt,252))'},

    # ── earningsmomentummodel_fc_y2repsg (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsmomentummodel_fc_y2repsg_alt,252))'},

    # ── earningsqualityfactor_chgsagasale (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_chgsagasale_alt,252))'},

    # ── earningsqualityfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_chgshare,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_opincltd,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_rau,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_saleeps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_salegpm,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_salerec,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_uar,252))'},

    # ── earningsqualityfactor_uar (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_uar_alt,252))'},

    # ── earningsqualityfactor_uinv (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_uinv_alt,252))'},

    # ── earningsqualityfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_wcacc,252))'},

    # ── earningsqualityfactor_wcacc (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningsqualityfactor_wcacc_alt,252))'},

    # ── fa (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_actrtn1m,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_astto,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_capacq,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_cashsev,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_chgnoa,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_chgocfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_chgsagasale,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_curratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_divcov,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_ebitdaev,252))'},

    # ── fa_fc (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_fc_egp,252))'},

    # ── fa (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_fcfroey1p,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_fcfroi,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_flowratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_monchsip,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_netcashp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_nlvolcap,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_nnastp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_ocfratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fa_ratrev6m,252))'},

    # ── fangma_dvm_usa_fangma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_dvm_usa_fangma_dvm1,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_dvm_usa_fangma_dvm4,252))'},

    # ── fangma_emf_usa_fangma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf15,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf20,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf28,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf3,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf4,252))'},

    # ── fangma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_gpam11,252))'},

    # ── fangma_gpam_usa_fangma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_gpam_usa_fangma_gpam10,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_gpam_usa_fangma_gpam5,252))'},

    # ── fangma_mam_usa_fangma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam11,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam16,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam5,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam6,252))'},

    # ── fangma_rvm_usa_fangma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_fangma_rvm_usa_fangma_rvm1,252))'},

    # ── garpanalystmodel_qgp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_alert,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_avgrating,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_growthval,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_garpanalystmodel_qgp_valuation,252))'},

    # ── growthanalystmodel_qga_iarsales (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_growthanalystmodel_qga_iarsales_alt,252))'},

    # ── historicalgrowthfactor_chg3ycfp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chg3ycfp_alt,252))'},

    # ── historicalgrowthfactor_chg3yeps (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chg3yeps_alt,252))'},

    # ── historicalgrowthfactor_chg3yepsast (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chg3yepsast_alt,252))'},

    # ── historicalgrowthfactor_chg3yepsp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chg3yepsp_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chg3yocfast,252))'},

    # ── historicalgrowthfactor_chg3yocfast (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chg3yocfast_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgars,252))'},

    # ── historicalgrowthfactor_chgars (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgars_alt,252))'},

    # ── historicalgrowthfactor_chgcf (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgcf_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgcfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgeps,252))'},

    # ── historicalgrowthfactor_chgeps (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgeps_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgepsp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgis,252))'},

    # ── historicalgrowthfactor_chgis (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgis_alt,252))'},

    # ── historicalgrowthfactor_chgocf (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgocf_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgocfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgopm,252))'},

    # ── historicalgrowthfactor_chgopm (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_chgopm_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_cv4qocf3y,252))'},

    # ── historicalgrowthfactor_fcfequity (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_fcfequity_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchg3ycf,252))'},

    # ── historicalgrowthfactor_pctchg3ycf (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchg3ycf_alt,252))'},

    # ── historicalgrowthfactor_pctchg3yeps (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchg3yeps_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchgastto,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchgcf,252))'},

    # ── historicalgrowthfactor_pctchgcf (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchgcf_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchgeps,252))'},

    # ── historicalgrowthfactor_pctchgeps (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_pctchgeps_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_reinrate,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_salesaccel4q,252))'},

    # ── historicalgrowthfactor_slope4qcf3y (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_slope4qcf3y_alt,252))'},

    # ── historicalgrowthfactor_slope4qeps3y (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_slope4qeps3y_alt,252))'},

    # ── historicalgrowthfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_susgrowth,252))'},

    # ── historicalgrowthfactor_susgrowth (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_susgrowth_alt,252))'},

    # ── historicalgrowthfactor_totalsaleg (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_historicalgrowthfactor_totalsaleg_alt,252))'},

    # ── industryrelativevaluefactor_curindcfp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_industryrelativevaluefactor_curindcfp_alt,252))'},

    # ── industryrelativevaluefactor_curindfcf p (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_industryrelativevaluefactor_curindfcf p_alt,252))'},

    # ── industryrelativevaluefactor_curindocfp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_industryrelativevaluefactor_curindocfp_alt,252))'},

    # ── industryrelativevaluefactor_curindsp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_industryrelativevaluefactor_curindsp_,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_industryrelativevaluefactor_curindsp_alt,252))'},

    # ── liquidityriskfactor_altmanz (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_altmanz_alt,252))'},

    # ── liquidityriskfactor_aqi (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_aqi_alt,252))'},

    # ── liquidityriskfactor_bdi (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_bdi_alt,252))'},

    # ── liquidityriskfactor_booklev (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_booklev_alt,252))'},

    # ── liquidityriskfactor_cashratio (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_cashratio_alt,252))'},

    # ── liquidityriskfactor_divcov (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_divcov_alt,252))'},

    # ── liquidityriskfactor_flowratio (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_flowratio_alt,252))'},

    # ── liquidityriskfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_growdura,252))'},

    # ── liquidityriskfactor_growdura (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_growdura_alt,252))'},

    # ── liquidityriskfactor_impduration (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_impduration_alt,252))'},

    # ── liquidityriskfactor_mad3yttmni (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_mad3yttmni_alt,252))'},

    # ── liquidityriskfactor_milliq (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_milliq_alt,252))'},

    # ── liquidityriskfactor_mktcappera (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_mktcappera_alt,252))'},

    # ── liquidityriskfactor_netcashp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_netcashp_alt,252))'},

    # ── liquidityriskfactor_ocfratio (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_ocfratio_alt,252))'},

    # ── liquidityriskfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_ohlsonscore,252))'},

    # ── liquidityriskfactor_ohlsonscore (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_ohlsonscore_alt,252))'},

    # ── liquidityriskfactor_pcurlia (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_pcurlia_alt,252))'},

    # ── liquidityriskfactor_qr (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_qr_alt,252))'},

    # ── liquidityriskfactor_si (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_si_ratio,252))'},

    # ── liquidityriskfactor_sip (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_sip_alt,252))'},

    # ── liquidityriskfactor_tobinq (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_tobinq_alt,252))'},

    # ── liquidityriskfactor_voldiff_pc (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_voldiff_pc_alt,252))'},

    # ── liquidityriskfactor_yoychgcr (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_yoychgcr_alt,252))'},

    # ── liquidityriskfactor_yoychgda (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_liquidityriskfactor_yoychgda_alt,252))'},

    # ── momemtumanalystmodel_qma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_chgnowc,252))'},

    # ── momemtumanalystmodel_qma_earnxp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_earnxp_alt,252))'},

    # ── momemtumanalystmodel_qma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_epsgrwth,252))'},

    # ── momemtumanalystmodel_qma_epsgrwth (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_epsgrwth_alt,252))'},

    # ── momemtumanalystmodel_qma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_rskadj,252))'},

    # ── momemtumanalystmodel_qma_ttmfcfchg (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_momemtumanalystmodel_qma_ttmfcfchg_alt,252))'},

    # ── multi_factor_acceleration_score (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_multi_factor_acceleration_score_derivative,252))'},

    # ── multi_factor_static_score (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_multi_factor_static_score_derivative,252))'},

    # ── pricemomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentumfactor_actrtn1m,252))'},

    # ── pricemomentumfactor_indrelrtn5d (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentumfactor_indrelrtn5d_alt,252))'},

    # ── pricemomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentumfactor_varresirtn,252))'},

    # ── pricemomentummodel_indrelrtn5d (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentummodel_indrelrtn5d_,252))'},

    # ── pricemomentummodel_pmm (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentummodel_pmm_composite,252))'},

    # ── pricemomentummodel (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentummodel_rationalalpha,252))'},

    # ── pricemomentummodel_relpricestrength (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentummodel_relpricestrength_,252))'},

    # ── pricemomentummodel_voldiff (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_pricemomentummodel_voldiff_pc,252))'},

    # ── put_put (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_put_put_indepsp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_put_put_momod,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_put_put_siratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_put_put_valmod,252))'},

    # ── putput_siratio (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_putput_siratio_alt,252))'},

    # ── relativevaluemodel_rvm (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_relativevaluemodel_rvm_composite,252))'},

    # ── v1_400 (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_capexast,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_cashburnrate,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_cfroi,252))'},

    # ── v1_400_curindsp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_curindsp_,252))'},

    # ── v1_400_fc (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_fc_proformaep,252))'},

    # ── v1_400_indrelrtn5d (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_indrelrtn5d_,252))'},

    # ── v1_400 (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_nlvolcap,252))'},

    # ── v1_400_pr (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_pr_1536,252))'},

    # ── v1_400 (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_ptchgqtrast,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_reinrate,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_sue,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_tobinq,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_ttmaccu,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_ttmsaleev,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_v1_400_uar,252))'},

    # ── valanalystmodel_qva (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_capexdep,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_epmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_finstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_invsentiment,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_pegy,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_valuation,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valanalystmodel_qva_yoychgdebt,252))'},

    # ── valueanalystmodel_ccaghc (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_ccaghc_avq,252))'},

    # ── valueanalystmodel_qva (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_alertrank,252))'},

    # ── valueanalystmodel_qva_alertrank (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_alertrank_alt,252))'},

    # ── valueanalystmodel_qva_capexdep (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_capexdep_alt,252))'},

    # ── valueanalystmodel_qva_cashflow (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_cashflow_alt,252))'},

    # ── valueanalystmodel_qva_chginv (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_chginv_alt,252))'},

    # ── valueanalystmodel_qva_earnquality (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_earnquality_alt,252))'},

    # ── valueanalystmodel_qva (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_earnval,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_epmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_finstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_incstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_pegy,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_valuation,252))'},

    # ── valueanalystmodel_qva_valuation (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_valuation_alt,252))'},

    # ── valuemomentummodel (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valuemomentummodel_earningsqualitymodule,252))'},

    # ── valuemomentummodel_vm (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_valuemomentummodel_vm_compositesn,252))'},

    # ── vra (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_vra_earningsqualitymodule,252))'},

    # ── vra_qma (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_vra_qma_epsgrwth,252))'},

    # ── vra_qva (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_vra_qva_valuation,252))'},
]

print(f"Total expressions queued: {len(DATA)}")
print(f"  v17b: Full Model sweep part B — 209 fields")
print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")
