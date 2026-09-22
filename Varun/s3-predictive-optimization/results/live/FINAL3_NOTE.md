# Varun final-3+ note (independence)

**Authoritative confirmatory live packs (independent):** `evaluation_r4` + `evaluation_r5`  
**Archival (non-independent):** `evaluation_r1|r2|r3` share identical `raw_costs` SHA (`dbc3c0f1…`) and `rebuilt_from_run_log=true` — retained for history; **do not** cite as three independent evals.

## SHA256 of `raw_costs.json`

| Pack | SHA1 (shasum) | Independent? |
|------|---------------|--------------|
| r1–r3 | `dbc3c0f1d944b644a052e641d53195d6f9a1a505` (identical) | No |
| r4 | `7babd39cee64656b34bc876a34b645e2b460c3a5` | Yes (seed 4242) |
| r5 | `53bec5e526389e479ef524c67be2a7dafe65cfd5` | Yes (seed 5252) |

## Protocol
`ca2_three_workload_wilcoxon` — 10 trials × 80 objects × 3 workloads; live S3 put + HeadObject metadata rebuild; costs via SavingsEstimator vs Lifecycle + Intelligent-Tiering; Wilcoxon paired; `rebuilt_from_run_log=false` on r4/r5.

## Results (r4 / r5)

| Workload | r4 vs both natives | r5 vs both natives |
|----------|--------------------|--------------------|
| static_archival | True (ΔLC≈0.00249, p≈0.00195) | True (ΔLC≈0.00267, p≈0.00195) |
| mixed_access | True (ΔLC≈0.00238, p≈0.00195) | True (ΔLC≈0.00234, p≈0.00195) |
| high_churn | True (ΔLC≈0.00013, p≈0.0488) | True (ΔLC≈0.00025, p≈0.0098) |
| `meets_ca2_two_of_three` | **true** (3/3) | **true** (3/3) |

Also: `BASELINE_COMPARE.md` / `baseline_compare_e1_e2_e3.json` remain for the archival e1–e3 pack.

## Destroy-after
Terraform destroy completed 2026-09-22 after r5 (bucket `s3-pred-opt-6f20925a7e37bceee781030afa` removed).
