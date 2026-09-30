# An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB

**Student:** Vikas Reddy Amanagantti  
**Student ID:** X25178849  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Baseline:** Qi et al. Halfmoon (2025) ACM TOCS — DOI 10.1145/3725985  
**Format:** Short explanation guide (5–6 pages) — matches `Vikas_Explanation_Guide.pdf`

---
## 1. What is the project?
When Lambda is retried, does DynamoDB write twice? Compares P1 plain Put, P2 conditional Put, P3 idempotency-key on stock Lambda+DynamoDB. P4 TransactWrite quarantined. Live: N=1000×3×3 = 24000 deliveries; E1–E3 supported; stack destroyed.

## 2. Problem statement + real-life example
After-commit timeout → platform retry → plain Put duplicates side effects. **Bank transfer double-click:** P1 posts every click; P2 only if slip new; P3 stamps request ID first. Halfmoon rebuilds the ledger machine; I change how the teller writes.

## 3. Baseline paper
Qi et al. (2025) Halfmoon / asymmetric logging on custom runtime (DOI 10.1145/3725985). **Gap:** not installable on managed Lambda. We share correctness criterion only.

## 4. How we solve it / research question
**RQ:** How much do P2/P3 cut duplicate mutations vs P1 under injected retries, and at what latency/capacity cost? Live: P1 dup=1.0 at mult 2/5; P2/P3=0.0; P3 = P2 + 2 WCU/request. p3_between crash window remains.

## 5. Dataset / data
Synthetic injected (request_id, delivery_count). Seed 25178849. Streams GT 21387 records. Moto = plumbing only.

## 6. Implementation + technologies / AWS services
Lambda (P1|P2|P3), DynamoDB + Streams, Terraform, Python driver, CloudWatch, pytest/moto, Holm-corrected stats.

## 7. End-to-end flow
Apply → pick path/mult → write + after-commit timeout → redeliver → Streams metrics → factorial N=1000 → destroy.

## 8. Exact speaking script
“My dataset is synthetic Lambda requests with known injected retry counts. One Lambda writes three ways: plain put, conditional put, idempotency-key. Streams give ground truth. Live campaign: one thousand requests per path and multiplicity in eu-west-1, then destroy. I did not install Halfmoon.”

## 9. Five likely Q&A
- **Q:** Run Halfmoon? **A:** No — idea only on stock AWS.
- **Q:** P4? **A:** TransactWrite quarantined.
- **Q:** Cite moto as AWS? **A:** No.
- **Q:** Guarded paths stop dups? **A:** Yes — P2/P3=0.0; P1=1.0 at mult 2/5.
- **Q:** P3 still fail? **A:** Crash between write and COMPLETED (p3_between).
