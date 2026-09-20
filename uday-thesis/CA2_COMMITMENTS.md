# CA2 Commitments — Uday (formal)

**Source:** Derived from formal CA2 file `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx` (*Evaluating MQTT Quality-of-Service Reliability in AWS IoT Core…*).  
**Status:** Binding research contract = **formal CA2**.  
**Artefact:** `uday-thesis/mqtt-qos-iot-core/` (this pass: Terraform + mock dry-run; **not** live AWS).  
**Quarantine:** `uday-thesis/_superseded_proxy/iot-reliability/` — federated RF vs Et-Tousy; **not** this CA2; do not revive as evidence.  
**AWS:** **Required.** Formal experiment is a live (account-owned) **AWS IoT Core** campaign with rules → Lambda → DynamoDB matching. Synthetic device telemetry is **explicitly allowed**. This agent pass does **not** deploy.

## Research question (formal)
To what extent does publishing at MQTT QoS level 1 rather than level 0 reduce telemetry message loss in AWS IoT Core when the publishing device undergoes controlled disconnections of varying duration?

## Objectives (must evidence)
1. Quantify message **loss** at QoS 0 vs 1 across controlled disconnection durations (none, 15s, 1m, 5m).
2. Quantify **duplication** and end-to-end **latency** (mean / p95 / p99) as the price of reliability.
3. Measure **reconnection** behaviour and backlog survival.
4. Place each configuration on a **reliability–cost** surface (estimated from published unit prices × counted operations).

## Method (formal)
- Simulated devices; device-side ID log before publish; match delivered records in DynamoDB.
- Factors: QoS ∈ {0,1} × disconnect ∈ {0,15s,1m,5m} × rate ∈ {steady, bursty}; 5 devices × 1000 msgs; 5 replications; α=0.05 Holm–Bonferroni.
- Provision via IaC; destroy identically; stay free-tier-safe.

## Baseline (formal)
Shvaika et al. (2025) managed/self-hosted MQTT broker characterisation — contrast under disconnection on a broker the tenant does **not** control.

## Variables / metrics
| Metric | Formal commitment |
|--------|-------------------|
| Loss rate | Primary DV |
| Duplicate-delivery rate | Secondary |
| E2E latency (mean, p95, p99) | Secondary |
| Reconnection time / backlog / rule-trigger success | Secondary |
| Estimated service cost | Objective 4 |

## Non-goals / honesty
- Prior proxy “federated RF recovers centralized Et-Tousy accuracy” is **not** this CA2.
- Synthetic telemetry is **not** a blocker (formal commits to synthetic).
- QoS 2, multi-region, physical radios: deferred in formal CA2.
- Mock dry-run in `mqtt-qos-iot-core/results/mock/` is **harness proof**, not IoT Core evidence.
