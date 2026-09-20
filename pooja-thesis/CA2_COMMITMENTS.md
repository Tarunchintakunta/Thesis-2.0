# CA2 Commitments (proxy) — Pooja

**Status:** Formal CA2 file **NOT FOUND** in-repo. This document is the **binding research contract** until a real CA2 is added.  
**AWS deploy:** **Not required** for research alignment (local synthetic K8s-policy simulation). Lambda/SAM is packaging only — **do not deploy AWS**.

## Research question
Can a proactive autoscaler keep most of its SLA-violation advantage over reactive HPA while substantially reducing instability (scaling-event frequency, pod-count volatility) that an unfiltered proactive policy exhibits?

## Objectives (must evidence)
1. Reproduce NimbusGuard’s agility–instability trade-off with a simpler feed-forward predictor (not identical DQN+LSTM+LLM agent).
2. Build stability fix (EMA + hysteresis/cooldown) named as future work in NimbusGuard.
3. Quantify trade-offs across SLA / over-provisioning / scaling events / volatility over multiple seeds.

## Baseline
Wanigasooriya & Ekanayake (2026), NimbusGuard, IEEE ICOIN 2026. DOI `10.1109/ICOIN68469.2026.11480646` / arXiv:2604.11017. PDF under `baseline_papers/`.

## Variables / metrics (eval↔CSV)
| Metric | Artefact |
|--------|----------|
| SLA Violations | `paks-framework/results/results_summary.csv` |
| Over-provisioning % | same |
| Scaling Events | same |
| Pod Count Volatility | same |
| Seeds | 42–46 (`results_per_seed.csv`) |

## Non-goals (honest)
- Live Kubernetes / HPA / KEDA testbed (NimbusGuard method not fully replicated)
- Live AWS Lambda/Kinesis deploy
- Claiming identical agent to NimbusGuard DQN
