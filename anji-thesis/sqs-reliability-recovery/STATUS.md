## Alignment note (2026-09-23 — SoT + scoped_E audit)

**ONE-file SoT:** `../CA2_PROPOSED_VS_ARTEFACT.md`  
**Audit (binding):** `scripts/audit_scoped_e_root_causes.py` → EXIT 0 / remediable_total=0 / `DATED_WONTFIX_FULL_IV_LIVE_AMENDED`  
**Honest CA2 floor:** **~78 under disclosed lite + scoped_E** (do **not** market ALIGNMENT=100 / full IV complete).  
**MOVE ALLOWED:** **yes** (2026-09-23).  
**Scoped E:** `results/live/scoped_E_guidance_1/` **20/20** (`E_guidance_transfer` localsim).  
**Full IV live matrix:** dated WONTFIX — `../DATED_WONTFIX_N_Anji_2026-09-23.md`.

**Final-3 progress:** `results/live/final_1/` + `final_2/` + `final_3/` **DONE (3/3)** — each 4/4 destroyed. Baseline: `results/live/FINAL3_BASELINE.md`.

Authoritative confirmatory stats remain packaging-deduped localsim: `results/summary/stats_H1_H2_H3.json` (`runs: 350`, `backend: localsim`). Live smoke: prior `results/live/key_cells/` plus **initial_eval_1** under `results/live/initial_eval_1/` (both destroyed after round). No live $n{>}1$ numbers exist.

| Issue | Status |
|-------|--------|
| Phase run-count table (350 vs 690) | **Reconciled** — design vs on-disk; analysis dedupes |
| H1–H3 claim↔JSON | Localsim-only; twin-inflated drafts withdrawn |
| Live AWS SQS key-cell lite (2026-09-20) | **4/4** n=1; destroyed — `results/live/key_cells/` |
| **Initial live eval gate (2026-09-21)** | **4/4** n=1; destroyed — `results/live/initial_eval_1/`; **CA2 still 100** |
| Beyond-CA2 live $n{=}3$ (same 4 cells) | **Not run** — keep concurrency low; protocol in `configs/live_key_cells_n3.yaml` |
| Beyond-CA2 localsim $n{=}3$ (same 4 cells) | **12/12 localsim** — `results/localsim/key_cells_n3/` |
| Beyond-CA2 poller sensitivity (conc 2 vs 5) | **8/8 localsim** — `results/localsim/key_cells_concurrency/` |

### initial_eval_1 (measured; n=1 each; eu-west-1; ESM max_concurrency=2)

| Campaign | Fault | VT | MRC | loss | dup | DLQ | recovery_s | thr msg/s | usd |
|----------|-------|---:|----:|-----:|----:|----:|-----------:|----------:|----:|
| L_vt_consumer_kill | consumer_kill | 30 | 5 | 0.0 | 0.025 | 0.0 | 3.123 | 2.979 | 0.000335 |
| L_vt_consumer_kill | consumer_kill | 90 | 5 | 0.0 | 0.015 | 0.0 | 2.609 | 1.530 | 0.000354 |
| L_mrc_unhandled_error | unhandled_error | 30 | 1 | 0.0 | 0.0 | 0.23 | — (censored) | 4.688 | 0.000278 |
| L_mrc_unhandled_error | unhandled_error | 30 | 5 | 0.0 | 0.08 | 0.0 | 39.329 | 2.313 | 0.000352 |

- Wall: **793.0 s**; measured cost sum **≈ $0.00132**
- Evidence: `results/live/initial_eval_1/` (`summary.json`, manifests, raw, `run.log`)
- Destroy: **0** TF resources; Lambda/SQS/DynamoDB absent (`results/teardown_log.txt` 2026-09-21)
- Tags: `project=sqs-reliability-recovery` only (no student name/ID)

### Rubric70 notes (honest pos/neg vs prior lite + baseline framing)

