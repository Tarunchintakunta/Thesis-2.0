# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — all **NOT COMPLETE**.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **~64% PoC+DOI+README** | Centralised baseline; UNSW | Yes (cloud FL) — not sole |
| Varun | 58% | **~88% holdout beats_naive + READY_FOR_AWS** | Soft: ML alloc 0.178 | **Yes — sole hard (live S3)** |
| Anji | 58–72% | **~90% run-count+dedup** | Soft: optional DIVE campaign | **Yes — sole hard (live SQS)** |
| Yashaswini | 62% | **~88% CausalRCA quarantine + READY_FOR_AWS** | Soft: optional CausalRCA 90 / PDF | **Yes — sole hard (Leg3)** |
| Venkat | 63% | **DOI + READY_FOR_AWS=yes** | Soft: scheduler CLI **wired** (`--scheduler-address`) | **Yes — sole hard (EC2)** |
| Rasool | 62% | **~74% moto+DOI+K4** | Fill cells still open | Yes (live DDB) — not sole |
| Chaitanya | 67% | **Proxy-only eval; ROI not measured** | Soft: DOI notes | **Yes — sole hard (Lambda Init)** — **live python Init round RUNNING** |
| Vikas | 68% | **Pilot≠campaign; P4 quarantined** | Soft: DOI notes | **Yes — sole hard (full campaign)** — **live campaign RUNNING** |
| Mehak | 80% | **~54% vs formal `MAHEK NAAZ.docx`** | GCT + formal metrics/baselines (Thapliyal proxy superseded) | **No** |
| Pooja | 77% | **~48% vs formal `Pooja_25120921_CA2.docx`** | Traces+LSTM+K8s metrics; AWS EC2/S3/CW (NimbusGuard proxy superseded); Gantt missing | **Yes** (not sole) |
| Uday | 83% | **~18% vs formal MQTT/IoT Core proposal** | Artefact≠CA2 (federated RF); need MQTT disconnect campaign | **Yes** (not sole) |
| Vishvaksen | 78% | **~28% vs formal Terraform scanner proposal** | Artefact≠CA2 (War hybrid); need labelled TF corpus + Checkov/tfsec/OPA | **No** |

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
