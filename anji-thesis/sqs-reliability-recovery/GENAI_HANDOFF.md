# GENAI_HANDOFF.md — Anji (sqs-reliability-recovery)

Evidence-only handoff. Artefact-only paths under `anji-thesis/sqs-reliability-recovery/` unless noted. Unknowns marked explicitly. No invented metrics.

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Anjaneya Reddy Gurram |
| Student ID | 24288853 |
| Programme | MSc in Cloud Computing — Research Project (NCI) |
| Title | Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures |
| Artefact root | `anji-thesis/sqs-reliability-recovery/` |
| Honest CA2 floor | **Closed under disclosed lite scope (~78)** — key_cells_n3 + smoke finals Demonstrated; full IV live matrix beyond-floor; STATUS prior `ALIGNMENT=100` overstated |
| Eval completeness | Localsim confirmatory H1–H3 (350 packaging-deduped) **null**; live AWS = lite 4 key cells only (n=1 smoke packs + confirmatory **n=3**); **full CA2 IV matrix not on live** |
| AWS | **Required and applied** (eu-west-1; destroy-after rounds) |
| Handoff date | 2026-09-22 |
| Authority | `AnjaneyaReddyGurram_24288853_MASTER_PROMPT.md` (binding RQ/objectives; **`CA2_COMMITMENTS.md` not present on disk**), `_analysis_extract/reports/INDEPENDENT_REVIEW_ANJI.md`, `STATUS.md`, `results/live/KEY_CELLS_N3_BASELINE.md`, `results/live/key_cells_n3/` |

**§0 honesty:** 3–5 full-scale final AWS evaluations of the full IV matrix are **not** done. Live finals (`final_1|2|3`) are **method-scale n=1 smoke** on the same 4 lite cells. Live confirmatory authority for those 4 cells is **`key_cells_n3` (12/12)**.

## 1. Research problem, motivation, research question, and objectives

**Problem:** Managed SQS configuration (visibility timeout, `maxReceiveCount`/DLQ redrive, batch) is commonly tuned under healthy steady-state load; message-level reliability and recovery under consumer/downstream failure are under-measured.

**Motivation:** Kyrychenko et al. (2025) give steady-state throughput/latency/cost optima (e.g. batch ~50, VT ~600 s) without fault injection. Chaos/resilience work often holds queue settings fixed. Need controlled fault injection with SQS config as IVs and message-level DVs.

**RQ (master prompt / independent review):**  
> How does Amazon SQS configuration affect message reliability and recovery under injected consumer and downstream failures?

**Objectives (must evidence):**
1. Quantify how **VT**, **`maxReceiveCount`**, and **DLQ redrive** affect **message loss** and **duplicate processing** under injected failure.
2. Measure **recovery time to steady state** as a function of the same parameters.
3. Test whether **reliability implied by steady-state guidance** (Kyrychenko) **persists once failures occur**.
4. Characterise the **trade-off** among reliability, recovery, and latency/invocation cost.

**Hypotheses (α=0.05; Holm–Bonferroni):** H1 (VT→loss under consumer failure); H2 (MRC→recovery); H3 (throughput-optimal config vs alternatives on loss/recovery under fault).

## 2. Identified literature gap and how this research addresses it

**Gap (master prompt §5.2):** Steady-state SQS optimisation varies the right parameters under the wrong conditions (no consumer/downstream failure). Resilience/chaos work varies failure but typically not SQS VT/`maxReceiveCount`/DLQ as primary IVs, and not message-level loss/dup/DLQ/recovery DVs.

**Addressed by:** Holding async architecture constant; varying SQS configuration under injected faults; measuring loss, duplicates, DLQ capture, recovery (plus throughput/latency/cost for baseline comparability). Live evidence is limited to **4 lite key cells**; full multi-fault / batch / burst IV matrix remains **localsim** (and exploratory where noted).

## 3. CA2 proposal alignment and any extensions beyond the proposal

**Aligned (artefact + evidence):**
- RQ and four objectives as in master prompt.
- SAM + Terraform SQS Standard + DLQ + Lambda + DynamoDB + fault switch.
- Localsim campaigns A–H / baseline / burst; H1–H3 on packaging-deduped 350 runs.
- Live AWS key cells: VT 30/90 under `consumer_kill`; MRC 1/5 under `unhandled_error` (200 orders, lite protocol).

**Not fully met on live (floor drivers for ~78):**
- Full CA2 IV matrix (batch, burst, multi-fault, full VT grid) **not on live**.
- Live Holm H1–H3 **not met** (n=3 directional only; no new live Holm pack).
- Localsim H1–H3 **uniformly fail to reject** after Holm — must not be cited as effects.

