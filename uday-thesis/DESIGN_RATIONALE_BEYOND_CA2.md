# Design rationale — CA2 floor + beyond-floor formal depth (Uday)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Bar:** 100% CA2 = RQ / objectives / gap / method / artefact / eval **scope** — not perfect marks.  
**AWS:** required. Live lite applied, measured, **destroyed** (2026-09-21).

## CA2 floor (met)

| Commitment | Delivered evidence | Scope note |
|------------|-------------------|------------|
| RQ: QoS 1 vs 0 loss under controlled disconnect on **AWS IoT Core** | Lite live 16-cell factorial; QoS1 loss **0.0** all cells; QoS0 loss **0.30** (15 s) / **0.68** (60 s & 300 s) | Bound in `mqtt-qos-iot-core/results/live/LIVE_EVIDENCE.json` |
| Method: device-side ID log; rules→Lambda→DynamoDB match; factors QoS × disconnect × rate | IaC + live runner; smoke then full lite | Synthetic devices allowed by formal CA2 |
| Objectives: loss; duplication+latency; reconnection/backlog; reliability–cost | Lite cells report loss, dup_id_rate, latency mean/p95/p99, backlog queued/survived, usd_est | Cost = unit prices × counted ops |
| Baseline: Shvaika et al. (2025) | Gap mapping in `baseline_papers/BASELINE_PAPER.md`; lite supplies managed-broker disconnect numbers Shvaika defer | Final-report prose fold soft |
| Free-tier + destroy | lite ~6 k msgs (~2.4% of 250 k); stack destroyed (43 resources); state empty; `.certs` scrubbed | formal single-month blocked |

## Explicitly beyond floor (not blockers)

| Extension | Why beyond floor |
|-----------|------------------|
| Formal **80 cells / ~600 000 IoT messages** (5 devices × 1000 msgs × 5 reps) | Exceeds single-month IoT free tier (250 000). Needs **multi-month staging** or accepted overage — stronger power / separates long disconnects, not required to answer the RQ at research-scope depth |
| Holm–Bonferroni at formal N | Lite is n=1 replication/cell — **directional**; confirmatory multiplicity control is a power upgrade |
| Separating disconnect 60 s vs 300 s loss | Under lite ~49 s publish schedule both cuts cover remaining messages → identical QoS0 loss 0.68. Formal 5 s × 1000 msgs schedule would separate them |
| Shvaika VoR line-by-line numeric clone | Baseline is a **gap** paper (self-hosted steady load); contrast is managed + disconnect, not hyperparam clone |

**COMPLETE decision:** Full 16-cell live IoT Core factorial under Free Tier, with destroy-after, answers the formal MQTT QoS method at floor depth. The 80-cell / 600 k-msg campaign is a multi-month beyond-floor programme.

## Soft residuals (report quality — not reopen floor)

1. Fold Shvaika contrast prose into the final report using bound lite tables.  
2. Config-manual / report rewrite against MQTT (federated RF remains quarantined).  
3. Optional staged formal when credits allow.

## Alignment

**Formal CA2 research-scope: 100%.** Soft / beyond-floor items above do **not** reopen the floor.
