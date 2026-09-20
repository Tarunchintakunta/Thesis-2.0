# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — all **NOT COMPLETE**.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **~58%** PoC metrics + no Docker/K8s/AWS overclaim; TF not applied | Centralised baseline; real UNSW data; DOI notes | Yes (CA2 cloud) |
| Varun | 58% | LaTeX de-boilerplate + honest dry-run narrative | Live S3 Wilcoxon; beats\_naive | Yes (live S3) |
| Anji | 58–72% | **H1–H3↔JSON + DIVE softened** | Obj4 live cost; live SQS | Yes (live SQS) |
| Yashaswini | 62% | **Eval↔raw fixed** (concl+eval+abstract+STATUS) | CausalRCA n=4; PDF rebuild; Leg3 live | Yes (Leg3) |
| Venkat | 63% | **DOI notes + residual doc; READY_FOR_AWS=yes** | Soft: scheduler CLI | **Yes — sole hard residual (EC2)** |
| Rasool | 62% | **~68%** K4 quarantined; moto-only; no Cost Explorer; STATUS <100%; iac no student tags | Live factorial; DOI notes | Yes (live DDB) |
| Chaitanya | 67% | **Eval+STATUS+concl ROI quarantined** (~75%*) | Sole residual: live Lambda Init (+H3/H4) | Yes (Lambda) — sole hard residual |
| Vikas | 68% | **STATUS/eval/abstract + P4 quarantine** (~74%*) | Sole residual: empty full campaign | Yes (campaign) — sole hard residual |

\*Nemi: abstract/intro/eval/conclusion/STATUS/README match PoC `results.json` (0.793/0.800, F1≈0); Docker/K8s/AWS overclaims removed; `terraform/` noted not applied. Still **NOT 100%**.
*Chaitanya/Vikas: claim hygiene pass 2026-09-20; % approximate pending re-score. Still **NOT 100%**; AWS residual only.

## Iteration log
1. **2026-09-20 — Nemi claims hygiene + DOI notes.** AWS not started.  
2. **2026-09-20 — Baseline CA2-fit audit;** Varun→SkyStore; Halfmoon PDF fixed; all BASELINE_PAPER.md expanded.  
<<<<<<< HEAD
<<<<<<< HEAD
3. **2026-09-20 — Exploration gate closed (Venkat DONE).** Alignment-first gate still open. Anji/Venkat/Yashaswini claim hygiene agents running. Rasool eval softened (no “ready for production” claim).  
4. **2026-09-20 — Varun LaTeX rewritten** (removed spam boilerplate; abstract/related/eval honest dry-run; SkyStore primary). Mehak/Pooja STATUS no longer claim research 100%/SUBMIT-READY for CA2.
=======
=======
>>>>>>> 1f5fde5 (Raise Chaitanya/Vikas CA2 claim hygiene without AWS deploy.)
3. **2026-09-20 — Exploration gate closed (Venkat DONE).** Alignment-first gate still open.  
4. **2026-09-20 — Varun LaTeX rewritten**; Mehak/Pooja STATUS honesty.  
5. **2026-09-20 — Venkat/Anji/Yashaswini claim↔evidence fixes.**  
6. **2026-09-20 — Terraform for all 8 AWS-goal theses**; no personal IDs in `.tf` (`TERRAFORM_POLICY.md`).  
7. **2026-09-20 — Exploration gate file restored (all 8 DONE).** Claim hygiene agents: Venkat DOI/AWS-residual, Chaitanya+Vikas, Nemi+Rasool. AWS creds present but **apply not started**.
8. **2026-09-20 — Venkat READY_FOR_AWS_ALIGNMENT_PATH=yes** (`venkat_AWS_RESIDUAL.md`). Still NOT COMPLETE until live EC2 evidence.
9. **2026-09-20 — Nemi + Rasool claim hygiene (this pass).** Nemi: PoC metrics locked; no Docker/K8s/AWS/production overclaims; TF not applied. Rasool: K4 dominance quarantined; Cost Explorer pilot claim removed; STATUS <100%; iac tags already project-only. AWS **not** started.
<<<<<<< HEAD
10. **2026-09-20 — Chaitanya+Vikas claim hygiene.** Eval/STATUS honesty; ROI/ADOPT not measured; P4 quarantined; full campaign empty called out. No AWS deploy.
9. **2026-09-20 — Venkat DOI+AWS residual merged from agent onto feature branch.** READY_FOR_AWS=yes; NOT COMPLETE.
>>>>>>> 8532d9c (fix(nemi,rasool): raise CA2 claim hygiene without AWS deploy)
=======
8. **2026-09-20 — Chaitanya+Vikas claim hygiene.** Eval/STATUS honesty; ROI/ADOPT not measured; P4 quarantined; full campaign empty called out. No AWS deploy.
9. **2026-09-20 — Venkat DOI+AWS residual merged from agent onto feature branch.** READY_FOR_AWS=yes; NOT COMPLETE.
>>>>>>> 1f5fde5 (Raise Chaitanya/Vikas CA2 claim hygiene without AWS deploy.)