**Beyond-CA2 (documented; partial):**
- Live confirmatory **n=3** same 4 cells: `results/live/key_cells_n3/` — **DONE 12/12**.
- Localsim n=3 + concurrency sensitivity: `results/localsim/key_cells_n3/`, `results/localsim/key_cells_concurrency/`.
- **DIVE / `adaptive_vt`:** **not enabled** in committed matrix (`adaptive_vt: false`).

**Missing contract file:** `CA2_COMMITMENTS.md` — **not on disk** under `anji-thesis/`; use master prompt + independent review.

## 4. Research methodology and experimental design

- **Design:** Controlled two-arm system (sync HTTP vs queue-decoupled); primary treatment = queue arm. Fault injection via SSM switch (`consumer_kill`, `unhandled_error`, `datastore_reject`, `datastore_timeout`).
- **IVs (design):** VT, `maxReceiveCount`, batch size, load (normal/burst), fault type, arm.
- **DVs:** loss_rate, duplicate_rate, dlq_capture_rate, success_rate, recovery_time_s, throughput_msg_s, latency p50/p95, usd_total.
- **Localsim confirmatory:** packaging-deduped **350** design runs; H1–H3 + exploratory tests in `results/summary/stats_H1_H2_H3.json`.
- **Live lite protocol:** `configs/live_key_cells.yaml` / `live_key_cells_n3.yaml` — 4 cells; order_count=200; rate 10 msg/s; fault window 30 s @ rate 0.25; batch_size=10; region **eu-west-1**; destroy-after.
- **Stats plan:** non-parametric fallback; Holm–Bonferroni across confirmatory family. Live n=1/n=3 underpowered for new Holm tests.

## 5. Artefact purpose and artefact-only project structure

**Purpose:** Runnable SAM/Terraform SQS reliability experiment harness + localsim + live runner + analysis scripts producing manifests and stats.

```text
anji-thesis/sqs-reliability-recovery/
├── template.yaml / samconfig.toml   # SAM stack (SQS+DLQ, Lambdas, DynamoDB, SSM fault)
├── terraform/                       # Live apply/destroy (project tags only; name_prefix sqs-rr)
├── src/
│   ├── queue_consumer/              # SQS ESM Lambda (ReportBatchItemFailures)
│   ├── sync_api/                    # HTTP control arm
│   ├── common/                      # faults, processing, metrics, dynamo, idempotency
│   ├── producer/                    # synthetic orders
│   ├── control/                     # experiment_runner, live backend, cost guard, manifests
│   └── localsim/                    # virtual-clock SQS/Lambda/Dynamo simulator
├── configs/                         # pilot, baseline, arms, fault_campaigns, live_key_cells*, analysis_plan
├── analysis/                        # stats_tests, plot_results, load_results
├── scripts/                         # scaffold, deploy, destroy, run helpers
├── results/                         # manifests, summaries, figures, live/, localsim/, summary/
├── docs/                            # ARCHITECTURE, CONFIGURATION_MANUAL, DEMO_*, VIVA_QA
├── tests/                           # unit + integration (moto)
├── report/ weekly/                  # report notes, weekly template
├── STATUS.md                        # gate + measured live tables
├── DESIGN_RATIONALE_BEYOND_CA2.md
└── RUBRIC_EVIDENCE_MATRIX.md
```

Parent thesis folder also holds master prompt, proposal.docx, latex_report (not rewritten here).

## 6. AWS architecture, services, configurations, and experimental setup

**Applied (not N/A).**

| Component | Role |
|-----------|------|
| Amazon SQS Standard + DLQ | Orders queue; redrive after `maxReceiveCount` |
| Lambda (queue consumer + sync API) | Shared `processing.py`; ESM BatchSize + ReportBatchItemFailures |
| DynamoDB | Orders (conditional put) + ProcessingEvents |
| SSM Parameter | Fault switch window (`/sqs-rr/.../fault/`) |
| Terraform | Live stack apply/destroy; tags `project=sqs-reliability-recovery` only (no student name/ID) |
| Region | **eu-west-1** |
| ESM concurrency | initial_eval_1: max_concurrency=**2**; key_cells_n3: max_concurrency=**5** |

Fault modes and message lifecycle: `docs/ARCHITECTURE.md`. Live destroy verified TF resources **0** after rounds (`KEY_CELLS_N3_BASELINE.md`, `FINAL3_BASELINE.md`, `results/teardown_log.txt`).

