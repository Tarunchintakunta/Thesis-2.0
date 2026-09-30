# Explanation Guide — for viva / weekly explanation

**Student:** Anjaneya Reddy Gurram (Anji)  
**Student ID:** 24288853  
**Programme:** MSc Cloud Computing, National College of Ireland  
**Title:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Artefact:** `sqs-reliability-recovery/`  
**Baseline:** Kyrychenko et al. (2025) Optimization of SQS Configurations… DOI 10.37394/23202.2025.24.4  
**STATUS lock:** 2026-09-21 — CA2 floor COMPLETE; INITIAL_EVAL_PASS=yes; Final-3 done (artefact STATUS); live confirmatory n>1 not run  

**How to use this pack:** Read aloud in simple English. Every number comes from STATUS.md / results files. If a number is not there, say “planned” or “measured in STATUS as …”. Do not invent live AWS metrics. Do **not** claim DIVE/adaptive_vt results — that path was disabled in committed runs.

---

# 1. Project in one page (what it is / what it does)

This project studies Amazon SQS — a cloud queue that holds messages between a producer and a consumer. Think of a ticket dispenser at a busy shop. Tickets wait in line; workers take tickets one by one.

Prior work (Kyrychenko et al., 2025) tunes SQS settings for **speed** when everything is healthy. My project asks a different question: when the worker crashes or the database refuses writes, do those “fast” settings still keep messages safe? Do we lose messages? Do we process the same order twice? Do broken messages land in a dead-letter queue? How long until the line clears again?

I built a small order pipeline with two arms: a synchronous HTTP API (control) and an SQS → Lambda consumer (treatment). I inject faults on purpose. I measure loss, duplicates, DLQ capture, recovery time, throughput, and latency. Most confirmatory statistics come from a **local simulator** (350 packaging-deduplicated design cells). Live AWS was run as **lite smoke** (n=1 key cells), then destroyed.

## One-sentence pitch

> “I test how Amazon SQS settings like visibility timeout and retry limits affect message safety and recovery when consumers or databases fail — not only when the system is healthy.”

## What success means here

- Replicate steady-state thinking from Kyrychenko (throughput/latency language).
- Extend into failure regimes with controlled injection.
- Report honest stats (Holm–Bonferroni on localsim H1–H3).
- Show lite live AWS evidence without over-claiming n=1 smoke as confirmatory.

---

# 2. Problem statement (simple + real-life example)

## The simple problem

Queues decouple producers and consumers. Amazon SQS Standard promises **at-least-once** delivery: a message might be delivered more than once, but should not vanish silently if the system is correct. Settings such as **visibility timeout** (how long a message stays invisible after a worker picks it), **maxReceiveCount** (how many tries before the dead-letter queue), and **batch size** change behaviour a lot when workers fail.

Papers that only optimise healthy throughput can recommend long visibility timeouts or large batches that look great on a good day and behave badly on a bad day.

## Real-life analogy: a café pager system

Customers get a pager. Staff take the next ticket from a wall spike (the queue).

- **Visibility timeout** = how long a ticket stays “taken” before it returns to the spike if the waiter disappears.
- **maxReceiveCount / DLQ** = after N failed tries, put the ticket in a “manager’s problem drawer” instead of looping forever.
- **Batch size** = grabbing five tickets at once — if the waiter drops the tray, five customers suffer.

Kyrychenko’s work is like timing how fast waiters serve when nobody drops trays. My work is: what if waiters faint, or the till rejects cards?

## Another analogy: airport baggage belt

Bags (messages) ride a belt (SQS). Handlers (Lambda) pull bags. If a handler collapses mid-scan, the bag must reappear after a delay (visibility timeout). After too many failures, send the bag to the oversized / problem room (DLQ). Counting “bags per hour” on a calm morning does not tell you what happens during a handler strike.

## Spoken problem paragraph

> “SQS configuration guides often optimise throughput when consumers are healthy. I study loss, duplicates, dead-letter capture, and recovery time when I deliberately kill consumers or break the datastore — because reliability under failure is not implied by healthy throughput.”

---

# 3. Why this matters in industry

Almost every event-driven AWS design uses SQS somewhere: order intake, image pipelines, notifications, payment events. Mis-tuned visibility timeout causes either:

- **Duplicate storms** (timeout too short → message reappears while still processing), or
- **Long recovery** (timeout too long → failed messages sit invisible forever from the ops view).

