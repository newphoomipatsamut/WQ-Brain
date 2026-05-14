# parameters_d1_v12.py — D1 batch v12
#
# Strategy: TOP200 fangma family only.
#
# Rationale:
#   - fangma_rvm6 TOP3000: corr 0.87–0.92 (dead) BUT TOP200 (RRNLElmo) corr 0.449, score +496 ✅
#   - fangma_gpam11 TOP3000: corr 0.97–0.99 (dead) → must test TOP200
#   - fangma_mam6 TOP3000: sharpe 1.36, fitness 0.91 (borderline) → TOP200 may fix fitness + corr
#   - Rule confirmed: fangma siblings only viable at TOP200. TOP3000 always corr-toxic vs vmm11.
#
# Skipped (confirmed dead from d1v11):
#   - fangma_emf: best sharpe 1.00, fitness 0.56 — too weak even for TOP200
#   - fangma_dvm: best sharpe 0.84 — dead
#   - fangma_rvm1: sharpe 0.78 — dead
#   - valanalystmodel siblings: all unknown variables
#   - valueanalystmodel: best sharpe 1.12, fitness 0.64 — too weak
#   - vma2 siblings: best sharpe 1.00, fitness 0.74 — too weak
#   - 5yearrelvalue siblings: best sharpe 1.23, fitness 0.76 — below threshold
#   - earningmomentumfactor400: best sharpe 0.71 — dead family
#
# Run: cp parameters_d1_v12.py parameters.py && python3 main.py
# ~16 expressions, ~25 min runtime

from commands import *

B200 = {'neutralization': 'SUBINDUSTRY', 'decay': 6, 'truncation': 0.08,
        'delay': 1, 'region': 'USA', 'universe': 'TOP200'}

DATA = [
    # ── fangma_gpam TOP200 ────────────────────────────────────────────────────
    # gpam11 TOP3000: sharpe 1.89, fitness 1.71, corr 0.97 (dead).
    # gpam11 TOP200 — same vmm11 pattern should apply: lower corr, higher score.
    # gpam10 also tested at TOP3000 (sharpe 1.16–1.20) — worth trying TOP200.
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_gpam_usa_fangma_gpam11,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_gpam_usa_fangma_gpam11,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_gpam_usa_fangma_gpam10,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_gpam_usa_fangma_gpam10,252))'},

    # ── fangma_rvm TOP200 (additional variants) ───────────────────────────────
    # rvm6 zscore TOP200 = RRNLElmo +496 ✅ (already submittable)
    # rvm6 ts_rank TOP200 not yet tested — may score differently
    # rvm1 was dead at TOP3000 (sharpe 0.78) — skip, not worth TOP200 test
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_rvm_usa_fangma_rvm6,252))'},

    # ── fangma_mam TOP200 ─────────────────────────────────────────────────────
    # mam6 TOP3000: sharpe 1.36, fitness 0.91 — borderline, failed fitness cutoff.
    # mam16 TOP3000: sharpe 1.02, fitness 1.01 — just passed fitness but very weak.
    # TOP200 may push fitness over 1.00 for mam6 and clean corr.
    # mam11/mam5 tested at TOP3000 — both weak (sharpe ~0.5). Skip those.
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam6,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_mam_usa_fangma_mam6,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_mam_usa_fangma_mam16,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_mam_usa_fangma_mam16,252))'},

    # ── fangma_emf TOP200 (selective) ────────────────────────────────────────
    # emf25 was the best at TOP3000 (sharpe 1.00, fitness 0.56) — marginal.
    # emf20 next best. Low probability but only 4 expressions — worth a quick check
    # given vmm11 TOP200 scored +639 vs TOP3000 +396 (64% uplift).
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf25,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_emf_usa_fangma_emf25,252))'},
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_emf_usa_fangma_emf20,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_emf_usa_fangma_emf20,252))'},

    # ── fangma_vmm siblings at TOP200 ────────────────────────────────────────
    # vmm11 is the confirmed signal. vmm10 / vmm5 untested at TOP200.
    # vmm11 TOP200 = 9q90GOld +639. vmm10/vmm5 may be worth a quick check.
    {**B200, 'code': '-rank(ts_zscore(mdl177_fangma_vmm_usa_fangma_vmm10,252))'},
    {**B200, 'code': '-rank(ts_rank(mdl177_fangma_vmm_usa_fangma_vmm10,252))'},
]

print(f"Total expressions queued: {len(DATA)}")
print("  v12: fangma TOP200 only — gpam11/10, rvm6 ts_rank, mam6/16, emf25/20, vmm10")
print(f"Estimated runtime: ~{len(DATA) * 1.5:.0f} min")