## 7. Evaluation metrics and why they were selected

| Metric | Why |
|--------|-----|
| loss_rate | Core reliability under at-least-once + faults (Obj 1) |
| duplicate_rate | Excess reprocessing vs no-fault floor (Obj 1) |
| dlq_capture_rate | MRC/redrive policy outcome (Obj 1, 3) |
| recovery_time_s | Backlog clearance after fault OFF (Obj 2) |
| throughput_msg_s / latency | Comparability with Kyrychenko steady-state baseline (Obj 3–4) |
| usd_total | Cost proxy for reliability–recovery–cost trade-off (Obj 4) |

## 8. Baseline definition and baseline comparison

**Literature baseline:** Kyrychenko et al. (2025) WSEAS — steady-state SQS batch pipeline; claimed optima ~batch 50, VT 600 s, delivery delay 300 s; throughput/latency/cost under healthy consumers (DOI `10.37394/23202.2025.24.4`).

**Artefact baseline arm:** `configs/baseline_kyrchenko.yaml` / localsim `results/baseline/` — no-fault VT×batch grid (exploratory throughput by batch in `stats_H1_H2_H3.json`).

**Guidance-transfer (Obj 3 / H3):** campaign `E_guidance_transfer` — compare Kyrychenko-favourable long VT/batch under fault vs alternatives. Localsim H3_recovery: opt mean recovery **600 s** vs rest mean **224 s**; **fail to reject after Holm** (p_adj=0.084).

**Live vs baseline framing:** under fault, MRC=1 trades success for DLQ capture — reliability under failure is **not** implied by no-fault throughput guidance (STATUS / initial_eval_1 notes).

## 9. Complete evaluation process and number of runs

| Pack | Path | Scale | Backend | Destroyed? |
|------|------|-------|---------|------------|
| Localsim confirmatory design | `results/` campaigns + `results/summary/` | **350** packaging-deduped | localsim | N/A |
| Live prior lite | `results/live/key_cells/` | 4 cells × n=1 | live | yes (TF=0) |
| Live initial eval | `results/live/initial_eval_1/` | 4 × n=1; conc=2 | live | yes |
| Live final_1 | `results/live/final_1/` | 4 × n=1 smoke | live | yes (TF=0) |
| Live final_2 | `results/live/final_2/` | 4 × n=1 smoke | live | yes (TF=0) |
| Live final_3 | `results/live/final_3/` | 4 × n=1 smoke | live | yes (TF=0) |
| **Live confirmatory n=3** | `results/live/key_cells_n3/` | **4 cells × 3 = 12/12** | live | **yes; DESTROY TF=0** |
| Beyond-CA2 localsim n=3 | `results/localsim/key_cells_n3/` | 12 | localsim | N/A |
| Concurrency sensitivity | `results/localsim/key_cells_concurrency/` | 8 | localsim | N/A |

**Not done:** full IV matrix live; live Holm H1–H3; dedicated adaptive_vt campaign; live↔sim fidelity hypothesis test.

## 10. Final results and key findings (committed evidence only)

### 10.1 Live confirmatory n=3 (authoritative live pack)

Source: `results/live/KEY_CELLS_N3_BASELINE.md` + `results/live/key_cells_n3/` (`summary.csv`, 12 manifests, `PROVENANCE.txt`).  
**12/12** · region eu-west-1 · max_concurrency=5 · APPLY=0 RUN=0 **DESTROY=0** · TF_LEFT=**0** · measured USD sum ≈ **$0.00443**.

| Campaign | VT | MRC | loss | dup | DLQ | recovery_s | thr msg/s |
|----------|---:|----:|-----:|----:|----:|-----------:|----------:|
| L_vt_consumer_kill | 30 | 5 | **0.0** | 0.0067 | 0.0 | 12.84 | 2.43 |
| L_vt_consumer_kill | 90 | 5 | **0.0** | 0.0100 | 0.0 | 30.15 | 1.59 |
| L_mrc_unhandled_error | 30 | 1 | **0.0** | 0.0000 | **0.097** | 2.76 | 5.31 |
| L_mrc_unhandled_error | 30 | 5 | **0.0** | 0.0483 | **0.0** | 2.45 | 2.63 |

- **loss=0** on all 12 live runs.
- MRC1 DLQ mean **0.097** vs MRC5 **0.0**.
- Mean VT30 recovery (12.8 s) < VT90 (30.2 s) on means; outliers present (VT30 one run 33.7 s; VT90 one run 85.6 s per baseline note).

