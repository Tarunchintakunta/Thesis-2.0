#!/usr/bin/env python3
"""Generate Vikas_Explanation_Guide.pdf + .md (~40-45 pages)."""
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
    "Core concepts with everyday examples (idempotency, retries, Lambda, DynamoDB)",
    "Dataset / synthetic traffic and what the code does",
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
        "title": "An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB",
        "student": "Vikas Reddy Amanagantti",
        "student_id": "X25178849",
        "artefact": "vikas-thesis/lambda-idempotency-eval/",
        "baseline": "Qi et al. Halfmoon (TOCS / arXiv), DOI 10.1145/3725985",
    })
    toc_page(s, st, SECTIONS)

    # 1
    s.append(P("1. The project in one page", st["h1"])); s.append(hr())
    s.append(P(
        "Vikas Reddy Amanagantti (student ID X25178849) is measuring a very practical fear: when AWS Lambda is retried, "
        "does your DynamoDB write happen twice? Managed Lambda gives <b>at-least-once</b> delivery for many invocation "
        "modes. That means the same logical request can run more than once. If your function writes to DynamoDB with a "
        "plain PutItem, the second run can overwrite or duplicate business state. The thesis asks how much three "
        "<b>application-level</b> write strategies reduce those duplicate mutations — and what they cost in latency and "
        "consumed capacity — on <b>stock</b> AWS Lambda and DynamoDB.", st["body"]))
    s.append(P(
        "The three paths. <b>P1 Plain Put</b> — unconditional PutItem (the “no guard” control). <b>P2 Conditional Put</b> — "
        "PutItem with <font face='Courier'>attribute_not_exists(pk)</font> so a second insert fails the condition. "
        "<b>P3 Idempotency-key</b> — Powertools-style pattern: claim an <font face='Courier'>IDEMP#&lt;request_id&gt;</font> "
        "token, write the business item, mark the token COMPLETED; a redelivery replays or refuses. <b>P4 TransactWrite</b> "
        "is quarantined / out of scope for CA2 (ASSUMPTIONS A12; experiment.yaml = P1–P3 only). Older markdown that claimed "
        "P4 wins is <b>NON-AUTHORITATIVE</b>.", st["body"]))
    s.append(P(
        "The baseline is Qi et al. (2025) Halfmoon (ACM TOCS, DOI 10.1145/3725985; SOSP’23 precursor). Halfmoon gets "
        "exactly-once effects with <b>asymmetric logging on a custom serverless runtime</b>. Vikas does <b>not</b> install "
        "Halfmoon. He shares the <b>correctness idea</b> (no duplicate mutation after retry) and measures what application "
        "guards achieve on unmodified managed AWS.", st["body"]))
    s.append(P(
        "<b>Live evidence (STATUS, 21 September 2026).</b> Full campaign in eu-west-1: N=1000 requests × paths {P1,P2,P3} × "
        "multiplicities {1,2,5} = 9000 requests / 24000 deliveries; 0 driver errors; seed 25178849; workers 6. Streams ground "
        "truth. Pre-registered E1/E2/E3 all <b>supported</b>. Headline: P1 dup_rate = 1.0 at mult 2 and 5; P2/P3 dup_rate = 0.0; "
        "P3 capacity = P2 + 2 WCU/request. Sensitivity <font face='Courier'>p3_between</font> (crash between business write and "
        "COMPLETED mark) shows P3 dup_rate = 1.0 — the crash window. Stack destroyed (8 resources). Moto results are plumbing "
        "only — never cite moto latency/capacity as AWS.", st["body"]))
    s.append(P(
        "Nervous-student sentence: <i>“I injected known retries into Lambda writing to DynamoDB three ways; plain put always "
        "duplicated on retry; conditional put and idempotency keys stopped duplicates in the main campaign but the key pattern "
        "still fails if you crash between the two writes; I did not run Halfmoon; moto is not AWS.”</i>", st["body"]))

    # 2
    s.append(PageBreak())
    s.append(P("2. Problem statement and a real-life example", st["h1"])); s.append(hr())
    s.append(P("2.1 The problem", st["h2"]))
    s.append(P(
        "Academic version. Serverless platforms often provide at-least-once execution. Retries after timeouts can re-apply "
        "side effects. Runtime research (Halfmoon, Boki, CausalMesh, …) solves this by changing the runtime. Managed Lambda "
        "users cannot swap the runtime. They must use application-level controls. The measured costs and residual failure "
        "modes of the three common DynamoDB write guards under a <b>known</b> injected retry schedule were not established.", st["body"]))
    s.append(P(
        "Kitchen version. You tell a waiter “put this order on table 7”. The waiter sometimes gets interrupted after writing "
        "the order but before telling you “done”, so the manager sends the waiter again. If the waiter writes again blindly, "
        "table 7 gets two identical orders (or a overwritten note). You can (P1) keep writing blindly, (P2) only write if "
        "table 7 is empty, or (P3) stamp a ticket saying “request 42 already handled” before and after writing. Halfmoon is "
        "like rebuilding the whole restaurant with a special logging kitchen. Vikas stays in the normal restaurant and times "
        "the three waiter habits.", st["body"]))
    s.append(P("2.2 Real-life story you can tell", st["h2"]))
    s.append(P(
        "Imagine a payments microservice on Lambda. A client submits <font face='Courier'>request_id = pay-991</font>. The "
        "function writes a ledger item <font face='Courier'>REQ#pay-991</font>. The function then times out — on purpose in "
        "this experiment, after the write committed — so the driver thinks it failed and delivers the same request again "
        "(multiplicity 2 or 5). Under P1, every delivery writes again: duplicate mutation rate 1.0. Under P2, the second "
        "Put sees the primary key already exists and fails the condition: no second mutation, but the failed check still "
        "costs capacity. Under P3, the idempotency item blocks or replays. Unless you crash <b>between</b> the business "
        "write and marking COMPLETED — then sensitivity shows P3 can look like P1 (dup_rate 1.0).", st["body"]))
    s.append(P("2.3 What is not the problem", st["h2"]))
    B(s, st, [
        "Not reimplementing Halfmoon / Boki / custom FaaS.",
        "Not claiming moto numbers as live AWS latency or capacity.",
        "Not P4 TransactWrite as a CA2 result (quarantined).",
        "Not multi-item distributed transactions as primary evidence.",
        "Not GCP or Azure.",
        "Not real customer payment data — synthetic payloads only.",
    ])

    # 3
    s.append(PageBreak())
    s.append(P("3. Why it matters", st["h1"])); s.append(hr())
    s.append(P(
        "It matters because most teams on AWS Lambda cannot install Halfmoon. Surveys and AWS docs put idempotency on the "
        "application. Choosing plain put versus conditional put versus an idempotency key changes both correctness and the "
        "bill (failed condition checks still consume capacity; P3 does extra writes).", st["body"]))
    s.append(P(
        "It matters because retries are not rare folklore. Timeouts, async retries, and operator replays happen. Without a "
        "<b>known</b> injected delivery count, you cannot compute duplicate-mutation rate against ground truth. Vikas’s "
        "driver logs intended deliveries before invoke and forces after-commit timeout — so the denominator is known.", st["body"]))
    s.append(P(
        "It matters methodologically because Wen et al. (2025) show huge serverless performance variance and warn that many "
        "papers under-replicate. This project pilots, sizes N, then runs the full campaign with confidence intervals and "
        "Holm–Bonferroni corrections.", st["body"]))
    s.append(P(
        "It matters for honesty in the classroom. A friend who says “we achieved exactly-once like Halfmoon” fails. A friend "
        "who says “application guards cut duplicates to zero in the main campaign, P3 costs about two extra WCU per request "
        "versus P2, and P3 still fails in the between-writes crash sensitivity” passes.", st["body"]))

    # 4
    s.append(PageBreak())
    s.append(P("4. The baseline paper, the gap, and this thesis problem", st["h1"])); s.append(hr())
    s.append(P("4.1 Bibliographic facts", st["h2"]))
    s.append(P(
        "Qi, S., Feng, H., Liu, X. and Jin, X. (2025) Efficient fault tolerance for stateful serverless computing with "
        "asymmetric logging. <i>ACM Transactions on Computer Systems</i>, 43(1–2). doi: <b>10.1145/3725985</b>. "
        "Conference precursor: Qi, Liu and Jin (2023) Halfmoon, SOSP ’23, doi:10.1145/3600006.3613154. "
        "PDF in <font face='Courier'>vikas-thesis/baseline_papers/</font>.", st["body"]))
    s.append(P("4.2 Problem / solution / gap", st["h2"]))
    s.append(P(
        "<b>Problem Halfmoon attacks:</b> stateful serverless needs fault tolerance without duplicate external effects when "
        "functions retry. <b>Solution:</b> asymmetric logging on a <b>custom</b> runtime that intercepts state changes. "
        "<b>Gap for practitioners on managed Lambda:</b> you cannot swap AWS’s runtime for Halfmoon without leaving managed "
        "FaaS. The shared correctness criterion remains: <b>absence of duplicate mutation after retry</b>. The mechanism "
        "differs. This thesis measures application-level DynamoDB controls under known injected retries, with latency and "
        "consumed capacity — without claiming Halfmoon’s logging-overhead numbers.", st["body"]))
    s.append(P("4.3 Thesis problem from the gap", st["h2"]))
    s.append(P(
        "By how much do a conditional write and an idempotency-key write reduce duplicate state mutation, relative to a "
        "plain write, when a Lambda function is retried under injected timeouts — and what do they cost in end-to-end "
        "latency and consumed capacity?", st["body"]))

    # 5
    s.append(PageBreak())
    s.append(P("5. Research question and solution approach", st["h1"])); s.append(hr())
    s.append(P(
        "<b>RQ</b> (from master prompt): By how much do a conditional write and an idempotency-key write reduce duplicate "
        "state mutation, relative to a plain write, when an AWS Lambda function is retried under injected timeouts — and "
        "what do they cost in end-to-end latency and consumed capacity?", st["body"]))
    s.append(P("Objectives:", st["body"]))
    B(s, st, [
        "Quantify duplicate-mutation rate for P1, P2, P3 under multiplicities {1, 2, 5}.",
        "Quantify mean/p95 latency and consumed capacity per request for each path.",
        "Measure control behaviour: conditional-check-failure rate; successful-retry rate.",
        "Place each path on the correctness–cost surface; discuss against Halfmoon’s criterion (not Halfmoon’s overhead numbers).",
    ])
    s.append(P("Pre-registered expectations (STATUS: all supported on live campaign):", st["body"]))
    B(s, st, [
        "E1: Plain write duplicates on a majority of injected retries (after-commit timeout case).",
        "E2: P2 and P3 reduce that rate by >90% relative to P1.",
        "E3: Idempotency-key path costs more consumed capacity than conditional path.",
    ])
    s.append(P("Approach:", st["body"]))
    s.append(P(
        "One Lambda, one DynamoDB table (on-demand), path selector P1|P2|P3. Driver schedules known "
        "<font face='Courier'>(request_id, delivery_count)</font>. After-commit timeout injection on non-final deliveries. "
        "Streams as mutation ground truth. Pilot sized N=1000. Full factorial live campaign. Analysis with Wilson/cluster "
        "CIs, z-tests, χ², Mann–Whitney, Holm–Bonferroni. Terraform destroy-after.", st["body"]))

    # 6 concepts
    s.append(PageBreak())
    s.append(P("6. Core concepts with everyday examples", st["h1"])); s.append(hr())
    s.append(P("6.1 Idempotency", st["h2"]))
    s.append(P(
        "A operation is idempotent if doing it once or doing it several times leaves the same final effect. Pressing "
        "“pay” twice should not charge twice. Analogy: a light switch labelled “ON” that you can push repeatedly — the "
        "light stays on; pushing again does not brighten it further. P1 is not idempotent for state. P2 and P3 aim to be.", st["body"]))
    s.append(P("6.2 At-least-once delivery", st["h2"]))
    s.append(P(
        "The platform promises the message/function will run <b>at least</b> once, not <b>exactly</b> once. Duplicates are "
        "allowed. Analogy: a postal service that may deliver two copies of the same letter if the first acknowledgement "
        "was lost. Your job is to make two copies harmless.", st["body"]))
    s.append(P("6.3 Retries and injected duplicates", st["h2"]))
    s.append(P(
        "A retry is a second (or fifth) delivery of the same logical request. This experiment <b>injects</b> retries with "
        "known counts {1,2,5}. It does not guess retries from CloudWatch. After-commit timeout: write succeeds, then the "
        "function hangs past timeout so the caller retries even though state changed.", st["body"]))
    s.append(P("6.4 Conditional writes", st["h2"]))
    s.append(P(
        "DynamoDB ConditionExpression can require <font face='Courier'>attribute_not_exists(pk)</font>. First write "
        "succeeds; second fails with ConditionalCheckFailed. Failed checks still consume capacity (documented rule / "
        "reported units). Analogy: a hotel receptionist who only creates a booking if the room slot is empty.", st["body"]))
    s.append(P("6.5 Idempotency keys (P3)", st["h2"]))
    s.append(P(
        "Store a key <font face='Courier'>IDEMP#&lt;request_id&gt;</font> as IN_PROGRESS, perform the business write, mark "
        "COMPLETED with a stored result. Redelivery sees the key and returns the stored result (REPLAYED) or waits/refuses "
        "while IN_PROGRESS. Analogy: a stamp on a form saying “already processed — here is the previous answer”. Risk: if "
        "you crash after the business write but before COMPLETED, the stamp can expire and a retry redoes the work "
        "(sensitivity <font face='Courier'>p3_between</font>: dup_rate 1.0).", st["body"]))
    s.append(P("6.6 AWS Lambda and Amazon DynamoDB (roles here)", st["h2"]))
    s.append(P(
        "Lambda runs the function. DynamoDB holds business items and idempotency items. Streams provide ordered mutation "
        "records used as ground truth. On-demand capacity. Single region eu-west-1 for live runs. Analogy: Lambda is the "
        "waiter; DynamoDB is the order book; Streams is the CCTV that shows how many times the book was written.", st["body"]))
    s.append(P("6.7 moto — say this clearly", st["h2"]))
    s.append(P(
        "moto emulates AWS in unit tests. STATUS: moto validates plumbing (P1 100% dups; P2/P3 0% at mult 2 and 5 in the "
        "functional check). Latency/capacity on moto are <b>not</b> AWS measurements and must not answer the RQ.", st["body"]))
    s.append(P("6.8 Halfmoon versus this thesis (one table)", st["h2"]))
    s.append(simple_table([
        [P("<b>Lens</b>", st["cheat"]), P("<b>Halfmoon (Qi et al.)</b>", st["cheat"]), P("<b>This thesis</b>", st["cheat"])],
        [P("Goal idea", st["cheat"]), P("No duplicate mutation after retry", st["cheat"]), P("Same criterion", st["cheat"])],
        [P("Mechanism", st["cheat"]), P("Custom runtime + asymmetric logging", st["cheat"]), P("App-level P1/P2/P3 on stock AWS", st["cheat"])],
        [P("Platform", st["cheat"]), P("Modified serverless runtime", st["cheat"]), P("Managed Lambda + DynamoDB", st["cheat"])],
        [P("What we claim", st["cheat"]), P("Their paper’s results", st["cheat"]), P("Our measured dup/latency/capacity only", st["cheat"])],
    ], col_widths=[100, 200, 200]))

    # continue

    # 7
    s.append(PageBreak())
    s.append(P("7. Dataset / synthetic traffic and what the code does", st["h1"])); s.append(hr())
    s.append(P(
        "There is no million-row customer dump here. The “dataset” is a schedule of synthetic requests: each has a "
        "<font face='Courier'>request_id</font>, a path (P1/P2/P3), a multiplicity (1, 2, or 5), and a small JSON payload "
        "from <font face='Courier'>data/payload_template.json</font>. No personal data. Seed <b>25178849</b> (the student "
        "ID digits) makes request ids reproducible.", st["body"]))
    s.append(P("What the code does, step by step:", st["body"]))
    B(s, st, [
        "schedule.py builds the list of deliveries (9000 requests → 24000 deliveries in the full campaign).",
        "run.py invokes Lambda (or a local backend) with workers (live used 6; account ConcurrentExecutions=10 Free-Tier guard).",
        "handler.py selects path, optionally sleeps past timeout after commit on non-final deliveries.",
        "paths.py performs P1/P2/P3 against DynamoDB with ReturnConsumedCapacity=TOTAL.",
        "streams.py reads DynamoDB Streams to count business mutations per request_id.",
        "analyse.py computes dup rates, CIs, tests, figures; writes results/live/summary.md.",
    ])
    s.append(P("Speaking script — dataset (~60s):", st["h2"]))
    s.append(P(
        "“Our data are synthetic request schedules, not personal records. Each request has an id derived from a fixed seed "
        "25178849, a write path, and a planned delivery count of one, two, or five. The full live campaign had nine thousand "
        "requests and twenty-four thousand deliveries. Payloads are small template JSON with no names or cards. Ground truth "
        "for mutations comes from DynamoDB Streams, not from guessing.”", st["script"]))

    # 8
    s.append(PageBreak())
    s.append(P("8. Architecture and end-to-end flow", st["h1"])); s.append(hr())
    s.append(P(
        "Driver → AWS Lambda (path P1|P2|P3) → DynamoDB table (on-demand) → response metadata (ConsumedCapacity) + "
        "CloudWatch. Parallel: DynamoDB Streams → ground-truth mutation counts. Ground-truth log fields include request_id, "
        "path, delivery_i, timeout_injected?, write_outcome, capacity.", st["body"]))
    B(s, st, [
        "make deploy — build zip, terraform apply (table, function, IAM, logs, alarms, budget).",
        "make pilot — small live run; pilot_size chooses N (STATUS: N=1000; binding P2 latency req 392).",
        "make campaign WORKERS=6 — full factorial.",
        "Sensitivity run: P3 × {2,5} with p3_between injection (1400 deliveries).",
        "analyse → results/live/summary.md + figures.",
        "terraform destroy — 8 resources; verify absent.",
    ])

    # 9
    s.append(PageBreak())
    s.append(P("9. Implementation modules and short code snippets", st["h1"])); s.append(hr())
    s.append(simple_table([
        [P("<b>Path</b>", st["cheat"]), P("<b>Job</b>", st["cheat"])],
        [P("src/lambda_fn/handler.py", st["cheat"]), P("Event, injection, structured log", st["cheat"])],
        [P("src/lambda_fn/paths.py", st["cheat"]), P("P1 / P2 / P3 write implementations", st["cheat"])],
        [P("src/driver/schedule.py", st["cheat"]), P("Known delivery schedule", st["cheat"])],
        [P("src/driver/run.py", st["cheat"]), P("Invoke Lambda / local; workers; budget stop", st["cheat"])],
        [P("src/driver/streams.py", st["cheat"]), P("Streams ground truth", st["cheat"])],
        [P("analysis/analyse.py", st["cheat"]), P("CIs, tests, E1–E3, figures", st["cheat"])],
        [P("infra/", st["cheat"]), P("Terraform stack", st["cheat"])],
        [P("config/experiment.yaml", st["cheat"]), P("P1–P3 only; pinned design", st["cheat"])],
        [P("tests/", st["cheat"]), P("63 pytest tests (STATUS claim)", st["cheat"])],
    ], col_widths=[200, 300]))
    s.append(P("Illustrative snippets from paths.py:", st["h2"]))
    s.append(code_block(
        "def p1(client, table, request_id, payload, exec_id, delivery, **_):\n"
        "    item = business_item(request_id, payload, exec_id, delivery)\n"
        "    resp = client.put_item(TableName=table, Item=typed(item),\n"
        "                           ReturnConsumedCapacity=\"TOTAL\")\n"
        "    return _result(\"APPLIED\", wcu=_cc(resp), calls=1, business_writes=1)\n"
        "\n"
        "def p2(...):\n"
        "    # PutItem with ConditionExpression=\"attribute_not_exists(pk)\"\n"
        "    # on ConditionalCheckFailed → outcome SUPPRESSED (still billed)\n"
        "\n"
        "def p3(...):\n"
        "    # claim IDEMP#<id> IN_PROGRESS → business Put → mark COMPLETED\n"
        "    # optional between= crash window for sensitivity",
        st))
    s.append(P(
        "Say while showing: “exec_id changes every delivery, so a repeated P1 write always changes the item. That is how "
        "we detect duplicate mutation.”", st["body"]))

    # 10
    s.append(PageBreak())
    s.append(P("10. AWS services used (what / why / analogy)", st["h1"])); s.append(hr())
    s.append(P("AWS-only. Not GCP. Not Azure.", st["body"]))
    s.append(simple_table([
        [P("<b>Service</b>", st["cheat"]), P("<b>Why</b>", st["cheat"]), P("<b>Analogy</b>", st["cheat"])],
        [P("AWS Lambda", st["cheat"]), P("Runs the three write paths; timeout injection", st["cheat"]), P("The waiter who may be sent twice", st["cheat"])],
        [P("Amazon DynamoDB", st["cheat"]), P("Business + idempotency items; conditions", st["cheat"]), P("The order book", st["cheat"])],
        [P("DynamoDB Streams", st["cheat"]), P("Mutation ground truth", st["cheat"]), P("CCTV over the order book", st["cheat"])],
        [P("IAM", st["cheat"]), P("Least privilege for function", st["cheat"]), P("Door badge", st["cheat"])],
        [P("CloudWatch", st["cheat"]), P("Invocations cross-check; logs", st["cheat"]), P("Dashboard", st["cheat"])],
        [P("Budgets / alarms", st["cheat"]), P("Spend guard", st["cheat"]), P("Prepaid meter", st["cheat"])],
        [P("Terraform", st["cheat"]), P("Apply/destroy reproducible stack", st["cheat"]), P("Recipe + washing up", st["cheat"])],
    ], col_widths=[120, 200, 180]))

    # 11
    s.append(PageBreak())
    s.append(P("11. Experiment design and metrics", st["h1"])); s.append(hr())
    s.append(P(
        "IV: path ∈ {P1,P2,P3}; multiplicity ∈ {1,2,5}. DV primary: duplicate-mutation rate = (# injected retries that cause "
        "a second state change) / (# injected retries). Secondary: CCF rate; successful-retry rate; latency mean/p95; "
        "consumed capacity. Pilot → N=1000. Alpha 0.05, Holm–Bonferroni.", st["body"]))
    s.append(P("Live campaign headline cells (STATUS / summary.md):", st["h2"]))
    s.append(simple_table([
        [P("<b>Path</b>", st["cheat"]), P("<b>mult</b>", st["cheat"]), P("<b>dup_rate</b>", st["cheat"]),
         P("<b>capacity_mean</b>", st["cheat"]), P("<b>notes</b>", st["cheat"])],
        [P("P1", st["cheat"]), P("2", st["cheat"]), P("1.0", st["cheat"]), P("2", st["cheat"]), P("every retry mutates", st["cheat"])],
        [P("P1", st["cheat"]), P("5", st["cheat"]), P("1.0", st["cheat"]), P("5", st["cheat"]), P("every retry mutates", st["cheat"])],
        [P("P2", st["cheat"]), P("2", st["cheat"]), P("0.0", st["cheat"]), P("2", st["cheat"]), P("CCF suppresses", st["cheat"])],
        [P("P2", st["cheat"]), P("5", st["cheat"]), P("0.0", st["cheat"]), P("5", st["cheat"]), P("CCF suppresses", st["cheat"])],
        [P("P3", st["cheat"]), P("2", st["cheat"]), P("0.0", st["cheat"]), P("4", st["cheat"]), P("key pattern; +2 WCU vs P2", st["cheat"])],
        [P("P3", st["cheat"]), P("5", st["cheat"]), P("0.0", st["cheat"]), P("7", st["cheat"]), P("key pattern; +2 WCU vs P2", st["cheat"])],
    ], col_widths=[60, 50, 70, 90, 200]))
    s.append(P("E1/E2/E3 all supported. Sensitivity p3_between: P3 dup_rate=1.0 at mult 2 and 5 (400 req / 1400 deliveries).", st["body"]))
    s.append(P(
        "Latency note: campaign means include cold starts (cold_final_share often ~0.8 on retry cells). Warm means are "
        "much lower (~200 ms). Quote cold share if discussing latency. Do not pretend moto latency is AWS.", st["body"]))

    # 12
    s.append(PageBreak())
    s.append(P("12. Class speaking scripts", st["h1"])); s.append(hr())
    s.append(P("12.1 Dataset / traffic script", st["h2"]))
    s.append(P(
        "“Data are synthetic request schedules with seed 25178849. Nine thousand requests, twenty-four thousand deliveries "
        "in the live campaign. No personal data. Streams tell us how many times each business item mutated.”", st["script"]))
    s.append(P("12.2 Implementation progress script", st["h2"]))
    s.append(P(
        "“Artefact complete for P1–P3. Moto functional tests pass but are not the RQ answer. Live pilot on 19 September sized "
        "N to 1000. Live full campaign on 21 September in eu-west-1 supported E1, E2, and E3. Sensitivity showed P3’s "
        "between-writes crash window. Stack destroyed — eight resources. P4 is out of scope.”", st["script"]))
    s.append(P("12.3 Technologies script", st["h2"]))
    s.append(P(
        "“Python on Lambda, boto3 to DynamoDB, DynamoDB Streams for ground truth, Terraform for IaC, CloudWatch for "
        "cross-checks, pytest and moto for plumbing. Not Halfmoon. Not GCP. Not Azure.”", st["script"]))
    s.append(P("12.4 Baseline gap script", st["h2"]))
    s.append(P(
        "“Qi et al. Halfmoon get exactly-once style effects with a custom runtime and asymmetric logging. We keep that "
        "correctness idea but stay on managed Lambda and DynamoDB and measure three application write paths under known "
        "injected retries.”", st["script"]))
    s.append(P("12.5 Results script", st["h2"]))
    s.append(P(
        "“Plain put duplicated on every injected retry. Conditional put and the idempotency-key path dropped duplicate rate "
        "to zero in the main campaign, more than a ninety percent relative reduction. The idempotency-key path cost about "
        "two extra write capacity units per request versus conditional put. When we crashed P3 between the business write "
        "and marking the key complete, duplicates came back at rate one — so the key pattern is not magic.”", st["script"]))

    # 13
    s.append(PageBreak())
    s.append(P("13. Professor Q&A — exact answers", st["h1"])); s.append(hr())
    add_qa(s, st, [
        ("What is your research question?",
         "By how much do conditional writes and idempotency-key writes reduce duplicate mutations versus plain writes under injected Lambda retries, and what do they cost in latency and consumed capacity?"),
        ("What is Halfmoon and why is it your baseline?",
         "Qi et al. (2025) TOCS system for fault-tolerant stateful serverless via asymmetric logging on a custom runtime. We share the no-duplicate-mutation criterion; we do not install their runtime."),
        ("Did you implement Halfmoon?",
         "No. Unmodified managed Lambda and DynamoDB only."),
        ("What are P1, P2, P3?",
         "P1 plain PutItem; P2 PutItem with attribute_not_exists; P3 idempotency-key claim / business write / COMPLETED pattern."),
        ("What about P4 / TransactWrite?",
         "Out of scope for CA2. Quarantined. experiment.yaml is P1–P3 only. Do not cite the old markdown that claimed P4 wins."),
        ("How do you know how many retries happened?",
         "The driver schedules intended deliveries before invoke. Retries are injected, not inferred."),
        ("What is after-commit timeout?",
         "The function writes successfully, then hangs past Lambda timeout so the caller retries even though state already changed."),
        ("What were the live headline rates?",
         "P1 dup_rate 1.0 at multiplicity 2 and 5; P2 and P3 dup_rate 0.0; E1–E3 supported."),
        ("Does P3 always work?",
         "In the main campaign yes for the after-commit-on-final-path pattern; sensitivity p3_between shows dup_rate 1.0 if you crash between business write and COMPLETED."),
        ("What does E3 say about cost?",
         "P3 consumed about two more WCU per request than P2; supported on live data."),
        ("Is moto your AWS evidence?",
         "No. Moto is plumbing only. Primary RQ answer is the live campaign."),
        ("How big was the campaign?",
         "N=1000 × 3 paths × 3 multiplicities = 9000 requests / 24000 deliveries; 0 driver errors; eu-west-1; 21 September 2026."),
        ("How did you choose N?",
         "Live pilot on 19 September; pilot rule chose N=1000 (binding: P2 latency requirement 392)."),
        ("Still running in AWS?",
         "No. Terraform destroy removed 8 resources after the fold."),
        ("Why Streams?",
         "Independent ground truth for how many times the business item mutated, cross-checked with self-report and CloudWatch."),
        ("Exactly-once?",
         "We never claim exactly-once for P1. For P2/P3 we report measured duplicate-mutation reduction on stock AWS — not Halfmoon’s formal runtime guarantees."),
        ("GCP or Azure?",
         "Not used. AWS-only artefact."),
        ("Personal data?",
         "None. Synthetic payloads and request ids."),
    ])

    # 14
    s.append(PageBreak())
    s.append(P("14. Honest STATUS and limitations", st["h1"])); s.append(hr())
    B(s, st, [
        "CA2 alignment formal: 100/100 with live full campaign complete (STATUS).",
        "INITIAL_EVAL_PASS=yes. Final-3 separate series not started (campaign is the evidence pack).",
        "Moto ≠ AWS latency/capacity.",
        "P4 quarantined.",
        "Cold-start share is high on some retry cells — discuss warm vs overall latency honestly.",
        "Single region, one account, on-demand, single-item primary paths.",
        "Injected timeout is clean; real failures may be messier (threats to validity).",
        "vikas_final_report.md P4 narrative is NON-AUTHORITATIVE.",
    ])

    # 15
    s.append(PageBreak())
    s.append(P("15. One-page cheat sheet", st["h1"])); s.append(hr())
    s.append(P(
        "<b>Student / ID:</b> Vikas Reddy Amanagantti / X25178849<br/>"
        "<b>Title:</b> Application-level idempotency strategies for retry correctness on Lambda + DynamoDB<br/>"
        "<b>Artefact:</b> lambda-idempotency-eval/<br/>"
        "<b>Baseline:</b> Qi et al. Halfmoon TOCS DOI 10.1145/3725985 (custom runtime)<br/>"
        "<b>RQ:</b> How much do P2/P3 cut duplicate mutations vs P1 under injected retries, at what latency/capacity cost?<br/>"
        "<b>Paths:</b> P1 plain put · P2 conditional put · P3 idempotency-key · (P4 out of scope)<br/>"
        "<b>Live:</b> 21 Sep 2026 eu-west-1 · N=1000×3×3 · 24000 deliveries · E1–E3 supported<br/>"
        "<b>Headline:</b> P1 dup=1.0; P2/P3 dup=0.0; P3 ≈ P2+2 WCU/request; p3_between dup=1.0<br/>"
        "<b>Do not say:</b> we ran Halfmoon · moto=AWS · P4 won · exactly-once like Halfmoon runtime<br/>"
        "<b>Destroy:</b> yes (8 resources)",
        st["cheat"]))

    # expansions for page count
    s.append(PageBreak())
    s.append(P("Appendix A — Expectation decisions in plain words", st["h1"])); s.append(hr())
    s.append(P(
        "E1 supported: P1 duplicate rate at multiplicity 2 and 5 has Wilson/cluster lower bounds above 0.5 (actually 1.0). "
        "E2 supported: relative reduction of P2 and P3 versus P1 has lower bound above 0.90 (actually 100% reduction in "
        "main campaign). E3 supported: P3−P2 capacity per request CI above 0 (difference 2 WCU) with Holm significance.", st["body"]))
    s.append(PageBreak())
    s.append(P("Appendix B — Practice dialogue", st["h1"])); s.append(hr())
    for who, line in [
        ("Professor", "So you built Halfmoon?"),
        ("Friend", "No. Halfmoon needs a custom runtime. We measured three application write paths on managed Lambda and DynamoDB."),
        ("Professor", "Did conditional put and idempotency keys work?"),
        ("Friend", "In the main live campaign both cut duplicate rate from 1.0 to 0.0 versus plain put. The idempotency-key path cost about two extra WCU per request. A sensitivity crash between P3’s two writes brought duplicates back."),
        ("Professor", "Are moto numbers fine for the thesis results chapter?"),
        ("Friend", "Only as plumbing. The RQ answer is the live campaign summary."),
        ("Professor", "What about transactions?"),
        ("Friend", "TransactWrite / P4 is future work and quarantined for CA2."),
    ]:
        s.append(P(f"<b>{who}:</b> {line}", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix C — Glossary", st["h1"])); s.append(hr())
    for term, defn in [
        ("Idempotency", "Repeating an operation does not change the effect beyond the first time."),
        ("At-least-once", "Platform may deliver more than once; duplicates allowed."),
        ("Duplicate mutation", "A retry that changes business state again."),
        ("P1 / P2 / P3", "Plain put / conditional put / idempotency-key paths."),
        ("ConditionExpression", "DynamoDB guard on a write; failure → ConditionalCheckFailed."),
        ("Idempotency key", "Stored token IDEMP#<id> coordinating claim and completion."),
        ("After-commit timeout", "Hang after successful write so caller retries."),
        ("Multiplicity", "Planned deliveries per request_id: 1, 2, or 5."),
        ("Streams ground truth", "Mutation count from DynamoDB Streams."),
        ("Halfmoon", "Qi et al. custom-runtime asymmetric logging system."),
        ("moto", "Local AWS emulator — not live evidence."),
        ("Holm–Bonferroni", "Multiple-testing correction used on the test family."),
        ("E1 E2 E3", "Pre-registered expectations; all supported on live campaign."),
        ("p3_between", "Sensitivity: timeout between business write and COMPLETED mark."),
        ("WCU", "Write capacity units consumed / billed for writes."),
        ("Destroy-after", "Terraform destroy when campaign finishes."),
    ]:
        s.append(P(f"<b>{term}.</b> {defn}", st["cheat"]))

    s.append(PageBreak())
    s.append(P("Appendix D — Five-minute overview script", st["h1"])); s.append(hr())
    s.append(P(
        "“This project evaluates application-level idempotency on AWS Lambda and DynamoDB. The baseline idea comes from "
        "Qi and colleagues’ Halfmoon system, which prevents duplicate mutations using a custom runtime. We cannot install "
        "that runtime on managed Lambda, so we measure three write strategies developers actually use: plain put, "
        "conditional put, and an idempotency-key pattern. A driver injects known retries by timing out after a successful "
        "write. On the twenty-first of September twenty twenty-six we ran nine thousand requests and twenty-four thousand "
        "deliveries in eu-west-1. Plain put duplicated every retry. The two guarded paths did not, in the main campaign, "
        "and the idempotency-key path spent about two extra write units per request. A sensitivity test showed the "
        "idempotency-key pattern still fails if you crash between its two DynamoDB writes. We destroyed the stack afterwards. "
        "Moto tests are not our AWS results. P4 transactions are out of scope.”", st["script"]))

    s.append(PageBreak())
    s.append(P("Appendix E — Common mistakes", st["h1"])); s.append(hr())
    B(s, st, [
        "Saying we implemented Halfmoon.",
        "Citing moto latency as AWS.",
        "Claiming P4 / TransactWrite results from the quarantined markdown.",
        "Claiming exactly-once runtime guarantees for P2/P3.",
        "Forgetting the p3_between sensitivity when praising P3.",
        "Inventing personal data.",
        "Claiming multi-cloud.",
        "Forgetting destroy-after.",
    ])

    s.append(PageBreak())
    s.append(P("Appendix F — Cell walkthrough notes", st["h1"])); s.append(hr())
    s.append(P(
        "P1 mult=2: 1000 requests, 1000 injected retries, 1000 dup mutations, rate 1.0. Capacity mean 2. Shows the "
        "control problem clearly. P2 mult=2: dup 0.0, ccf_per_retry 1.0, successful_retry_rate 1.0, capacity mean 2. "
        "P3 mult=2: dup 0.0, capacity mean 4 (two above P2). P3 mult=5: capacity mean 7 versus P2’s 5. Sensitivity "
        "P3 mult=2 between: 200 requests, 200 retries, 200 dups, rate 1.0 — teach this as the residual risk.", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix G — Technologies deep dive", st["h1"])); s.append(hr())
    for name, blurb in [
        ("Python 3.12 on Lambda", "Handler and paths; pinned in config/versions.yaml."),
        ("boto3", "PutItem, conditions, consumed capacity, streams APIs."),
        ("Terraform", "Table, function, IAM, log group, alarms, budget."),
        ("pytest + moto", "63 tests; functional correctness only."),
        ("pandas/scipy-style analysis", "CIs, z/χ²/Mann–Whitney, Holm, figures."),
        ("CloudWatch", "Invocation cross-check against driver counts."),
        ("DynamoDB Streams", "Mutation ground truth (21387 campaign stream records per STATUS)."),
    ]:
        s.append(P(f"<b>{name}.</b> {blurb}", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix H — Threats to validity (speakable)", st["h1"])); s.append(hr())
    s.append(P(
        "Internal: injected after-commit timeout is cleaner than many real failures; we measure post-commit duplicates "
        "by design. External: one region, one account, one datastore, one function service. Construct: capacity from "
        "service-reported units. Conclusion: campaign is the pack; Wen-style variance addressed via pilot + large N, "
        "but cold-start share remains visible in latency means.", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix I — Whiteboard sketch", st["h1"])); s.append(hr())
    s.append(P(
        "Left: Halfmoon box “custom runtime + logs → no dup mutations”. Crossed arrow “not installable on managed Lambda”. "
        "Right: Driver → Lambda P1/P2/P3 → DynamoDB + Streams. Under right box write “dup 1.0 / 0.0 / 0.0” and “P3 +2 WCU” "
        "and “p3_between = 1.0”. Stamp “destroyed”. Stamp “moto ≠ AWS”.", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix J — Closing line", st["h1"])); s.append(hr())
    s.append(P(
        "<i>“Halfmoon’s idea is no duplicate mutation after retry. On stock Lambda and DynamoDB, plain put always "
        "duplicated under our injected retries; conditional put and idempotency keys stopped duplicates in the main "
        "campaign at measurable capacity cost; the idempotency-key crash window still matters; we did not run Halfmoon.”</i>",
        st["body"]))


    s.append(PageBreak())
    s.append(P("Appendix K — Latency table talking points (live summary)", st["h1"])); s.append(hr())
    s.append(P(
        "Overall latency means are inflated by cold starts. Examples from summary.md: P1 mult=1 latency_mean 590.5 ms with "
        "warm mean 206.8 ms and cold_final_share 0.294; P1 mult=2 latency_mean 1290 ms with warm mean 200 ms and "
        "cold_final_share 0.832. When a professor asks “is idempotency slow?”, separate cold-start effects from DynamoDB "
        "path cost (ddb_mean_ms is much smaller — e.g. ~52 ms on mult=1 cells, ~138–141 ms on mult=2).", st["body"]))
    s.append(P(
        "Capacity tests: P3 versus P1/P2 differs by a flat +2 units per request at each multiplicity (Mann–Whitney, Holm "
        "reject). Latency tests are mixed; some pairwise differences significant, many not — do not invent a “P3 is always "
        "slower end-to-end” slogan beyond what the CIs support.", st["body"]))

    s.append(P("Appendix L — Path semantics table (memorise)", st["h1"])); s.append(hr())
    s.append(simple_table([
        [P("<b>Path</b>", st["cheat"]), P("<b>First delivery</b>", st["cheat"]), P("<b>Duplicate delivery</b>", st["cheat"])],
        [P("P1", st["cheat"]), P("Unconditional PutItem", st["cheat"]), P("Writes again → duplicate mutation", st["cheat"])],
        [P("P2", st["cheat"]), P("Put if attribute_not_exists(pk)", st["cheat"]), P("Condition fails → no second mutation; CCF billed", st["cheat"])],
        [P("P3", st["cheat"]), P("Claim IDEMP key → business write → COMPLETED", st["cheat"]), P("Replay/refuse; unless crash between steps", st["cheat"])],
    ], col_widths=[60, 200, 240]))

    s.append(PageBreak())
    s.append(P("Appendix M — Analogies pack", st["h1"])); s.append(hr())
    s.append(P(
        "Postal service (at-least-once): two copies of one letter may arrive. Light switch ON (idempotency): pressing again "
        "does not brighten further. Hotel receptionist (P2): only create booking if slot empty. Rubber stamp (P3): mark "
        "form processed; if you stamp after filing and lose the stamp pad mid-way, a clerk may file twice. Custom kitchen "
        "(Halfmoon): rebuild the restaurant; we stayed in the ordinary restaurant and timed three waiter habits. Dollhouse "
        "(moto): practise doors; do not claim city traffic times.", st["body"]))

    s.append(P("Appendix N — Implementation progress checklist", st["h1"])); s.append(hr())
    B(s, st, [
        "P1/P2/P3 paths + injection — done.",
        "Driver schedule + ground truth — done.",
        "Streams ground truth + CloudWatch cross-check — done.",
        "Analysis pipeline + figures — done.",
        "Terraform IaC — done; destroyed after campaign.",
        "Moto functional — done (not RQ).",
        "Live pilot — done (19 Sep 2026).",
        "Live campaign — done (21 Sep 2026).",
        "Sensitivity p3_between — done.",
        "P4 — out of scope.",
        "Separate final-3 series — not started (campaign is the pack).",
    ])

    s.append(PageBreak())
    s.append(P("Appendix O — More Q&A", st["h1"])); s.append(hr())
    add_qa(s, st, [
        ("Why multiplicity 1, 2, and 5?",
         "1 is the no-retry control; 2 is a single retry; 5 stresses repeated redelivery. Pre-registered in the design."),
        ("Why on-demand only?",
         "Constants in the master prompt: single region, on-demand, pinned versions — isolate path effects from provisioned throttling."),
        ("What is ReturnConsumedCapacity=TOTAL?",
         "Asks DynamoDB to return consumed units on each write so we can meter capacity per request."),
        ("Why exec_id on every delivery?",
         "So a repeated P1 put always changes the item bytes/version fields — making duplicate mutation detectable."),
        ("What was worker count and why?",
         "Live campaign workers=6 because ConcurrentExecutions=10 Free-Tier guard; Makefile default WORKERS=4."),
        ("How many stream records?",
         "STATUS: 21387 campaign stream records; invocations matched CloudWatch cross-check."),
        ("Pilot date versus campaign date?",
         "Pilot 19 September 2026; campaign 21 September 2026 — both eu-west-1."),
        ("Can I cite vikas_final_report.md?",
         "Not for CA2 evaluation if it claims P4. Use STATUS.md and latex_report / live summary."),
    ])

    s.append(P("Appendix P — Friend 30-second briefing", st["h1"])); s.append(hr())
    s.append(P(
        "“Vikas measured three ways a Lambda can write to DynamoDB when retries are injected on purpose. Plain put always "
        "duplicated. Conditional put and idempotency keys did not, in the main live run, but the key pattern still fails if "
        "you crash between its two writes. Extra cost for the key pattern is about two write units. He did not run Halfmoon. "
        "Moto is not AWS. Stack destroyed.”", st["script"]))

    s.append(PageBreak())
    s.append(P("Appendix Q — Weekly-style narrative (for class progress)", st["h1"])); s.append(hr())
    s.append(P(
        "Week-style story you can tell: scaffolded IaC and three paths; proved on moto that P1 duplicates and P2/P3 do not "
        "in the emulator; ran a live pilot to size N; ran the full live factorial; analysed with CIs and Holm; ran the "
        "P3 between-writes sensitivity; destroyed the stack; quarantined any P4 rhetoric. That is the progress arc without "
        "inventing unfinished weeks.", st["body"]))

    s.append(P("Appendix R — What success looks like vs Halfmoon", st["h1"])); s.append(hr())
    s.append(P(
        "Success here is measured duplicate-mutation reduction and documented capacity/latency on stock AWS. Success is "
        "<b>not</b> matching Halfmoon’s formal guarantees or logging-overhead figures. Say: same criterion, different "
        "mechanism, different claim scope.", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix S — Closing reminder", st["h1"])); s.append(hr())
    s.append(P(
        "Keep section 15 open. If interrupted, answer with P1=1.0, P2/P3=0.0, P3+2 WCU, p3_between=1.0, Halfmoon not "
        "installed, moto not AWS, P4 out of scope, destroyed.", st["body"]))


    s.append(P("Appendix T — Deep dive: why injected retries beat inferred retries", st["h1"])); s.append(hr())
    s.append(P(
        "If you only watch CloudWatch and guess which invocations were retries, your denominator is fuzzy. Two timeouts "
        "might be one logical request or two. Vikas’s driver writes the intended delivery count first. That makes "
        "duplicate-mutation rate a proper fraction: numerator is retries that caused a second state change; denominator "
        "is injected retries. Professors who care about measurement construction should hear that sentence.", st["body"]))
    s.append(P(
        "After-commit timeout is the interesting case because the write already happened. A timeout before the write would "
        "not create a duplicate mutation. The experiment deliberately creates the harmful case production systems fear.", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix U — Deep dive: P3 crash window for a non-expert", st["h1"])); s.append(hr())
    s.append(P(
        "P3 takes multiple DynamoDB round trips: claim the idempotency item as IN_PROGRESS, write the business item, then "
        "mark the idempotency item COMPLETED. Imagine three stamps on a passport desk. If the clerk stamps “in progress”, "
        "files the visa (business write), then faints before stamping “completed”, another clerk later may see an expired "
        "in-progress mark and file a second visa. Sensitivity p3_between forces that faint on purpose. Result: dup_rate 1.0 "
        "at multiplicity 2 and 5 (200+200 and 200+800 style counts in STATUS). That does not erase P3’s main-campaign "
        "success; it bounds the claim.", st["body"]))

    s.append(P("Appendix V — Deep dive: capacity arithmetic intuition", st["h1"])); s.append(hr())
    s.append(P(
        "P1 and P2 at multiplicity 1 both show capacity_mean 1 — one write unit for a ~1 KB item path. At multiplicity 2, "
        "means are 2 because two deliveries each spend about one unit (P2’s second delivery is a failed condition that is "
        "still billed). P3 at multiplicity 1 shows 3 — claim + business + complete style spending. At multiplicity 2, P3 "
        "mean 4; at 5, mean 7. The E3 contrast is the per-request gap versus P2 of +2 units. You do not need to derive "
        "the internal call graph in the viva; you need to say “extra idempotency item traffic costs about two WCU per "
        "request relative to conditional put, and that was pre-registered as E3 and supported.”", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix W — Literature neighbourhood (speakable, no invented papers)", st["h1"])); s.append(hr())
    s.append(P(
        "Runtime replacements: Halfmoon (Qi), Boki (Jia & Witchel), CausalMesh (Zhang et al.), LambdaStore (Mast et al.), "
        "Styx, Netherite, µ2sls — all change or own more of the execution path than managed Lambda allows. Surveys "
        "(Shafiei; Wen systematic review) and AWS docs put idempotency on the application. Flux verifies idempotence; it "
        "does not meter P1/P2/P3 on stock Lambda+DynamoDB under known injected retries. Wen et al. (2025) EMSE force "
        "multi-run thinking — hence pilot + N=1000. Niche sentence: no prior study measures duplicate mutation across all "
        "three application-level DynamoDB write paths on unmodified Lambda under a known injected retry count, reporting "
        "latency + consumed capacity with CIs.", st["body"]))

    s.append(P("Appendix X — Extended Q&A drill (rapid fire)", st["h1"])); s.append(hr())
    add_qa(s, st, [
        ("Define idempotency in one breath.",
         "Doing the operation several times leaves the same effect as doing it once."),
        ("Define at-least-once in one breath.",
         "The platform may run your function more than once for one logical event."),
        ("Why not trust CloudWatch retries alone?",
         "Because we need a known denominator; we inject and log intended deliveries."),
        ("What failed condition costs?",
         "Capacity — failed ConditionalCheckFailed writes are still billed."),
        ("Name the three outcomes language in paths.py.",
         "APPLIED, SUPPRESSED, and replay-style outcomes for P3 (REPLAYED) as implemented."),
        ("What seed?",
         "25178849 — student id digits — for reproducibility."),
        ("What region?",
         "eu-west-1."),
        ("What N?",
         "1000 requests per path per multiplicity after pilot."),
        ("What is ASSUMPTIONS A12?",
         "The assumption/quarantine that keeps P4 / TransactWrite out of the primary experiment."),
        ("What figures exist?",
         "results/live/figures style outputs for dup_rate, latency, capacity, surface — cite live figures, not moto."),
    ])

    s.append(PageBreak())
    s.append(P("Appendix Y — Slide outline (seven slides)", st["h1"])); s.append(hr())
    B(s, st, [
        "Slide 1: Title, name, ID, artefact folder.",
        "Slide 2: Problem — at-least-once Lambda; duplicate DynamoDB mutations.",
        "Slide 3: Baseline Halfmoon — custom runtime; our gap — managed platform.",
        "Slide 4: P1/P2/P3 semantics diagram.",
        "Slide 5: Method — injected deliveries, Streams ground truth, pilot→N.",
        "Slide 6: Results — 1.0 / 0.0 / 0.0; +2 WCU; p3_between 1.0; E1–E3.",
        "Slide 7: Limits — moto≠AWS; P4 out; single region; destroy-after.",
    ])

    s.append(P("Appendix Z — Full class scripts (longer forms)", st["h1"])); s.append(hr())
    s.append(P("Dataset (90 seconds):", st["h3"]))
    s.append(P(
        "“I want to be clear that we are not using personal or production data. The experiment’s data are synthetic request "
        "schedules. A fixed seed, 25178849, generates request identifiers. Each request is assigned a write path — plain put, "
        "conditional put, or idempotency key — and a planned delivery multiplicity of one, two, or five. In the live campaign "
        "that produced twenty-four thousand deliveries across nine thousand requests. The JSON payload is a small template "
        "without names, emails, or card numbers. When we count duplicate mutations, we do not guess: DynamoDB Streams tell us "
        "how many times the business item changed, and we compare that to the known retry schedule.”", st["script"]))
    s.append(P("Implementation progress (2 minutes):", st["h3"]))
    s.append(P(
        "“The artefact implements three write paths in one Lambda function against one DynamoDB table, with Terraform for "
        "infrastructure, a driver that schedules injected timeouts after commit, Streams-based ground truth, and an analysis "
        "pipeline with confidence intervals and Holm correction. We validated plumbing on moto — explicitly not as AWS "
        "evidence. We ran a live pilot on the nineteenth of September to choose N equals one thousand. On the twenty-first "
        "we ran the full campaign in eu-west-1 with six workers under a free-tier concurrency guard. Pre-registered "
        "expectations E1, E2, and E3 were all supported. We also ran a sensitivity where P3 crashes between its business "
        "write and the completion mark; duplicates returned. We destroyed eight Terraform resources afterwards. P4 "
        "transactions remain out of scope.”", st["script"]))
    s.append(P("Technologies (90 seconds):", st["h3"]))
    s.append(P(
        "“Technologies are AWS Lambda for compute, Amazon DynamoDB for state and idempotency items, DynamoDB Streams for "
        "mutation ground truth, IAM for least privilege, CloudWatch for invocation cross-checks, AWS Budgets as a guardrail, "
        "and Terraform as infrastructure as code. Application code is Python with boto3. Tests use pytest and moto. Analysis "
        "uses standard scientific Python tooling for intervals and hypothesis tests. We did not deploy Halfmoon, Boki, or any "
        "custom runtime. We did not use GCP or Azure in this artefact.”", st["script"]))

    s.append(PageBreak())
    s.append(P("Appendix AA — Ethics speaking notes", st["h1"])); s.append(hr())
    B(s, st, [
        "No human participants.",
        "Synthetic payloads only.",
        "Own AWS account; study resources only.",
        "Force timeouts inside the function — not a DoS against third parties.",
        "Budget/alarm guardrails; destroy-after.",
        "Report failed condition checks (they cost capacity) rather than hiding them.",
    ])

    s.append(P("Appendix AB — Mapping STATUS flags to spoken English", st["h1"])); s.append(hr())
    s.append(P(
        "INITIAL_EVAL_PASS=yes → “the live evaluation pack required for the gate is complete.” "
        "CA2 alignment 100/100 → “formal alignment document marks the live campaign as the completed factorial evidence.” "
        "Final-3 not started as separate series → “we are not claiming an extra post-gate triplicate beyond the campaign pack.” "
        "SOLE AWS residual closed → “deploy, measure, destroy — no leftover stack for this campaign.”", st["body"]))

    s.append(PageBreak())
    s.append(P("Appendix AC — Final rehearsal card", st["h1"])); s.append(hr())
    s.append(P(
        "Before knocking on the professor’s door, say aloud: Halfmoon is the idea baseline, not our binary. P1 duplicates. "
        "P2 and P3 did not in the main live run. P3 costs about two extra WCU. P3 between-writes sensitivity duplicates. "
        "Moto is not AWS. P4 is out. Destroyed. Seed 25178849. eu-west-1. N=1000. 24000 deliveries. E1 E2 E3 supported.",
        st["body"]))


    s.append(PageBreak())
    s.append(P("Appendix AD — One more rehearsal: answering “so what?”", st["h1"])); s.append(hr())
    s.append(P(
        "So what for practitioners? If you only plain-put from Lambda, injected retries will duplicate state under the "
        "conditions we tested. Conditional puts stop that for create-once keys at the cost of billed failed checks. "
        "Idempotency keys also stop it in the main pattern but cost more capacity and still need care around crash windows "
        "between their steps. So what for researchers? Application-level controls can be measured with known retry ground "
        "truth on managed platforms without installing Halfmoon; the residual P3 window is a measurable limitation, not an "
        "anecdote. So what for the viva? Quote STATUS, not hope.", st["body"]))
    s.append(P(
        "End of guide. Return to the cheat sheet. Speak as Tarun’s outsourcing lane briefing for Vikas — clear, honest, "
        "no invented metrics.", st["body"]))

    return s


def build_md() -> str:
    return """# Vikas Explanation Guide (speakable)

**Student:** Vikas Reddy Amanagantti (X25178849)
**Artefact:** `lambda-idempotency-eval/`
**Baseline:** Qi et al. Halfmoon, DOI 10.1145/3725985

Companion to `Vikas_Explanation_Guide.pdf`. Numbers from STATUS / live summary only.

## Headline
P1 dup_rate=1.0; P2/P3 dup_rate=0.0 on live campaign; P3 ≈ P2+2 WCU/request; p3_between dup_rate=1.0; E1–E3 supported; moto≠AWS; P4 quarantined; stack destroyed.
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    st = styles()
    pdf_path = OUT_DIR / "Vikas_Explanation_Guide.pdf"
    md_path = OUT_DIR / "Vikas_Explanation_Guide.md"
    md_path.write_text(build_md(), encoding="utf-8")
    doc = make_doc(pdf_path, "Vikas Explanation Guide")
    doc.build(build_story(st), onFirstPage=_footer, onLaterPages=_footer)
    print(f"Wrote {pdf_path}")


if __name__ == "__main__":
    main()
