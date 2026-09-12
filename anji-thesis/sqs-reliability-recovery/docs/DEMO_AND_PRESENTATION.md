# Demo and Presentation Outline

**Name:** Anjaneya Reddy Gurram
**Student ID:** 24288853
**Module:** Research Project

## Part 1: Presentation Outline (10 min)

1. **Problem Statement & Motivation (1.5 min):** 
   - Introduce modern asynchronous, event-driven architectures utilizing SQS to decouple workloads.
   - Highlight the gap: While steady-state configurations are thoroughly researched (Kyrychenko et al., 2025), failure state recoveries and reliability tuning are often unverified in practice.
2. **Gap / Contribution vs Kyrychenko Baseline (2 min):**
   - Summarize the Kyrychenko baseline which optimizes purely for throughput with healthy endpoints.
   - Note that my contribution tests these "optimal" throughput configurations dynamically when injected with consumer/datastore failures.
3. **Methodology & Experimental Design (2 min):**
   - Explain the controlled two-arm experiment comparing standard execution to controlled failure injection.
   - Outline the primary IVs: Visibility Timeout and `maxReceiveCount` (redrive).
   - Outline DVs measured: duplicate rates, message loss, DLQ capture, recovery time.
4. **Key Results (3 min):**
   - **Figure 1:** Duplicate Rate vs Visibility Timeout over a failure window.
   - **Figure 2:** Recovery Time vs `maxReceiveCount` (trade-off diagram).
   - **Figure 3:** Dynamic visibility optimization introducing the **DIVE (Dynamic Intelligent Visibility Extender) algorithm**, showcasing how adaptive extensions alleviate static tuning constraints under failure conditions and heavily limit duplicate pollution over time.
5. **Implications for Practitioners (1 min):**
   - Advice on how engineering teams should adjust static timeouts and when they should utilize the upcoming DIVE mechanism.
   - Reassess "ideal" throughput config when factoring in resilience guarantees.
6. **Limitations & Q&A Tease (0.5 min):**
   - Cloud provider drifts.
   - Scape limitation restricted to Standard queues rather than FIFO.
   - Call to action for Q&A.

---

## Part 2: Demo Script Outline (5-10 min)

1. **Show Architecture Diagram (1 min):**
   - Display the flow: Producer → API Gateway/SQS → AWS Lambda (Consumer) → DynamoDB.
   - Contrast the Synced Arm vs the Queue-Decoupled Arm + DLQ.
2. **Deployed Resources in Console (1 min):**
   - Open up the AWS Console or recorded screenshot showing the active SAM deployment (SQS, DLQ, Lambda, DynamoDB table).
3. **Produce 100 Orders & Happy Path (1.5 min):**
   - Issue command to produce 100 synthetic orders.
   - Open DynamoDB, demonstrating successful idempotent writes.
4. **Enable `FAULT_MODE=unhandled_error` (2 min):**
   - Trigger the fault injection parameters in the CLI runner.
   - Observe the Lambda CloudWatch logs displaying exceptions and watch SQS push affected messages back onto the queue for retry.
   - Demonstrate DLQ capture via the AWS SQS console displaying items shifting from primary to DLQ.
5. **Varying Configuration (`maxReceiveCount`) (1.5 min):**
   - Change `maxReceiveCount` parameter from 5 to 1.
   - Rerun experiment and plot the immediate contrast in how fast the DLQ absorbs failing tasks.
6. **Show Recovery Plot and DIVE Reference (1 min):**
   - Output the visual Python plotting from the most recent campaign.
   - Briefly overview how the **DIVE (Dynamic Intelligent Visibility Extender) algorithm** dynamically updates the timeout in response to backpressure on these same graphs, demonstrating lowered duplicate profiles against standard static rules.
7. **Traceability and Reproducibility (1 min):**
   - Point out the `results/manifests/` storing exact configurations and git hashes.
   - Mention the Configuration Manual detailing all deployment logic.

Anjaneya Reddy Gurram