### 10.2 Live final-3 smoke (n=1 each; not Holm)

From `FINAL3_BASELINE.md`: loss=0 all cells/rounds; MRC1 DLQ final_1/2/3 = **0.18 / 0.17 / 0.155**; MRC5 DLQ = **0**.

### 10.3 Localsim confirmatory H1–H3 (350 runs)

From `results/summary/stats_H1_H2_H3.json` / `hypotheses.md`:

| Test | Decision | Key numbers |
|------|----------|-------------|
| H1 loss × VT | fail to reject | loss=0 all groups; p_adj=1 |
| H2 recovery × MRC | fail to reject | H=2.43, p=0.489, p_adj=1.0, ε²=0.128 |
| H3_loss | fail to reject | loss=0; not estimable |
| H3_recovery | fail to reject after Holm | U=62.5, p=0.021, **p_adj=0.084**, r=0.667; opt 600 s vs rest 224 s |

**Do not cite localsim nulls as demonstrated effects.** Exploratory localsim (e.g. DLQ × MRC, VT→recovery under kill) show strong descriptive contrasts in the same JSON — separate from confirmatory H1–H3.

## 11. How results satisfy or address each research objective

1. **VT / MRC / DLQ → loss + dup:** **Partial.** Live + localsim show **loss=0** under tested lite/campaign faults; MRC=1 vs 5 **DLQ contrast** replicates on live (0.097 vs 0). Dup varies by cell; full IV matrix live **unknown/not run**.
2. **Recovery time:** **Partial.** Localsim campaign-A exploratory: recovery tracks VT nearly 1:1. Live lite n=1 mixed; live n=3 means orderly (12.8 vs 30.2 s) but outlier-heavy / underpowered.
3. **Kyrychenko guidance under fault:** **Partial / descriptive.** Localsim H3_recovery fails Holm; live MRC=1 shows success↔DLQ trade-off under fault. Not a live confirmatory reject of H3.
4. **Reliability–recovery–cost trade-off:** **Partial.** usd_total logged on live packs (~$0.0013–$0.0044 per pack); systematic Pareto analysis across full matrix **not claimed**.

## 12. How results answer the research question

On committed evidence: **SQS configuration (especially MRC→DLQ and VT→recovery direction on means) affects recovery and poison-message capture under injected faults, while message loss remained 0 in the measured live key cells and localsim confirmatory loss DV.** Confirmatory hypothesis tests on localsim **do not reject** H1–H3 after Holm. Live evidence answers the RQ **directionally for 4 lite cells only**, not the full proposed IV space. Honest answer = **partial empirical support + null confirmatory stats + incomplete live matrix**.

## 13. How findings relate to the literature gap and previous research

Findings support the gap framing: steady-state optima (long VT / aggressive settings) are **not automatically reliability-optimal under fault** — long VT lengthens mean recovery in localsim guidance-transfer (descriptive); aggressive MRC=1 captures to DLQ at cost of success. Compared with Kyrychenko (healthy consumers), this work adds **fault-conditioned message-level DVs**. No claim that this study outperforms or replaces broker-comparison or chaos papers beyond that niche.

## 14. Statistical analysis and significance

- **Confirmatory (localsim only):** H1–H3 all **fail to reject H0** after Holm (`stats_H1_H2_H3.json`, runs=350).
- **Live:** **no** new Holm pack on n=1 or n=3; independent review: n=3 directional only.
- **Exploratory localsim:** several Kruskal–Wallis / ANOVA contrasts with small p-values (e.g. DLQ×MRC, VT→recovery) — **exploratory only**, not confirmatory family.
- **Unknown:** live statistical power analysis for full matrix — not on disk as completed live Holm.

## 15. Important observations, trends, positive/negative findings, and anomalies

**Positive**
- Live **12/12** confirmatory completed; **loss=0**; destroy **TF=0**.
- MRC1 DLQ mean **0.097** vs MRC5 **0** replicates across smoke and n=3.
- Localsim packaging twin / 350-run reconciliation documented (`results/README.md`).

**Negative / mixed**
- Confirmatory H1–H3 **null**.
- Lite protocol does **not** recover campaign-A 1:1 VT–recovery law (STATUS / DESIGN_RATIONALE).
- n=1 finals: VT→recovery **not** monotone; n=3: heavy recovery outliers.
- Prior STATUS `ALIGNMENT=100` / `COMPLETE=yes` **incorrect** vs independent floor **~78**.

