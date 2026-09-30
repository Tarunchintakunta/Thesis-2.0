# Lightweight Fault Detection and Localisation in AWS Serverless Microservices

**Student:** Yashaswini Penumarthi  
**Student ID:** 24262404  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Baseline:** Xing et al. (2025) Sensors — DOI 10.3390/s25113396  
**Format:** Short explanation guide (5–6 pages) — matches `Yashaswini_Explanation_Guide.pdf`

---
## 1. What is the project?
This project builds a small serverless online-shop backend on Amazon Web Services and studies how well simple CloudWatch rules plus X-Ray ranking can detect and localise faults — compared with heavy deep-learning detectors that need lots of labelled training data.

The artefact is a four-function order path: orders-api, inventory, payments, and notify. Traffic enters through API Gateway. State lives in DynamoDB. An SSM Parameter Store switch injects faults on purpose. A lightweight detector watches CloudWatch metrics and X-Ray traces.

Three research legs: (1) Xing et al. as published accuracy ceiling (not same-rig); (2) rules versus RCAEval baselines on the same ninety public RE2-OB cases; (3) live AWS lite tracing overhead — full versus policy versus off. The live stack was destroyed after the round.

**Pitch:** “I study how well simple CloudWatch rules plus X-Ray ranking can find faults in a serverless shop, compared with heavy deep models, and what continuous tracing costs.”

## 2. Problem statement + real-life example
When a serverless checkout slows down, the customer only sees the front door fail. The root cause may be an inventory timeout, a payment throttle, or a slow notify path. Deep detectors need large labelled telemetry corpora that a newly deployed, cost-constrained service does not have.

Practical question: how good is a no-training method that only uses CloudWatch alarms and X-Ray traces — and what does continuous monitoring cost in volume, latency, and money when accuracy and overhead are measured together?

**Real-life example — pizza shop.** Orders-api is the counter; inventory is the kitchen; payments is the card terminal; notify is the SMS. If the kitchen freezes, customers still complain at the counter. A fancy AI doctor needs thousands of past failures; a new small clinic cannot afford that. This project is the nurse with a checklist (CloudWatch rules) and a corridor map (X-Ray ranking).

## 3. Baseline paper
Xing, Wang and Liu (2025), Sensors 25(11):3396 (DOI 10.3390/s25113396). Dual-channel deep model (TCN + VAE with contrastive learning and causal inference). Verified claims: detection F1 ≈ 0.938, accuracy ≈ 0.954, fault-component localisation precision ≈ 0.876 under ideal labelled-data conditions.

**Gap:** needs training data and compute; does not jointly report continuous monitoring overhead on AWS serverless. We use Xing as a published accuracy ceiling — not a same-rig re-run. Like-for-like work uses RCAEval (Pham et al., 2025).

## 4. How we solve it / research question
**RQ:** What accuracy–overhead position does rule-based fault detection and localisation occupy relative to learned deep baselines in AWS serverless microservices?

**Solution:** freeze CloudWatch rules + X-Ray dependency ranker (no training); compare on RCAEval RE2-OB; measure live tracing overhead (full / policy / off). Competitive only if F1 within 10 pp of strongest baseline AND telemetry volume cut by ≥50%.

**Honest STATUS:** rule F1 = 0.469; AC@3 = 0.611; policy vs full volume reduction ≈ 0.803. CausalRCA n=4 quarantined.

**Do not claim:** beating Xing same-rig; CausalRCA as strongest peer; lite Leg 3 as full 30-min confirmatory; stack still running.

## 5. Dataset / data
Two sources — synthetic or public. No real customer PII. Own AWS account; destroy-after.

- **RCAEval RE2-OB (Leg 2):** public microservice fault cases (Pham et al., 2025). Ninety cases for rules, BARO, CIRCA, TraceRCA, hybrid.
- **Live AWS lite (Leg 3):** synthetic HTTP at 1 rps × 5 min × 3 tracing conditions (≈300 req/condition) on faultlab, eu-west-1.
- **Faults:** SSM switches (timeout, error, throttle, latency). Ground truth = injection schedule.

## 6. Implementation + technologies / AWS services
- AWS Lambda — four functions (orders, inventory, payments, notify)
- API Gateway — REST entry
- DynamoDB — order / inventory state
- CloudWatch — metrics + alarms for rule detector
- AWS X-Ray — traces; sampling full / policy / off
- SSM Parameter Store — fault switches
- SAM + Terraform — deploy/destroy faultlab
- Python 3 + pytest/moto — 76 unit tests; RCAEval scripts

## 7. End-to-end flow
1. Deploy faultlab (API + 4 Lambdas + DynamoDB + X-Ray + SSM)
2. Warm shop; start synthetic load
3. Flip SSM fault switches; log ground-truth windows
4. CloudWatch rules fire → detection
5. X-Ray ranker → localisation
6. Offline: rules + RCAEval on 90 RE2-OB cases → AC@k / F1
7. Live lite: full vs policy vs off → overhead.json
8. Destroy stack; keep results only

## 8. Exact speaking script
“My dataset has two parts. First, the public RCAEval RE2-OB fault cases — ninety labelled microservice failures I use offline so my rule detector and published baselines see the same data. Second, synthetic live traffic on my own AWS account: about one request per second for five minutes under three tracing settings. I never use real customer data. I implemented a four-function serverless shop with Lambda, API Gateway, DynamoDB, CloudWatch, X-Ray, and an SSM fault switch. Infrastructure is SAM and Terraform. The detector is frozen CloudWatch rules plus an X-Ray ranker — no model training. After the lite overhead round I destroyed the stack. Technologies are Python, AWS managed services, and the RCAEval benchmark tooling.”

## 9. Five likely Q&A
- **Q:** Real customer traffic? **A:** No — RCAEval + synthetic on my account.
- **Q:** Beat Xing F1 0.938? **A:** No. Rule F1=0.469; Xing is published ceiling.
- **Q:** AWS services? **A:** Lambda, API Gateway, DynamoDB, CloudWatch, X-Ray, SSM; SAM/Terraform.
- **Q:** Stack still running? **A:** No — lite Leg 3 destroyed.
- **Q:** Localisation vs detection? **A:** Detection = something wrong; localisation = which service.
