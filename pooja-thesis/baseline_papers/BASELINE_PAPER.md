# Baseline paper — Pooja (CA2-mapped)

**Student folder:** `pooja-thesis`  
**Citation:** Wanigasooriya & Ekanayake (2026) — *NimbusGuard… DQN* — IEEE ICOIN 2026  
**Identifier:** `doi: 10.1109/ICOIN68469.2026.11480646` / arXiv:2604.11017

## File
- `PRESENT: Wanigasooriya_Ekanayake_2026_NimbusGuard_baseline.pdf`

## Problem → CA2 commitment
Proactive K8s autoscaling improves SLA vs reactive HPA/KEDA but is **most agile and least stable** (high replica count / scaling events). Authors name stability as future work.

## Solution (paper)
DQN + LSTM (+ LLM elements) proactive autoscaler on a real Kubernetes testbed.

## Gap
Stability cost not fixed. Our commitments reproduce the **trade-off** with a **simpler MLP simulator** (intentional method simplification) and add EMA + hysteresis/cooldown.

## Metrics mapped to eval
| Paper emphasis | Ours (CSV) |
|----------------|------------|
| Responsiveness / SLA | SLA Violations |
| Resource cost | Over-provisioning % |
| Instability | Scaling Events, Pod Count Volatility |

Evidence: `paks-framework/results/results_summary.csv`. Do **not** claim identical DQN agent metrics.
