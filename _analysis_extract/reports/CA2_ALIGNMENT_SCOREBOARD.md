# CA2 alignment scoreboard (12 theses — Kasi excluded)

**Updated:** 2026-09-21 (Pooja CA2 floor closed — dumps scoped out)  
**Bar:** **100% CA2** = RQ/objectives/gap/method/artefact/eval scope — **not** perfect marks.  
**Rubric 70%+:** JPEG + `master_rubric.md` → `RUBRIC_QUALITY_BAR.md`.  
**Handoff MD:** only after 3–5 full-scale evals. **Kasi:** never.

| # | Thesis | CA2_% | Rubric70 | Block full-eval? | Next |
|--:|--------|------:|----------|:----------------:|------|
| 1 | Anji | **100** | yes | no | initial_eval_1 done; CA2 still 100 → ready for final-3 |
| 2 | Chaitanya | **100** | partial | no | stale conclusion fold |
| 3 | Yashaswini | **100** | yes | no | soft only |
| 4 | Rasool | **100** | partial | no | optional W1/W2 |
| 5 | Varun | **100** | yes | no | soft only; handoff deferred |
| 6 | Vikas | **100** | partial | no | campaign done (N=1000×3×3); soft LaTeX fold optional |
| 7 | Nemi | **100** | partial | no | optional beyond-CA2 |
| 8 | Venkat | **100** | partial | no | soft only (Holm/DOI); matmul closed |
| 9 | Mehak | **100** | partial | no | INITIAL_EVAL_PASS=yes; next=3 local full GCT runs (not AWS) |
| 10 | Pooja | **100** | partial | soft only | floor COMPLETE; optional dumps / larger live beyond floor |
| 11 | Uday | **~65** | no | **YES** | formal-scale IoT (smoke live done+destroyed) |
| 12 | Vishvaksen | **100** | partial | no | oracle-labelled method; soft Verdet/report polish |

**Fix order:** Uday formal-scale; Pooja + Venkat + Mehak + Nemi + Vikas CA2 floor closed.
Venkat raise 2026-09-21: round-2 multi-instance `da.matmul` n=250 **ok** (0.2546 s per `ec2_round2_summary.json`); destroy verified → **100%**.
Pooja live AWS k3s 2026-09-21: 1× t3.micro + S3 + CW, live HPA vs PAKS scale, destroy confirmed → was **~92%**.
Pooja floor close 2026-09-21: full GCT/Alibaba dumps reframed **scoped-out optional** (`DESIGN_RATIONALE_BEYOND_CA2.md`) → **100%** (samples + live method evidence; not perfect marks).
Pooja non-AWS raise 2026-09-21: GCT 2011 part + Alibaba RANGE → was **~67%**.
Vikas rescore 2026-09-21: scoreboard **~74→100** — live full campaign N=1000×3×3 (24000 deliveries), E1–E3 supported, stack destroyed; see `vikas_alignment.md` / `vikas_AWS_RESIDUAL.md`.

## Assess follow-up

- [Assess CA2 alignment cohort A](bc-6dee112d-0199-5306-a490-49f520cd3aaa)
- [Assess CA2 alignment cohort B](bc-c8002071-fd7c-55bf-acae-d413dceec23e)
- [Scaffold Uday MQTT QoS CA2 artefact](bc-cff00b22-64f1-597a-886a-ed9c64d38f63) → ~42%, READY_FOR_AWS=NO
- Uday lite/smoke Free-Tier path + smoke live destroyed (2026-09-21) → **~65%**, READY_FOR_AWS=yes (formal still blocked)
- [Correct Vikas scoreboard honesty](bc-f205d25b-c03e-5db7-8f8c-d4c0d1b3fb4d) → was ~74% empty campaign; **2026-09-21 live campaign closed → 100%**

Vishvaksen 2026-09-21: labelled-oracle method confirmed → **100%** CA2 floor.
