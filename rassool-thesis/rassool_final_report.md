# Final Research Report (side document — quarantine notice)

**Student:** Rasool Basha Durbesula  
**Student ID:** 24205478  
**Programme:** MSc in Cloud Computing, National College of Ireland  
**Title:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads

---

## QUARANTINE / CLAIM HYGIENE (2026-09-20)

This markdown side document previously asserted **K4 Adaptive Tiered Sharding “dominance”** (throttle avoidance, ~90% RCU cuts, burst weathering) as if measured. Those claims are **unsupported**:

- CA2 factorial is **K1 / K2 / K3** only (`config/experiment.yaml`).
- No live DynamoDB campaign CSVs exist (`results/` is schema-only).
- Moto smoke does **not** validate production adaptive capacity, burst, or Cost Explorer bills.
- K4 may exist as **optional code / design-check arithmetic** only — it is **off-CA2** and must not be cited as an empirical win in the LaTeX report or STATUS.

**Authoritative honesty:** `dynamodb-pk-capacity-eval/STATUS.md` and `latex_report/text/evaluation.tex` (moto-only).

---

## 1. Context and Baseline Analysis

The project evaluates the performance-cost trade-offs bounded by Amazon DynamoDB table configurations (Partition-Key design × Capacity mode) when driven by bursty, serverless (Lambda) workloads.

**Baselines Evaluated:**
The foundational framework of this experiment originates from Pantelić et al. (2026)—"Benchmarking SQL and NoSQL persistence in microservices under variable workloads." While their evaluation quantified latency and throughput for conventional SQL/NoSQL architectures on self-hosted instances under variable loads (W1–W4), those configurations completely bypassed cloud-native architectural realities: auto-scaling timeouts, Physical Partition RCU/WCU limits, Pay-Per-Request constraints, and operation-level metering costs. Thus, this project translated these workload distributions into Serverless infrastructure (AWS Lambda and DynamoDB) **as a design and artefact**, pending live measurement.

The CA2 PK (Partition Key) schemas are:
1. **K1 (Simple):** `orderId`
2. **K2 (Composite):** `customerId + orderTs`
3. **K3 (Workload-Aware Sharding):** `orderId#shard` (N=10)

## 2. Identified Gap in the Baseline (design rationale)

K3 mitigates write hotspots but imposes scatter-gather reads (up to 10× RCU) for every item. In Zipfian traffic this may be economically costly on on-demand metering. That gap motivates the CA2 factorial; it does **not** by itself prove any alternative design wins without live data.

## 3. Optional off-factorial code path (K4) — not an empirical result

Repository code may include an exploratory **K4** adaptive/tiered sharding path (hot keys sharded, cold keys single-shard). This is:

- **Not** part of the CA2 3×2 factorial tables provisioned in `iac/main.tf` designs map (K1–K3).
- **Not** evidenced by campaign results.
- **Not** to be described as dominating K1/K2/K3 on latency, throttle, or cost.

Design-check CSVs that mention K4 are arithmetic predictions only.

## 4. What is actually evidenced today

- Terraform + Lambda + Zipfian + analysis pipeline exist and are moto-tested.
- Report evaluation tables remain simulation placeholders.
- Cost model uses `config/prices.yaml` list prices — **no** Cost Explorer pilot artefact.
- IaC default tags contain **no** student name/ID.

## 5. Next step for CA2 completion

Run the live K1–K3 × capacity × workload campaign under the alignment-first gate, fill `results/`, replace `[MOTO SIM]` cells, and keep K4 (if studied later) clearly labelled as optional/extra-factorial.
