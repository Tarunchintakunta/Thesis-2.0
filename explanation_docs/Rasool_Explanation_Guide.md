# Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads

**Student:** Rasool Basha Durbesula  
**Student ID:** 24205478  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Baseline:** Pantelić et al. (2026) Future Internet — DOI 10.3390/fi18010053  
**Format:** Short explanation guide (5–6 pages) — matches `Rasool_Explanation_Guide.pdf`

---
## 1. What is the project?
Measures how DynamoDB partition-key design × capacity mode changes latency, throttling, consumed capacity, and list-price cost under serverless Lambda workloads.

K1=orderId; K2=customerId+orderTs; K3=orderId#shard (N=10). On-demand vs provisioned. Live: 12 W3/W4 cells, 100k seed, throttle_rate=0.0; stack destroyed.

## 2. Problem statement + real-life example
Hot partitions throttle; capacity modes price differently. **Warehouse aisles:** K1 unique barcodes; K2 celebrity customer jam; K3 split hot aisle into 10 shards; provisioned = rented forklifts, on-demand = pay per trip.

## 3. Baseline paper + brief SQL vs NoSQL
Pantelić et al. (2026) SQL vs NoSQL on self-hosted single node — latency/throughput ranking. **Gap:** no RCU/WCU, throttle, or per-op price. **SQL vs NoSQL:** SQL=joins/fixed schema; DynamoDB=key design + horizontal partitions. This thesis is DynamoDB-native, not a re-bench.

## 4. How we solve it / research question
**RQ:** How does PK design × capacity mode determine performance–cost under serverless workloads? Live floor = 12/12 W3/W4 cells. Soft: W1/W2, confirmatory ANOVA. K4 off factorial.

## 5. Dataset / data
Synthetic Zipfian. Design: ~1M orders / 10k customers; sizes 1/8/32 KB. Live seed: 100k. Cost = list-price YAML, not Cost Explorer.

## 6. Implementation + technologies / AWS services
DynamoDB, Lambda generators, Terraform, Python Zipfian + cost model, CloudWatch, moto plumbing only.

## 7. End-to-end flow
Apply → seed 100k → run cell → measure p99/thr/throttle/RCU-WCU → cost → all 12 cells → destroy 32 resources.

## 8. Exact speaking script
“My dataset is synthetic Zipfian orders — design one million orders / ten thousand customers; live seeded one hundred thousand. I implemented K1–K3 × on-demand/provisioned with Lambda generators in Terraform. I meter latency, throttles, capacity, and list-price cost. I did not re-run Pantelić’s SQL/NoSQL container bench. After twelve live cells I destroyed the stack.”

## 9. Five likely Q&A
- **Q:** Re-bench Pantelić SQL/NoSQL? **A:** No — DynamoDB-native meters.
- **Q:** Live 1M rows? **A:** Design 1M; live seed 100k.
- **Q:** K1/K2/K3? **A:** orderId; customerId+ts; sharded orderId.
- **Q:** Throttling? **A:** 0.0 on all 12 cells.
- **Q:** Live ANOVA? **A:** No — n=1 exploratory only.
