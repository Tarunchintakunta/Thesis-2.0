# Baseline paper — Uday (CA2-mapped)

**Student folder:** `uday-thesis`  
**Citation:** Shvaika, A., Shvaika, D., Landiak, D. and Artemchuk, V. (2025). *A distributed architecture for MQTT messaging: the case of TBMQ.* Journal of Big Data, 12(1), 224. doi: 10.1186/s40537-025-01271-x  
**Companion (replay path, still connected):** Shvaika, D., Shvaika, A. and Artemchuk, V. (2025). MQTT broker architectural enhancements… *IoT*, 6(3), 34.

## File
- Formal CA2: `../UdayKiranReddyDodda_X25166484_proposal.docx`
- PDF on disk (if present): `baseline_papers/` — add the Shvaika VoR when obtained; **do not** treat `EtTousy_et_al_2026_Federated_QoS_baseline.pdf` as this CA2's baseline.

## Problem → CA2 commitment
Shvaika et al. (2025) characterise a **self-hosted**, Kafka/Redis-backed broker at **steady high load** and **name as future work** varying QoS, intermittent connectivity, and varying client conditions. The formal CA2 inverts that: measure a **managed** broker (AWS IoT Core) under **controlled publisher disconnect**, at QoS 0 and 1, against per-message ground truth.

## Gap the thesis takes up
No reviewed study jointly has: managed broker + client disconnection + more than one service level + per-message device-side log. Shvaika is the named baseline because it states the omitted conditions.

## Metrics mapped to eval
| Paper / commitment | Ours |
|--------------------|------|
| Delivery completeness | Loss rate (primary) |
| (unnamed in baseline under disconnect) | Duplicate-id rate; E2E latency mean/p95/p99 |
| Persistence / replay (companion, clients still connected) | Reconnection time + backlog survival |
| Operational cost (not in baseline) | Estimated USD from published unit prices × counted ops |

**No live AWS numbers yet.** Mock CSVs in `mqtt-qos-iot-core/results/mock/` are not a Shvaika contrast.

## Superseded mapping (do not use)
Et-Tousy et al. (2026) federated-RF offload mapping belonged to the quarantined proxy (`../_superseded_proxy/iot-reliability/`).