Mis-tuned retry/DLQ settings either poison the main queue forever or drop work into a DLQ nobody watches.

## Who cares

- Backend engineers building SQS → Lambda pipelines
- SREs measuring recovery time after incidents
- FinOps watching Lambda retries burn money
- Architects tempted to copy “batch size 50, VT 600” from a throughput paper into a failure-prone path

## Industry story

> “If a blog says visibility timeout six hundred seconds is optimal for throughput, I still need to know whether that setting makes my queue take ten minutes to recover after a consumer crash. Throughput is not reliability.”

## What this project does NOT claim

- DIVE / adaptive visibility was **not evaluated** (`adaptive_vt: false`).
- Live n=1 cells are **smoke**, not confirmatory Holm tests.
- Localsim is not a perfect twin of AWS (no cold starts, no network jitter, etc.).
- Results do not automatically transfer to Kafka or RabbitMQ parameter-for-parameter.

---

# 4. Baseline paper (problem / solution / gap / metrics)

## Citation

Kyrychenko, O.O., Ostapov, S.E. and Kyrychenko, O.L. (2025). Optimization of SQS configurations for efficient batch data processing. *WSEAS Transactions on Systems*, 24, pp. 36–43. DOI: https://doi.org/10.37394/23202.2025.24.4

PDF: `anji-thesis/baseline_papers/Kyrychenko_et_al_2025_SQS_baseline.pdf`

## Problem they solve

SQS configuration choices (batch size, visibility timeout, delivery delay) affect batch throughput, latency, queue length, and utilisation in a serverless batch pipeline.

## Solution they propose

Empirically optimise those knobs under **healthy** consumers, supported by classical M/M/1 and M/M/k thinking. Verified scale note from master prompt: experimental validation processing **500,000** records; varied batch size 10–100, visibility timeout 10–900 s, delivery delay 0–900 s; reported optimum around **batch size ~50**, **visibility timeout ~600 s**, **delivery delay ~300 s**.

## Gap they leave

Steady-state optima; limited measurement of **fault / recovery** behaviour (loss, duplicates, DLQ, recovery time). Reliability is often asserted via service guarantees rather than measured under injected failure.

## Gap → this thesis problem

**Their gap is my problem.** I keep SQS knobs as independent variables, but I inject consumer and downstream failures and measure reliability/recovery DVs while still reporting throughput/latency for comparability.

## Metrics map

| Field | Baseline | This thesis |
|---|---|---|
| Problem | Config → throughput/latency | Same knobs under fault |
| Solution | Empiric optima when healthy | Controlled fault campaigns |
| Gap | Little failure/recovery behaviour | Measure loss, dup, DLQ, recovery |
| Metrics | Throughput, response time, queue length | Keep those + reliability DVs |
| Alignment | — | ~88% baseline→CA2 fit (BASELINE_PAPER.md) |

---

# 5. Research question and how we solve it

## Research question

> “How does Amazon SQS configuration affect message reliability and recovery under injected consumer and downstream failures?”

## Objectives

1. Quantify how visibility timeout, maxReceiveCount / DLQ redrive, and batch size affect loss and duplicates under injected failure.
2. Measure recovery time to steady state as those parameters change.
3. Test whether steady-state-optimal guidance still looks favourable under fault (H3).
4. Characterise trade-offs with latency / cost proxies (monetary cost was not the main experimental DV in the locked write-up).

## Hypotheses (non-directional; Holm–Bonferroni)

- **H1:** VT affects loss under consumer failure (localsim: fail to reject — loss stayed 0).
- **H2:** maxReceiveCount affects recovery time (localsim: fail to reject).
- **H3:** throughput-optimal config differs in loss/recovery under fault (loss not estimable; recovery fail to reject after Holm).

## How we solve it

1. Build SAM app: sync arm + SQS/DLQ arm sharing the same processing code.
2. Inject faults via SSM window: consumer_kill, unhandled_error, datastore_reject, datastore_timeout.
3. Run randomised config matrix on **localsim** for confirmatory stats (350 design runs after packaging-dedup).
4. Run **lite live** AWS key cells (n=1) for cloud evidence; destroy after.
5. Analyse with pre-registered tests; disclose limitations.

## Speakable method sentence

> “I hold the async architecture constant, vary SQS settings under injected faults, and measure message-level reliability — instead of only timing a healthy queue.”

---