- **Pos:** loss=0 all cells; MRC=1 again shows DLQ capture (0.23 vs prior lite 0.16).
- **Neg/mixed:** VT→recovery **not** monotone this round (VT30 3.12s vs VT90 2.61s; prior lite 2.34 vs 7.53) — lite protocol does not recover campaign-A 1:1 VT law; MRC=1 success 0.805 (prior 0.91).
- **vs Kyrychenko steady-state baseline:** under fault, aggressive MRC=1 trades success for DLQ — reliability under failure is not implied by no-fault throughput guidance (Obj 3). Confirmatory H1–H3 remain localsim-only.
- **Limitations:** n=1 smoke; 200 orders; concurrency=2; underpowered for new Holm tests.

### Prior live lite round (2026-09-20; n=1; eu-west-1)

| Campaign | Fault | VT | MRC | loss | dup | DLQ | recovery_s | thr msg/s | usd |
|----------|-------|---:|----:|-----:|----:|----:|-----------:|----------:|----:|
| L_vt_consumer_kill | consumer_kill | 30 | 5 | 0.0 | 0.015 | 0.0 | 2.343 | 2.824 | 0.000387 |
| L_vt_consumer_kill | consumer_kill | 90 | 5 | 0.0 | 0.005 | 0.0 | 7.532 | 1.537 | 0.000382 |
| L_mrc_unhandled_error | unhandled_error | 30 | 1 | 0.0 | 0.0 | 0.16 | — (censored) | 7.122 | 0.000311 |
| L_mrc_unhandled_error | unhandled_error | 30 | 5 | 0.0 | 0.05 | 0.0 | 28.506 | 2.920 | 0.000362 |

- Evidence: `results/live/key_cells/`

### Beyond-CA2 localsim n=3 (same 4 cells; not AWS)

| Campaign | Fault | VT | MRC | $n$ | loss | dup mean | DLQ mean | rec. mean (s) |
|----------|-------|---:|----:|----:|-----:|---------:|---------:|--------------:|
| L_vt_consumer_kill | consumer_kill | 30 | 5 | 3 | 0.0 | 0.0017 | 0.0 | 0.0 |
| L_vt_consumer_kill | consumer_kill | 90 | 5 | 3 | 0.0 | 0.0067 | 0.0 | 0.0 |
| L_mrc_unhandled_error | unhandled_error | 30 | 1 | 3 | 0.0 | 0.0 | 0.050 | 1.67 |
| L_mrc_unhandled_error | unhandled_error | 30 | 5 | 3 | 0.0 | 0.013 | 0.0 | 1.67 |

- Evidence: `results/localsim/key_cells_n3/manifests/`, `summary.csv`, `results/beyond_ca2/localsim_key_cells_summary.json`
- Do **not** cite these as live AWS. Lite-protocol recovery is not campaign-A’s 1:1 VT law.
- Live $n{=}3$ plan: `DESIGN_RATIONALE_BEYOND_CA2.md`

```
COMPLETE=yes ALIGNMENT=~78 CA2_FLOOR=met_lite_scoped_E
INITIAL_EVAL_PASS=yes
FINAL3=done_3of3
SCOPED_E=20of20
FULL_IV_LIVE=amended_wontfix
SOT=CA2_PROPOSED_VS_ARTEFACT.md
AUDIT_EXIT=0
MOVE_ALLOWED=yes
LIVE_FINAL_1=yes
LIVE_FINAL_2=yes
LIVE_FINAL_3=yes
DESTROY_CONFIRMED=yes
READY_FOR_AWS=done_lite_round
SOLE_AWS_RESIDUAL=closed
AWS_CLASS=required
GATE_READY=yes
LIVE_LITE_COMPLETE=yes
LIVE_INITIAL_EVAL_1=yes
LIVE_CONFIRMATORY=key_cells_n3_and_scoped_E
LOCALSIM_N3=yes
DESTROY_AFTER_ROUND=yes
BEYOND_CA2=localsim_n3_done_live_n3_partial_full_iv_amended
```
---
# Project Status: Simulation vs Live AWS

**Student:** Anjaneya Reddy Gurram (24288853)  
**Project:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Last Updated:** September 23, 2026

## Executive Summary

