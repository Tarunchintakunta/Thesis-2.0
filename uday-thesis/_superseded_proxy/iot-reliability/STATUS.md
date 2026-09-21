# Project Status: uday-thesis / iot-reliability

**Last Updated:** 2026-09-21  
**Research Alignment to formal CA2:** **~18% as a stand-alone tree** — this directory does **not** implement formal CA2.  
**Status:** **QUARANTINED (PROXY)** — **not** formal CA2 fulfilment.

## Quarantine note (binding)

Formal CA2 is **MQTT QoS 0 vs 1 reliability under controlled disconnect on AWS IoT Core**
(`uday-thesis/CA2_COMMITMENTS.md`). The **formal artefact** is:

`uday-thesis/mqtt-qos-iot-core/`

This `iot-reliability/` tree implements **federated RF vs Et-Tousy OneM2M** — a **different research question**. Shared surface is only “IoT” + an old SAM scaffold. Treat all accuracy/F1 tables below as **PROXY-era evidence**, not MQTT/IoT Core CA2 results.

**Federated RF is PROXY, not formal CA2.**

## Evidence-bound results (seeds 42–46) — artefact as-built (PROXY; not formal MQTT)

Source: `results/results_summary.csv` (+ `results_per_seed.csv`).

| Model | Accuracy | Macro-F1 | Critical Recall (class 2) |
|--------|---------:|---------:|-------------------------:|
| Centralized RF (baseline) | 0.9995 ± 0.0005 | 0.9996 ± 0.0005 | 0.9994 ± 0.0013 |
| Federated Ensemble RF | 0.9959 ± 0.0024 | 0.9949 ± 0.0024 | 0.9997 ± 0.0007 |
| Single-Site Local Only | 0.9761 ± 0.0046 | 0.9737 ± 0.0051 | 0.9958 ± 0.0031 |

These numbers do **not** answer the formal MQTT/IoT Core CA2.

## AWS

Formal CA2 **requires** AWS IoT Core. Live campaign lives under `mqtt-qos-iot-core/` and is **not deployed** this pass. See `mqtt-qos-iot-core/STATUS.md` (`READY_FOR_AWS: NO`).
