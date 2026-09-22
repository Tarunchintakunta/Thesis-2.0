# Independent review — Varun (s3-predictive-optimization)

**Date:** 2026-09-22  
**STATUS claim overturned:** `CA2 100%` with three full live evaluations — **not accepted as three independent evals**.  
**Honest CA2 floor:** **partial (~70)**

## RQ (CA2 `VarunGampa_RIC_CA2.txt`)
> To what extent does an integrated predictive storage-class optimisation framework … reduce Amazon S3 storage cost and improve storage-class allocation accuracy, relative to AWS-native Lifecycle Policies and Intelligent-Tiering, when evaluated in a live AWS environment?

## Artefact reality
Pipeline under `Varun/s3-predictive-optimization/` (recommendation, Prophet forecast, savings, simulator, `src/metadata/` collector, Terraform). Dry-run + live lite + evaluation packs present.

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Dry-run forecast beats naive | **Demonstrated** | `results/data/*_results.json`: pilot MAPE 0.016 vs naive 0.44; baseline 0.006; improved 0.231 — all `beats_naive=true`. Allocation acc: pilot 0.32, baseline 0.504, improved **0.178** |
| Live lite S3 | **Demonstrated** | `results/live/live_lite_summary.json`: 48 objects; PUT mean STANDARD 1008.3 ms / IA 681.6; CE sum **$3.6e-09**; Wilcoxon probe p=9.63e-07 |
| e1–e3 two-of-three vs natives | **Partial / Unverifiable independence** | `evaluation_r{1,2,3}/summary.json`: `meets_ca2_two_of_three=true`; static_archival ΔLC=0.005119 p=0.00195; mixed_access ΔLC=0.003180; high_churn ΔLC=**6.53e-05** p=**0.557** (null). **raw_costs.json SHA256 identical across r1=r2=r3** (`8c8b853dc2767396…`); all `rebuilt_from_run_log=true` |
| Allocation accuracy improvement (RQ limb) | **Not supported on improved arm** | Live eval is cost Wilcoxon, not allocation-acc; dry-run improved alloc=0.178 |
| CE-settled production savings | **Not claimed / not demonstrated** | Trial cost model; lite CE ≠ campaign |

## Floor
**Partial.** Live protocol structure and negative high_churn honesty are real. Treating e1–e3 as three independent full evaluations is **Claimed** — disk shows one rebuilt cost matrix copied thrice.

## Highest-value next steps
1. Fresh independent trial sampling for ≥2 new evaluations (new raw hashes).  
2. Report allocation accuracy on live recommendations, not only modeled $ deltas.  
3. Keep high_churn null visible in LaTeX.
