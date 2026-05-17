# parameters_d1_v17a.py — D1 batch v17a
#
# Strategy: Full sweep of ALL untested Model fields (part A of 2)
# Fields: 208 | Estimated runtime: ~312 min
#
# Skipped families (confirmed dead):
#   - globaldevnorthamerica (score -228)
#   - industryrrelativevaluefactor (ALL fitness<1.0)
#
# Run: cp parameters_d1_v17a.py parameters.py && python3 main.py

from commands import *

BATCH_NAME = 'd1v17a'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
        'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B200 = {**BASE, 'universe': 'TOP200'}

DATA = [

    # ── 5yearrelativevaluefactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5ycoreepsp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5yep,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5ysp,252))'},

    # ── deepvaluefactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_coreepsp,252))'},

    # ── deepvaluefactor_curep (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_curep_alt,252))'},

    # ── deepvaluefactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_divyield,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ebitdap,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ebop,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_nnastp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_past,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmcapexp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmcfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmepa,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmepb,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmgfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmsaleev,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluefactor_ttmsp,252))'},

    # ── deepvaluemodel2_dv (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluemodel2_dv_currroe,252))'},

    # ── deepvaluemodel (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluemodel_indidivy,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_deepvaluemodel_ttmfcev,252))'},

    # ── earningmomentumfactor400 (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_cvfy1eps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_cvy2eps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_dypeg,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_epsrm,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_fcfroey1p,252))'},

    # ── earningmomentumfactor400_fqsurs (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_fqsurs_std,252))'},

    # ── earningmomentumfactor400 (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_lagegp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_numrevq1,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_numrevy1,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_perg,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_rev6,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_salesurp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_stdvfy1epsp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_stockrating,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_y1aepsg,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_y2aepsg,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningmomentumfactor400_y2repsg,252))'},

    # ── earningsmomentummodel_fc (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsmomentummodel_fc_rev3y2,252))'},

    # ── earningsqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_chgshare,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_ttmaccu,252))'},

    # ── earningsqualityfactor_uap (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_uap_alt,252))'},

    # ── earningsqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_uinv,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_earningsqualityfactor_yoychgaa,252))'},

    # ── garpanalystmodel_qgp (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_alert,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_avgrating,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_relgrowth,252))'},

    # ── garpanalystmodel_qgp_relgrowth (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_relgrowth_alt,252))'},

    # ── garpanalystmodel_qgp (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_relpegy,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_valuation,252))'},

    # ── garpanalystmodel_qgp_vfpriceratio (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_garpanalystmodel_qgp_vfpriceratio_alt,252))'},

    # ── growthanalystmodel2_qga (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel2_qga_ltepssurprise,252))'},

    # ── growthanalystmodel_qga (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_composite,252))'},

    # ── growthanalystmodel_qga_eps (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_eps_capex,252))'},

    # ── growthanalystmodel_qga (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_iarsales,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_niroe,252))'},

    # ── historicalgrowthfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chg3ycfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chg3yepsp,252))'},

    # ── historicalgrowthfactor_chg3yepsp (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chg3yepsp_alt,252))'},

    # ── historicalgrowthfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chg3yocfast,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chg3yocfp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chgcf,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chgis,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chgnpm,252))'},

    # ── historicalgrowthfactor_chgnpm (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chgnpm_alt,252))'},

    # ── historicalgrowthfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_chgopm,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_div5yg,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_pctchg3ycf,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_pctchg3yeps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_pctchgeps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_pctchgfcf,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_pctchgqtrast,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_pctchgqtrsales,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_reinrate,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_saleg5y,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_salesaccel4q,252))'},

    # ── historicalgrowthfactor_salesaccel4q (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_historicalgrowthfactor_salesaccel4q_alt,252))'},

    # ── industryrelativevaluefactor_curindcfp (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_industryrelativevaluefactor_curindcfp_,252))'},

    # ── industryrelativevaluefactor_curindfcfp (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_industryrelativevaluefactor_curindfcfp_,252))'},

    # ── industryrelativevaluefactor_curindocta (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_industryrelativevaluefactor_curindocta_,252))'},

    # ── industryrelativevaluefactor_curindoctp (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_industryrelativevaluefactor_curindoctp_,252))'},

    # ── liquidityriskfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_altmanz,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_aqi,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_atmcallvol,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_bap20d,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_bidask20d,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_booklev,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_cashratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_covol,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_curratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_cvvolp20d,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_dfl,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_divcov,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_gear,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_intcov,252))'},

    # ── liquidityriskfactor_intcov (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_intcov_alt,252))'},

    # ── liquidityriskfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_liqcoeff,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_mktcappera,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_monchsip,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_netcashp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_nlprice,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_numest,252))'},

    # ── liquidityriskfactor_numest (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_numest_alt,252))'},

    # ── liquidityriskfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_ocfratio,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_ohlsonscore,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_pcurlia,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_volto,252))'},

    # ── managementqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_acp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_adverint,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_astto,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_capacq,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_capexast,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_capexsale,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_cashburnrate,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_cashc,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_cashsale,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_cfroi,252))'},

    # ── managementqualityfactor_cfroi (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_cfroi_alt,252))'},

    # ── managementqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_chgnoa,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_chgreccast,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_cllev,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_fcfsale,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_fwdroe,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_investto,252))'},

    # ── managementqualityfactor_investto (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_investto_alt,252))'},

    # ── managementqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_min1ygrossmargin,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_min1yopmargin,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_min2ygrossmargin,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_min3yopmargin,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_netdebt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_niroe,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_nopatmargin,252))'},

    # ── managementqualityfactor_nopatmargin (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_nopatmargin_alt,252))'},

    # ── managementqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_npm,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_ocfroi,252))'},

    # ── managementqualityfactor_ollev (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_ollev_alt,252))'},

    # ── managementqualityfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_opmb,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_pinoa,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_revper,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_roe,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_wcinv,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_yoychggpm,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_yoychgroa,252))'},

    # ── momemtumanalystmodel_qma (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_chgnowc,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_earnxp,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_eplinkage,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_epsgrwth,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_repearnmom,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_momemtumanalystmodel_qma_rskadj,252))'},

    # ── pricemomentumfactor (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentumfactor_actrtn2m,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentumfactor_pctabv260low,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentumfactor_pvt51w,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentumfactor_rationalalpha,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentumfactor_skew90cortn,252))'},

    # ── pricemomentummodel2_indrelrtn5d (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentummodel2_indrelrtn5d_,252))'},

    # ── pricemomentummodel_pmm (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_pricemomentummodel_pmm_composite,252))'},

    # ── put_put (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_put_put_qualmod,252))'},

    # ── relativevaluemodel (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_relativevaluemodel_roe,252))'},

    # ── relativevaluemodel_rvm (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_relativevaluemodel_rvm_composite,252))'},

    # ── sensitivityfactor400 (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_ag,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_ceroe,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_crp,252))'},

    # ── sensitivityfactor400_dm (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_dm_alt,252))'},

    # ── sensitivityfactor400 (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_impvol,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_nasales,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_sensitivityfactor400_oilprice,252))'},

    # ── surpriseanalystmodel_qsa (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_surpriseanalystmodel_qsa_efficiency,252))'},

    # ── surpriseanalystmodel_qsa_efficiency (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_surpriseanalystmodel_qsa_efficiency_alt,252))'},

    # ── surpriseanalystmodel_qsa (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_surpriseanalystmodel_qsa_estexpect,252))'},

    # ── surpriseanalystmodel_qsa_surpsn (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_surpriseanalystmodel_qsa_surpsn_alt,252))'},

    # ── valanalystmodel_qva (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valanalystmodel_qva_composite,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valanalystmodel_qva_epmodule,252))'},

    # ── valanalystmodel_qva_incstmt (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valanalystmodel_qva_incstmt_alt,252))'},

    # ── valueanalystmodel_qva (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valueanalystmodel_qva_alertrank,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valueanalystmodel_qva_finstmt,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valueanalystmodel_qva_pegy,252))'},

    # ── valuemomentummodel (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valuemomentummodel_earningsexpectationmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valuemomentummodel_earningsvaluationmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valuemomentummodel_financialstatementmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valuemomentummodel_managementsignalingmodule,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valuemomentummodel_reportedenarningsmomentummodule,252))'},

    # ── valuemomentummodel_vm (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_valuemomentummodel_vm_compositesn,252))'},

    # ── vma2_vma2 (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma,252))'},

    # ── vma2_vma2_ma (mdl177_2_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma_ee,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma_em,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2_vma2_vma2_ma_pm,252))'},

    # ── 2deepvaluefactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_2deepvaluefactor_cashsev,252))'},

    # ── deepvaluefactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_bp,252))'},

    # ── deepvaluefactor_bp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_bp_alt,252))'},

    # ── deepvaluefactor_cashsev (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_cashsev_alt,252))'},

    # ── deepvaluefactor_divyield (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_divyield_alt,252))'},

    # ── deepvaluefactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ebitdaev,252))'},

    # ── deepvaluefactor_ebitdaev (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ebitdaev_alt,252))'},

    # ── deepvaluefactor_ebop (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ebop_alt,252))'},

    # ── deepvaluefactor_indidivy (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_indidivy_alt,252))'},

    # ── deepvaluefactor_navp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_navp_alt,252))'},

    # ── deepvaluefactor_nnastp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_nnastp_alt,252))'},

    # ── deepvaluefactor_proformaep (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_proformaep_alt,252))'},

    # ── deepvaluefactor_ttmepb (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ttmepb_alt,252))'},

    # ── deepvaluefactor_ttmfcev (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ttmfcev_alt,252))'},

    # ── deepvaluefactor_ttmgfp (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ttmgfp_alt,252))'},

    # ── deepvaluefactor_ttmsaleev (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_ttmsaleev_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_cvfy1eps,252))'},
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_cvfy2eps,252))'},

    # ── earningmomentumfactor_cvfy2eps (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_cvfy2eps_alt,252))'},

    # ── earningmomentumfactor (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_dypeg,252))'},

    # ── earningmomentumfactor_dypeg (mdl177_) ──
    {**BASE, 'code': '-rank(ts_zscore(mdl177_earningmomentumfactor_dypeg_alt,252))'},
]

print(f"Total expressions queued: {len(DATA)}")
print(f"  v17a: Full Model sweep part A — 208 fields")
print(f"Estimated runtime: ~{len(DATA)*1.5:.0f} min")