**Anomalies / caveats**
- Some n=3 recovery fields empty/censored in raw CSV for individual repeats — means in `KEY_CELLS_N3_BASELINE.md` are the published cell summaries.
- `run_id` can collide across live/localsim when derived from config hash+seed — do not mix folders in one analysis (DESIGN_RATIONALE).

## 16. Limitations, validity, reproducibility, and generalisability

- **Internal:** lite 200-order / short fault window; ESM concurrency 2 or 5 on shared account ConcurrentExecutions=10; synthetic faults ≠ organic timing.
- **Construct:** recovery = backlog clearance, not full consumer repair.
- **External:** one region (eu-west-1), Standard queue only, one account, synthetic orders.
- **Simulator:** no cold starts; no network variability; account concurrency sharing not fully modelled (STATUS).
- **Reproducibility:** manifests + configs + seeds on disk; live requires own AWS + destroy discipline.
- **Generalisability:** do not generalise 4-cell lite live results to full VT/batch/burst/multi-fault space.

## 17. Final conclusions and research contribution

**Contribution:** An open, reproducible SQS fault-injection artefact measuring message-level reliability and recovery while varying VT and MRC, with Kyrychenko steady-state baseline as the no-fault reference and honest null confirmatory tests.

**Conclusion (evidence-bound):** Under the tested faults, **loss stayed at 0** and **MRC policy strongly gated DLQ capture**; **VT influences recovery directionally on live n=3 means** but confirmatory tests remain **null** on localsim and **untested by Holm on live**. CA2 research floor is **PARTIAL (~78)**, not complete.

## 18. What changed or improved during the evaluation process

- Packaging-dedup reconciliation (design 350 vs on-disk twin inflation) — analysis uses deduped rows.
- Live path: prior lite → `initial_eval_1` → `final_1|2|3` n=1 smoke → **`key_cells_n3` confirmatory**.
- Independent review **overturned** `ALIGNMENT=100`; floor set to **partial (~78)**.
- Beyond-CA2 live n=3 unblocked after earlier concurrency deferral (DESIGN_RATIONALE had blocked; later executed 2026-09-22).

## 19. Remaining issues or recommended future work

1. Keep `KEY_CELLS_N3_BASELINE.md` as live confirmatory authority; do not restore STATUS `ALIGNMENT=100`.
2. Report localsim H1–H3 as **null** honestly.
3. Optional: burst / VT600 / full IV matrix live cells (not required for current floor).
4. Optional: dedicated adaptive_vt / DIVE campaign (currently disabled).
5. Optional: live↔localsim fidelity statistical comparison.
6. Create `CA2_COMMITMENTS.md` if a one-page binding extract is required for cohort tooling (**currently absent**).

## 20. Important files, scripts, configurations, datasets, and artefacts to reproduce/continue

| Role | Path |
|------|------|
| Binding RQ/objectives | `anji-thesis/AnjaneyaReddyGurram_24288853_MASTER_PROMPT.md` |
| Independent floor | `_analysis_extract/reports/INDEPENDENT_REVIEW_ANJI.md` |
| Status / measured tables | `STATUS.md`, `anji-thesis/STATUS.md` |
| Live n=3 authority | `results/live/KEY_CELLS_N3_BASELINE.md`, `results/live/key_cells_n3/` |
| Live smoke finals | `results/live/final_{1,2,3}/`, `results/live/FINAL3_BASELINE.md` |
| Live gate | `results/live/initial_eval_1/`, `results/live/key_cells/` |
| Localsim Holm pack | `results/summary/stats_H1_H2_H3.json`, `results/summary/hypotheses.md` |
| Live n=3 config | `configs/live_key_cells_n3.yaml` |
| Lite config | `configs/live_key_cells.yaml` |
| Analysis plan | `configs/analysis_plan.yaml` |
| Architecture | `docs/ARCHITECTURE.md`, `docs/CONFIGURATION_MANUAL.md` |
| Beyond-CA2 rationale | `DESIGN_RATIONALE_BEYOND_CA2.md` |
| Runner | `python -m src.control.experiment_runner --config ... --live` |
| Make targets | `Makefile` (`make experiments`, `make stats`, `make figures`) |
| Teardown evidence | `results/teardown_log.txt`, terraform destroy exits in baselines |

**Reproduce live n=3 (high level):** build Lambda zips → `terraform apply` → `experiment_runner --config configs/live_key_cells_n3.yaml --live --out results/live/key_cells_n3` → `terraform destroy` (see DESIGN_RATIONALE for concurrency gate).

---

Anjaneya Reddy Gurram
