# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `main` only (no new `cursor/*` agent branches/worktrees).  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — Mehak + Nemi **CA2 floor COMPLETE**; others open.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **100% CA2 floor** (centralised + UNSW sample + live lite FL destroyed) | Soft/beyond-CA2 only (2.5M-flow, 50-round, Docker/K8s) | **No — sole AWS residual closed** |
| Varun | 58% | **~90% live lite S3/CE/CW/Wilcoxon (destroyed)** | Soft: ML alloc 0.178; full FinOps campaign open | **Yes — sole hard (full live S3 FinOps)** |
| Anji | 58–72% | **~90% run-count+dedup** | Soft: optional DIVE campaign | **Yes — sole hard (live SQS)** |
| Yashaswini | 62% | **~88% CausalRCA quarantine + READY_FOR_AWS** | Soft: optional CausalRCA 90 / PDF | **Yes — sole hard (Leg3)** |
| Venkat | 63% | **DOI + READY_FOR_AWS=yes** | Soft: scheduler CLI **wired** (`--scheduler-address`) | **Yes — sole hard (EC2)** |
| Rasool | 62% | **~74% moto+DOI+K4** | Fill cells still open | Yes (live DDB) — not sole |
| Chaitanya | 67% | **Proxy-only eval; ROI not measured** | Soft: DOI notes | **Yes — sole hard (Lambda Init)** — **live python Init round RUNNING** |
| Vikas | 68% | **~74% Pilot≠campaign; P4 quarantined; campaign deliveries 0 B** | Soft: DOI notes | **Yes — sole hard (full campaign)** — **NOT running** (r2/r3 = run.log only) |
| Mehak | 80% | **100% CA2 floor (2011 GCT + scoped residuals)** | Soft only: optional dump/2019/net-bytes | **No** |
| Pooja | 77% | **~48% vs formal `Pooja_25120921_CA2.docx`** | Traces+LSTM+K8s metrics; AWS EC2/S3/CW (NimbusGuard proxy superseded); Gantt missing | **Yes** (not sole) |
| Uday | 83% | **~18% vs formal MQTT/IoT Core proposal** | Artefact≠CA2 (federated RF); need MQTT disconnect campaign | **Yes** (not sole) |
| Vishvaksen | 78% | **~82% vs formal Terraform scanner CA2** | Independent human checklist; independent 2nd human (protocol+Holm/McNemar prose done) | **No** |

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
12. **2026-09-20 — Varun + Yashaswini non-AWS raise toward sole-AWS:** Varun forecast temporal-holdout fix (all arms `beats_naive=true`); Yashaswini CausalRCA quarantined + final_report hygiene; both `READY_FOR_AWS=yes`. **No terraform apply.**
13. **2026-09-20 — Mehak/Pooja/Uday/Vishvaksen formal-CA2 rescore.** Formal docx now binding; proxy extras dropped. Scores: Mehak ~54%, Pooja ~48%, Uday ~18%, Vishvaksen ~28%. Synthetic OK for Uday/Vish; GCT required for Mehak/Pooja. AWS required: Pooja+Uday yes (not deployed); Mehak+Vish no. **No AWS deploy; no invented results.**
14. **2026-09-20 — Varun live lite fold-in:** measured S3/CE/CW/Wilcoxon ($n{=}24$) into STATUS + LaTeX; residual/cohort **~90%**; SOLE_AWS_RESIDUAL still **yes** (full FinOps campaign); stack destroyed.
15. **2026-09-21 — Nemi live cloud FL lite closed:** `cloud_lite_summary.json` verified (baseline 0.5000 / improved 0.5480; destroy complete, 9 resources); scoreboard/cohort/tracker → **100% COMPLETE**; `SOLE_AWS_RESIDUAL=closed`; block-full-eval=no. No new AWS runs.
16. **2026-09-21 — Vishvaksen checklist protocol + Verdet Holm/McNemar prose:** human-executable sheet + NON-INDEPENDENT scripted samples; `holm_bonferroni.csv` + `docs/VERDET_COMPARISON.md` / `latex/verdet_comparison.tex`; alignment **~82%** (not 100% — independent humans still missing). No AWS apply.
17. **2026-09-21 — Vikas CA2 honesty rescore:** working-tree verify — pilot `deliveries.jsonl` 300 lines; campaign `deliveries.jsonl` **0 bytes**; r2/r3 start logs only. Scoreboard **100→~74**; `vikas_alignment.md` + `vikas_AWS_RESIDUAL.md`; block-full-eval=yes. **No campaign invented; no AWS apply.**
