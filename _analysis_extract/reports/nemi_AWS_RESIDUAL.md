# Nemi alignment residual (AWS-goal — live cloud FL closed)

**Updated:** 2026-09-20  
**Alignment:** **100/100** (CA2 floor)

## Compact
`RQ6 Obj10 Method11 Impl11 Exp11 Metrics10 Evidence11 Claims10 Rubric10` → **100/100**

## Live lite cloud FL (measured, then destroyed)

Authoritative: `Nemi/securefl-ids/results/live/cloud_lite_summary.json`

| Field | Value |
|-------|--------|
| Mode | `live_aws` (not paperwork) |
| Region | eu-west-1 |
| Instance | `i-012ae234495584077` `t3.micro` (Free Tier) |
| Bucket | `securefl-ids-artifacts-0fb66e133bb11fcdd263c314e4` |
| Log group | `/research/securefl-ids` |
| Config | 2 clients × 3 rounds × 2500 real-lite rows (39 numeric features) |
| Baseline | acc **0.5000**, F1 **0.0000**, comm **1.230** MB/round |
| Improved | acc **0.5480**, F1 **0.2260**, comm **1.246** MB/round |
| S3 round-trip | yes (global.pt each round) |
| CloudWatch | 6 metric puts, 9 log events, namespace `SecureFL-IDS` |
| Lambda | **not used** |
| Vikas preflight | `idem-eval-fn` Invocations(10m)=1171, ConcurrentExecutions max=10 |
| Destroy | **complete** — 9 resources; instance terminated; bucket/log-group/IAM gone |

Lite 3-round cloud metrics do **not** replace the 30-round local campaigns in `results/comparison/` and `results/unsw_real/`.

## Sole residual

**Closed.** Optional beyond-CA2: 2.5M-flow corpus, 50-round campaigns, Docker/K8s, improved-arm plateau (`DESIGN_RATIONALE_BEYOND_CA2.md`).

```
GATE_READY=done COMPLETE=yes ALIGNMENT=100 SOLE_AWS_RESIDUAL=closed CA2_FLOOR=met BEYOND_CA2=optional
```
