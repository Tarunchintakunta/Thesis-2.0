# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — all **NOT COMPLETE**.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | ~55%* | Centralised baseline; real UNSW data; Docker/K8s claims | Yes (CA2 cloud) |
| Varun | 58% | LaTeX de-boilerplate + honest dry-run narrative | Live S3 Wilcoxon; beats\_naive | Yes (live S3) |
| Anji | 58–72% | H1–H3 text↔JSON largely aligned | DIVE/Obj4 cost; live SQS | Yes (live SQS) |
| Yashaswini | 62% | in progress | Eval↔JSON; CausalRCA N; Leg3 live | Yes (Leg3) |
| Venkat | 63% | in progress | Eval↔JSON; config manual; local≠EC2 | Yes (EC2) |
| Rasool | 62% | K4 quarantine + moto honesty | Live factorial; Cost Explorer | Yes (live DDB) |
| Chaitanya | 67% | abstract proxy-honest | Live Init Duration | Yes (Lambda) |
| Vikas | 68% | — | Empty full campaign; P4 quarantine | Yes (campaign) |

\*Nemi: abstract/intro/eval/conclusion match PoC `results.json`; DOI notes. Still **NOT 100%**.

## Iteration log
1. **2026-09-20 — Nemi claims hygiene + DOI notes.** AWS not started.  
2. **2026-09-20 — Baseline CA2-fit audit;** Varun→SkyStore; Halfmoon PDF fixed; all BASELINE_PAPER.md expanded.  
3. **2026-09-20 — Exploration gate closed (Venkat DONE).** Alignment-first gate still open. Anji/Venkat/Yashaswini claim hygiene agents running. Rasool eval softened (no “ready for production” claim).  
4. **2026-09-20 — Varun LaTeX rewritten** (removed spam boilerplate; abstract/related/eval honest dry-run; SkyStore primary). Mehak/Pooja STATUS no longer claim research 100%/SUBMIT-READY for CA2.
