#!/usr/bin/env python3
"""Generate Rasool_Explanation_Guide.pdf + .md (~40-45 pages)."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from explanation_pdf_lib import (
    styles, make_doc, P, simple_table, hr, code_block, title_page, toc_page, _footer, add_qa,
)
from reportlab.platypus import PageBreak, Spacer

OUT_DIR = Path("/workspace/explanation_docs")
SECTIONS = [
    "The project in one page",
    "Problem statement and a real-life example",
    "Why it matters",
    "The baseline paper, the gap, and this thesis problem",
    "Research question and solution approach",
    "Core concepts with everyday examples (SQL, NoSQL, DynamoDB, keys, capacity)",
    "Dataset and how the synthetic data is produced",
    "Architecture and end-to-end flow",
    "Implementation modules and short code snippets",
    "AWS services used (what / why / analogy)",
    "Experiment design and metrics",
    "Class speaking scripts",
    "Professor Q&A — exact answers",
    "Honest STATUS and limitations",
    "One-page cheat sheet",
]

def B(story, st, items):
    for t in items:
        story.append(P("• " + t, st["bullet"]))

def build_story(st):
    s = []
    title_page(s, st, {
        "doc_label": "Speakable explanation guide · thesis outsourcing lane",
        "title": "Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads",
        "student": "Rasool Basha Durbesula",
        "student_id": "24205478",
        "artefact": "rassool-thesis/dynamodb-pk-capacity-eval/",
        "baseline": "Pantelić et al. (2026), Future Internet 18(1):53, DOI 10.3390/fi18010053",
    })
    toc_page(s, st, SECTIONS)

    # ---- 1 ----
    s.append(P("1. The project in one page", st["h1"])); s.append(hr())
    s.append(P(
        "If you have two minutes before you walk into a professor’s office, this is the whole project. "
        "Rasool Basha Durbesula (student ID 24205478) is doing an MSc Cloud Computing research project at the "
        "National College of Ireland. The artefact folder is <font face='Courier'>dynamodb-pk-capacity-eval/</font>. "
        "The title names the two knobs he actually turns and the kind of traffic he uses.", st["body"]))
    s.append(P(
        "The two knobs are <b>partition-key design</b> and <b>capacity mode</b>. The traffic is <b>serverless</b>: "
        "AWS Lambda functions send reads and writes at a planned rate into Amazon DynamoDB. He measures how long "
        "requests take (including the slow tail: p95 and p99), how many requests DynamoDB rejects (throttles), how "
        "many read and write capacity units were consumed, and what that would cost at published list prices per "
        "10,000 successful operations.", st["body"]))
    s.append(P(
        "He does <b>not</b> claim to have re-run Pantelić et al. (2026) inside AWS. Pantelić compared SQL and NoSQL "
        "persistence for microservices on a <b>self-hosted single node</b>. That paper is the baseline because it "
        "gives the workload language (read-heavy, write-heavy, mixed, burst) and the classic metrics (latency, "
        "throughput). Rasool’s move is: keep those metrics, then add the meters that only a managed DynamoDB table "
        "has. The professor should hear the contrast in one breath: <i>they ranked engines; he meters a configuration.</i>", st["body"]))
    s.append(P(
        "Three key designs sit in the committed factorial. <b>K1</b> uses a simple partition key "
        "<font face='Courier'>orderId</font> (one million distinct values in the planned dataset). <b>K2</b> uses a "
        "composite key: partition key <font face='Courier'>customerId</font> and sort key "
        "<font face='Courier'>orderTs</font> (ten thousand partition-key values). <b>K3</b> is workload-aware write "
        "sharding: partition key <font face='Courier'>orderId#shard</font> with a fixed N = 10 shards. Writes to a "
        "hot order are spread; a logical read gathers all ten shards and keeps the newest version. A fourth design, "
        "<b>K4</b> adaptive / tiered sharding, exists as optional code. It is <b>off the CA2 factorial</b>. Nobody "
        "should say K4 “won”. The side file <font face='Courier'>rassool_final_report.md</font> previously used that "
        "language; STATUS quarantines it.", st["body"]))
    s.append(P(
        "Capacity mode has two levels. <b>On-demand</b> (PAY_PER_REQUEST) charges for what you consume. "
        "<b>Provisioned</b> reserves read and write units, with auto-scaling bounds written in Terraform. Crossing "
        "three keys and two modes gives six table configurations. Four workload profiles condition every configuration: "
        "W1 read-heavy (~95% GetItem / 5% PutItem) at a sustained 200 operations per second; W2 write-heavy "
        "(~30% Get / 70% Put) at 200 ops/s; W3 mixed 50/50 at 200 ops/s; W4 burst (same mix as W3, 60 seconds at "
        "200 ops/s alternating with 30 seconds at 1,000 ops/s). Batches of 25 items are used where BatchGet / "
        "BatchWrite apply. Access is Zipfian so that roughly 90% of operations hit roughly 10% of keys.", st["body"]))
    s.append(P(
        "<b>What is actually on the table as live evidence (STATUS, 20 September 2026).</b> A key-cell campaign filled "
        "12 of 12 cells: K1–K3 × on-demand/provisioned × W3/W4, n = 1 each, region <font face='Courier'>eu-west-1</font>, "
        "100,000 seed items for that round (not the full 1,000,000). Throttle rate was 0.0 on every measured cell. "
        "Request-path list-price sum was about <b>$0.251</b>. The stack was destroyed afterwards (32 Terraform resources; "
        "no leftover <font face='Courier'>ddbpk*</font> tables or Lambda). W1 and W2 live cells are still placeholders. "
        "Confirmatory ANOVA on live data is not claimed — n = 1 saturates the interaction residual. Exploratory additive "
        "OLS and request-level Kruskal–Wallis exist in a generated JSON; they are not confirmatory.", st["body"]))
    s.append(P(
        "One-sentence version for a nervous student: <i>“I measured six DynamoDB table setups under mixed and burst "
        "Lambda traffic, and I can show latency, throughput, zero throttles on those cells, and a list-price cost, "
        "but I have not yet filled the read-heavy and write-heavy live cells or run a proper repeated ANOVA.”</i>", st["body"]))
    s.append(P(
        "That is the whole project. Everything else in this guide is so a friend can explain the words, the dataset, "
        "the code, the AWS services, the experiment, and the honest limits without inventing a number.", st["body"]))

    # ---- 2 ----
    s.append(PageBreak())
    s.append(P("2. Problem statement and a real-life example", st["h1"])); s.append(hr())
    s.append(P("2.1 The problem in academic English, then in kitchen English", st["h2"]))
    s.append(P(
        "Academic version. Amazon DynamoDB meters every request in read capacity units (RCU) and write capacity units "
        "(WCU). Requests that exceed the units available are rejected rather than queued. Two configuration decisions "
        "taken early — the partition-key schema and the billing mode — jointly determine latency, rejection rate, and "
        "per-operation cost. The persistence-benchmarking literature that supplies Rasool’s workload language establishes "
        "its findings on self-hosted infrastructure, where those meters do not exist. Absolute, configuration-attributed "
        "cost and throttle measurements on the live managed service are therefore missing.", st["body"]))
    s.append(P(
        "Kitchen version. DynamoDB is a restaurant that charges you per plate and will refuse you at the door if the "
        "kitchen is full. How you label the tickets (the key) decides whether one chef gets all the Friday-night tickets. "
        "How you pay (reserved tables versus walk-in) decides whether you overpay on a quiet Tuesday or get turned away "
        "on Saturday. The famous paper Rasool starts from compared two kinds of restaurant kitchen (SQL vs NoSQL) in a "
        "lab kitchen they owned. They can tell you which kitchen was faster. They cannot tell you the cover charge, "
        "because their kitchen does not print a cover charge.", st["body"]))
    s.append(P("2.2 A story you can tell out loud", st["h2"]))
    s.append(P(
        "Picture “CityEats”, a made-up food-delivery firm. They store every order as a small record: a fake order id "
        "like <font face='Courier'>o0000421</font>, a fake customer id like <font face='Courier'>c01307</font>, a timestamp, "
        "a status, and a padding field so the record is 1 KB, 8 KB or 32 KB. None of this is a real person. The generator "
        "prints the ids from a formula. Ten thousand fake customers own one million fake orders in the planned dataset.", st["body"]))
    s.append(P(
        "Traffic is unfair, on purpose. A Zipfian sampler is set so that about ninety percent of the GetItem and PutItem "
        "calls land on about ten percent of the keys. That is how real catalogues behave: a few restaurants, a few SKUs, "
        "a few user ids are celebrities. If CityEats uses K1, each order is its own partition key. Celebrity orders still "
        "exist (the same hot <font face='Courier'>orderId</font> is hit again and again). If they use K2, all of one "
        "customer’s orders sit together under that customer id. A celebrity customer becomes a hot partition. If they "
        "use K3, a hot order’s writes are sprayed across ten shard suffixes. The write heat spreads. The next time "
        "someone asks “what is the latest version of this order?”, the function must ask all ten shards and pick the "
        "newest. That extra read work is the price of spreading the writes. STATUS later shows K3 often paying more "
        "p99 and more list-price cost than K1 or K2 on the mixed workload. That is allowed. The thesis is not a "
        "marketing brochure for sharding.", st["body"]))
    s.append(P(
        "Now add money. On-demand is the walk-in queue: you pay for the plates you actually order, and the kitchen "
        "tries to grow with you. Provisioned is a booking: you reserved a number of plates per second. If Saturday "
        "exceeds the booking, DynamoDB can throttle. Adaptive capacity and burst credits exist in the product, which "
        "is why the design includes a settling interval before measurement, and why moto (the local emulator) is "
        "forbidden as a source of latency or throttle truth.", st["body"]))
    s.append(P(
        "Lambda is the waiter. About 200 operations per second in the sustained profiles. Batches of 25 when batch APIs "
        "are used. A burst profile that jumps to 1,000 ops/s for thirty seconds. The waiter is warmed up so cold-start "
        "delay is not blamed on the table. The waiter does not retry inside the SDK, because a hidden retry would hide "
        "throttles.", st["body"]))
    s.append(P(
        "The problem, restated as a practitioner question: <i>If I am about to create a DynamoDB table for this kind of "
        "order traffic, which key do I pick, which billing mode do I pick, and do those two choices fight each other "
        "when I look at speed, rejections, and money together?</i>", st["body"]))
    s.append(P("2.3 What is <i>not</i> the problem", st["h2"]))
    B(s, st, [
        "Not “is SQL better than NoSQL?” — that is Pantelić’s question on a self-hosted node.",
        "Not “did K4 adaptive sharding dominate?” — K4 is code-only, off factorial, quarantined.",
        "Not “what did Cost Explorer bill?” — cost is a list-price proxy from <font face='Courier'>config/prices.yaml</font>.",
        "Not GCP Spanner versus Azure Cosmos — this artefact is AWS only.",
        "Not a production migration of a real company dataset — data is synthetic, no PII.",
    ])

    # ---- 3 ----
    s.append(PageBreak())
    s.append(P("3. Why it matters", st["h1"])); s.append(hr())
    s.append(P(
        "It matters first to the person who will click “Create table” and then live with the bill. Partition keys and "
        "capacity modes are cheap to type and expensive to undo. A wrong key on a Zipfian catalogue concentrates heat. "
        "A wrong mode either wastes reserved units or surprises the team with on-demand prices, or throttles during a sale. "
        "Vendor pages describe the mechanisms (Elhemali et al. 2022 on DynamoDB’s design; AWS developer-guide pages on "
        "capacity mode, adaptive capacity, and write sharding). They do not hand you a six-cell trade-off surface under "
        "Lambda-driven, Zipfian, 200 ops/s traffic with published prices applied to consumed units.", st["body"]))
    s.append(P(
        "It matters second to the research conversation. Persistence benchmarks (Pantelić; Ferreira’s cloud-NoSQL consistency "
        "work) compare engines. Skew papers (Kanellis et al. 2025; Li, Wang and Zhang 2023) show that key placement can "
        "swing throughput by large factors, but often on stores that queue rather than reject, and that have no RCU meter. "
        "Cost surveys (Haubenschild and Leis 2025; van Renen and Leis 2023; Bodner et al. 2025; Lei et al. 2024) either "
        "formalise charging or price a service as a unit of selection. van Renen and Leis give a vivid warning that the "
        "latency-optimal choice can be several times more expensive than the cost-optimal choice. Rasool’s third objective "
        "is that same tension, inside one service, with tenant-owned knobs.", st["body"]))
    s.append(P(
        "It matters third in the classroom. A professor who hears “SQL versus NoSQL” will think engine bake-off. A student "
        "who answers with RCU, WCU, throttle_rate, and cost_per_10k is showing they understood the <b>move</b> from the "
        "baseline. That is the pedagogical point of this PDF. If the friend explaining the work cannot say that sentence, "
        "the viva will slide back into “we compared Mongo and Postgres”.", st["body"]))
    s.append(P(
        "It matters fourth for honesty. Live evidence is a 12-cell, n=1, W3/W4 round with 100k seed. The planned 1,000,000 "
        "item / 10,000 customer dataset and the W1/W2 cells and the n=30 ANOVA are the <b>design</b>. Overclaiming would "
        "matter more than any missing cell, because the module marks evaluation honesty. STATUS already writes the residual "
        "in public: alignment after the live fold is about 94%, not 100%; CA2 floor for the initial-eval gate was met; "
        "soft residual remains.", st["body"]))
    s.append(P(
        "A last, human reason. Serverless teams often treat DynamoDB as “just a JSON bucket that scales”. The thesis treats "
        "it as a <b>metered admission-control system</b>. Once you see it that way, key design stops being a naming "
        "preference and becomes a load-placement decision, and capacity mode stops being a billing checkbox and becomes "
        "a rejection policy. That shift is the intellectual contribution even before any cell is filled.", st["body"]))

    # ---- 4 ----
    s.append(PageBreak())
    s.append(P("4. The baseline paper, the gap, and this thesis problem", st["h1"])); s.append(hr())
    s.append(P("4.1 Bibliographic facts (say them cleanly)", st["h2"]))
    s.append(P(
        "Pantelić, N., Matić, L., Jakovljević, L., Erić, S., Erić, M., Stefanović, M. and Djordjević, A. (2026) "
        "‘Benchmarking SQL and NoSQL persistence in microservices under variable workloads’, <i>Future Internet</i>, "
        "18(1), 53. doi: <b>10.3390/fi18010053</b>. Open at https://www.mdpi.com/1999-5903/18/1/53. "
        "The master prompt records it as a real MDPI article (published 15 January 2026). Replacements: none. "
        "The PDF lives in <font face='Courier'>rassool-thesis/baseline_papers/</font>.", st["body"]))
    s.append(P("4.2 Problem they attacked", st["h2"]))
    s.append(P(
        "Microservices persist state. Teams argue about SQL versus NoSQL as if the brand of database were the whole "
        "story. Pantelić et al. put that argument under a controlled workload: read-heavy, write-heavy and mixed "
        "microservice traffic, concurrency rising, engines compared on a machine the experimenters operate. The "
        "question is about <b>persistence model</b> and <b>workload composition</b>, not about a cloud bill.", st["body"]))
    s.append(P("4.3 What they built and what they measured", st["h2"]))
    s.append(P(
        "They built a benchmarking setup for SQL and NoSQL persistence in a microservice setting. The metrics that "
        "Rasool is required to <b>retain for comparability</b> are latency (including percentile language; they use "
        "p95) and throughput (completed work per unit time). Their findings, as used in the proposal extract, are "
        "that the persistence model and the mix — not the hardware — drive the observed performance, and that results "
        "are reported as <b>relative ordering</b> rather than as a cloud invoice.", st["body"]))
    s.append(P(
        "Do not invent extra Pantelić numbers. If a professor asks “what was their exact millisecond?”, the honest "
        "answer is: quote only what you have in the PDF in front of you; this explanation guide does not copy their "
        "tables. The baseline is used for <b>problem, method shape, and metric names</b>, not as a number to beat.", st["body"]))
    s.append(P("4.4 Gap — the sentence you must not soften", st["h2"]))
    s.append(P(
        "A self-hosted single node has no RCU, no WCU, no <font face='Courier'>ProvisionedThroughputExceeded</font>, "
        "no PAY_PER_REQUEST versus PROVISIONED, and no per-operation price. The dependent variables this project needs "
        "<b>do not exist</b> in that design. That is not a polite “they didn’t have time”. It is a property of the "
        "setting. Retain their latency and throughput measures. Add consumed capacity, throttles, and cost per 10k.", st["body"]))
    s.append(P("4.5 How Pantelić frames SQL / NoSQL versus how this thesis moves", st["h2"]))
    s.append(P(
        "Pantelić’s axis is <b>engine family</b>: relational tables with SQL, versus non-relational stores. The unit "
        "of comparison is “which persistence style is faster / more throughput-y under this mix, on our node”. "
        "Rasool’s axis is <b>configuration of one managed NoSQL service</b>: how you key the table, and how you buy "
        "capacity. The unit of comparison is a cell on a 3 × 2 surface, conditioned by workload, reported in ms, "
        "ops/s, throttle_rate, and USD/10k at list prices. Same family of mixes (read-heavy, write-heavy, mixed, plus "
        "an explicit burst). Different object of study. Different meters.", st["body"]))
    s.append(P(
        "If a professor says “so you compared Postgres and DynamoDB”, the correction is immediate: <i>No. The baseline "
        "compared SQL and NoSQL on a node they hosted. I hosted nothing. I varied key and capacity on DynamoDB and "
        "read the meters they could not have.</i>", st["body"]))
    s.append(P("4.6 Thesis problem taken from that gap", st["h2"]))
    s.append(P(
        "The proposal extract states it without ornament: how does Amazon DynamoDB table configuration determine the "
        "performance–cost trade-off under serverless workloads? Four objectives follow (key → latency/throttle; mode → "
        "throttle/cost; joint latency-versus-cost; trade-off surface). Hypotheses are two-sided. Nothing in the reviewed "
        "measurements justifies naming a winner before the data. STATUS then records what the first live key-cell "
        "round actually showed, including the uncomfortable cell: K3 is not free.", st["body"]))

    # ---- 5 ----
    s.append(PageBreak())
    s.append(P("5. Research question and solution approach", st["h1"])); s.append(hr())
    s.append(P(
        "<b>Research question (committed).</b> How does Amazon DynamoDB table configuration (partition-key design × "
        "capacity mode) determine the performance–cost trade-off under serverless workloads?", st["body"]))
    s.append(P("Objectives, in the order a friend should recite them:", st["body"]))
    B(s, st, [
        "Quantify how partition-key design affects latency and throttling under each workload profile.",
        "Quantify how capacity mode affects throttling and cost at equivalent load.",
        "Determine whether the latency-minimising configuration also minimises cost.",
        "Express each configuration as a position on the surface spanned by latency, rejected-request rate, and cost per 10,000 operations.",
    ])
    s.append(P("5.1 Solution approach — the artefact, not a slogan", st["h2"]))
    s.append(P(
        "The solution is a reproducible ICT artefact, not a new database engine. Terraform under <font face='Courier'>iac/</font> "
        "parameterises key schema and billing mode so the six configurations rebuild identically. Tags on the live "
        "stack were <font face='Courier'>project=dynamodb-pk-capacity</font>, <font face='Courier'>managed_by=terraform</font>, "
        "<font face='Courier'>purpose=research-eval</font>, <font face='Courier'>data=synthetic</font> — no student name "
        "or student ID on resources (STATUS verified this).", st["body"]))
    s.append(P(
        "Workload code under <font face='Courier'>workloads/</font> has a Zipfian sampler, key helpers for K1–K3 "
        "(and optional K4), profiles W1–W4, a 1M-item seeder that uses BatchWriteItem of 25, and a Lambda handler "
        "that is an open-loop load generator with no SDK retries and a raw CSV per batch. "
        "<font face='Courier'>scripts/run_matrix.py</font> walks the factorial. Analysis scripts apply the list-price "
        "cost model and, when asked, the ANOVA / ART / Tukey / Holm pipeline. Unit tests run against <b>moto</b>. "
        "Moto is plumbing. Moto is not DynamoDB.", st["body"]))
    s.append(P(
        "The live command that filled the key-cells (STATUS) was: "
        "<font face='Courier'>scripts/run_matrix.py --blocks 1 --workloads W3,W4 --key-designs K1,K2,K3 --orders 100000</font>. "
        "Then collect, analyse, destroy. Evidence retained: "
        "<font face='Courier'>results/batches.csv</font>, twelve raw <font face='Courier'>*.csv.gz</font> files, "
        "<font face='Courier'>keycell_summary.csv</font>, the run log. Wall window recorded as "
        "2026-09-20T11:55:38Z to 12:47:42Z (that is 5:25 pm to 6:17 pm IST on 20 September 2026).", st["body"]))
    s.append(P("5.2 What “success” looks like without lying", st["h2"]))
    s.append(P(
        "The master prompt’s falsifiable success condition is: a third party can rebuild the six tables from IaC, "
        "re-run the four profiles from Lambda, recompute cost-per-10k from published prices × consumed units, and "
        "map every citation to the verified corpus. STATUS says the 12 key-cells were measured and destroyed; W1/W2 "
        "and confirmatory n&gt;1 ANOVA remain soft residuals. Speak that way. Do not upgrade 12 cells of n=1 into "
        "“the full factorial is done”.", st["body"]))

    # --- sections 6+ continue below ---

    # ---- 6 Core concepts ----
    s.append(PageBreak())
    s.append(P("6. Core concepts with everyday examples", st["h1"])); s.append(hr())
    s.append(P(
        "This section is the longest on purpose. A friend who can explain these words can survive any professor "
        "interruption. Every analogy is a teaching aid, not a measurement.", st["body"]))

    s.append(P("6.1 What is SQL? (the baseline’s first family)", st["h2"]))
    s.append(P(
        "SQL means Structured Query Language. People also say “a SQL database” to mean a <b>relational</b> database: "
        "data in tables with named columns, rows that must fit the schema, and relations expressed with keys. You ask "
        "questions in sentences like “give me every order for customer 1307 placed last Tuesday, joined to the payment "
        "table, grouped by restaurant”. The engine plans that question — indexes, joins, locks — and returns a precise set.", st["body"]))
    s.append(P(
        "Everyday example. A paper ledger in a shop: one book of customers, one book of invoices, one book of payments. "
        "The invoice book does not repeat the customer’s address; it stores a customer number and you look across. That "
        "look-across is a join. If two clerks write the same invoice number, the ledger’s rules (constraints) should "
        "refuse the second. Banks, airlines, payroll, university registry, hospital billing — organisations that live on "
        "multi-table consistency — grew up on this model. Classic products: PostgreSQL, MySQL, Microsoft SQL Server, "
        "Oracle Database. Cloud hosted versions exist (Amazon RDS, Amazon Aurora), but they are still the same idea: "
        "you are buying a <b>relational engine</b>, often with a server you can point at.", st["body"]))
    s.append(P(
        "What SQL is good at, in one breath: ad-hoc questions, joins, transactions across several tables, a schema that "
        "refuses garbage. What it costs you: you must design the schema up front; scaling writes across many machines is "
        "a specialist sport; a self-hosted node (exactly Pantelić’s setting) gives you full control and <b>no cloud "
        "capacity meter</b>.", st["body"]))
    s.append(P(
        "Companies that typically lean SQL. High-street banks and payment processors for the core ledger. Airlines and "
        "rail for bookings that must not double-sell a seat. ERP and HR systems. Governments and universities for "
        "structured records. Any team whose first question is “can I join these five tables and trust the answer”. "
        "Start-ups use PostgreSQL for the same reason: it is honest, well understood, and cheap to reason about while "
        "the data still fits on one primary.", st["body"]))

    s.append(P("6.2 What is NoSQL? (the baseline’s second family)", st["h2"]))
    s.append(P(
        "NoSQL is a family name, not one product. It usually means “not only SQL”: stores that relax the rigid relational "
        "schema, often scale by <b>partitioning</b> (sharding) keys across machines, and offer APIs that look like “get "
        "this item”, “put this item”, “query this partition”, rather than a join-heavy SQL string. Flavours include "
        "document stores (MongoDB, Amazon DocumentDB), key-value stores (Redis, DynamoDB in its simplest use), "
        "wide-column stores (Apache Cassandra, Amazon Keyspaces), and others. They are not all the same. Saying “we used "
        "NoSQL” in a viva without naming the product is like saying “we used a vehicle”.", st["body"]))
    s.append(P(
        "Everyday example. A wall of lockers in a station. Each locker has a number (the key). You open one locker, you "
        "put a bag in, you close it. You do not ask the locker wall to “join locker 17 to locker 845 and sum the weights”. "
        "If locker 17 is popular, that door gets all the traffic. The wall can add more lockers (more partitions) but it "
        "cannot magically make one celebrity locker less busy unless you change how you number the bags.", st["body"]))
    s.append(P(
        "What NoSQL is good at, in one breath: large, simple access patterns you knew in advance; horizontal scale; "
        "flexible item shapes; low operational romance if the service is managed. What it costs you: you must design the "
        "access path into the key; ad-hoc joins become your problem; some products are eventually consistent unless you "
        "pay extra; and on DynamoDB specifically, the meter and the throttle are part of the contract.", st["body"]))
    s.append(P(
        "Companies that typically lean NoSQL. Consumer internet firms with huge, simple “fetch this profile / this shopping "
        "cart / this session” paths (the original Amazon.com retail story is the folklore behind Dynamo / DynamoDB). "
        "Gaming leaderboards and session stores. IoT fleets writing telemetry. Ad-tech and mobile backends that outgrew a "
        "single Postgres primary. Media catalogues. Teams that already know their queries and would rather buy a managed "
        "partition store than hire a database administrator to shard MySQL at 3 a.m. Many serious companies run <b>both</b>: "
        "SQL for the ledger, DynamoDB or Cassandra for the high-QPS path. That “both” is important. This thesis is not a religion.", st["body"]))

    s.append(P("6.3 SQL versus NoSQL — a speaking table", st["h2"]))
    s.append(simple_table([
        [P("<b>Lens</b>", st["cheat"]), P("<b>SQL / relational</b>", st["cheat"]), P("<b>NoSQL / DynamoDB-style</b>", st["cheat"])],
        [P("Shape of data", st["cheat"]), P("Tables, columns, rows, joins", st["cheat"]), P("Items in partitions, key-first access", st["cheat"])],
        [P("Question style", st["cheat"]), P("Ad-hoc SQL, planner decides", st["cheat"]), P("You designed the key for the question", st["cheat"])],
        [P("Scale story", st["cheat"]), P("Vertical, then careful sharding", st["cheat"]), P("Horizontal by partition key", st["cheat"])],
        [P("Typical firms", st["cheat"]), P("Banks, ERP, registries, many SaaS cores", st["cheat"]), P("High-QPS internet, gaming, IoT, retail carts", st["cheat"])],
        [P("Pantelić’s use", st["cheat"]), P("One side of the bake-off, self-hosted", st["cheat"]), P("Other side of the bake-off, self-hosted", st["cheat"])],
        [P("This thesis", st["cheat"]), P("Not re-run", st["cheat"]), P("One managed product; key × capacity metered", st["cheat"])],
        [P("Meters on self-hosted node", st["cheat"]), P("No RCU/WCU/throttle/price", st["cheat"]), P("No RCU/WCU/throttle/price", st["cheat"])],
        [P("Meters on DynamoDB", st["cheat"]), P("Not applicable", st["cheat"]), P("RCU, WCU, throttle, list-price cost", st["cheat"])],
    ], col_widths=[110, 195, 195]))
    s.append(P("Table. How to talk about SQL vs NoSQL without mixing up the baseline and the thesis.", st["caption"]))

    s.append(P("6.4 How Pantelić uses that contrast — and the exact move this thesis makes", st["h2"]))
    s.append(P(
        "Pantelić et al. (2026) treat SQL versus NoSQL as the <b>independent variable that matters</b>. Workload mix and "
        "concurrency are the conditions. Latency and throughput are the scores. The node is theirs, so they can install "
        "both families and be fair. That is a legitimate systems-benchmark question. It is also why their paper is the "
        "right baseline to <b>keep</b>: Rasool needs those mix labels and those score names so a reader can place a "
        "managed-service result next to a self-hosted ordering.", st["body"]))
    s.append(P(
        "The move. Once you stand on DynamoDB, “SQL versus NoSQL” is already decided. You are on a NoSQL service. The live "
        "questions become: which <b>partition key</b>, which <b>capacity mode</b>, what is the <b>consumed</b> RCU/WCU, "
        "did the service <b>throttle</b>, and what is the <b>list-price cost per 10k successful ops</b>. That is PK × "
        "capacity metering. It is not a container rematch of Postgres and Mongo. STATUS says this in the rubric notes: "
        "“this thesis is DynamoDB-native PK+capacity under serverless workloads — not a container SQL/NoSQL re-bench.”", st["body"]))
    s.append(P(
        "A professor who is fond of the baseline may ask “then why cite them?”. Answer: because they fixed the "
        "<b>workload language</b> this study reuses (read-heavy ~95% reads, write-heavy ~70% writes, mixed 50/50, plus "
        "burst), and because their missing meters are the <b>gap statement</b>. You cite a baseline for the problem it "
        "leaves, not only for the numbers it prints.", st["body"]))

    s.append(P("6.5 Amazon DynamoDB, in one picture", st["h2"]))
    s.append(P(
        "DynamoDB is AWS’s fully managed NoSQL database service. You do not patch the OS. You create a table, declare a "
        "partition key (and optionally a sort key), pick on-demand or provisioned, and send PutItem / GetItem / Query / "
        "BatchWrite / BatchGet. Behind the curtain, AWS spreads items across <b>physical partitions</b> using the partition "
        "key. Elhemali et al. (2022) describe the product as aiming for predictable latency with adaptive capacity and "
        "admission control. Admission control is the polite name for “we will say no”.", st["body"]))
    s.append(P(
        "Analogy. A huge automated warehouse. You never meet the forklift drivers. You address every crate by a label you "
        "chose (the key). The warehouse charges you per fetch and per put, in whole units. If one aisle is famous, that "
        "aisle’s robots saturate. The warehouse may later move stock (adaptive capacity). If you ask too hard too soon, "
        "the door light goes red (throttle).", st["body"]))

    s.append(P("6.6 Partition key, sort key, and the three designs", st["h2"]))
    s.append(P(
        "The <b>partition key</b> (hash key) is the label DynamoDB uses to choose a partition. Items with the same "
        "partition-key value live together. The optional <b>sort key</b> (range key) orders items inside that partition "
        "so you can query “all orders for this customer, newest first”.", st["body"]))
    s.append(P(
        "<b>K1 Simple.</b> Partition key = <font face='Courier'>orderId</font>. No sort key. High cardinality: the planned "
        "million orders are a million partition-key values. Heat still exists if the Zipfian sampler loves a few order ids. "
        "Analogy: every parcel has its own unique locker number.", st["body"]))
    s.append(P(
        "<b>K2 Composite.</b> Partition key = <font face='Courier'>customerId</font>, sort key = "
        "<font face='Courier'>orderTs</font>. Ten thousand customers in the planned dataset. A celebrity customer is a "
        "celebrity aisle. Analogy: one locker per customer, parcels stacked by time inside it.", st["body"]))
    s.append(P(
        "<b>K3 Workload-aware write-sharded.</b> Partition key = <font face='Courier'>orderId#shard</font>, shard in 0..9. "
        "On write, the shard is drawn uniformly at random so repeated writes to one hot order spread across ten keys. On "
        "read, BatchGetItem of all ten, newest <font face='Courier'>version</font> wins. On seed, each order is loaded once "
        "at shard = index mod N. Analogy: the celebrity’s parcels are forced into ten lockers; finding “the latest” means "
        "opening all ten. That is why K3 can cost more on reads. STATUS’s W3 cells show K3 on-demand p99 at 10.320 ms and "
        "cost_per_10k 0.007062, against K1 on-demand 7.047 ms and 0.003901. Those are measured cells, n=1, not a law of "
        "nature — but they are exactly the sort of “sharding is not free” result the design hoped it could be wrong about.", st["body"]))
    s.append(P(
        "<b>K4 (say this and stop).</b> Adaptive / tiered sharding appears in <font face='Courier'>keys.py</font> and in "
        "design-check arithmetic. It is not in the CA2 3×2 tables. No dominance claim. If a professor saw an old markdown "
        "that said otherwise, that markdown is quarantined.", st["body"]))

    s.append(P("6.7 Hot partition", st["h2"]))
    s.append(P(
        "A hot partition is one physical partition that receives far more traffic than its siblings. Zipfian access is how "
        "you manufacture that risk on purpose. If you used a uniform sampler, K3 would have nothing to fix and the "
        "comparison would be fake. Design-check arithmetic in the README (not a live result) says the hottest order gets "
        "10.65% of operations; with 1 KB items, no hot key reaches the documented per-partition limits (3,000 RCU/s, 1,000 "
        "WCU/s) in a main-factorial cell, so throttling there would have to come from table-level provisioned capacity under "
        "burst. The 32 KB sensitivity run is where K1/K2’s hottest key is predicted to cross the write limit. Speak "
        "design-check numbers as <b>predictions</b>, never as STATUS cells.", st["body"]))
    s.append(P(
        "Analogy. One till at a supermarket, all the self-checkouts idle. Adaptive capacity is the manager eventually sending "
        "another clerk. Burst credits are a short queue of goodwill. Throttling is a closed lane. Settling time is how long "
        "you wait after the rush starts before you start the stopwatch.", st["body"]))

    s.append(P("6.8 On-demand versus provisioned", st["h2"]))
    s.append(P(
        "<b>On-demand</b> (PAY_PER_REQUEST): you pay per request. You do not reserve a floor of RCU/WCU. It is the default "
        "story for spiky, unknown traffic. <b>Provisioned</b>: you reserve units. Auto-scaling can move the reservation "
        "inside bounds you wrote in IaC. Under a burst (W4), provisioned is the mode that can theoretically throttle if the "
        "reservation and the burst credits are not enough. In the measured W3/W4 key-cells, throttle_rate was 0.0 everywhere. "
        "That is a result, not a promise for W1/W2 or for 32 KB items.", st["body"]))
    s.append(P(
        "Cost cells already show the joint objective is not trivial. On W3, K1 provisioned cost_per_10k is 0.002328 versus "
        "K1 on-demand 0.003901, with similar p99 (7.339 vs 7.047 ms). On the same W3, K2 <b>provisioned</b> cost_per_10k is "
        "0.010498 — higher than K2 on-demand 0.003874 — while throughput stays ~199.92 ops/s. Do not invent a story about "
        "why without the analysis notes; do say: <i>list-price cost and latency do not rank the six cells the same way, even "
        "in this n=1 slice.</i> On W4, K1 provisioned cost_per_10k is 0.000998 with p99 10.232 ms; K1 on-demand is 0.003886 "
        "with p99 7.640 ms. Faster and cheaper are already arguing.", st["body"]))
    s.append(P(
        "Analogy. On-demand is a taxi meter. Provisioned is a monthly railcard. The railcard wins if you ride every day. "
        "The taxi wins if you ride twice. A burst is a football crowd at the station. A throttle is “this train is full”.", st["body"]))

    s.append(P("6.9 RCU and WCU", st["h2"]))
    s.append(P(
        "A <b>Read Capacity Unit</b> is DynamoDB’s coin for reads. A strongly consistent read of an item up to 4 KB costs "
        "one RCU; eventually consistent reads are cheaper (two reads per unit). A <b>Write Capacity Unit</b> is the coin "
        "for writes: one WCU for a write up to 1 KB. Larger items cost more coins. That is why the design includes a 1 / 8 / "
        "32 KB sensitivity on the best and worst configurations only, and why the main factorial holds item size at 1 KB. "
        "Cost per 10k ops in this project is published unit prices times consumed RCU/WCU, normalised to 10,000 successful "
        "operations, <b>excluding</b> storage and data-transfer. Prices live in <font face='Courier'>config/prices.yaml</font>, "
        "publication date 2026-09-11. Not Cost Explorer. Not a made-up tariff.", st["body"]))
    s.append(P(
        "Analogy. A library that charges one stamp to fetch a thin book and more stamps for a fat book, and one stamp to "
        "put a thin book back. On-demand counts the stamps you used. Provisioned sold you a book of stamps in advance. If "
        "you run out, the librarian says no.", st["body"]))

    s.append(P("6.10 Throttling", st["h2"]))
    s.append(P(
        "Throttling is a rejected request: <font face='Courier'>ProvisionedThroughputExceeded</font>, "
        "<font face='Courier'>ThrottlingException</font>, or CloudWatch <font face='Courier'>ThrottledRequests</font>. "
        "The thesis treats throttles as a first-class dependent variable, not as noise to hide. The live key-cell table "
        "reports throttle_rate = 0.0 on all twelve cells. That is good news for those cells and a limitation for the story: "
        "the interesting “who throttles under W4 provisioned” contrast did not appear at 1 KB with the reserved bounds they "
        "used. A friend must not invent throttles to make the thesis sound more dramatic.", st["body"]))
    s.append(P(
        "Analogy. A nightclub with a fire-limit. The bouncer’s “no” is a throttle. An empty night (rate 0.0) does not prove "
        "the bouncer is unemployed. It proves that, on that night, with that door size, nobody hit the limit.", st["body"]))

    s.append(P("6.11 AWS Lambda", st["h2"]))
    s.append(P(
        "Lambda is Functions-as-a-Service. You upload code; AWS runs it when invoked; you do not manage a server. Cold start "
        "is the extra delay when a new execution environment is created. The design warms functions before measured batches "
        "and excludes cold-start tails from primary latency tables if they are separately reported. Liu et al. (2023) "
        "FaaSLight is in the corpus to justify that control. Lambda here is the <b>driver</b> of DynamoDB load, not the "
        "object of a cold-start paper.", st["body"]))
    s.append(P(
        "Analogy. Food-delivery riders who appear when an order is placed and vanish when idle. The first rider of the "
        "evening takes longer to find the bike (cold start). You do not time the kitchen by that first rider if you can "
        "send a few dummy orders first.", st["body"]))

    s.append(P("6.12 Synthetic data, Zipfian, and ethics", st["h2"]))
    s.append(P(
        "Synthetic means manufactured by code. Order ids look like <font face='Courier'>o0000001</font>. Customer ids look "
        "like <font face='Courier'>c00013</font>. Timestamps start at 2025-01-01 UTC and step by 31 seconds. Payload is the "
        "letter <font face='Courier'>x</font> repeated to pad the item to the target size. There is no name, email, card, "
        "address, or production extract. Ethics: no human participants; own AWS account; free-tier-safe / budget-capped; "
        "acceptable use; single account, single region, single table class.", st["body"]))
    s.append(P(
        "Zipfian means a heavy-tailed popularity curve, the same family as “a few web pages get most of the clicks”. The "
        "README states Zipf s = 1.070916 for the 90%-on-10% target. Uniform access is forbidden for primary runs because it "
        "would nullify K3. Analogy: a city where 10% of the cafés serve 90% of the coffee.", st["body"]))

    s.append(P("6.13 Serverless workloads, batches of 25, ~200 ops/s", st["h2"]))
    s.append(P(
        "“Serverless workload” here means the client of the database is Lambda. Sustained profiles target 200 operations "
        "per second. Burst adds 1,000 ops/s windows. Batch size 25 matches DynamoDB’s BatchWriteItem limit. Those numbers "
        "are design constants from the master prompt. The live W3 throughput column sits at about 199.92 ops/s; W4 at about "
        "466.5 ops/s (burst average over the window). Use those STATUS numbers when asked “what did you actually get?”.", st["body"]))

    s.append(P("6.14 Moto, and the sentence that saves a mark", st["h2"]))
    s.append(P(
        "Moto is a Python library that pretends to be AWS. Unit tests use it so the seeder, handler, and stats plumbing can "
        "run on a laptop. Moto does not replicate network latency, adaptive capacity, burst credits, or auto-scaling delays. "
        "Fixture ANOVA significance is not a DynamoDB finding. If a friend says “our tests showed K3 is faster”, interrupt them.", st["body"]))


    # ---- 7 Dataset ----
    s.append(PageBreak())
    s.append(P("7. Dataset and how the synthetic data is produced", st["h1"])); s.append(hr())
    s.append(P("7.1 The numbers you must be able to say in order", st["h2"]))
    B(s, st, [
        "Planned dataset: <b>1,000,000</b> synthetic order items over <b>10,000</b> customer IDs.",
        "No personal data. Ids are formatted strings from a formula, not people.",
        "Item sizes: main factorial <b>1 KB</b>; sensitivity <b>1 / 8 / 32 KB</b> on best- and worst-performing configurations only.",
        "Access: Zipfian, ≈90% of operations on ≈10% of keys (README: Zipf s = 1.070916).",
        "Workloads: read-heavy ~95% reads; write-heavy ~70% writes; mixed 50/50; burst (W3 mix, 60 s @ 200 + 30 s @ 1,000 ops/s).",
        "Sustained rate: ~200 ops/s from Lambda. Batches of 25.",
        "Live key-cell seed actually used: <b>100,000</b> orders (STATUS). Do not say the live round loaded one million.",
        "Live region: eu-west-1. Live date: 20 September 2026 (wall 11:55:38Z–12:47:42Z → 17:25–18:17 IST).",
    ])
    s.append(P("7.2 What the generator actually does", st["h2"]))
    s.append(P(
        "File <font face='Courier'>workloads/generator/keys.py</font> is the dictionary. "
        "<font face='Courier'>order_id(i)</font> returns <font face='Courier'>o</font> plus a 7-digit number. "
        "<font face='Courier'>customer_of(i)</font> is <font face='Courier'>(i * 7919 + 13) % 10000</font> "
        "formatted as <font face='Courier'>c#####</font>. That multiplier is just a way to spread orders across "
        "customers; it is not a real hash of a person. <font face='Courier'>order_ts(i)</font> walks forward 31 seconds "
        "from 1 January 2025 UTC. <font face='Courier'>make_item</font> copies the key fields, sets status and version, "
        "then pads <font face='Courier'>payload</font> with the letter x until the item is the requested number of "
        "kilobytes. There is no CSV of customers. There is no scrape. There is no GDPR subject.", st["body"]))
    s.append(P(
        "The Zipf sampler (<font face='Courier'>workloads/generator/zipf.py</font>) draws the order index that will be "
        "read or written. Profiles (<font face='Courier'>profiles.py</font>) decide whether that draw becomes a GetItem "
        "or a PutItem, and at what rate. The seeder (<font face='Courier'>workloads/seed/seed.py</font>) walks "
        "i = 0 .. N-1, builds items for the active key design, and writes them with BatchWriteItem in groups of 25. For "
        "K3, seed shard is index mod N. For live key-cells, N was 100,000. For a full campaign as designed, N is 1,000,000.", st["body"]))
    s.append(P("7.3 Why synthetic, and why skew, in sentences a professor likes", st["h2"]))
    s.append(P(
        "Synthetic data removes consent, leakage, and “can we use the company dump?” from the ethics form. It also lets "
        "every third party rebuild the same 1,000,000 items from the same functions. Skew is not decoration: without it, "
        "partition-key design is a naming argument. With it, K2 can concentrate a celebrity customer, K3 can spread a "
        "celebrity order, and K1 can still be hot on a celebrity orderId. Design-check notes estimate the hottest order "
        "share at 10.65% of operations. That figure is arithmetic on the sampler, not a CloudWatch metric.", st["body"]))
    s.append(P("7.4 What a friend should draw on a whiteboard", st["h2"]))
    s.append(P(
        "Draw one million small boxes. Label ten thousand of them as “owners”. Draw a fat arrow into 10% of the boxes and "
        "a thin arrow into the rest. Write “90% of ops” on the fat arrow. Under the boxes write three stickers: K1 (one box "
        "per order), K2 (boxes bundled by owner), K3 (each hot order torn into ten stickers). On the side write “Lambda "
        "200/s, batch 25, 1 KB, no PII”. Under that, in a smaller hand: “live round used 100k boxes, W3 and W4 only”. That "
        "last line is the difference between design and STATUS.", st["body"]))
    s.append(P("7.5 Speaking script — dataset (full, ~90 seconds)", st["h2"]))
    s.append(P(
        "“Our dataset is entirely synthetic. In the committed design we generate one million order items belonging to ten "
        "thousand fake customer identifiers. An order id looks like o0000421. A customer id looks like c01307. The payload "
        "is just the letter x padded to one kilobyte in the main experiment, and to eight or thirty-two kilobytes in a "
        "sensitivity pass. There are no names and no production rows. We do not sample keys uniformly. We use a Zipfian "
        "sampler so that about ninety percent of reads and writes hit about ten percent of the keys, because that is what "
        "makes a partition key decision real. Workloads are read-heavy at about ninety-five percent reads, write-heavy at "
        "about seventy percent writes, mixed fifty-fifty, and a burst profile that jumps from two hundred to one thousand "
        "operations per second. The driver is Lambda. Batch writes use twenty-five items, which is the DynamoDB batch limit. "
        "I need to be precise about what we have actually loaded on AWS: the live key-cell round seeded one hundred thousand "
        "items, not the full million, and it ran mixed and burst only. The million-item figure is the design, and it is still "
        "the right figure to quote when you ask what the artefact is built to do.”", st["script"]))

    # ---- 8 Architecture ----
    s.append(PageBreak())
    s.append(P("8. Architecture and end-to-end flow", st["h1"])); s.append(hr())
    s.append(P("8.1 The picture", st["h2"]))
    s.append(P(
        "Left to right. (1) A laptop or CI shell runs <font face='Courier'>make</font> / "
        "<font face='Courier'>scripts/run_matrix.py</font>. (2) Terraform in <font face='Courier'>iac/</font> creates six "
        "logical table configurations (parameterised module / for_each), one Lambda, IAM roles, CloudWatch bits, S3 for "
        "artefacts, and a budget guard. (3) The seeder writes synthetic items into the table under test. (4) A warm-up "
        "invokes Lambda so containers are hot. (5) A settling interval holds load so adaptive capacity is not mid-walk. "
        "(6) The measured batch: Lambda issues GetItem / PutItem / batch variants according to the profile, no SDK retries, "
        "Zipfian keys, target rate. (7) Each batch writes a raw CSV. CloudWatch is collected. (8) Analysis joins raw rows, "
        "applies <font face='Courier'>prices.yaml</font>, writes cell summaries. (9) Terraform destroy. Evidence stays in "
        "<font face='Courier'>results/</font>.", st["body"]))
    s.append(P("8.2 End-to-end flow as a numbered recipe", st["h2"]))
    B(s, st, [
        "Prerequisites: AWS CLI profile, Terraform, Python 3.12, region chosen (live used eu-west-1).",
        "Render tfvars; terraform apply — six table configs, Lambda, IAM, monitoring, budget.",
        "Seed N items (design 1,000,000; live key-cell 100,000) with BatchWrite of 25.",
        "Warm Lambda. Settle at load for the documented interval (README: 120 s before every batch in the full design).",
        "Run the matrix block: randomise order across configurations; one batch per cell in the key-cell command.",
        "Handler records per-request latency, success, throttle, consumed capacity into gzip CSVs.",
        "collect_metrics.py pulls CloudWatch; analyse applies cost model and (if asked) stats.",
        "Inspect keycell_summary.csv / batches.csv. Compare to list prices. Cost Explorer cross-check was not done.",
        "terraform destroy. Confirm no ddbpk* tables or Lambda remain. Keep the CSVs.",
    ])
    s.append(P("8.3 What “open loop, no retries” means", st["h2"]))
    s.append(P(
        "Closed-loop load testers slow down when the system slows down, which can hide overload. Open loop keeps trying to "
        "send at the planned rate, so a throttle appears as a throttle. Disabling SDK retries stops the client from politely "
        "coughing twice and calling it success. Those two choices are how throttle_rate can be trusted when it is zero or not.", st["body"]))
    s.append(P("8.4 Destroy-after is part of the architecture", st["h2"]))
    s.append(P(
        "STATUS is proud of destroy for a reason. The first live key-cell campaign is recorded as SOLE_AWS_RESIDUAL=closed, "
        "DESTROY_EXIT=0, 32 resources destroyed. Leaving tables up would keep charging and would violate the free-tier / tags "
        "policy the runbook uses. A professor who asks “is this still running in your account?” should hear “no, destroyed "
        "the same day, evidence kept”.", st["body"]))
    s.append(P("8.5 Flow diagram in words (for a slide)", st["h2"]))
    s.append(P(
        "Orchestrator → Terraform apply → Seed (BatchWrite × 25) → Warm Lambda → Settle → Measured open-loop load "
        "(Zipf keys, W3 or W4) → Raw CSV.gz + CloudWatch → Cost model (prices.yaml) → Cell summary → Terraform destroy. "
        "Side path: pytest + moto never joins the right-hand “live evidence” box.", st["body"]))

    # ---- 9 Implementation ----
    s.append(PageBreak())
    s.append(P("9. Implementation modules and short code snippets", st["h1"])); s.append(hr())
    s.append(P("9.1 Map of the repo (what to wave at on screen)", st["h2"]))
    s.append(simple_table([
        [P("<b>Path</b>", st["cheat"]), P("<b>Job</b>", st["cheat"])],
        [P("iac/", st["cheat"]), P("Terraform: tables ×6, Lambda, IAM, monitoring, budgets", st["cheat"])],
        [P("workloads/generator/keys.py", st["cheat"]), P("K1–K3 (and K4 code), synthetic item factory", st["cheat"])],
        [P("workloads/generator/zipf.py", st["cheat"]), P("Zipfian key sampler", st["cheat"])],
        [P("workloads/generator/profiles.py", st["cheat"]), P("W1–W4 mix and arrival", st["cheat"])],
        [P("workloads/seed/seed.py", st["cheat"]), P("BatchWriteItem × 25 loader", st["cheat"])],
        [P("workloads/lambda_handler/handler.py", st["cheat"]), P("Open-loop driver, raw CSV, no SDK retries", st["cheat"])],
        [P("workloads/matrix.py", st["cheat"]), P("Randomised blocks, per-Lambda events", st["cheat"])],
        [P("scripts/run_matrix.py", st["cheat"]), P("The command that filled 12 live cells", st["cheat"])],
        [P("analysis/cost_model.py", st["cheat"]), P("RCU/WCU × prices.yaml → cost/10k", st["cheat"])],
        [P("analysis/ (stats)", st["cheat"]), P("ANOVA / ART / Tukey / Holm — not confirmatory on n=1", st["cheat"])],
        [P("config/experiment.yaml", st["cheat"]), P("Committed factors; K1–K3 only for CA2", st["cheat"])],
        [P("config/prices.yaml", st["cheat"]), P("Dated list prices (2026-09-11)", st["cheat"])],
        [P("tests/", st["cheat"]), P("pytest + moto plumbing", st["cheat"])],
        [P("results/", st["cheat"]), P("Live CSVs + SCHEMA; no invented numbers", st["cheat"])],
    ], col_widths=[210, 290]))
    s.append(P("Table. Modules a friend should be able to point at.", st["caption"]))
    s.append(P("9.2 Key factory (illustrative, shortened from keys.py)", st["h2"]))
    s.append(code_block(
        "N_ORDERS, N_CUSTOMERS = 1_000_000, 10_000\n"
        "def order_id(i):     return f\"o{i:07d}\"\n"
        "def customer_of(i):  return f\"c{(i * 7919 + 13) % N_CUSTOMERS:05d}\"\n"
        "def key_for(design, i, shard=0):\n"
        "    if design == \"K1\": return {\"orderId\": order_id(i)}\n"
        "    if design == \"K2\": return {\"customerId\": customer_of(i), \"orderTs\": order_ts(i)}\n"
        "    if design == \"K3\": return {\"shardKey\": f\"{order_id(i)}#{shard}\"}\n"
        "# make_item(...) pads payload with 'x' to 1, 8 or 32 KB. No personal fields.",
        st))
    s.append(P(
        "What to say while this is on the slide: “This is the entire personal-data story. There isn’t one. The functions "
        "invent ids. K3’s shard is part of the key, not part of a person.”", st["body"]))
    s.append(P("9.3 What the handler is allowed to do", st["h2"]))
    s.append(P(
        "The Lambda handler is a load generator, not a business app. It receives a profile, a key design, a duration, a "
        "target rate. It samples Zipfian indices, builds keys, issues DynamoDB API calls, notes latency and consumed capacity "
        "and whether the error was a throttle, and writes a CSV. It does not retry. It does not “help” a failing cell look "
        "cleaner. That restraint is a feature.", st["body"]))
    s.append(P("9.4 Cost model, in words a finance tutor would accept", st["h2"]))
    s.append(P(
        "Take consumed RCU and WCU from the API and from CloudWatch. Multiply by the unit prices in "
        "<font face='Courier'>prices.yaml</font> for the region and date. Divide so the figure is USD per 10,000 successful "
        "operations. Do not add storage. Do not add data transfer. Do not “adjust” to match a monthly bill. STATUS’s "
        "request-path list-price sum for the key-cell wall is about $0.251. Per-cell cost_per_10k values are in the STATUS "
        "table and are repeated in section 11.", st["body"]))
    s.append(P("9.5 Tests — what they prove and what they do not", st["h2"]))
    s.append(P(
        "pytest plus moto proves: keys build, seeder paginates batches of 25, handler writes a CSV schema, cost function "
        "multiplies, stats code can run on a fixture. It does not prove p99, adaptive capacity, or a dollar figure. The "
        "README’s <font face='Courier'>make smoke</font> is “whole pipeline on in-memory DynamoDB, not DynamoDB data”. A "
        "friend who confuses smoke with the 20 September live round will be asked a follow-up they will fail.", st["body"]))

    # ---- 10 AWS ----
    s.append(PageBreak())
    s.append(P("10. AWS services used (what / why / analogy)", st["h1"])); s.append(hr())
    s.append(P(
        "This project is AWS-only. It is not a multi-cloud comparison. Do not mention GCP or Azure unless you are saying "
        "“we did not use them”.", st["body"]))
    s.append(simple_table([
        [P("<b>Service</b>", st["cheat"]), P("<b>What it is</b>", st["cheat"]),
         P("<b>Why here</b>", st["cheat"]), P("<b>Analogy</b>", st["cheat"])],
        [P("Amazon DynamoDB", st["cheat"]), P("Managed NoSQL with partition keys and a capacity meter", st["cheat"]),
         P("System under test; six configurations", st["cheat"]), P("Warehouse that charges per fetch and can refuse you", st["cheat"])],
        [P("AWS Lambda", st["cheat"]), P("Managed function runner", st["cheat"]),
         P("Issues the workload; serverless client", st["cheat"]), P("Riders who appear when an order is placed", st["cheat"])],
        [P("IAM", st["cheat"]), P("Roles and policies", st["cheat"]),
         P("Least-privilege for Lambda → DynamoDB / logs", st["cheat"]), P("A badge that opens only two doors", st["cheat"])],
        [P("Amazon CloudWatch", st["cheat"]), P("Metrics and logs", st["cheat"]),
         P("Consumed capacity, throttles, invocations", st["cheat"]), P("Dashboard above the warehouse door", st["cheat"])],
        [P("Amazon S3", st["cheat"]), P("Object storage", st["cheat"]),
         P("Artefacts / raw outputs as wired in IaC", st["cheat"]), P("A labelled crate in a back room", st["cheat"])],
        [P("AWS Budgets / alarms", st["cheat"]), P("Spend and metric guards", st["cheat"]),
         P("Abort if the campaign runs away", st["cheat"]), P("A prepaid electricity meter", st["cheat"])],
        [P("Terraform (IaC tool)", st["cheat"]), P("Declarative infrastructure", st["cheat"]),
         P("Rebuild and destroy the six tables", st["cheat"]), P("A recipe that also washes the dishes", st["cheat"])],
    ], col_widths=[100, 135, 140, 125]))
    s.append(P("Table. AWS pieces and the one-line analogy for each.", st["caption"]))
    s.append(P(
        "Not used as platforms under test: Google Cloud Run, Cloud Spanner, Azure Functions, Cosmos DB. If asked “why AWS?”, "
        "the answer is: because the meters this gap needs are DynamoDB’s meters, and the serverless driver the design "
        "committed to is Lambda.", st["body"]))

    # ---- 11 Experiment ----
    s.append(PageBreak())
    s.append(P("11. Experiment design and metrics", st["h1"])); s.append(hr())
    s.append(P("11.1 Factorial as designed", st["h2"]))
    s.append(P(
        "Independent variables: key design K1/K2/K3; capacity mode on-demand/provisioned. Conditioning: W1–W4. Item size "
        "held at 1 KB in the main factorial; 1/8/32 KB sensitivity on best and worst only. Replication in the analysis plan: "
        "n = 30 batches per cell in 30 randomised blocks, 120 s settling and Lambda warm-up, no SDK retries, two-way ANOVA "
        "with interaction (or aligned rank transform), Tukey simple effects, Holm over the family, α = 0.05, practical "
        "significance 10% of baseline mean latency and 5% of cost/10k. Power story: medium effect f = 0.25 at 80%.", st["body"]))
    s.append(P("11.2 Factorial as measured (STATUS — the only numbers table you should recite)", st["h2"]))
    s.append(P(
        "Live key-cell round, n=1 each, eu-west-1, orders=100000. Throttle_rate = 0.0 on every row. Throughput is successful "
        "ops/s. cost_per_10k is list-price USD.", st["body"]))
    s.append(simple_table([
        [P("<b>Cell</b>", st["cheat"]), P("<b>p99 ms</b>", st["cheat"]), P("<b>thr ops/s</b>", st["cheat"]),
         P("<b>throttle</b>", st["cheat"]), P("<b>cost/10k</b>", st["cheat"])],
        [P("K1-od-W3", st["cheat"]), P("7.047", st["cheat"]), P("199.922", st["cheat"]), P("0.0", st["cheat"]), P("0.003901", st["cheat"])],
        [P("K1-prov-W3", st["cheat"]), P("7.339", st["cheat"]), P("199.925", st["cheat"]), P("0.0", st["cheat"]), P("0.002328", st["cheat"])],
        [P("K2-od-W3", st["cheat"]), P("6.948", st["cheat"]), P("199.918", st["cheat"]), P("0.0", st["cheat"]), P("0.003874", st["cheat"])],
        [P("K2-prov-W3", st["cheat"]), P("7.499", st["cheat"]), P("199.919", st["cheat"]), P("0.0", st["cheat"]), P("0.010498", st["cheat"])],
        [P("K3-od-W3", st["cheat"]), P("10.320", st["cheat"]), P("199.919", st["cheat"]), P("0.0", st["cheat"]), P("0.007062", st["cheat"])],
        [P("K3-prov-W3", st["cheat"]), P("8.333", st["cheat"]), P("199.920", st["cheat"]), P("0.0", st["cheat"]), P("0.007128", st["cheat"])],
        [P("K1-od-W4", st["cheat"]), P("7.640", st["cheat"]), P("466.531", st["cheat"]), P("0.0", st["cheat"]), P("0.003886", st["cheat"])],
        [P("K1-prov-W4", st["cheat"]), P("10.232", st["cheat"]), P("466.532", st["cheat"]), P("0.0", st["cheat"]), P("0.000998", st["cheat"])],
        [P("K2-od-W4", st["cheat"]), P("9.631", st["cheat"]), P("466.530", st["cheat"]), P("0.0", st["cheat"]), P("0.003899", st["cheat"])],
        [P("K2-prov-W4", st["cheat"]), P("7.667", st["cheat"]), P("466.533", st["cheat"]), P("0.0", st["cheat"]), P("0.000998", st["cheat"])],
        [P("K3-od-W4", st["cheat"]), P("10.623", st["cheat"]), P("466.483", st["cheat"]), P("0.0", st["cheat"]), P("0.007063", st["cheat"])],
        [P("K3-prov-W4", st["cheat"]), P("11.490", st["cheat"]), P("466.531", st["cheat"]), P("0.0", st["cheat"]), P("0.005567", st["cheat"])],
    ], col_widths=[110, 80, 95, 80, 90]))
    s.append(P("Table. STATUS live key-cell round only (od = on_demand, prov = provisioned). Do not add rows.", st["caption"]))
    s.append(P(
        "Speaking the table without drowning. “On mixed traffic, K1 and K2 sit around 7 ms p99; K3 is higher, about 8 to "
        "10 ms, and about twice the list-price cost of K1 on-demand. On burst, throughput averages about 467 ops/s. "
        "Provisioned K1 and K2 on burst show the lowest cost-per-10k in this slice, 0.000998, but K1 provisioned p99 rose "
        "to 10.2 ms against 7.6 ms on-demand. Throttles were zero. n is one. I will not call this ANOVA.”", st["body"]))
    s.append(P("11.3 Dependent variables", st["h2"]))
    B(s, st, [
        "Mean latency, p95, p99 — client-observed milliseconds (Pantelić language retained).",
        "Successful ops/s — completed operations / wall time (Pantelić throughput retained).",
        "Throttled request count / throttle_rate — new versus baseline.",
        "Consumed RCU / WCU — API + CloudWatch — new.",
        "Cost per 10,000 operations — list price × consumption — new. Storage and transfer excluded.",
    ])
    s.append(P("11.4 What you must not claim from this table", st["h2"]))
    B(s, st, [
        "W1/W2 cells — not measured.",
        "Confirmatory live ANOVA / Tukey — not computed (exploratory n=1 OLS/KW only).",
        "Cost Explorer validation — not claimed.",
        "K4 dominance — quarantined.",
        "Zipfian calibrated at 1M with the 100k seed — STATUS lists this as not claimed.",
        "That throttle_rate=0 means DynamoDB never throttles — it means these cells did not.",
    ])

    # ---- 12 Speaking scripts ----
    s.append(PageBreak())
    s.append(P("12. Class speaking scripts", st["h1"])); s.append(hr())
    s.append(P("12.1 Dataset script (~90 seconds)", st["h2"]))
    s.append(P(
        "“I will start with the data, because it is the part people worry about ethically and the part that makes the "
        "key-design factor real. Everything is synthetic. The artefact is built for one million order items and ten thousand "
        "customer identifiers. Ids are printed by a formula — o0000421, c01307 — and the payload is the letter x padded to "
        "one kilobyte, or eight or thirty-two in a sensitivity pass. There is no personal data. We force Zipfian access so "
        "about ninety percent of operations hit about ten percent of keys. Without that skew, write-sharding would look like "
        "a fashion choice. Workloads are read-heavy near ninety-five percent reads, write-heavy near seventy percent writes, "
        "mixed fifty-fifty, and a burst that jumps from two hundred to one thousand operations per second. Lambda drives the "
        "load; batches are twenty-five. One honesty line: the live key-cell round on the twentieth of September seeded one "
        "hundred thousand items and ran mixed and burst only. The million-item figure is what the code is designed to do.”", st["script"]))
    s.append(P("12.2 Implementation-progress script (~2 minutes)", st["h2"]))
    s.append(P(
        "“On the artefact side we are complete for the CA2 floor. Terraform stands up six table configurations, Lambda, IAM, "
        "CloudWatch, S3, and a budget. The Zipfian generator, the four workload profiles, the seeder, the open-loop handler, "
        "the cost model, and the ANOVA pipeline all exist and are unit-tested against moto. On the twentieth of September we "
        "ran a live key-cell round in eu-west-1: twelve cells, K1 through K3, on-demand and provisioned, mixed and burst, "
        "one replicate each, one hundred thousand seed items. Throttle rate was zero on every cell. We destroyed thirty-two "
        "Terraform resources afterwards. Soft residuals remain: read-heavy and write-heavy live cells, and confirmatory "
        "repeats for ANOVA. Exploratory n-equals-one stats exist; they are not confirmatory. K4 adaptive sharding is code "
        "only and off the factorial — we do not claim it won. Alignment after the live fold is about ninety-four percent, "
        "not one hundred.”", st["script"]))
    s.append(P("12.3 Technologies script (~90 seconds)", st["h2"]))
    s.append(P(
        "“The stack is Amazon DynamoDB as the system under test, AWS Lambda as the serverless workload driver, IAM for "
        "least privilege, CloudWatch for capacity and throttle metrics, S3 for artefacts, and AWS Budgets as a guardrail. "
        "Infrastructure is Terraform. Analysis and generators are Python 3.12. Local plumbing tests use moto — and I will "
        "say this twice — moto is not live DynamoDB. Cost figures use dated list prices in prices.yaml from the eleventh of "
        "September twenty twenty-six, not Cost Explorer. We did not use GCP or Azure in this artefact. The literature pack "
        "has twenty-one peer-reviewed items from twenty twenty-two to twenty twenty-six plus three AWS documentation URLs "
        "for billing and sharding mechanisms.”", st["script"]))
    s.append(P("12.4 Baseline-and-gap script (~60 seconds)", st["h2"]))
    s.append(P(
        "“Our baseline is Pantelić and colleagues, Future Internet, twenty twenty-six, DOI 10.3390/fi18010053. They "
        "benchmarked SQL and NoSQL persistence for microservices under variable workloads on a self-hosted single node. "
        "They give us the workload language and the latency and throughput metrics. What they cannot give us is RCU, WCU, "
        "throttling, or per-operation price, because those meters do not exist on a self-hosted node. Our thesis therefore "
        "stays on DynamoDB and varies partition-key design against capacity mode under Lambda-driven Zipfian load. We are "
        "not re-running a Postgres-versus-Mongo bake-off.”", st["script"]))
    s.append(P("12.5 Results honesty script (~45 seconds)", st["h2"]))
    s.append(P(
        "“From the twelve live cells: on mixed load, K1 and K2 p99 are about seven milliseconds; K3 is higher, about eight "
        "to ten, and more expensive on list price. On burst, throughput averages about four hundred sixty-seven operations "
        "per second. Provisioned K1 and K2 show the lowest cost-per-ten-thousand in that slice, but K1 provisioned p99 rose "
        "relative to on-demand. Throttles were zero. n equals one. I will not present this as confirmatory ANOVA.”", st["script"]))

    # ---- 13 Q&A ----
    s.append(PageBreak())
    s.append(P("13. Professor Q&A — exact answers", st["h1"])); s.append(hr())
    s.append(P(
        "Read the answer as written. Do not decorate with numbers that are not here.", st["body"]))
    add_qa(s, st, [
        ("What is your research question?",
         "How does Amazon DynamoDB table configuration — partition-key design crossed with capacity mode — determine the performance–cost trade-off under serverless workloads?"),
        ("Why Pantelić et al. (2026) and not a DynamoDB paper as baseline?",
         "Because they fix the workload language and the latency/throughput scores we retain. Their gap is structural: a self-hosted node has no RCU, WCU, throttle, or per-op price. That missing meter is our problem."),
        ("Did you compare SQL and NoSQL?",
         "No. Pantelić did, on a node they hosted. We are already on DynamoDB. We vary key design and capacity mode and read the meters."),
        ("What is a partition key, in one sentence?",
         "It is the label DynamoDB uses to place an item on a physical partition; bad labels under Zipfian traffic create hot partitions."),
        ("Explain K1, K2, K3 without jargon.",
         "K1: one locker per order. K2: one locker per customer with parcels stacked by time. K3: spray a hot order across ten lockers; reading the latest means opening all ten."),
        ("What is a hot partition?",
         "One physical partition that gets far more traffic than the others. We force that risk with a Zipfian sampler so key design actually matters."),
        ("On-demand versus provisioned?",
         "On-demand pays per request. Provisioned reserves units (with auto-scaling bounds in our Terraform). Provisioned can throttle if demand exceeds the reservation and burst credits."),
        ("What are RCU and WCU?",
         "Read and write capacity units — DynamoDB’s coins. Cost per 10k ops in this project is published unit prices times consumed coins, excluding storage and transfer."),
        ("What data did you use? Is it personal?",
         "Synthetic only. Planned: 1,000,000 orders over 10,000 fake customer ids. Live key-cell seed: 100,000. No names, emails, or production extracts."),
        ("Why Zipfian, not uniform?",
         "Uniform access would concentrate load on no partition and would leave K3 with nothing to correct. Skew is a precondition of the comparison."),
        ("What did you actually measure on AWS?",
         "Twelve cells on 20 September 2026 in eu-west-1: K1–K3 × on-demand/provisioned × W3/W4, n=1, 100k seed. Throttle_rate 0.0 everywhere. Stack destroyed afterwards."),
        ("Why is throttle_rate zero — is that a problem?",
         "It is a measured result for those cells at 1 KB with our reserved bounds. It does not prove DynamoDB never throttles. We do not invent throttles for drama."),
        ("Is this confirmatory ANOVA?",
         "No. n=1 saturates the interaction residual. Exploratory OLS/KW exist; confirmatory repeats are a soft residual."),
        ("What about K4?",
         "Optional code / design-check arithmetic only. Off CA2 factorial. No dominance claims. Older markdown that said otherwise is quarantined."),
        ("Did Cost Explorer validate your dollar figures?",
         "No. We use list prices in prices.yaml dated 2026-09-11. Cost Explorer validation is not claimed."),
        ("Is moto a live AWS result?",
         "No. Moto is an emulator for unit tests. It does not replicate network latency, adaptive capacity, or auto-scaling delays."),
        ("Why Lambda?",
         "Because the research question is under serverless workloads. Lambda is the committed driver; we warm it so cold starts do not masquerade as table latency."),
        ("Why not GCP or Azure?",
         "The meters in the gap statement are DynamoDB’s. The artefact is AWS-only by design."),
        ("What companies use SQL vs NoSQL?",
         "SQL-leaning: banks, airlines, ERP, registries — join-heavy consistency. NoSQL-leaning: high-QPS internet, gaming, IoT, retail carts — key-first access. Many firms run both."),
        ("Did latency-optimal equal cost-optimal in your cells?",
         "Even in the n=1 slice they argue: for example on W4, K1 on-demand p99 7.640 ms at cost 0.003886 versus K1 provisioned p99 10.232 ms at cost 0.000998. We do not upgrade that into a confirmed hypothesis test."),
        ("What is still incomplete?",
         "W1/W2 live cells; confirmatory n>1 ANOVA; Cost Explorer cross-check. STATUS alignment ~94%. Hard sole AWS residual for the first key-cell campaign is closed after destroy."),
        ("What is your contribution in one sentence?",
         "A controlled empirical evaluation that varies partition-key design and capacity mode together on live DynamoDB while measuring latency, throttling, consumed capacity, and per-operation list-price cost under Lambda-driven Zipfian workloads."),
    ])

    # ---- 14 STATUS ----
    s.append(PageBreak())
    s.append(P("14. Honest STATUS and limitations", st["h1"])); s.append(hr())
    s.append(P("14.1 Compact STATUS flags (from STATUS.md)", st["h2"]))
    B(s, st, [
        "COMPLETE for the initial-eval gate: INITIAL_EVAL_PASS=yes; FINAL3=done_3of3 (for that gate’s definition).",
        "ALIGNMENT after live key-cell fold ≈ 94% (was ~92%); CA2 not literally 100% with W1/W2 still open.",
        "SOLE_AWS_RESIDUAL=no / closed for the first live key-cell campaign after destroy.",
        "LIVE_KEYCELL_COMPLETE=yes (12/12). LIVE_FULL_FACTORIAL=no. LIVE_ANOVA=exploratory_n1_only.",
        "DESTROY_AFTER_ROUND=yes (32 resources).",
        "Request-path list-price sum ≈ $0.251 for the measured wall.",
    ])
    s.append(P("14.2 Limitations you should volunteer before being asked", st["h2"]))
    B(s, st, [
        "Single account, single region (eu-west-1), single table class.",
        "Live seed 100k, not 1M; W1/W2 not live; n=1 per key-cell.",
        "List-price cost proxy; not Cost Explorer–validated.",
        "Throttle_rate=0 on measured cells — limited contrast on rejection.",
        "K4 not in factorial; older dominance rhetoric quarantined.",
        "Moto tests are plumbing only.",
        "Adaptive capacity settling is controlled but the provider’s control plane is not ours (König et al. 2023 motivate the settling interval).",
        "Item-size sensitivity is designed; do not invent filled 32 KB live cells unless STATUS later says so.",
    ])
    s.append(P("14.3 External / internal / construct validity (short)", st["h2"]))
    s.append(P(
        "External: one account, one region, one service — not a statement about Cosmos DB or Cassandra. Internal: open "
        "loop, no SDK retries, warm-up, settling, randomised order — aimed at clean attribution; n=1 still limits "
        "inference. Construct: cost excludes storage and transfer by design so the figure tracks the request path the "
        "configuration governs. Conclusion validity: no confirmatory ANOVA claimed.", st["body"]))

    # ---- 15 Cheat sheet ----
    s.append(PageBreak())
    s.append(P("15. One-page cheat sheet", st["h1"])); s.append(hr())
    s.append(P(
        "<b>Student / ID:</b> Rasool Basha Durbesula / 24205478<br/>"
        "<b>Title:</b> Partition-Key Design and Capacity Mode in Amazon DynamoDB… under Serverless Workloads<br/>"
        "<b>Artefact:</b> dynamodb-pk-capacity-eval/<br/>"
        "<b>Baseline:</b> Pantelić et al. (2026) Future Internet 18(1):53 — DOI 10.3390/fi18010053<br/>"
        "<b>RQ:</b> How does DynamoDB table configuration (PK design × capacity mode) set the performance–cost trade-off under serverless workloads?<br/>"
        "<b>Move:</b> Keep Pantelić latency/throughput language; add RCU/WCU, throttle, cost/10k on live DynamoDB.<br/>"
        "<b>Factors:</b> K1 orderId · K2 customerId+orderTs · K3 orderId#shard (N=10) × on-demand/provisioned · W1–W4<br/>"
        "<b>Data (design):</b> 1,000,000 synthetic orders / 10,000 customers · Zipf ~90% on ~10% · 1/8/32 KB · ~200 ops/s · batch 25 · no PII<br/>"
        "<b>Data (live):</b> 100k seed · W3/W4 only · 12 cells · n=1 · eu-west-1 · 20 Sep 2026 · destroyed<br/>"
        "<b>Headline live:</b> throttle 0.0 all cells · W3 ~200 ops/s · W4 ~467 ops/s · K3 often higher p99/cost on W3 · list-price sum ≈ $0.251<br/>"
        "<b>Do not say:</b> SQL vs NoSQL rematch · K4 won · Cost Explorer validated · confirmatory ANOVA · moto = AWS · 1M live seed<br/>"
        "<b>Soft residual:</b> W1/W2 live · n&gt;1 ANOVA · Cost Explorer<br/>"
        "<b>SQL vs NoSQL one-liner:</b> Pantelić ranked engine families on a self-hosted node; this thesis meters PK × capacity on DynamoDB.",
        st["cheat"]))
    s.append(Spacer(1, 8))
    s.append(P(
        "Keep this page open in the viva. If you forget everything else, read the “Do not say” line out loud before you answer.",
        st["body"]))

    # ---- PAGE EXPANSION: deep dives (factual / pedagogical) ----
    s.append(P("Appendix A — Cell-by-cell speaking notes (STATUS only)", st["h1"])); s.append(hr())
    s.append(P(
        "These notes exist so a friend can talk through the STATUS table without inventing a story. Each cell is n=1. "
        "Treat every sentence as descriptive, not as a confirmed main effect.", st["body"]))
    cells = [
        ("K1-on_demand-W3", "p99 7.047 ms; thr 199.922; throttle 0.0; cost/10k 0.003901",
         "Simple orderId key, pay-per-request, mixed 50/50. Clean reference cell: about 200 ops/s, sub-10 ms p99, mid-pack list price among W3 on-demand rows."),
        ("K1-provisioned-W3", "p99 7.339 ms; thr 199.925; throttle 0.0; cost/10k 0.002328",
         "Same key, reserved capacity. p99 almost matches on-demand; list-price cost is lower in this slice."),
        ("K2-on_demand-W3", "p99 6.948 ms; thr 199.918; throttle 0.0; cost/10k 0.003874",
         "Customer-localised key, on-demand. Slightly lowest p99 among W3 on-demand rows here. Do not crown a winner from one replicate."),
        ("K2-provisioned-W3", "p99 7.499 ms; thr 199.919; throttle 0.0; cost/10k 0.010498",
         "List-price cost jumps to 0.010498, higher than K2 on-demand. Clearest W3 warning that cheaper mode depends on the cell."),
        ("K3-on_demand-W3", "p99 10.320 ms; thr 199.919; throttle 0.0; cost/10k 0.007062",
         "Write-sharded key. Higher p99 and about 1.8× K1 on-demand cost. Scatter-gather reads are the intuitive explanation; still n=1."),
        ("K3-provisioned-W3", "p99 8.333 ms; thr 199.920; throttle 0.0; cost/10k 0.007128",
         "p99 improves versus K3 on-demand in this slice; cost stays elevated versus K1/K2 on-demand. Sharding is not free."),
        ("K1-on_demand-W4", "p99 7.640 ms; thr 466.531; throttle 0.0; cost/10k 0.003886",
         "Burst average ~467 ops/s. On-demand keeps K1 p99 near the mixed-load region."),
        ("K1-provisioned-W4", "p99 10.232 ms; thr 466.532; throttle 0.0; cost/10k 0.000998",
         "Lowest cost/10k in the table, but p99 rises to 10.232 ms. Latency-optimal and cost-optimal disagree."),
        ("K2-on_demand-W4", "p99 9.631 ms; thr 466.530; throttle 0.0; cost/10k 0.003899",
         "Burst on-demand for the composite key. p99 higher than K1 on-demand W4; cost similar."),
        ("K2-provisioned-W4", "p99 7.667 ms; thr 466.533; throttle 0.0; cost/10k 0.000998",
         "Matches K1 provisioned W4 on cost/10k; p99 stays near 7.7 ms. Rankings flip by metric."),
        ("K3-on_demand-W4", "p99 10.623 ms; thr 466.483; throttle 0.0; cost/10k 0.007063",
         "Burst does not erase K3’s higher cost/10k relative to K1/K2 on-demand."),
        ("K3-provisioned-W4", "p99 11.490 ms; thr 466.531; throttle 0.0; cost/10k 0.005567",
         "Highest p99 in the table. Cost between K3 on-demand and the cheap provisioned K1/K2 cells."),
    ]
    for name, nums, note in cells:
        s.append(P(f"<b>{name}</b> — {nums}", st["h3"]))
        s.append(P(note, st["body"]))

    s.append(P("Appendix B — Extended analogies you can reuse", st["h1"])); s.append(hr())
    s.append(P("B.1 The warehouse (DynamoDB)", st["h2"]))
    s.append(P(
        "Imagine a warehouse the size of a city. You never meet the staff. Every crate has a label you chose. The warehouse "
        "charges stamps for fetching and putting. If one aisle is famous, that aisle’s robots saturate. Managers may later "
        "move stock (adaptive capacity). If you ask too hard too soon, the door light goes red (throttle). On-demand means "
        "you pay for the stamps you used. Provisioned means you bought a booklet of stamps in advance. Rasool’s experiment "
        "changes how you print the labels (K1/K2/K3), how you buy stamps (on-demand/provisioned), sends Zipfian traffic from "
        "a fleet of riders (Lambda), and writes down stamps, door lights, and stopwatch times.", st["body"]))
    s.append(P("B.2 The restaurant (SQL vs NoSQL in Pantelić)", st["h2"]))
    s.append(P(
        "Pantelić compared two kitchens they owned: a relational kitchen with recipes that join many books (SQL), and a "
        "NoSQL kitchen with locker-style tickets. They timed which kitchen finished plates faster under lunch-rush mixes. "
        "They did not have a cover-charge printer. Rasool moved into a managed DynamoDB restaurant that prints cover charges "
        "and can refuse entry. He stopped comparing kitchen brands and started comparing ticket labels and cover-charge plans.", st["body"]))
    s.append(P("B.3 The celebrity café (Zipfian)", st["h2"]))
    s.append(P(
        "In a city of cafés, ten percent serve ninety percent of the coffee. If your key is “café name”, the celebrity café "
        "is a hot partition. If your key is “order number”, celebrity orders still exist. If you tear each celebrity order "
        "into ten shards, the write heat spreads, but “what is the latest order state?” means asking ten tills. That is K3.", st["body"]))
    s.append(P("B.4 The railcard versus the taxi (capacity modes)", st["h2"]))
    s.append(P(
        "A monthly railcard (provisioned) wins if you ride every weekday. A taxi meter (on-demand) wins if you ride twice. "
        "A football crowd is a burst. “This train is full” is a throttle. Look at K1 on W4: on-demand p99 7.640 ms at cost "
        "0.003886; provisioned p99 10.232 ms at cost 0.000998.", st["body"]))
    s.append(P("B.5 The emulator dollhouse (moto)", st["h2"]))
    s.append(P(
        "Moto is a dollhouse version of AWS in Python. You can practise opening doors and writing receipts. You cannot claim "
        "the dollhouse measured the city’s traffic jams. Unit tests belong in the dollhouse. STATUS live cells belong in eu-west-1.", st["body"]))

    s.append(P("Appendix C — Glossary (speakable definitions)", st["h1"])); s.append(hr())
    glossary = [
        ("SQL", "Language and shorthand for relational databases: tables, joins, schemas."),
        ("NoSQL", "Family of non-relational stores; name the product (e.g. DynamoDB), not just the family."),
        ("Amazon DynamoDB", "AWS managed NoSQL service with partition keys and a capacity meter."),
        ("Partition key", "Label used to place an item on a physical partition."),
        ("Sort key", "Optional second key that orders items inside a partition."),
        ("Hot partition", "A partition that receives disproportionate traffic."),
        ("Zipfian", "Heavy-tailed popularity; here ≈90% of ops on ≈10% of keys."),
        ("On-demand", "PAY_PER_REQUEST billing; pay for consumed units."),
        ("Provisioned", "Reserved RCU/WCU (optionally auto-scaled within bounds)."),
        ("RCU", "Read capacity unit — DynamoDB’s read coin."),
        ("WCU", "Write capacity unit — DynamoDB’s write coin."),
        ("Throttling", "Request rejected because capacity was exceeded."),
        ("p99 latency", "99th percentile client-observed latency in milliseconds."),
        ("Throughput (ops/s)", "Successful operations per second of wall time."),
        ("cost_per_10k", "List-price USD for 10,000 successful ops from consumed units."),
        ("Lambda", "AWS Functions-as-a-Service; here the load driver."),
        ("Cold start", "Extra delay when a new Lambda execution environment starts."),
        ("Terraform", "Infrastructure-as-code tool used to apply and destroy the stack."),
        ("moto", "Local AWS emulator for unit tests — not live evidence."),
        ("Factorial design", "Crossing every level of every factor (here key × capacity, conditioned by workload)."),
        ("n=1", "One replicate per cell — descriptive, not confirmatory ANOVA."),
        ("Holm–Bonferroni", "p-value adjustment across a family of tests."),
        ("ANOVA interaction", "Whether the effect of one factor depends on the level of another."),
        ("Synthetic data", "Manufactured by code; no personal data."),
        ("BatchWriteItem (25)", "DynamoDB API limit used by the seeder and batch path."),
        ("Adaptive capacity", "DynamoDB reallocating throughput toward hot partitions over time."),
        ("Settling interval", "Wait under load before measuring, so adaptive capacity is not mid-walk."),
        ("Open-loop load", "Client keeps targeting a rate even if the system slows — exposes overload."),
        ("List price", "Published unit price in prices.yaml; not the monthly bill."),
        ("CA2 factorial", "Committed K1–K3 × on-demand/provisioned × W1–W4; live filled W3/W4 only so far."),
        ("K4", "Optional adaptive sharding code — off factorial, no dominance claim."),
        ("eu-west-1", "AWS region used for the live key-cell round (Ireland)."),
        ("Destroy-after", "Terraform destroy after the round; evidence retained on disk."),
        ("Pantelić et al. (2026)", "Baseline SQL vs NoSQL microservice persistence benchmark on a self-hosted node."),
        ("Gap", "Baseline cannot produce RCU/WCU/throttle/price because those meters do not exist there."),
    ]
    for term, defn in glossary:
        s.append(P(f"<b>{term}.</b> {defn}", st["cheat"]))

    s.append(P("Appendix D — Practice dialogue (friend ↔ professor)", st["h1"])); s.append(hr())
    dialogue = [
        ("Professor", "So you compared MongoDB and Postgres?"),
        ("Friend", "No. Pantelić compared SQL and NoSQL on a self-hosted node. Rasool varied partition-key design and capacity mode on DynamoDB and measured RCU, WCU, throttles, and list-price cost."),
        ("Professor", "Then why cite Pantelić?"),
        ("Friend", "For the workload language — read-heavy, write-heavy, mixed, burst — and for latency and throughput metrics we retain. Their missing meters are our gap."),
        ("Professor", "Show me one number you actually measured."),
        ("Friend", "K1 on-demand mixed: p99 7.047 milliseconds, about 199.9 operations per second, throttle rate zero, cost per ten thousand operations 0.003901 US dollars at list price. That is one cell, n equals one, on the twentieth of September in eu-west-1."),
        ("Professor", "Is sharding better?"),
        ("Friend", "Not free. On mixed load, K3 on-demand p99 was 10.320 milliseconds and cost 0.007062, higher than K1 on-demand. We do not crown a winner from n equals one."),
        ("Professor", "Where is your ANOVA?"),
        ("Friend", "The analysis code exists. Confirmatory live ANOVA is not claimed because n equals one saturates the interaction residual. Exploratory OLS and Kruskal–Wallis are labelled exploratory."),
        ("Professor", "Is the stack still running?"),
        ("Friend", "No. Thirty-two Terraform resources were destroyed after the round. Evidence is in results CSVs."),
        ("Professor", "Did you use real customer data?"),
        ("Friend", "No. Synthetic ids only. Planned one million orders over ten thousand fake customers. Live seed one hundred thousand."),
        ("Professor", "Moto showed significance — is that your result?"),
        ("Friend", "No. Moto is an emulator for plumbing tests. It is not DynamoDB latency or capacity."),
    ]
    for who, line in dialogue:
        s.append(P(f"<b>{who}:</b> {line}", st["body"]))

    s.append(P("Appendix E — Implementation progress checklist (for class)", st["h1"])); s.append(hr())
    s.append(P("Say “done” or “soft residual” — nothing in between.", st["body"]))
    B(s, st, [
        "Research design factorial written — done.",
        "Terraform six configs + Lambda + IAM + monitoring + budget — done.",
        "Zipfian generator + W1–W4 profiles + seeder + open-loop handler — done.",
        "Cost model wired to prices.yaml — done.",
        "ANOVA/ART/Tukey/Holm code + unit tests — done (not confirmatory on live n=1).",
        "Moto pytest plumbing — done (not AWS evidence).",
        "Live W3/W4 key-cells 12/12 — done.",
        "Destroy-after — done.",
        "Live W1/W2 — soft residual.",
        "Confirmatory n&gt;1 ANOVA — soft residual.",
        "Cost Explorer validation — soft residual / not claimed.",
        "K4 dominance — must not claim.",
    ])
    s.append(P(
        "Class line: “Artefact is implementable end-to-end; live evidence covers the twelve key-cells; soft residuals are "
        "named in STATUS; we are not pretending the residuals are filled.”", st["body"]))

    s.append(P("Appendix F — Technologies deep dive", st["h1"])); s.append(hr())
    tech = [
        ("Python 3.12", "Language of generators, handler, analysis. Pin it in the runbook so a marker can rebuild."),
        ("boto3 / botocore", "AWS SDK used by Lambda and scripts to call DynamoDB and CloudWatch."),
        ("Terraform", "Declarative IaC. apply builds; destroy tears down. Parameterises key schema and billing mode."),
        ("pytest", "Unit test runner. With moto, proves plumbing before spending money."),
        ("moto", "In-process AWS stub. Correctness of code paths only."),
        ("pandas / scipy / statsmodels (as wired)", "Analysis stack for summaries and planned ANOVA/ART."),
        ("CloudWatch", "Service metrics: consumed capacity, throttles, invocations."),
        ("IAM roles", "Least privilege for the function; no long-lived keys in the repo narrative."),
        ("S3", "Object store for artefacts as wired in IaC."),
        ("AWS Budgets / alarms", "Spend and metric guardrails so a runaway campaign aborts."),
        ("Make / RUNBOOK.md", "Human-readable entry points: test, smoke, deploy, run-matrix, teardown."),
        ("YAML configs", "experiment.yaml commits factors; prices.yaml commits dated unit prices."),
    ]
    for name, blurb in tech:
        s.append(P(f"<b>{name}.</b> {blurb}", st["body"]))
    s.append(P(
        "Technologies we are <b>not</b> claiming: Halfmoon runtime, custom FaaS, GCP, Azure, Kubernetes operators for "
        "this artefact, Cost Explorer as validation, or any third-party production account.", st["body"]))

    s.append(P("Appendix G — SQL vs NoSQL teaching monologue (~3 minutes)", st["h1"])); s.append(hr())
    s.append(P(
        "“Let me separate two questions that get tangled. The first question is: should a microservice keep its state in a "
        "relational SQL engine or in a NoSQL store? That is Pantelić’s question. SQL means tables, schemas, joins, and a "
        "query planner. Banks, airlines, payroll, and university registries lean that way because they live on multi-table "
        "consistency. NoSQL means a family of stores that scale by partitioning keys and that prefer simple get/put/query "
        "access paths. Consumer internet, gaming, IoT, and shopping-cart paths often lean that way. Many serious companies "
        "run both. Pantelić compared those families on a machine they operated, under read-heavy, write-heavy and mixed "
        "microservice loads, and reported latency and throughput as relative ordering.", st["script"]))
    s.append(P(
        "“The second question is: once you have already chosen Amazon DynamoDB, how should you name the partition key and "
        "how should you buy capacity, when Lambda is firing Zipfian traffic at you, and when every request spends RCU or "
        "WCU and can be refused? That is Rasool’s question. SQL versus NoSQL is already decided. The meters that appear — "
        "consumed units, throttles, list-price cost per ten thousand operations — are exactly the meters Pantelić’s "
        "self-hosted node could not print. So when I say baseline, I mean workload language and classic scores. When I say "
        "contribution, I mean PK times capacity metering on the live service. If I blur those two questions, I will sound "
        "like I re-ran their bake-off. I did not.”", st["script"]))

    s.append(P("Appendix H — Timeline and evidence map", st["h1"])); s.append(hr())
    s.append(P(
        "Wall clock for the live key-cell round (UTC): 2026-09-20T11:55:38Z → 12:47:42Z. In Asia/Calcutta that is "
        "20 September 2026, 5:25 pm to 6:17 pm IST. Evidence files named in STATUS: results/batches.csv, "
        "results/raw/*.csv.gz (twelve), results/keycell_summary.csv, keycell_round_run.log, "
        "report/generated/hypotheses_keycell_n1.json for exploratory stats. Destroy confirmed: 32 resources, "
        "DESTROY_EXIT=0, no ddbpk* leftovers in eu-west-1.", st["body"]))
    s.append(P(
        "Final-3 gate artefacts are also marked done in STATUS (results/final_{1,2,3}/ + FINAL3_BASELINE.md) for the "
        "alignment-first process; the twelve-cell table above is the key-cell measurement pack to speak in class. Soft "
        "W1/W2 and confirmatory ANOVA remain beyond the floor (see DESIGN_RATIONALE_BEYOND_CA2.md).", st["body"]))
    s.append(P(
        "If a marker asks where to recompute a cost figure: start from consumed units in the raw CSV, multiply by the "
        "dated unit prices in config/prices.yaml, normalise to 10,000 successful operations, exclude storage and transfer. "
        "That is the whole cost story.", st["body"]))

    s.append(P("Appendix I — Common mistakes checklist (read before every meeting)", st["h1"])); s.append(hr())
    B(s, st, [
        "Saying “we compared SQL and NoSQL on AWS”.",
        "Saying “K4 won” or quoting quarantined markdown as evidence.",
        "Saying “ANOVA confirmed” on n=1 key-cells.",
        "Saying “Cost Explorer matched our figures”.",
        "Saying “we loaded one million items on the live round” (it was 100k).",
        "Saying “moto latency is our result”.",
        "Inventing throttle counts because zero feels boring.",
        "Claiming W1/W2 are filled.",
        "Claiming multi-cloud.",
        "Showing personal data (there is none — do not improvise any).",
        "Forgetting destroy-after when asked about ongoing spend.",
        "Treating design-check 10.65% hot-key share as a CloudWatch metric.",
    ])
    s.append(P("End of expanded appendices. Return to section 15’s cheat sheet before the viva.", st["body"]))


    s.append(P("Appendix J — Metric formulas in plain English", st["h1"])); s.append(hr())
    s.append(P(
        "Latency (mean). Add up every successful request’s client-observed time in milliseconds, divide by the count. "
        "p95 / p99. Sort the times; pick the value below which 95% or 99% of requests fell. Pantelić language uses "
        "percentiles; we keep that habit.", st["body"]))
    s.append(P(
        "Throughput (ops/s). Count successful operations in a batch; divide by the wall-clock seconds of that batch. "
        "STATUS W3 sits near 199.92; W4 near 466.5 because burst windows raise the average.", st["body"]))
    s.append(P(
        "Throttle rate. Count throttled requests; divide by attempts (as implemented in the analysis). STATUS shows "
        "0.0 for all twelve key-cells.", st["body"]))
    s.append(P(
        "Consumed RCU / WCU. Prefer API ReturnConsumedCapacity and CloudWatch ConsumedReadCapacityUnits / "
        "ConsumedWriteCapacityUnits. Larger items spend more units. Main factorial holds 1 KB.", st["body"]))
    s.append(P(
        "Cost per 10,000 operations. (sum of list-price charges for consumed units in the window) × (10,000 / successful "
        "ops). Exclude storage and data transfer. prices.yaml date: 2026-09-11. Whole-round request-path sum ≈ $0.251.", st["body"]))
    s.append(P(
        "Why exclude storage? Because the configuration decision under study governs the request path. Storage would "
        "muddy attribution. Say that out loud if a finance-minded professor asks.", st["body"]))

    s.append(P("Appendix K — Objectives mapped to STATUS", st["h1"])); s.append(hr())
    s.append(P(
        "<b>Objective 1 — key design → latency and throttling.</b> W3/W4 cells show p99 differing across K1/K2/K3 "
        "(e.g. K3 often higher). Throttling did not differ — all zero. Partial picture; W1/W2 missing.", st["body"]))
    s.append(P(
        "<b>Objective 2 — capacity mode → throttling and cost.</b> Throttling again zero. Cost differs: see K1 W3 "
        "on-demand 0.003901 vs provisioned 0.002328; see also K2 W3 provisioned 0.010498 vs on-demand 0.003874.", st["body"]))
    s.append(P(
        "<b>Objective 3 — latency-optimal vs cost-optimal.</b> Already in tension on W4 K1 (faster on-demand, cheaper "
        "provisioned). Not a confirmed hypothesis test.", st["body"]))
    s.append(P(
        "<b>Objective 4 — trade-off surface.</b> The twelve-cell table is the current surface. Plot latency, throttle "
        "(flat zero), and cost/10k. Do not draw fake confidence ellipses.", st["body"]))

    s.append(P("Appendix L — What “serverless workloads” means here (and what it does not)", st["h1"])); s.append(hr())
    s.append(P(
        "Means: the client that generates DynamoDB traffic is AWS Lambda. The function scales without you patching a "
        "fleet of load-generator VMs. Billing for the driver is per invocation/duration. Cold starts are controlled by "
        "warm-up so they do not masquerade as table latency.", st["body"]))
    s.append(P(
        "Does not mean: the thesis is about Lambda cold-start optimisation (Liu FaaSLight is cited to justify control, "
        "not as the RQ). Does not mean: Step Functions workflows, multi-function sagas, or Halfmoon-style custom runtimes. "
        "Does not mean: “we have no servers anywhere” — DynamoDB still runs on AWS’s servers; you just do not operate them.", st["body"]))
    s.append(P(
        "Everyday analogy. You hire a temp agency (Lambda) to send parcels into a warehouse (DynamoDB). You study how "
        "the warehouse labels and pricing affect parcel times and refusals. You do not study how long the temp agency "
        "takes to find a bike — you send a few dummy parcels first so the bikes are already there.", st["body"]))

    s.append(P("Appendix M — Ethics and AUP speaking notes", st["h1"])); s.append(hr())
    B(s, st, [
        "No human participants; no consent forms for people.",
        "No personal data; synthetic ids only.",
        "Own AWS account; resources created for the study.",
        "Free-tier-safe / budget-capped load; budgets and alarms in IaC.",
        "Acceptable-use: no attacks on third-party systems.",
        "Destroy-after reduces lingering spend and shared-capacity footprint.",
        "Single-account, single-region external-validity bound stated in the report.",
        "IaC tags avoid student name/ID on live resources (STATUS verified).",
    ])
    s.append(P(
        "If asked “could this overload AWS?”, the answer is: the campaign is rate-bounded, budget-guarded, short-walled, "
        "and destroyed. It is a measurement campaign, not a stress attack.", st["body"]))

    s.append(P("Appendix N — How a third party would reproduce (falsifiable success)", st["h1"])); s.append(hr())
    s.append(P(
        "The master prompt’s success condition is the reproduction checklist. Say it as a recipe.", st["body"]))
    B(s, st, [
        "Clone the artefact; create a Python 3.12 venv; pip install requirements.",
        "make test — moto plumbing must pass.",
        "Configure an AWS profile and region (eu-west-1 to match live).",
        "Follow RUNBOOK.md: seed → deploy → warmup → run-matrix → collect → analyse → teardown.",
        "To mirror the key-cell command: run_matrix.py --blocks 1 --workloads W3,W4 --key-designs K1,K2,K3 --orders 100000.",
        "Recompute cost/10k from prices.yaml × consumed units.",
        "Map every in-text citation to the verified corpus in the master prompt §4.",
        "Do not expect bit-identical milliseconds; expect the same meters and the same protocol.",
    ])

    s.append(P("Appendix O — Literature pack themes (without cataloguing)", st["h1"])); s.append(hr())
    s.append(P(
        "Theme 1 — Persistence benchmarking without meters (Pantelić; Ferreira cloud NoSQL). Theme 2 — Skew and key "
        "placement (Kanellis; Li et al.; Eldeeb Neuroshard; Elhemali hot partitions). Theme 3 — Metered cost models and "
        "cloud OLTP economics (Lei; Haubenschild & Leis; van Renen & Leis; Bodner; Zhou). Theme 4 — Serverless capacity / "
        "FaaS interference (Barnhart Aurora Serverless; Liu FaaSLight; König DBaaS control plane). Theme 5 — Gap: no study "
        "varies key design × capacity mode on live DynamoDB while measuring throttles + RCU/WCU + cost/10k under "
        "Lambda-driven Zipfian workloads. That last sentence is the niche. Memorise it.", st["body"]))
    s.append(P(
        "Vendor docs (not peer-reviewed evidence): AWS capacity mode page; burst and adaptive capacity page; partition-key "
        "sharding best practices. Cite them for mechanisms, not for experimental findings.", st["body"]))

    s.append(P("Appendix P — Longer class script: full five-minute overview", st["h1"])); s.append(hr())
    s.append(P(
        "“Good morning. I am explaining Rasool Basha Durbesula’s MSc Cloud Computing project, student ID 24205478. The "
        "title is Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under "
        "Serverless Workloads. The artefact folder is dynamodb-pk-capacity-eval.", st["script"]))
    s.append(P(
        "“The baseline paper is Pantelić and colleagues, twenty twenty-six, Future Internet, DOI 10.3390/fi18010053. They "
        "benchmarked SQL and NoSQL persistence for microservices under variable workloads on a self-hosted single node. They "
        "report latency and throughput as relative ordering. That paper cannot print RCU, WCU, throttles, or per-operation "
        "price, because those meters do not exist on a self-hosted node. That absence is our gap.", st["script"]))
    s.append(P(
        "“Our research question asks how DynamoDB table configuration — partition-key design crossed with capacity mode — "
        "determines the performance–cost trade-off under serverless workloads. We keep Pantelić’s latency and throughput "
        "language and add the meters. We are not re-running a Postgres-versus-Mongo bake-off.", st["script"]))
    s.append(P(
        "“On design: three keys — K1 simple orderId, K2 customerId plus orderTs, K3 orderId hash shard with ten shards — "
        "crossed with on-demand and provisioned capacity, conditioned by four workloads: read-heavy, write-heavy, mixed, "
        "and burst. Data are synthetic: one million orders and ten thousand customers in the design, Zipfian access, one "
        "kilobyte items in the main factorial, Lambda at about two hundred operations per second, batches of twenty-five, "
        "no personal data.", st["script"]))
    s.append(P(
        "“On live evidence: on the twentieth of September twenty twenty-six in eu-west-1 we measured twelve cells — K1 to "
        "K3, both capacity modes, mixed and burst only — with one hundred thousand seed items and one replicate each. "
        "Throttle rate was zero everywhere. Mixed throughput was about two hundred operations per second; burst averaged "
        "about four hundred sixty-seven. K3 often showed higher p99 and higher list-price cost on mixed traffic. Whole-round "
        "request-path list-price sum was about twenty-five cents. We destroyed thirty-two Terraform resources afterwards.", st["script"]))
    s.append(P(
        "“Honesty: W1 and W2 live cells are still open. Confirmatory ANOVA is not claimed because n equals one. Cost is "
        "list-price, not Cost Explorer. K4 adaptive sharding is off the factorial. Moto tests are plumbing only. Alignment "
        "after the live fold is about ninety-four percent. That is the project.”", st["script"]))

    s.append(P("Appendix Q — Whiteboard drawing instructions", st["h1"])); s.append(hr())
    s.append(P(
        "Box 1: “Pantelić 2026 — SQL vs NoSQL — self-hosted — latency/throughput — NO meters”. Box 2 arrow to Box 3: "
        "“Gap = RCU/WCU/throttle/price missing”. Box 3: “DynamoDB — K1/K2/K3 × on-demand/provisioned — Lambda Zipf — "
        "measure meters”. Under Box 3 draw a mini table of twelve cells with “n=1 W3/W4” stamped across it. Side note: "
        "“1M design / 100k live”. Side note: “destroy-after”. Cross out a sticky that says “K4 won”. Cross out a sticky "
        "that says “moto = AWS”. That board is the whole thesis.", st["body"]))

    s.append(P("Appendix R — FAQ rapid-fire (ten more answers)", st["h1"])); s.append(hr())
    add_qa(s, st, [
        ("What is BatchWriteItem’s relevance?",
         "The seeder and batch paths use groups of 25, which is DynamoDB’s BatchWriteItem limit. It is a design constant, not a mysterious tuning knob."),
        ("Why warm Lambda?",
         "So cold-start delay is not blamed on the table. Liu et al. (2023) motivate that control."),
        ("Why no SDK retries?",
         "Hidden retries would hide throttles and distort open-loop behaviour."),
        ("What is scatter-gather in K3?",
         "A logical read fetches all N shard keys and keeps the newest version. That is the read price of spreading writes."),
        ("Is on-demand always more expensive?",
         "Not in every cell of our n=1 table. Example: K2 provisioned W3 cost/10k 0.010498 exceeds K2 on-demand 0.003874."),
        ("What does INITIAL_EVAL_PASS mean?",
         "STATUS gate flag: the required live initial evaluation pack was accepted for the alignment process. It is not a claim that every soft residual is closed."),
        ("What is FINAL3?",
         "A three-final measurement pack referenced in STATUS as done for the gate. Speak the twelve-cell key-cell table as the primary class evidence."),
        ("Can I quote 10.65% hottest-order share as a result?",
         "No — that is design-check arithmetic on the sampler, not a CloudWatch measurement."),
        ("Why British spelling in the report?",
         "NCI academic English convention in the master prompt. This speakable guide uses mixed plain English for the friend."),
        ("What if the professor only has two minutes?",
         "Read section 1’s one-sentence nervous-student line, then the cheat sheet’s “Do not say” line."),
    ])

    s.append(P("Appendix S — Closing reminder", st["h1"])); s.append(hr())
    s.append(P(
        "You now have the story (sections 1–5), the vocabulary including SQL vs NoSQL (section 6), the dataset (7), the "
        "architecture (8), the modules (9), the AWS map (10), the experiment and STATUS numbers (11), the speaking scripts "
        "(12), the Q&A (13), the limitations (14), the cheat sheet (15), and the appendices for depth. The only numbers "
        "that matter in a viva are the STATUS numbers. Everything else is explanation.", st["body"]))
    s.append(P(
        "Last line to practise: <i>“They ranked SQL and NoSQL on a node without meters. We metered partition-key design "
        "times capacity mode on live DynamoDB under Lambda-driven Zipfian load — twelve key-cells measured, throttles "
        "zero, K3 not free, stack destroyed, soft residuals named.”</i>", st["body"]))



    s.append(P("Appendix T — Worked example: explaining one STATUS row out loud", st["h1"])); s.append(hr())
    s.append(P(
        "Take K3-on_demand-W3. Say: “This cell is the write-sharded key under pay-per-request billing while Lambda sent a "
        "fifty-fifty mix at about two hundred operations per second. The ninety-ninth percentile client latency was ten "
        "point three two zero milliseconds. Throughput was one hundred ninety-nine point nine one nine successful operations "
        "per second. No requests were throttled. The list-price cost per ten thousand successful operations was zero point "
        "zero zero seven zero six two US dollars. Compared with K1 on-demand on the same workload, p99 and cost are both "
        "higher. That matches the intuition that scatter-gather reads are not free. This is one replicate. I am not "
        "calling it a population law.”", st["script"]))
    s.append(P(
        "Now take K1-provisioned-W4. Say: “Same simple key, but reserved capacity, under the burst profile. Throughput "
        "averaged about four hundred sixty-six point five operations per second. p99 rose to ten point two three two "
        "milliseconds, while cost per ten thousand fell to zero point zero zero zero nine nine eight — among the cheapest "
        "cells. So in this slice the cheaper configuration is not the fastest. That is exactly the tension objective three "
        "was written to detect. Still n equals one; still not ANOVA.”", st["script"]))
    s.append(P("Appendix U — What to put on a single PowerPoint slide", st["h1"])); s.append(hr())
    B(s, st, [
        "Title + student name/ID.",
        "One line: baseline Pantelić SQL/NoSQL self-hosted → gap = no meters.",
        "One line: our RQ = PK × capacity on DynamoDB under Lambda Zipf.",
        "Tiny diagram: K1/K2/K3 × on-demand/provisioned × W1–W4 (circle W3/W4 live).",
        "Dataset line: 1M/10k design; 100k live; no PII; Zipf 90/10.",
        "STATUS headline: 12 cells, throttle 0, K3 not free, ~$0.251, destroyed.",
        "Do-not-say box: moto≠AWS; K4≠won; no confirmatory ANOVA; not SQL rematch.",
    ])
    s.append(P("Appendix V — Friend briefing card (30 seconds)", st["h1"])); s.append(hr())
    s.append(P(
        "“Rasool measures how DynamoDB key design and capacity mode affect speed, refusals, and list-price cost when Lambda "
        "sends unfair Zipfian traffic. The baseline SQL/NoSQL paper could not see those meters. He has twelve live cells for "
        "mixed and burst, zero throttles, K3 often dearer, stack destroyed, and he will not pretend ANOVA is done.”", st["script"]))

    return s


def build_md() -> str:
    return """# Rasool Explanation Guide (speakable)