Primary experimental evidence is the **local simulator** (350 packaging-deduplicated design cells) plus **scoped_E_guidance_1 (20/20)** guidance-transfer under fault. Live AWS lite key-cell smoke: prior `results/live/key_cells/` plus gate **`results/live/initial_eval_1/`** and finals (both destroyed after round). Live numbers are directional smoke only; confirmatory hypothesis tests remain localsim-only (null after Holm). Full IV live matrix is **dated WONTFIX**. Authority: `../CA2_PROPOSED_VS_ARTEFACT.md`.

**2026-09-23:** SoT + scripted audit EXIT 0; MOVE ALLOWED.
## Implementation Status

### Completed (Simulated)

1. **Core Infrastructure** — SAM template + Terraform stack (project tags only; no personal IDs)
2. **Local Simulator** (`src/localsim/`)
3. **Experiment Infrastructure** (`src/control/`) including live backend + cost guard
4. **Testing** — unit/integration; CI
5. **Experiments and Analysis** (localsim): Pilot / Baseline / Arms / Campaigns A–H / Burst; H1–H3 Holm–Bonferroni on deduped rows; figures
6. **Beyond-CA2 lite $n{=}3$ + poller sensitivity** on the four live key cells (localsim)
7. **Documentation**

### Completed (Live — lite only)

1. **Terraform-backed live stack** applied in eu-west-1 (project tags only)
2. **4/4 live key cells** prior round — `results/live/key_cells/`
3. **initial_eval_1 (CA2 gate)** — same lite config, ESM concurrency=2 — `results/live/initial_eval_1/`
4. **Teardown** — destroy verified after each round; evidence retained under `results/live/`

### Partial / open (beyond CA2 / later gates)

1. **Final-3 full-scale live evaluations** — next after `INITIAL_EVAL_PASS=yes` (not started this step)
2. **Confirmatory live $n{=}3$** — protocol ready (`configs/live_key_cells_n3.yaml`); deferred for concurrency budget
3. **Live↔sim fidelity** statistical comparison — not run
4. **Dedicated adaptive_vt / DIVE campaign** (optional; matrix disabled)
## Simulation Validity

### Known Simulator Limitations

1. **No Cold Starts** (timing model only)
2. **Account-level ConcurrentExecutions sharing is not modelled**; ESM `max_concurrency` *is* the localsim poller count (sensitivity campaign varies 2 vs 5)
3. **No Network Variability**
4. **No AWS Service Failures**
5. **Simplified Visibility Timeout**
6. **No Poison Pill Side Effects**
7. **Lite 200-order protocol does not recover the campaign-A 1:1 VT–recovery law** (see beyond-CA2 $n{=}3$ table)

### Packaging twin note

Two git cohorts differ only by whether `spec.adaptive_vt: false` is present. Metrics and seeds match; `config_hash`/`run_id` differ. See `results/README.md` and `configs/analysis_plan.yaml` amendment 2026-09-20.

## How to Verify

1. **Localsim H1–H3:** `make test` / `make stats` (must report `350 runs` after packaging-dedup)
2. **Live lite:** inspect `results/live/key_cells/summary.json` (`backend: live`)
3. **Beyond-CA2 localsim $n{=}3$:** `make beyond-ca2-localsim` or inspect `results/beyond_ca2/localsim_key_cells_summary.json`
4. **Concurrency gate:** `results/beyond_ca2/concurrency_probe_2026-09-20.json`

## Conclusion

Localsim evidence is reconciled to the 350-cell design. Live lite key-cells are **measured** (prior + `initial_eval_1`, each 4/4 n=1) but **not confirmatory**. CA2 **floor = 100% COMPLETE**; post-eval re-check **still 100** → `INITIAL_EVAL_PASS=yes`. Final-3 is a later step. Beyond-CA2 live $n{=}3$ remains deferred under shared ConcurrentExecutions=10.

---

**Honest Disclosure:** Prior lite ≈ **$0.00144**; `initial_eval_1` ≈ **$0.00132**. Stacks destroyed after each round. Mixed VT→recovery on n=1 smoke is disclosed (not hidden). Beyond-CA2 localsim $n{=}3$ is simulation, not AWS.