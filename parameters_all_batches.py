# parameters_all_batches.py
# ALL POST-IQC2026 BATCHES — Single login run (v2, corrected field names)
# Generated: 2026-05-24
#
# Changes from v1:
#   - Fixed 5 wrong field names (niroe, valanalyst, earningsmomentum, pricemomentum, industryrr)
#   - Fixed si_ratio missing _2_
#   - Dropped 5 fields confirmed not in subscription (rau, cllev, investto_alt, curindocta_, curindoctp_)
#
# Batches (in priority order):
#   1. fix_fitness     (28) — CLV, ADV20, VWAP Fitness Block repairs
#   2. 5yr_rv_new      (20) — 5 untested 5yr RelValue fields
#   3. short_snt_devna (24) — 4 devNorthAmerica short sentiment fields
#   4. backlog_retest  (37) — remaining backlog fields (corrected names, dropped unavailable)
#
# Run: cp parameters_all_batches.py parameters.py && python3 main.py

from commands import *
BATCH_NAME = 'all_batches_v2'

BASE = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08, 'delay': 1, 'region': 'USA', 'universe': 'TOP3000'}
B500 = {**BASE, 'universe': 'TOP500'}
B200 = {**BASE, 'universe': 'TOP200'}

DATA = [

    # ════════════════════════════════════════════════════════════════════════════
    # BATCH 1 — fix_fitness (28 expressions)
    # ════════════════════════════════════════════════════════════════════════════

    # ── CLV Reversion ── confirmed: hump kills signal, decay5 best (sharpe=1.82 fit=0.96)
    {**BASE, 'code': '-rank(hump(((2*close-high-low)/(high-low))*ts_rank(volume,5)))'},
    {**B500, 'code': '-rank(hump(((2*close-high-low)/(high-low))*ts_rank(volume,5)))'},
    {**B200, 'code': '-rank(hump(((2*close-high-low)/(high-low))*ts_rank(volume,5)))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**B500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 5))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume,5), 10))'},
    {**BASE, 'code': '-rank(hump(((2*close-high-low)/(high-low))*ts_rank(volume,3)))'},

    # ── CLV+Vol/ADV20 ── decay5 TOP3000 sharpe=1.65 fit=0.89
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**B500, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**B200, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*(volume/adv20), 5))'},
    {**BASE, 'code': '-rank(hump(((2*close-high-low)/(high-low))*(volume/adv20)))'},
    {**B500, 'code': '-rank(hump(((2*close-high-low)/(high-low))*(volume/adv20)))'},
    {**BASE, 'code': '-rank(ts_decay_linear(((2*close-high-low)/(high-low))*ts_rank(volume/adv20,10), 5))'},

    # ── ADV20 Reversion ── decay10 TOP500 sharpe=1.82 fit=0.97; hump TOP3000 sharpe=1.93 fit=0.85
    {**BASE, 'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},
    {**B500, 'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},
    {**B200, 'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 10))'},
    {**BASE, 'code': '-rank(ts_decay_linear(ts_delta(close,1)/adv20, 5))'},
    {**BASE, 'code': '-rank(hump(ts_delta(close,1)/adv20))'},
    {**BASE, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},
    {**B200, 'code': '-rank(ts_rank(ts_delta(close,1)/adv20, 21))'},

    # ── VWAP Zscore × Volume ──
    {**BASE, 'code': '-rank(ts_decay_linear(ts_zscore((close-vwap)/vwap, 20)*rank(volume), 10))'},
    {**B500, 'code': '-rank(ts_decay_linear(ts_zscore((close-vwap)/vwap, 20)*rank(volume), 10))'},
    {**BASE, 'code': '-rank(ts_decay_linear(ts_zscore((close-vwap)/vwap, 20)*rank(volume), 5))'},
    {**BASE, 'code': '-rank(ts_decay_linear(ts_zscore((close-vwap)/vwap, 10)*rank(volume), 5))'},
    {**BASE, 'code': '-rank(hump(ts_zscore((close-vwap)/vwap, 20)*rank(volume)))'},
    {**B500, 'code': '-rank(hump(ts_zscore((close-vwap)/vwap, 20)*rank(volume)))'},
    {**BASE, 'code': '-rank(ts_rank((close-vwap)/vwap, 20)*rank(volume))'},
    {**B200, 'code': '-rank(ts_rank((close-vwap)/vwap, 20)*rank(volume))'},

    # ════════════════════════════════════════════════════════════════════════════
    # BATCH 2 — 5yr_rv_new (20 expressions)
    # ════════════════════════════════════════════════════════════════════════════

    {**BASE, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 252))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5ycfp, 21) * rank(ts_delta(close, 5)))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5yocfp, 21) * rank(ts_delta(close, 5)))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5yebitdap, 21) * rank(ts_delta(close, 5)))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 252))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5yfcfp, 21) * rank(ts_delta(close, 5)))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ydivp, 252))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_2_5yearrelativevaluefactor_rel5ydivp, 252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_5yearrelativevaluefactor_rel5ydivp, 252))'},
    {**BASE, 'code': '-rank(ts_decay_linear(mdl177_2_5yearrelativevaluefactor_rel5ydivp, 21) * rank(ts_delta(close, 5)))'},

    # ════════════════════════════════════════════════════════════════════════════
    # BATCH 3 — short_snt_devna (24 expressions)
    # ════════════════════════════════════════════════════════════════════════════

    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_days_to_cover, 63))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_days_to_cover, 63))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_days_to_cover, 63))'},
    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_days_to_cover, 21))'},
    {**BASE, 'code': 'rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_days_to_cover, 63))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_devnorthamericashortsentimentfactor_days_to_cover, 63))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_benchmark_fee, 63))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_benchmark_fee, 63))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_benchmark_fee, 63))'},
    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_benchmark_fee, 21))'},
    {**BASE, 'code': 'rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_benchmark_fee, 63))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_devnorthamericashortsentimentfactor_benchmark_fee, 63))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_act_util, 63))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_act_util, 63))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_act_util, 63))'},
    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_act_util, 21))'},
    {**BASE, 'code': 'rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_act_util, 63))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_devnorthamericashortsentimentfactor_act_util, 63))'},

    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_conc_ratio, 63))'},
    {**B500, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_conc_ratio, 63))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_conc_ratio, 63))'},
    {**BASE, 'code': '-rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_conc_ratio, 21))'},
    {**BASE, 'code': 'rank(ts_rank(mdl177_devnorthamericashortsentimentfactor_conc_ratio, 63))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_devnorthamericashortsentimentfactor_conc_ratio, 63))'},

    # ════════════════════════════════════════════════════════════════════════════
    # BATCH 4 — backlog_retest (37 expressions, corrected + pruned)
    # Dropped: rau, cllev, investto_alt, curindocta_, curindoctp_ (not in subscription)
    # Fixed:   si_ratio (+_2_), niroe (→growthanalyst), valanalyst, earningsmomentum,
    #          pricemomentum (momemtum typo), industryrr (double-r typo)
    # ════════════════════════════════════════════════════════════════════════════

    # ── indrelcroe_ — Sharpe 1.48, Fitness 0.98 in prior test ───────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_managementqualityfactor_indrelcroe_, 252)))'},
    {**B500, 'code': '-rank(hump(ts_rank(mdl177_2_managementqualityfactor_indrelcroe_, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_indrelcroe_, 252))'},
    {**B200, 'code': '-rank(hump(ts_rank(mdl177_2_managementqualityfactor_indrelcroe_, 252)))'},

    # ── pdy_alt ──────────────────────────────────────────────────────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},
    {**B500, 'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_pdy_alt, 252))'},
    {**B200, 'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_pdy_alt, 252)))'},

    # ── si_ratio — FIXED: mdl177_2_liquidityriskfactor_si_ratio ─────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_liquidityriskfactor_si_ratio, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_liquidityriskfactor_si_ratio, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_2_liquidityriskfactor_si_ratio, 252)))'},
    {**B200, 'code': 'rank(ts_zscore(mdl177_2_liquidityriskfactor_si_ratio, 252))'},

    # ── niroe — FIXED: mdl177_2_growthanalystmodel_qga_niroe ─────────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_growthanalystmodel_qga_niroe, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_growthanalystmodel_qga_niroe, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_2_growthanalystmodel_qga_niroe, 252)))'},

    # ── revper ───────────────────────────────────────────────────────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_managementqualityfactor_revper, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_revper, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_2_managementqualityfactor_revper, 252)))'},

    # ── adverint ─────────────────────────────────────────────────────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_managementqualityfactor_adverint, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_managementqualityfactor_adverint, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_2_managementqualityfactor_adverint, 252)))'},

    # ── qva_incstmt — FIXED: mdl177_valueanalystmodel_qva_incstmt_alt ───────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_valueanalystmodel_qva_incstmt_alt, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_valueanalystmodel_qva_incstmt_alt, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_valueanalystmodel_qva_incstmt_alt, 252)))'},

    # ── fc_rev3y2 — FIXED: mdl177_earningsmomemtummodel_fc_rev3y2_alt ───────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_earningsmomemtummodel_fc_rev3y2_alt, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_earningsmomemtummodel_fc_rev3y2_alt, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_earningsmomemtummodel_fc_rev3y2_alt, 252)))'},

    # ── navp_alt ─────────────────────────────────────────────────────────────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_deepvaluefactor_navp_alt, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_deepvaluefactor_navp_alt, 252))'},
    {**BASE, 'code': 'rank(hump(ts_rank(mdl177_deepvaluefactor_navp_alt, 252)))'},

    # ── indrelrtn5d — FIXED: mdl177_2_pricemomemtummodel2_indrelrtn5d_ ──────────
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_pricemomemtummodel2_indrelrtn5d_, 252)))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_pricemomemtummodel2_indrelrtn5d_, 252))'},
    {**BASE, 'code': '-rank(hump(ts_rank(mdl177_2_pricemomemtummodel2_indrelrtn5d_, 63)))'},

    # ── industryrelativevaluefactor — FIXED: double-r in industryrrelative ───────
    # curindocta_ and curindoctp_ dropped (not in subscription)
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_industryrrelativevaluefactor_curindfcfp_, 252))'},
    {**B200, 'code': 'rank(ts_zscore(mdl177_2_industryrrelativevaluefactor_curindfcfp_, 252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_2_industryrrelativevaluefactor_curindcfp_, 252))'},

]

print(f"Total expressions queued: {len(DATA)}")
print("  Batches: fix_fitness | 5yr_rv_new | short_snt_devna | backlog_retest (corrected)")
print(f"  Estimated runtime: ~{len(DATA)*1.5:.0f} min (~{len(DATA)*1.5/60:.1f} hours)")
