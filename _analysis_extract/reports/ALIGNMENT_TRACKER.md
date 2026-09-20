# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — all **NOT COMPLETE**.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **~64% PoC+DOI+README** | Centralised baseline; UNSW | Yes (cloud FL) — not sole |
| Varun | 58% | **~70% STATUS/LaTeX/DOI** | beats_naive fail; report depth | Yes (live S3) — not sole |
| Anji | 58–72% | **~90% run-count+dedup** | Soft: optional DIVE campaign | **Yes — sole hard (live SQS)** |
| Yashaswini | 62% | **~75% eval↔raw+STATUS** | CausalRCA n=4; PDF rebuild | Yes (Leg3) — not sole |
| Venkat | 63% | **DOI + READY_FOR_AWS=yes** | Soft: scheduler CLI **wired** (`--scheduler-address`) | **Yes — sole hard (EC2)** |
| Rasool | 62% | **~74% moto+DOI+K4** | Fill cells still open | Yes (live DDB) — not sole |
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
8. **2026-09-20 — Live AWS (READY subset):** Vikas campaign daemon (workers=4); Chaitanya live Python Init + H4-lite + Node.js Init collected; Venkat `--scheduler-address` wired (EC2 not applied).
9. **2026-09-20 — Mehak/Pooja/Uday/Vishvaksen claim hygiene** (CA2_COMMITMENTS, STATUS honesty, eval↔CSV, `note={doi:}`); **no AWS deploy**. Still NOT COMPLETE.
10. **2026-09-20 — Anji/Varun/Yashaswini/Rasool/Nemi claim hygiene raise** (eval↔JSON, STATUS demote, DOI notes, residual notes); **no AWS deploy**. Still NOT COMPLETE. Residuals: `anji_AWS_RESIDUAL.md`, `varun_AWS_RESIDUAL.md`, `yashaswini_AWS_RESIDUAL.md`, `rasool_AWS_RESIDUAL.md`, `nemi_AWS_RESIDUAL.md`.
11. **2026-09-20 — Anji phase run-count reconcile + packaging-dedup stats** (350 design / 690 on-disk; H3_recovery fail-to-reject after Holm; READY_FOR_AWS=yes, sole=live SQS); **no AWS deploy**.
