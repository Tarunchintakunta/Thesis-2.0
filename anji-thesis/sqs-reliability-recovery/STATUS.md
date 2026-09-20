## Alignment note (2026-09-20 — live lite key-cells measured)

**CA2 research alignment ≈ 96% — still < 100%. NOT COMPLETE.**

Authoritative confirmatory stats remain packaging-deduped localsim: `results/summary/stats_H1_H2_H3.json` (`runs: 350`, `backend: localsim`). Live evidence is a **lite 4-cell × n=1** smoke under `results/live/key_cells/` (`configs/live_key_cells.yaml`); it does **not** replace H1–H3. Live↔sim **relative ranks** agree (`results/live/key_cells/fidelity.json`); absolute recovery times are **not** scale-matched.

| Issue | Status |
|-------|--------|
| Phase run-count table (350 vs 690) | **Reconciled** — design vs on-disk; analysis dedupes |
| H1–H3 claim↔JSON | Localsim-only; twin-inflated drafts withdrawn |
| Live AWS SQS key-cell lite round | **4/4 cells measured** (see table below); stack **destroyed** after round |
| Confirmatory live / burst / VT600 CA2 depth | **Still open** — caps at <100% |

### Live lite round (measured; n=1 each; eu-west-1)

| Campaign | Fault | VT | MRC | loss | dup | DLQ | recovery_s | thr msg/s | usd |
|----------|-------|---:|----:|-----:|----:|----:|-----------:|----------:|----:|
| L_vt_consumer_kill | consumer_kill | 30 | 5 | 0.0 | 0.015 | 0.0 | 2.343 | 2.824 | 0.000387 |
| L_vt_consumer_kill | consumer_kill | 90 | 5 | 0.0 | 0.005 | 0.0 | 7.532 | 1.537 | 0.000382 |
| L_mrc_unhandled_error | unhandled_error | 30 | 1 | 0.0 | 0.0 | 0.16 | — (censored) | 7.122 | 0.000311 |
| L_mrc_unhandled_error | unhandled_error | 30 | 5 | 0.0 | 0.05 | 0.0 | 28.506 | 2.920 | 0.000362 |

- Wall: **772.3 s** (`run.log`); measured cost sum **≈ $0.00144**
- Evidence: `results/live/key_cells/manifests/*.json`, `raw/`, `summary.json`, `summary.csv`, `live_key_cells_summary.json`
- Destroy: Terraform state serial 43, **0 resources**; no `sqs-rr*` Lambda/SQS in eu-west-1 after round
- **Not claimed:** live confirmatory H1–H3; live n>1; burst/`key_cells.yaml` (VT 600 / MRC 10 / repeats=5)
- **Fidelity (non-AWS):** relative ranks agree (longer VT → longer recovery; MRC1 DLQ > MRC5; MRC5 dup > MRC1). Absolute recovery 2.3–28 s live vs ~32–61 s localsim (200 vs ~3600 orders). VT90 matched to sim VT60.

```
READY_FOR_AWS=done_lite_round
SOLE_AWS_RESIDUAL=partial
AWS_CLASS=required
GATE_READY=yes
LIVE_LITE_COMPLETE=yes
LIVE_CONFIRMATORY=no
DESTROY_AFTER_ROUND=yes
```

Remaining to 100%: confirmatory live repeats and/or CA2-depth key cells (burst / longer VT). Live↔sim relative-rank writeup is filled; do **not** treat it as live n>1.

---
# Project Status: Simulation vs Live AWS

**Student:** Anjaneya Reddy Gurram (24288853)  
**Project:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Last Updated:** September 20, 2026

## Executive Summary

Primary experimental evidence is the **local simulator** (350 packaging-deduplicated design cells). A **live AWS lite key-cell round (4/4, n=1)** was executed on eu-west-1 and archived under `results/live/key_cells/`. Live numbers are directional smoke only; confirmatory hypothesis tests remain localsim-only. Stack was **destroyed after the round** (evidence files kept). **DIVE/adaptive_vt was not enabled** in the committed experiment matrix.

## Implementation Status

### ✅ Completed (Simulated)

1. **Core Infrastructure** — SAM template + Terraform stack (project tags only; no personal IDs)
2. **Local Simulator** (`src/localsim/`)
3. **Experiment Infrastructure** (`src/control/`) including live backend + cost guard
4. **Testing** — unit/integration; CI
5. **Experiments and Analysis** (localsim): Pilot / Baseline / Arms / Campaigns A–H / Burst; H1–H3 Holm–Bonferroni on deduped rows; figures
6. **Documentation**

### ✅ Completed (Live — lite only)

1. **Terraform-backed live stack** applied in eu-west-1 for the lite round
2. **4/4 live key cells** in `configs/live_key_cells.yaml` with manifests + raw samples
3. **Teardown** — `terraform destroy` after round; evidence retained under `results/live/`

### ⚠️ Partial / open

1. **Confirmatory live campaigns** (repeats > 1; burst / VT 600 matrix from `key_cells.yaml`)
2. **Live↔sim fidelity** — relative ranks written (`results/live/key_cells/fidelity.json`); absolute recovery not comparable
3. **Dedicated adaptive_vt / DIVE campaign** (optional; matrix disabled)

## Simulation Validity

### Known Simulator Limitations

1. **No Cold Starts**
2. **No Concurrency Limits**
3. **No Network Variability**
4. **No AWS Service Failures**
5. **Simplified Visibility Timeout**
6. **No Poison Pill Side Effects**

### Packaging twin note

Two git cohorts differ only by whether `spec.adaptive_vt: false` is present. Metrics and seeds match; `config_hash`/`run_id` differ. See `results/README.md` and `configs/analysis_plan.yaml` amendment 2026-09-20.

## How to Verify

1. **Localsim:** `make test` / `make stats` (must report `350 runs` after packaging-dedup)
2. **Live evidence:** inspect `results/live/key_cells/summary.json` and manifests (`backend: live`)

## Conclusion

Localsim evidence is reconciled to the 350-cell design. Live lite key-cells are **measured (4/4)** but **not confirmatory**. Live↔sim relative ranks agree; absolute recovery does not match at this scale. **CA2 alignment ≈ 96% < 100%** until confirmatory/deeper live CA2 key-cell evidence lands.

---

**Honest Disclosure:** Live spend for this lite round ≈ **$0.00144** measured (cost-guard estimate was ~$0.01 with safety). Stack destroyed after round. CA2 alignment **≈ 96% < 100%**. **NOT COMPLETE.**