**Student:** Rasool Basha Durbesula (24205478)
**Title:** Partition-Key Design and Capacity Mode in Amazon DynamoDB: An Empirical Performance-Cost Evaluation under Serverless Workloads
**Artefact:** `dynamodb-pk-capacity-eval/`
**Baseline:** Pantelić et al. (2026), Future Internet 18(1):53, DOI 10.3390/fi18010053

Companion to `Rasool_Explanation_Guide.pdf`. Numbers from STATUS / live key-cell results only.

## One-page summary
Rasool measures how DynamoDB **partition-key design** and **capacity mode** jointly affect latency, throttling, consumed RCU/WCU, and list-price cost per 10k ops under Lambda-driven Zipfian workloads. Baseline Pantelić et al. (2026) compared SQL vs NoSQL on a self-hosted node (no meters). This thesis is **not** a SQL/NoSQL rematch.

## Live evidence (STATUS)
12 cells: K1–K3 × on-demand/provisioned × W3/W4, n=1, eu-west-1, 100k seed, 20 Sep 2026, throttle_rate=0.0, ~$0.251 list-price sum, stack destroyed. W1/W2 and confirmatory ANOVA are soft residuals. K4 off-factorial.

## Dataset (design)
1,000,000 synthetic orders / 10,000 customers; Zipfian ~90% on ~10%; item sizes 1/8/32 KB; workloads read-heavy (~95% reads), write-heavy (~70% writes), mixed 50/50, burst; ~200 ops/s Lambda; batches of 25; no personal data.

## Cheat sheet
See PDF section 15.
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    st = styles()
    pdf_path = OUT_DIR / "Rasool_Explanation_Guide.pdf"
    md_path = OUT_DIR / "Rasool_Explanation_Guide.md"
    md_path.write_text(build_md(), encoding="utf-8")
    doc = make_doc(pdf_path, "Rasool Explanation Guide")
    doc.build(build_story(st), onFirstPage=_footer, onLaterPages=_footer)
    print(f"Wrote {pdf_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
