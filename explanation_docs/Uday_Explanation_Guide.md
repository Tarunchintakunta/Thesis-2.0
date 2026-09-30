# MQTT QoS 0 vs 1 Message Loss under Controlled Disconnect on AWS IoT Core

**Student:** Uday Kiran Reddy Dodda  
**Student ID:** X25166484  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Format:** Short explanation guide (target 5–6 pages)

---

## What is the project?

MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core; lite 16 cells then destroy. Artefact: mqtt-qos-iot-core/ only.

## Problem + example

Disconnect drops QoS0; QoS1 survives with latency cost. Courier analogy.

## Baseline

Shvaika et al. 2025 TBMQ DOI 10.1186/s40537-025-01271-x; gap = managed+disconnect+multi-QoS.

## RQ / solution

Lite: QoS0 loss 0.30@15s / 0.68@60–300s; QoS1 loss 0.00.

## Dataset

Synthetic; device ID log; lite ≈6k msgs / 16 cells; destroyed.

## AWS / tech

- IoT Core, Rules, Lambda, DynamoDB, Terraform, Python simulator

## Speaking script

Synthetic telemetry; device log matched via IoT→Lambda→DynamoDB; Shvaika gap.

## STATUS + Q&A

- Lite INITIAL_EVAL_PASS; formal beyond floor.
- Same as Shvaika? No.
- Real devices? No.
- Lite=formal? No.
- QoS1 loss 0.00 in lite.
- Proxy? No.
