## Alignment note (2026-09-20 — beyond-CA2 confirmatory)

**CA2 research alignment = 100% (floor).** **COMPLETE.** Beyond-CA2 live $n{=}3$ was **gated off** (Vikas holding ConcurrentExecutions). Localsim $n{=}3$ on the same 4 lite cells **was executed**.

Authoritative confirmatory stats remain packaging-deduped localsim: `results/summary/stats_H1_H2_H3.json` (`runs: 350`, `backend: localsim`). Live evidence is still the **lite 4-cell × n=1** smoke under `results/live/key_cells/` (stack destroyed). No live $n{>}1$ numbers exist.

| Issue | Status |
|-------|--------|
| Phase run-count table (350 vs 690) | **Reconciled** — design vs on-disk; analysis dedupes |
| H1–H3 claim↔JSON | Localsim-only; twin-inflated drafts withdrawn |
| Live AWS SQS key-cell lite round | **4/4 cells measured** (n=1); stack **destroyed** after round |
| Beyond-CA2 live $n{=}3$ (same 4 cells) | **Not run** — probe `results/beyond_ca2/concurrency_probe_2026-09-20.json` (limit=10, observed max=4 on `idem-eval-fn`, Anji ESM=5 → 1 spare) |
| Beyond-CA2 localsim $n{=}3$ (same 4 cells) | **12/12 localsim** — `results/localsim/key_cells_n3/` |
| Beyond-CA2 poller sensitivity (conc 2 vs 5) | **8/8 localsim** — `results/localsim/key_cells_concurrency/` |

### Live lite round (measured; n=1 each; eu-west-1)

| Campaign | Fault | VT | MRC | loss | dup | DLQ | recovery_s | thr msg/s | usd |
|----------|-------|---:|----:|-----:|----:|----:|-----------:|----------:|----:|
| L_vt_consumer_kill | consumer_kill | 30 | 5 | 0.0 | 0.015 | 0.0 | 2.343 | 2.824 | 0.000387 |
| L_vt_consumer_kill | consumer_kill | 90 | 5 | 0.0 | 0.005 | 0.0 | 7.532 | 1.537 | 0.000382 |
| L_mrc_unhandled_error | unhandled_error | 30 | 1 | 0.0 | 0.0 | 0.16 | — (censored) | 7.122 | 0.000311 |
| L_mrc_unhandled_error | unhandled_error | 30 | 5 | 0.0 | 0.05 | 0.0 | 28.506 | 2.920 | 0.000362 |

- Wall: **772.3 s** (`run.log`); measured cost sum **≈ $0.00144**
- Evidence: `results/live/key_cells/`
- Destroy: Terraform state serial 43, **0 resources**; names = `sqs-rr-*` (no student IDs)

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
COMPLETE=yes ALIGNMENT=100 CA2_FLOOR=met
READY_FOR_AWS=done_lite_round
SOLE_AWS_RESIDUAL=closed
AWS_CLASS=required
GATE_READY=yes
LIVE_LITE_COMPLETE=yes
LIVE_CONFIRMATORY=blocked_concurrency
LOCALSIM_N3=yes
DESTROY_AFTER_ROUND=yes
BEYOND_CA2=localsim_n3_done_live_n3_blocked
```

---
# Project Status: Simulation vs Live AWS

**Student:** Anjaneya Reddy Gurram (24288853)  
**Project:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Last Updated:** September 20, 2026

## Executive Summary

Primary experimental evidence is the **local simulator** (350 packaging-deduplicated design cells). A **live AWS lite key-cell round (4/4, n=1)** was executed on eu-west-1 and archived under `results/live/key_cells/`. Live numbers are directional smoke only; confirmatory hypothesis tests remain localsim-only. Stack was **destroyed after the round** (evidence files kept). **DIVE/adaptive_vt was not enabled** in the committed experiment matrix.

Beyond-CA2 (2026-09-20): confirmatory live $n{=}3$ was **not** applied (Vikas `idem-eval-fn` holding ConcurrentExecutions max=4 of 10). Localsim $n{=}3$ on the same four lite cells **was** run (`results/localsim/key_cells_n3/`).

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

1. **Terraform-backed live stack** applied in eu-west-1 for the lite round
2. **4/4 live key cells** in `configs/live_key_cells.yaml` with manifests + raw samples
3. **Teardown** — `terraform destroy` after round; evidence retained under `results/live/`

### Partial / open (beyond CA2, not floor gates)

1. **Confirmatory live $n{=}3$** — protocol ready (`configs/live_key_cells_n3.yaml`); blocked by shared-account concurrency
2. **Live↔sim fidelity** statistical comparison — not run
3. **Dedicated adaptive_vt / DIVE campaign** (optional; matrix disabled)

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

Localsim evidence is reconciled to the 350-cell design. Live lite key-cells are **measured (4/4, n=1)** but **not confirmatory**. CA2 **floor = 100% COMPLETE**. Beyond-CA2 live $n{=}3$ remains the preferred AWS next step when the account has headroom; this pass recorded localsim $n{=}3$ instead of inventing live repeats.

---

**Honest Disclosure:** Live spend for the lite round ≈ **$0.00144** measured. Stack destroyed after that round. **No additional live SQS spend this pass.** Beyond-CA2 localsim $n{=}3$ is simulation, not AWS.
