# CA2 alignment scoreboard (12 thesis projects — Kasi excluded)

**Updated:** 2026-09-22 (Varun r4/r5 independence closed; soft deferred/amended where dated)  
**Bar:** **100% CA2** = complete match to approved RQ/objectives/gap/method/artefact/eval scope — **not** perfect marks.  
**Authority for honesty:** [`INDEPENDENT_CRITICAL_AUDIT.md`](INDEPENDENT_CRITICAL_AUDIT.md) + per-thesis `INDEPENDENT_REVIEW_*.md` + on-disk `GENAI_HANDOFF.md`.  
**Rubric strategy:** aim 70%+ band characteristics — **do not raise Rubric70 on a false CA2 floor**.

| # | Thesis | CA2_% (honest) | ×3 / final packs | Blocker vs full met |
|--:|--------|---------------:|------------------|---------------------|
| 1 | Anji | **~78** | live final_1–3 smoke + key_cells_n3 | Full IV matrix on live not done; localsim H1–H3 null |
| 2 | Chaitanya | **~78** | confirmatory_n30 r1–3 | H3/H4 warming residual |
| 3 | Yashaswini | **~72** | Leg3 final_1–3 | Original ≥0.50 **fails**; ≥0.35 **amended 2026-09-22**; F1 gap retained |
| 4 | Rasool | **~82** | final_1–3 W3/W4 + pooled ANOVA | W1/W2 **dated-deferred** 2026-09-22 |
| 5 | Varun | **~88** | archival r1–3 + **independent r4+r5** | Independence **closed**; alloc-acc limb still weak on dry-run improved |
| 6 | Vikas | **~88** | live campaign E1–E3 | P4 quarantined; campaign ≠ perfect-marks |
| 7 | Nemi | **~62** | live lite + Docker final_1–3 | K8s **dated-deferred** 2026-09-22 |
| 8 | Venkat | **~80** | time finals + rss_size_final_1–3 | Size ladder **dated-deferred** 2026-09-22 |
| 9 | Mehak | **~88 met** | gct final_1–3 | Keep negative MHSA honesty |
| 10 | Pooja | **~62** | causal lite final_1–3 | HPA/LSTM/cost/multi-intensity limbs |
| 11 | Uday | **~70** | lite final_1–3 | Formal N / Holm / d60≠d300 not met |
| 12 | Vishvaksen | **~90 met** | final_1–3 | Labelled-oracle met; Checkov recall honesty |

## Closed this session (evidence)

- **Varun:** restored `scripts/live_full_evaluation.py`; ran live `evaluation_r4` (SHA `7babd39c…`) + `evaluation_r5` (SHA `53bec5e5…`); both `meets_ca2_two_of_three=true` (3/3); terraform **destroyed**; AWS lock **FREE**.
- **Rasool / Yash / Nemi / Venkat:** dated ANALYSIS_PLAN / DESIGN amendments for soft limbs (not fabricated fills).

## Still blocking cohort “all CA2 100%”

Lite-vs-formal scale (Uday/Anji/Pooja), H3/H4 (Chaitanya), allocation-acc (Varun soft), F1 gap (Yash), quarantined P4 (Vikas). Closing requires either new evidence **or** further dated scope amendments that stop claiming those limbs.

**Kasi:** excluded. **GENAI_HANDOFF:** 12/12 on disk; floors above are authoritative over any STATUS “100%” prose.
