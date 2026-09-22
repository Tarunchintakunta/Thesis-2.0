# GENAI_HANDOFF.md — Venkat (distributed-matrix-scaling)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Venkat Bora |
| Artefact root | `venkat-bora-thesis/distributed-matrix-scaling/` |
| Honest CA2 floor | **PARTIAL → improved (~75–80)** after RSS/CPU live instrumentation; size-ladder still soft |
| Eval completeness | Prior time-only final_1–3 + **rss_size_final_1\|2\|3** with peak_rss_mb / avg_cpu_percent |
| AWS | eu-west-1 Free-Tier matched vCPU; destroy-after each round |
| Handoff date | 2026-09-22 |

## 1. Research problem, motivation, research question, and objectives

Compare scale-up vs scale-out matrix multiply on EC2 for completion time, **memory footprint**, and **CPU efficiency** (and ideally across increasing sizes).

## 2. Identified literature gap and how this research addresses it

Matched Free-Tier vCPU live comparison with instrumented RSS/CPU — not time-only anecdotes.

## 3. CA2 proposal alignment and any extensions beyond the proposal

Prior gap (independent review): memory/CPU unverifiable. **Closed on disk:** live peak RSS + avg CPU on same software stack. Soft residual: multi-order size ladder (timeouts as outcomes).

## 4. Research methodology and experimental design

Baseline: 1× t3.small numpy matmul (scale-up). Proposed: 2× t3.micro Dask multi-instance matmul. n=250; three independent destroy-after rounds with instrumented benches.

## 5. Artefact purpose and artefact-only project structure

```
distributed-matrix-scaling/
  scripts/quick_bench.py      # peak_rss_mb + avg_cpu_percent
  scripts/dist_bench.py
  scripts/run_ec2_rss_size_final.sh
  results/live/rss_size_final_{1,2,3}/
  results/live/RSS_FINAL3_BASELINE.md
```

## 6. AWS architecture, services, configurations, and experimental setup

EC2 + SSM; Dask scheduler on scale-out-0; one worker per micro; destroy-after.

## 7. Evaluation metrics and why they were selected

elapsed_s, peak_rss_mb, avg_cpu_percent — map to RQ limbs (time/memory/CPU).

## 8. Baseline definition and baseline comparison

| Role | Topology |
|------|----------|
| Baseline (scale-up) | 1× t3.small numpy |
| Proposed (scale-out) | 2× t3.micro Dask multi-instance |

Do not assume scale-out is faster — prior finals showed anti-crossover (scale-up much faster on n=250).

## 9. Complete evaluation process and number of runs

| Pack | Path |
|------|------|
| rss_size_final_1–3 | `results/live/rss_size_final_{1,2,3}/summary.json` |
| Baseline note | `results/live/RSS_FINAL3_BASELINE.md` |
| Prior time-only finals | `results/live/final_{1,2,3}/` (elapsed only) |

## 10. Final results and key findings (committed evidence)

| Round | scale-up elapsed_s | scale-up peak_rss_mb | multi elapsed_s | multi peak_rss_mb | multi avg_cpu% |
|------:|-------------------:|---------------------:|----------------:|------------------:|---------------:|
| 1 | 0.002467 | 37.43 | 0.2532 | **72.49** | 44.4 |
| 2 | 0.001914 | 0.0* | 0.2736 | **72.47** | 46.1 |
| 3 | 0.002016 | 37.34 | 0.2661 | **72.84** | 38.6 |

\*Ultra-short scale-up can miss sampler; multi-instance RSS/CPU is the stable RQ limb.

**Time limb (consistent with prior finals):** scale-up ≪ multi on n=250 (anti-crossover retained — honest negative for “scale-out is faster”).

## 11–12. Objectives / RQ

Memory/CPU limbs **now measurable** on live EC2. Time limb reconfirmed. Size-increasing limb still partial without ladder pack.

## 13–17. Literature / stats / observations / limitations / conclusions

Descriptive consistency across 3 instrumented rounds. Limitation: n=250 only in RSS packs; Free-Tier burst/RAM asymmetry; scale-up RSS sampler floor. Contribution: closes “unverifiable memory/CPU” gap with destroy-after evidence.

## 18–19. Changes / remaining

1. Optional size ladder 100/250/500 with timeouts-as-outcomes.  
2. Keep anti-crossover honesty in conclusions.

## 20. Important files

`scripts/{quick_bench,dist_bench,run_ec2_rss_size_final}.sh/.py`, `results/live/rss_size_final_{1,2,3}/`, `RSS_FINAL3_BASELINE.md`.
