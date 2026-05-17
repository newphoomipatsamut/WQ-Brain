# parameters_d1_v11.py
from commands import *

BASE = {
    'neutralization': 'SUBINDUSTRY',
    'decay':          4,
    'truncation':     0.08,
    'delay':          1,
    'universe':       'TOP3000',
    'region':         'USA',
}

# Add TOP500 fallback if naked versions pass cleanly
BASE_TOP500  = {**BASE, 'universe': 'TOP500'}

VARIABLES = [
    # 1. fangma siblings (gpam, rvm, mam, emf, dvm)
    'mdl177_fangma_gpam_usa_fangma_gpam11',
    'mdl177_fangma_gpam_usa_fangma_gpam10',
    'mdl177_fangma_gpam_usa_fangma_gpam5',
    'mdl177_fangma_rvm_usa_fangma_rvm6',
    'mdl177_fangma_rvm_usa_fangma_rvm1',
    'mdl177_fangma_mam_usa_fangma_mam16',
    'mdl177_fangma_mam_usa_fangma_mam11',
    'mdl177_fangma_mam_usa_fangma_mam6',
    'mdl177_fangma_mam_usa_fangma_mam5',
    'mdl177_fangma_emf_usa_fangma_emf28',
    'mdl177_fangma_emf_usa_fangma_emf25',
    'mdl177_fangma_emf_usa_fangma_emf20',
    'mdl177_fangma_emf_usa_fangma_emf15',
    'mdl177_fangma_emf_usa_fangma_emf4',
    'mdl177_fangma_emf_usa_fangma_emf3',
    'mdl177_fangma_dvm_usa_fangma_dvm4',
    'mdl177_fangma_dvm_usa_fangma_dvm1',
    
    # 2. valanalystmodel siblings (VA-1 qva_incstmt +238 verified working)
    'mdl177_valanalystmodel_qva_shortfall',
    'mdl177_valanalystmodel_qva_finstmt',
    'mdl177_valanalystmodel_qva_yoychgdebt',
    'mdl177_valanalystmodel_qva_capexdep',
    'mdl177_valanalystmodel_qva_epmodule',
    'mdl177_valanalystmodel_qva_invsentiment',
    'mdl177_valanalystmodel_qva_valuation',
    'mdl177_valanalystmodel_qva_pegy',
    
    # 3. valueanalystmodel (Different model from valanalystmodel)
    'mdl177_valueanalystmodel_qva_chgacc',
    'mdl177_2_valueanalystmodel_qva_composite',
    'mdl177_valueanalystmodel_qva_finstmt',
    'mdl177_valueanalystmodel_qva_epmodule',
    'mdl177_valueanalystmodel_qva_valuation',
    'mdl177_valueanalystmodel_qva_alertrank',
    'mdl177_valueanalystmodel_qva_pegy',
    'mdl177_valueanalystmodel_qva_earnval',
    
    # 4. vma2 siblings (VMA-2 vma2_va +66 verified working)
    'mdl177_2_vma2_vma2_ma',
    'mdl177_2_vma2_vma2_ma_ee',
    'mdl177_2_vma2_vma2_ma_em',
    'mdl177_2_vma2_vma2_ma_pm',
    
    # 5. 5yearrelativevaluefactor siblings (rel5yfwdep +385, rel5ybp +238 verified working)
    'mdl177_2_5yearrelativevaluefactor_rel5ycoreepsp',
    'mdl177_2_5yearrelativevaluefactor_rel5yep',
    'mdl177_2_5yearrelativevaluefactor_rel5ysp',
    
    # 6. earningmomentumfactor400 (Fresh analyst momentum family)
    'mdl177_2_earningmomentumfactor400_rev6',
    'mdl177_2_earningmomentumfactor400_numrevy1',
    'mdl177_2_earningmomentumfactor400_numrevq1',
    'mdl177_2_earningmomentumfactor400_epsrm',
    'mdl177_2_earningmomentumfactor400_fqsurs_std',
    'mdl177_2_earningmomentumfactor400_salesurp',
    'mdl177_2_earningmomentumfactor400_stockrating',
    'mdl177_2_earningmomentumfactor400_y1aepsg',
    'mdl177_2_earningmomentumfactor400_cvfy1eps',
    'mdl177_2_earningmomentumfactor400_fcfroey1p',
]

TEMPLATES = [
    # Tier 1 — Confirmed working
    "-rank(ts_rank({v},252))",
    "-rank(ts_rank({v},252)*rank(ts_delta(close,21)))",
]

DATA = [
    {**BASE, 'code': t.format(v=v)}
    for v in VARIABLES
    for t in TEMPLATES
]

print(f"Total expressions queued: {len(DATA)}")
print(f"Estimated runtime: ~{int(len(DATA) * 1.5)} minutes")