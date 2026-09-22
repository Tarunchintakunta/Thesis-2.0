# mqtt-qos-iot-core — formal CA2 artefact status

**Last updated:** 2026-09-21  
**Formal contract:** `uday-thesis/CA2_COMMITMENTS.md`  
**Alignment residual:** `_analysis_extract/reports/uday_alignment.md`  
**Design rationale:** `uday-thesis/DESIGN_RATIONALE_BEYOND_CA2.md`  
**CA2 align % (honest):** **100 / 100** (research-scope floor)  
**INITIAL_EVAL_PASS:** **yes** (lite 16-cell live treated as initial eval; CA2 still 100%). Final-3 **not** started.  
**READY_FOR_AWS:** **YES** (lite/smoke only; formal still free-tier-blocked as single-month apply)

## What this artefact is

Formal CA2: **MQTT QoS 0 vs 1 message loss under controlled publisher disconnect on AWS IoT Core**, with device-side ID log matched via **rules → Lambda → DynamoDB**. Factors: QoS × disconnect ∈ {0,15s,1m,5m} × rate ∈ {steady,bursty}. Synthetic devices are allowed (and used).

## Gates (READY_FOR_AWS)

| Gate | Status |
|------|--------|
| Project tags on terraform (`Project`, `Thesis`, `Environment`, `ManagedBy`, `Campaign`) | Pass |
| Destroy hook `scripts/destroy_stack.sh` | Pass |
| Free-tier cost plan: **lite** under monthly IoT budget with headroom; **formal** blocked | Pass (`make plan-ft`) |
| Live runner unblocked for **smoke/lite only** when gates pass | Pass |

Check: `python scripts/check_ready_for_aws.py`

## Live campaigns (eu-west-1) — done & destroyed

| Scale | Cells | Devices × msgs | IoT msgs upper | Stack | Evidence |
|-------|------:|----------------|----------------|-------|----------|
| smoke | 4 | 2 × 8 | ~96 | applied → **destroyed** (25) | `results/live/archive/smoke-2026-09-21/` |
| **lite** | **16** | **5 × 50** | **~6 000 (~2.4% FT)** | applied → **destroyed** (43) | `results/live/LIVE_EVIDENCE.json` |

### Lite directional result (bound; n=1 rep/cell)

| QoS | disconnect | loss (steady / bursty) | note |
|-----|------------|------------------------|------|
| 0 | 0 | 0.00 / 0.00 | connected path |
| 0 | 15 s | 0.30 / 0.30 | drops during cut |
| 0 | 60 s / 300 s | 0.68 / 0.68 | **identical under lite schedule** (cut covers remaining publishes; see limitations) |
| 1 | all disconnects | **0.00 / 0.00** | backlog flush survives; **latency cost** mean ~3–14 s under disconnect cells |

**Negatives / limitations retained (rubric honesty):** d60≡d300 QoS0 loss under lite wall-clock; n=1 replication (no Holm power claim); QoS1 reliability is paid in latency/backlog — not free.

## Free-tier reconciliation

| Scale | IoT msgs upper | vs 250 000 free | Headroom |
|-------|----------------|-----------------|----------|
| formal | ~600 000 | **exceeds** | blocked (single month) |
| lite | ~6 000 | ok (~2.4%) | ~97.6% |
| smoke | ~96 | ok | ~99.96% |

Formal **80 cells / ~600 000 msgs** is **beyond CA2 floor** — multi-month staged campaign or accepted overage (`DESIGN_RATIONALE_BEYOND_CA2.md`). Research-scope MQTT QoS IoT method is satisfied by **lite** (full 16-cell live factorial + destroy).

## What is done

| Piece | Status |
|-------|--------|
| Local mock harness | Done |
| Factorial + seeds | Done |
| lite + smoke configs | Done |
| Metrics + Holm on mock | Done |
| IaC modules + tags + `enable_apply` | Done |
| `run_live.py` smoke/lite after gates | Done (formal blocked) |
| Live smoke + **full lite 16-cell** + destroy | **Done** |

## Soft / beyond-floor (not floor blockers)

1. Multi-month **formal-scale** live (5×1000×16×5) for power + separating long disconnects.
2. Shvaika et al. (2025) **prose** contrast in the final report (mapping already in `baseline_papers/BASELINE_PAPER.md` + lite numbers bound).
3. Report / config-manual polish (MQTT, not federated RF).

## Measurement honesty

- `results/mock/` — **not** AWS measurements.
- `results/live/` — AWS IoT Core **lite** evidence (16 cells); **not** formal-scale N.

## Quarantine

`uday-thesis/iot-reliability/` (federated RF vs Et-Tousy) is a **PROXY / different RQ** — not formal CA2 fulfilment.
