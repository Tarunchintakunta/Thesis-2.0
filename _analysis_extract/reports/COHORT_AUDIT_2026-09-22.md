# Cohort requirement audit — 2026-09-22 (working tree)

**Goal:** 12 theses (Kasi excluded) to honest CA2 research-scope readiness + 3–5 evals + GENAI_HANDOFF; rubric aim 70%+ characteristics (not forced perfect marks).  
**Verdict this file:** **NOT COMPLETE** — do not UpdateGoal→complete until every row below is Demonstrated or explicitly dated-out-of-scope with over-claim removed.

## Cross-cutting requirements

| Requirement | Evidence | Status |
|-------------|----------|--------|
| 12× GENAI_HANDOFF.md | all 12 paths exist | **Demonstrated** |
| Handoff after ×3 packs | per-thesis finals/equiv on disk | **Demonstrated** (depth varies — see below) |
| Baseline comparison when CA2 defines baseline | handoffs §8 | **Mostly Demonstrated** |
| Honest negative results retained | Yash reduction; Varun alloc Acc≪Lifecycle; Mehak MHSA | **Demonstrated** |
| Single AWS slot destroy-after | `AWS_SLOT_LOCK.md` = FREE after Varun destroy | **Demonstrated** |
| All theses CA2 research-scope 100% (full proposal limbs) | scoreboard + reviews | **Not achieved** (lite/deferred limbs remain) |

## Per-thesis (abbrev)

| Thesis | ×3 packs | Hard residual vs full proposal match |
|--------|----------|--------------------------------------|
| Mehak | gct final_1–3 | Met floor if MHSA-negative kept |
| Vish | final_1–3 | Met floor |
| Varun | r4+r5 independent (+ archival r1–3) | Independence **closed**; alloc Acc negative vs Lifecycle retained |
| Vikas | campaign E1–E3 | P4 quarantined |
| Chaitanya | conf n30 ×3 | H3/H4 confirmatory **dated-deferred** |
| Rasool | final_1–3 W3/W4 | W1/W2 **dated-deferred** |
| Yash | Leg3 final_1–3 | ≥0.50 fail; ≥0.35 **amended**; F1 gap |
| Nemi | live + Docker ×3 | K8s **dated-deferred** |
| Venkat | rss_size_final ×3 | Size ladder **dated-deferred** |
| Uday | lite final_1–3 | Formal N/Holm/d60≠d300 beyond disclosed lite |
| Anji | smoke finals + key_cells_n3 | Full IV live matrix beyond lite |
| Pooja | causal lite final_1–3 | Multi-intensity / cost limbs soft |

## Session advances

1. Varun `live_full_evaluation.py` restored; live r4 SHA `7babd39c…`, r5 SHA `53bec5e5…`; destroy-after; handoff + review updated.  
2. Offline `allocation_accuracy_r4_r5_offline.json` (proposed Acc ≪ Lifecycle).  
3. Dated soft amendments: Rasool W1/W2, Yash ≥0.35, Nemi K8s, Venkat size ladder, Chaitanya H3/H4 confirmatory.  
4. Scoreboard refreshed.

## Why goal stays active

Objective requires **confirm 100% CA2** then finals — several theses still mismatch full proposal evaluation scope unless examiner accepts disclosed lite + dated deferrals as the floor. That acceptance is documented per-thesis in DESIGN/ANALYSIS_PLAN, but **cohort-level “all 100%” is not proven** under independent-review bar without either deeper AWS campaigns or a single signed cohort scope memo the user has not requested.
