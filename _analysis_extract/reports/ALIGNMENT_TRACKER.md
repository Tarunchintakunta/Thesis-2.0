# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — all **NOT COMPLETE**.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **~58% PoC metrics locked** | Centralised baseline; UNSW; DOI notes | Yes (cloud FL) — not sole |
| Varun | 58% | LaTeX de-boilerplate + honest dry-run | Live S3 Wilcoxon; beats_naive | Yes (live S3) |
| Anji | 58–72% | **H1–H3↔JSON + DIVE softened** | Obj4 live cost; live SQS | Yes (live SQS) |
| Yashaswini | 62% | **Eval↔raw fixed** | CausalRCA n=4; PDF rebuild; Leg3 | Yes (Leg3) |
| Venkat | 63% | **DOI + READY_FOR_AWS=yes** | Soft: scheduler CLI **wired** (`--scheduler-address`) | **Yes — sole hard (EC2)** |
| Rasool | 62% | **~68% moto honesty; K4 quarantined** | Live K1–K3 factorial; DOI notes | Yes (live DDB) — not sole |
| Chaitanya | 67% | **Proxy-only eval; ROI not measured** | Soft: DOI notes | **Yes — sole hard (Lambda Init)** — **live python Init round RUNNING** |
| Vikas | 68% | **Pilot≠campaign; P4 quarantined** | Soft: DOI notes | **Yes — sole hard (full campaign)** — **live campaign RUNNING** |
| Mehak | 80% | **~88% commitments + DOI + STATUS** | Formal CA2; synthetic traces; VoR PDF | **No** (alignment-only) |
| Pooja | 77% | **~85% commitments + DOI + STATUS** | Formal CA2; MLP≠DQN; synthetic | **No** |
| Uday | 83% | **~90% commitments + DOI + STATUS** | Formal CA2; real OneM2M; publisher PDF | **No** |
| Vishvaksen | 78% | **~86% commitments + DOI + STATUS** | Formal CA2; arXiv venue; Forge corpora | **No** |

## Iteration log
1. **2026-09-20 — Nemi claims hygiene + DOI notes.** AWS not started.  
2. **2026-09-20 — Baseline CA2-fit audit;** Varun→SkyStore; Halfmoon PDF fixed.  
3. **2026-09-20 — Exploration gate closed (all 8 DONE).** Alignment-first gate open.  
4. **2026-09-20 — Varun LaTeX / STATUS honesty; Terraform for 8 (no personal IDs).**  
5. **2026-09-20 — Venkat/Anji/Yashaswini claim↔evidence fixes; Venkat READY_FOR_AWS=yes.**  
6. **2026-09-20 — Nemi + Rasool claim hygiene merged.**  
7. **2026-09-20 — Chaitanya + Vikas claim hygiene merged** (proxy Init honesty; empty campaign called out; no student-ID tags). Still NOT COMPLETE.  
8. **2026-09-20 — Live AWS started (READY subset):** Vikas full campaign daemon (workers=4, seed 20260926); Chaitanya Terraform `coldstart-study` python×3 applied + `live_python_init` running; Venkat `--scheduler-address` wired (EC2 not applied yet).  
9. **2026-09-20 — Mehak/Pooja/Uday/Vishvaksen claim hygiene** (CA2_COMMITMENTS, STATUS honesty, eval↔CSV, `note={doi:}`); **no AWS deploy**. Still NOT COMPLETE.
