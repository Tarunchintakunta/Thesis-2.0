#!/usr/bin/env python3
"""Build four SHORT (target 5–6 page) explanation guides. A4, ~11pt, 1-inch margins."""
from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from pypdf import PdfReader

MARGIN = inch
OUT_DIR = Path(__file__).resolve().parent
DESKTOP = Path("/Users/tarunchintakunta/Desktop")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=14, leading=17, alignment=TA_CENTER, spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "M", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=3,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=12, leading=15, spaceBefore=12, spaceAfter=6,
            textColor=colors.HexColor("#1a1a1a"),
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=7,
        ),
        "bullet": ParagraphStyle(
            "Bu", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=14.5, leftIndent=14, spaceAfter=3,
        ),
        "script": ParagraphStyle(
            "Sc", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10.5, leading=14.5, leftIndent=8, rightIndent=8,
            spaceBefore=4, spaceAfter=6,
        ),
        "qa": ParagraphStyle(
            "QA", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, spaceAfter=6,
        ),
    }


def esc(t: str) -> str:
    return (
        t.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


class ShortGuide:
    def __init__(self, path: Path, student: str):
        self.path = Path(path)
        self.student = student
        self.s = styles()
        self.story = []

    def header(self, title: str, name: str, sid: str, baseline: str):
        s = self.s
        self.story.append(Paragraph(esc(title), s["title"]))
        self.story.append(Paragraph(
            f"<b>{esc(name)}</b> &nbsp;|&nbsp; Student ID: {esc(sid)}",
            s["meta"],
        ))
        self.story.append(Paragraph(
            "MSc Cloud Computing — National College of Ireland — Short Explanation Guide",
            s["meta"],
        ))
        self.story.append(Paragraph(esc(f"Baseline: {baseline}"), s["meta"]))
        self.story.append(HRFlowable(
            width="100%", thickness=0.9, color=colors.grey, spaceBefore=4, spaceAfter=8,
        ))
        self.story.append(Paragraph(
            "Read aloud in simple English. Numbers come from STATUS.md / results in the repo — "
            "do not invent live AWS metrics in class.",
            s["body"],
        ))

    def h(self, text):
        self.story.append(Paragraph(esc(text), self.s["h1"]))

    def p(self, text):
        self.story.append(Paragraph(esc(text), self.s["body"]))

    def bullets(self, items):
        for it in items:
            self.story.append(Paragraph(f"• {esc(it)}", self.s["bullet"]))
        self.story.append(Spacer(1, 4))

    def script(self, text):
        self.story.append(Paragraph(f"<i>“{esc(text)}”</i>", self.s["script"]))

    def qa(self, q, a):
        self.story.append(Paragraph(
            f"<b>Q:</b> {esc(q)}<br/><b>A:</b> {esc(a)}", self.s["qa"],
        ))

    def build(self):
        doc = SimpleDocTemplate(
            str(self.path),
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
            title=f"Explanation Guide — {self.student}",
            author=self.student,
        )
        student = self.student

        def _footer(canvas, doc_):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.drawCentredString(
                A4[0] / 2, 0.5 * inch,
                f"{student} — Short Explanation Guide — page {doc_.page}",
            )
            canvas.restoreState()

        doc.build(self.story, onFirstPage=_footer, onLaterPages=_footer)
        return self.path


def write_md(path: Path, title: str, name: str, sid: str, blocks: list[tuple[str, str | list]]):
    lines = [
        f"# {title}",
        "",
        f"**Student:** {name}  ",
        f"**Student ID:** {sid}  ",
        f"**Programme:** MSc Cloud Computing, National College of Ireland  ",
        f"**Format:** Short explanation guide (target 5–6 pages)",
        "",
        "---",
        "",
    ]
    for heading, body in blocks:
        lines.append(f"## {heading}")
        lines.append("")
        if isinstance(body, list):
            for item in body:
                lines.append(f"- {item}")
            lines.append("")
        else:
            lines.append(body.strip())
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ═══════════════════════════════════════════════════════════
# YASHASWINI
# ═══════════════════════════════════════════════════════════
def build_yashaswini(out: Path):
    g = ShortGuide(out, "Yashaswini Penumarthi")
    title = (
        "Lightweight Fault Detection and Localisation "
        "in AWS Serverless Microservices"
    )
    g.header(
        title, "Yashaswini Penumarthi", "24262404",
        "Xing et al. (2025) Sensors — DOI 10.3390/s25113396",
    )

    g.h("1. What is the project?")
    g.p(
        "This project builds a small serverless online-shop backend on Amazon Web Services "
        "and studies how well simple CloudWatch rules plus X-Ray ranking can detect and "
        "localise faults — compared with heavy deep-learning detectors that need lots of "
        "labelled training data."
    )
    g.p(
        "The artefact is a four-function order path: orders-api, inventory, payments, and "
        "notify. Traffic enters through API Gateway. State lives in DynamoDB. An SSM Parameter "
        "Store switch injects faults on purpose. A lightweight detector watches CloudWatch "
        "metrics and X-Ray traces. Work has three legs: (1) quote Xing et al. as a published "
        "accuracy ceiling, (2) compare rules vs RCAEval baselines on the same 90 public cases, "
        "(3) measure live AWS lite tracing overhead (full vs policy vs off). The live stack "
        "was destroyed after the round."
    )
    g.p(
        "One-sentence pitch: “I study how well simple CloudWatch rules plus X-Ray ranking "
        "can find faults in a serverless shop, compared with heavy deep models, and what "
        "continuous tracing costs.”"
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "When a serverless checkout slows down, the customer only sees the front door fail. "
        "The root cause may be an inventory timeout, a payment throttle, or a slow notify "
        "path. Deep detectors need large labelled telemetry corpora that a newly deployed, "
        "cost-constrained service does not have. So the practical question is: how good is a "
        "no-training method that only uses CloudWatch alarms and X-Ray traces — and what does "
        "continuous monitoring cost in volume, latency, and money?"
    )
    g.p(
        "Real-life example — pizza shop: orders-api is the counter, inventory is the kitchen, "
        "payments is the card terminal, notify is the SMS to the customer. If the kitchen "
        "freezes, customers still complain at the counter. A fancy AI doctor needs thousands "
        "of past ward failures; a new small clinic cannot afford that. This project is the "
        "nurse with a checklist (CloudWatch rules) and a corridor map (X-Ray ranking)."
    )
    g.p(
        "Why it is hard in serverless: functions are short-lived, you pay for every log line "
        "and trace segment, faults can be timeout / error / throttle / slow, and symptoms "
        "often show up at the entry service even when the root cause is downstream."
    )

    g.h("3. Baseline paper")
    g.p(
        "Xing, Wang and Liu (2025), “Multi-dimensional anomaly detection and fault localization "
        "in microservice architectures…”, Sensors 25(11):3396 (DOI 10.3390/s25113396). They "
        "built a dual-channel deep model (TCN + VAE with contrastive learning and causal "
        "inference) and reported detection F1 ≈ 0.938 (accuracy ≈ 0.954; fault-component "
        "localisation precision ≈ 0.876) under ideal labelled-data conditions."
    )
    g.p(
        "Their gap for this thesis: the method needs training data and compute; it does not "
        "jointly report continuous monitoring overhead on AWS serverless. We use Xing as a "
        "published accuracy ceiling — explicitly not a same-rig re-run. Like-for-like work "
        "uses the RCAEval benchmark (Pham et al., 2025) on common public cases."
    )

    g.h("4. How we solve it / research question")
    g.p(
        "Research question: What accuracy–overhead position does rule-based fault detection "
        "and localisation occupy relative to learned deep baselines in AWS serverless "
        "microservices?"
    )
    g.p(
        "Solution approach: freeze simple CloudWatch rules plus an X-Ray dependency ranker "
        "(no training); compare localisation on RCAEval RE2-OB cases; measure live tracing "
        "overhead under a lite protocol (full / policy / off). Pre-committed success rule: "
        "competitive only if detection F1 is within 10 percentage points of the strongest "
        "reproducible baseline AND telemetry volume is cut by ≥ 50%."
    )
    g.p(
        "Honest STATUS numbers (do not invent others): rule-arm F1 = 0.469 (not within 10 pp "
        "of Xing’s 0.938); AC@3 = 0.611; lite policy vs full volume reduction ≈ 0.803 "
        "(supports the ≥50% volume cut on the lite window). CausalRCA n=4 is quarantined."
    )

    g.h("5. Dataset / data (professor cares about this)")
    g.p(
        "Two data sources — both synthetic or public. No real customer PII."
    )
    g.bullets([
        "RCAEval RE2-OB (offline Leg 2): public microservice fault cases from the RCAEval "
        "benchmark (Pham et al., 2025). Online Boutique–style telemetry. Ninety cases used "
        "for rules / BARO / CIRCA / TraceRCA / hybrid. Same data for every method.",
        "Live AWS lite traffic (Leg 3): synthetic HTTP requests at 1 request/second for "
        "5 minutes × three tracing conditions (≈300 requests per condition) against the "
        "faultlab stack in eu-west-1.",
        "Faults: injected via SSM Parameter Store switches (timeout, error, throttle, "
        "latency). Ground truth is the injection schedule, not guessed from logs.",
        "Ethics: researcher’s own AWS account; synthetic only; stack destroyed after measurement.",
    ])

    g.h("6. Implementation + technologies / AWS services")
    g.bullets([
        "AWS Lambda — four microservice functions (orders, inventory, payments, notify).",
        "API Gateway — REST entry point for shop traffic.",
        "DynamoDB — order / inventory state tables.",
        "CloudWatch — metrics and alarms that feed the rule detector.",
        "AWS X-Ray — distributed traces for localisation ranking; sampling full vs policy vs off.",
        "SSM Parameter Store — on/off fault injection switches per fault type.",
        "SAM + Terraform — deploy and destroy the faultlab stack (destroyed after lite run).",
        "Python 3 + pytest/moto — local unit tests (76 reported in STATUS); RCAEval eval scripts.",
    ])

    g.h("7. End-to-end flow")
    g.bullets([
        "Deploy faultlab with SAM/Terraform (API + four Lambdas + DynamoDB + X-Ray + SSM).",
        "Warm the shop; start synthetic load at the planned rate.",
        "Flip SSM fault switches on a schedule; write ground-truth fault windows.",
        "CloudWatch rules fire on metric thresholds → detection.",
        "X-Ray dependency ranker scores likely root services → localisation.",
        "Offline: run rule arm + RCAEval baselines on 90 RE2-OB cases; write AC@k / F1.",
        "Live lite: compare tracing full vs policy vs off → results/live/overhead.json.",
        "Destroy the stack; keep only results under results/rcaeval/ and results/live/.",
    ])

    g.h("8. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My dataset has two parts. First, the public RCAEval RE2-OB fault cases — ninety "
        "labelled microservice failures I use offline so my rule detector and published "
        "baselines see the same data. Second, synthetic live traffic on my own AWS account: "
        "about one request per second for five minutes under three tracing settings. I never "
        "use real customer data. I implemented a four-function serverless shop with Lambda, "
        "API Gateway, DynamoDB, CloudWatch, X-Ray, and an SSM fault switch. Infrastructure "
        "is SAM and Terraform. The detector is frozen CloudWatch rules plus an X-Ray ranker — "
        "no model training. After the lite overhead round I destroyed the stack. Technologies "
        "are Python, AWS managed services, and the RCAEval benchmark tooling."
    )

    g.h("9. Five likely Q&A (one-liners)")
    g.qa("Is your data real customer traffic?",
         "No — public RCAEval cases plus synthetic load on my own AWS account.")
    g.qa("Did you beat Xing’s F1 of 0.938?",
         "No. Rule F1 is 0.469; Xing is a published ceiling, not a same-rig comparison.")
    g.qa("What AWS services did you use?",
         "Lambda, API Gateway, DynamoDB, CloudWatch, X-Ray, SSM; deployed with SAM/Terraform.")
    g.qa("Is the live stack still running?",
         "No — lite Leg 3 was measured then destroyed (STATUS: LITE_DESTROYED=yes).")
    g.qa("What is localisation versus detection?",
         "Detection means something is wrong; localisation means which service is the root cause.")

    g.build()
    write_md(out.with_suffix(".md"), title, "Yashaswini Penumarthi", "24262404", [
        ("What is the project?",
         "Serverless shop on AWS; rule-based CloudWatch+X-Ray fault detection/localisation "
         "vs deep baselines; three legs (Xing ceiling, RCAEval 90 cases, live lite overhead). "
         "Stack destroyed after live round."),
        ("Problem + example",
         "Checkout fails at the front door but root cause may be downstream. Deep models "
         "need labelled corpora. Pizza-shop analogy: counter vs kitchen vs payment vs SMS."),
        ("Baseline",
         "Xing et al. 2025 Sensors dual-channel TCN+VAE; F1≈0.938; gap = training need + "
         "no joint AWS serverless overhead."),
        ("RQ / solution",
         "Accuracy–overhead of untrained rules vs learned baselines; RCAEval like-for-like "
         "+ lite live overhead. Rule F1=0.469; policy volume cut ≈0.803."),
        ("Dataset",
         "RCAEval RE2-OB (90 cases) + synthetic live 1 rps × 5 min × 3 conditions; "
         "SSM-injected faults; no PII."),
        ("AWS / tech", [
            "Lambda, API Gateway, DynamoDB, CloudWatch, X-Ray, SSM",
            "SAM + Terraform; Python; pytest/moto; RCAEval scripts",
        ]),
        ("Speaking script",
         "Two datasets: public RCAEval + synthetic live load. Four Lambda shop with "
         "CloudWatch rules + X-Ray ranker. Stack destroyed after lite round."),
        ("Q&A", [
            "Real data? No — RCAEval + synthetic.",
            "Beat Xing F1? No — rule F1=0.469; Xing is ceiling.",
            "AWS services? Lambda, APIGW, DynamoDB, CW, X-Ray, SSM.",
            "Stack still up? No — destroyed.",
            "Localisation vs detection? Which service vs something wrong.",
        ]),
    ])


# ═══════════════════════════════════════════════════════════
# ANJI
# ═══════════════════════════════════════════════════════════
def build_anji(out: Path):
    g = ShortGuide(out, "Anjaneya Reddy Gurram")
    title = (
        "Reliability and Recovery of Amazon SQS Messaging "
        "under Injected Consumer and Downstream Failures"
    )
    g.header(
        title, "Anjaneya Reddy Gurram (Anji)", "24288853",
        "Kyrychenko et al. (2025) WSEAS — DOI 10.37394/23202.2025.24.4",
    )

    g.h("1. What is the project?")
    g.p(
        "This project studies Amazon SQS — a cloud queue that holds messages between a "
        "producer and a consumer — when things go wrong. Prior work tunes SQS settings for "
        "speed when consumers are healthy. I ask a different question: if the consumer dies "
        "or the database rejects writes, do those “optimal” settings still keep messages safe?"
    )
    g.p(
        "I built a small order pipeline: SQS Standard queue with a Dead-Letter Queue (DLQ), "
        "a Lambda consumer, DynamoDB for processed state, and an SSM fault switch. A local "
        "simulator runs the full experimental matrix for free. A live lite confirmation ran "
        "on AWS in eu-west-1. The stack was destroyed after the initial live evaluation."
    )
    g.p(
        "One-sentence pitch: “I test how Amazon SQS settings like visibility timeout and "
        "retry limits affect message safety and recovery when consumers or downstream stores fail.”"
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "Queues decouple producers and consumers. Amazon SQS Standard promises at-least-once "
        "delivery: a message might be delivered more than once. If visibility timeout or "
        "maxReceiveCount is wrong, you get message loss, duplicates, or endless retries that "
        "burn Lambda money. Papers that only optimise healthy throughput can recommend long "
        "visibility timeouts that look great on charts but recover slowly after a crash."
    )
    g.p(
        "Real-life example — café pager system: Visibility timeout = how long a ticket stays "
        "“taken” before it returns to the spike if the waiter disappears. maxReceiveCount / "
        "DLQ = after N failed tries, put the ticket in the manager’s problem drawer instead "
        "of looping forever. Batch size = grabbing five tickets at once — if the waiter drops "
        "the tray, five customers suffer. Kyrychenko times waiters when nobody drops trays; "
        "I study what happens when waiters faint or the kitchen rejects orders."
    )
    g.p(
        "Industry angle: almost every event-driven AWS design uses SQS somewhere — order "
        "intake, image pipelines, notifications. Copying a throughput-only optimum into a "
        "failure-prone path is risky without measuring loss and recovery."
    )

    g.h("3. Baseline paper")
    g.p(
        "Kyrychenko, Ostapov and Kyrychenko (2025), “Optimization of SQS configurations for "
        "efficient batch data processing”, WSEAS Transactions on Systems "
        "(DOI 10.37394/23202.2025.24.4). They model SQS-backed serverless batch pipelines "
        "with classical M/M/1 and M/M/k queues, process 500,000 records, and vary batch size "
        "(10–100), visibility timeout (10–900 s), and delivery delay (0–900 s). Reported "
        "optimum around batch size 50, visibility timeout 600 s, delivery delay 300 s."
    )
    g.p(
        "Their gap: they emphasise throughput, latency, and cost under steady-state healthy "
        "consumers. Reliability under injected consumer or downstream failure is asserted via "
        "service guarantees rather than measured. That is the niche this thesis fills."
    )

    g.h("4. How we solve it / research question")
    g.p(
        "Research question: How do SQS configuration knobs (visibility timeout, maxReceiveCount "
        "/ DLQ redrive) affect message loss, duplicates, DLQ capture, and recovery time under "
        "injected consumer and downstream failures?"
    )
    g.p(
        "Solution: hold the async architecture fixed; inject faults (consumer_kill, "
        "unhandled_error, datastore reject/timeout); systematically vary visibility timeout "
        "and maxReceiveCount; measure loss, duplicates, DLQ capture, recovery seconds, plus "
        "throughput/latency for baseline comparability. Authoritative confirmatory stats "
        "(H1–H3) stay in the local simulator. Live lite cells are smoke confirmation only "
        "(n=1, about 200 orders)."
    )
    g.p(
        "Example live cell from STATUS (do not invent others): consumer_kill, VT=30, MRC=5 → "
        "loss 0.0, dup 0.025, DLQ 0.0, recovery ≈ 3.1 s, success 1.0. MRC=1 unhandled_error "
        "shows DLQ capture 0.23 with success 0.805 — the reliability trade-off."
    )

    g.h("5. Dataset / data (professor cares about this)")
    g.p(
        "All traffic is synthetic orders generated by the artefact. No real customers. No PII."
    )
    g.bullets([
        "Localsim: full factorial matrix for confirmatory H1–H3 "
        "(results/summary/stats_H1_H2_H3.json). Cheap and repeatable.",
        "Live AWS initial eval: configs/live_key_cells.yaml — lite 4 cells × n=1, "
        "≈200 orders per cell, region eu-west-1, Terraform stack sqs-rr-dev, "
        "ESM max_concurrency=2.",
        "Faults are injected (consumer kill, unhandled error), not observed from production.",
        "Metrics: loss rate, duplicate rate, DLQ capture rate, recovery seconds, throughput, "
        "success. Destroy verified (0 Terraform resources remaining).",
    ])

    g.h("6. Implementation + technologies / AWS services")
    g.bullets([
        "Amazon SQS Standard — main queue holding order messages.",
        "SQS Dead-Letter Queue (DLQ) — captures messages after maxReceiveCount failures.",
        "AWS Lambda — consumer that processes orders (Event Source Mapping).",
        "DynamoDB — persistence for processed order state.",
        "SSM Parameter Store — fault injection switches.",
        "SAM + Terraform — deploy and destroy sqs-rr-dev (destroyed after initial_eval_1).",
        "Python experiment runner + local simulator — full matrix offline; --live for AWS.",
        "CloudWatch — invocations and metrics cross-checks during live runs.",
    ])

    g.h("7. End-to-end flow")
    g.bullets([
        "Generate synthetic orders; publish to SQS (optional sync API control arm).",
        "Lambda consumer receives a batch; visibility timeout clock starts.",
        "Optionally inject fault (kill consumer, raise unhandled error, reject/timeout store).",
        "On failure: message becomes visible again after VT, up to maxReceiveCount times.",
        "After MRC exhausted → message goes to DLQ (capture rate measured).",
        "On success: write DynamoDB; record latency and throughput.",
        "Runner writes a per-run manifest plus loss / dup / DLQ / recovery metrics.",
        "Destroy stack after live campaign; keep results/live/initial_eval_1/.",
    ])

    g.h("8. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My data is fully synthetic order messages — no real users. The big statistical matrix "
        "runs in a local simulator so I can afford confirmatory tests. On AWS I only ran a "
        "lite four-cell confirmation: about two hundred orders per cell in eu-west-1, then "
        "I destroyed the stack. I implemented an SQS Standard queue with a dead-letter queue, "
        "a Lambda consumer, DynamoDB for state, and an SSM switch to inject consumer and "
        "downstream faults. I vary visibility timeout and maxReceiveCount. Technologies are "
        "Python, SAM, Terraform, and the AWS SQS, Lambda, and DynamoDB APIs. I measure loss, "
        "duplicates, DLQ capture, and recovery time — not just healthy throughput."
    )

    g.h("9. Five likely Q&A (one-liners)")
    g.qa("Is this the same as Kyrychenko?",
         "No — they optimise healthy throughput; I inject failures and measure loss, duplicates, DLQ, and recovery.")
    g.qa("Do you use real customer data?",
         "No — synthetic orders only on my own AWS account.")
    g.qa("Are live n=1 cells your main statistics?",
         "No — live is smoke confirmation; H1–H3 confirmatory stats are from the local simulator.")
    g.qa("What knobs do you vary?",
         "Visibility timeout and maxReceiveCount / DLQ redrive, under injected faults.")
    g.qa("Is the AWS stack still running?",
         "No — DESTROY_CONFIRMED=yes after initial_eval_1.")

    g.build()
    write_md(out.with_suffix(".md"), title, "Anjaneya Reddy Gurram (Anji)", "24288853", [
        ("What is the project?",
         "SQS reliability under injected consumer/downstream failures; VT + MRC knobs; "
         "localsim stats + live lite smoke; stack destroyed."),
        ("Problem + example",
         "At-least-once + bad VT/MRC → loss/dup/slow recovery. Café pager analogy."),
        ("Baseline",
         "Kyrychenko et al. 2025 WSEAS SQS optimisation under healthy consumers; "
         "gap = no failure injection."),
        ("Dataset",
         "Synthetic orders; localsim full matrix; live 4 cells × n=1 ≈200 orders; eu-west-1."),
        ("AWS / tech", [
            "SQS + DLQ, Lambda, DynamoDB, SSM, SAM/Terraform, CloudWatch",
        ]),
        ("Speaking script",
         "Synthetic orders; localsim for stats; live lite 4 cells then destroy; "
         "SQS+DLQ+Lambda+DynamoDB+SSM; measure loss/dup/DLQ/recovery."),
        ("Q&A", [
            "Same as Kyrychenko? No — they healthy throughput; I inject faults.",
            "Real data? No — synthetic.",
            "Live n=1 main stats? No — localsim is confirmatory.",
            "Knobs? VT and MRC/DLQ.",
            "Stack up? No — destroyed.",
        ]),
    ])


# ═══════════════════════════════════════════════════════════
# RASOOL
# ═══════════════════════════════════════════════════════════
def build_rasool(out: Path):
    g = ShortGuide(out, "Rasool Basha Durbesula")
    title = (
        "Partition-Key Design and Capacity Mode in Amazon DynamoDB: "
        "An Empirical Performance-Cost Evaluation under Serverless Workloads"
    )
    g.header(
        title, "Rasool Basha Durbesula", "24205478",
        "Pantelić et al. (2026) Future Internet — DOI 10.3390/fi18010053",
    )

    g.h("1. What is the project?")
    g.p(
        "This project measures how Amazon DynamoDB table configuration — partition-key design "
        "times capacity mode — changes latency, throttling, consumed capacity, and list-price "
        "cost when AWS Lambda drives serverless workloads."
    )
    g.p(
        "Three key designs sit in the factorial: K1 simple (partition key = orderId), "
        "K2 composite (customerId + orderTs), K3 workload-aware write sharding "
        "(orderId#shard, N=10). Capacity mode is on-demand or provisioned. Workload profiles "
        "include mixed (W3) and burst (W4); read-heavy W1 and write-heavy W2 are in the design "
        "but not filled live (soft residual). Live evidence: 12 key cells measured, 100k seed "
        "items, eu-west-1, throttle_rate 0.0 on every measured cell; stack destroyed afterwards."
    )
    g.p(
        "One-sentence pitch: “I turn two DynamoDB knobs — partition key and capacity mode — "
        "under serverless Lambda load, and meter latency, throttles, capacity, and cost.”"
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "DynamoDB performance is not one number. A hot partition key can throttle even when "
        "the table has spare capacity overall. On-demand and provisioned price differently. "
        "Picking the wrong key design or mode wastes money or adds tail latency under burst "
        "traffic. Prior SQL/NoSQL engine benchmarks do not expose RCU/WCU or throttle meters."
    )
    g.p(
        "Real-life example — warehouse aisles: K1 = every box has a unique barcode (orderId) "
        "and spreads across many aisles. K2 = aisle = customer and shelf = time — a celebrity "
        "customer creates a jam in one aisle. K3 = split a hot aisle into ten sub-aisles "
        "(shards) so writes spread; a logical read gathers shards and keeps the newest "
        "version. Capacity mode is whether you rent fixed forklifts (provisioned) or pay per "
        "trip (on-demand)."
    )

    g.h("3. Baseline paper + brief SQL vs NoSQL")
    g.p(
        "Pantelić et al. (2026), “Benchmarking SQL and NoSQL persistence in microservices "
        "under variable workloads”, Future Internet 18(1):53 (DOI 10.3390/fi18010053). They "
        "compare SQL and NoSQL persistence for microservices under read-heavy, write-heavy, "
        "and mixed workloads on a self-hosted single node, ranking engines on latency and "
        "throughput."
    )
    g.p(
        "Their gap: that setting has no RCU/WCU, no throttling admission control, and no "
        "per-operation price — the dependent variables this DynamoDB thesis needs. We keep "
        "their workload language and classic metrics; we add metered DynamoDB quantities "
        "they cannot produce. This is not a container SQL/NoSQL re-bench."
    )
    g.p(
        "SQL vs NoSQL in one breath: SQL databases use fixed tables and joins — strong for "
        "complex queries, but scaling writes often means bigger servers. NoSQL here (DynamoDB) "
        "stores items by key and scales partitions horizontally; you design the key for access "
        "patterns, not ad-hoc joins. The thesis is DynamoDB-native configuration under "
        "serverless load."
    )

    g.h("4. How we solve it / research question")
    g.p(
        "Research question: How does Amazon DynamoDB table configuration (partition-key design "
        "× capacity mode) determine the performance–cost trade-off under serverless workloads?"
    )
    g.p(
        "Solution: factorial K1/K2/K3 × on-demand/provisioned × workloads; Lambda generators; "
        "measure p99 latency, throughput, throttle_rate, and cost per 10k ops (published list "
        "price × consumed RCU/WCU). Live research floor = W3/W4 key cells (12 of 12 filled). "
        "Soft beyond-CA2: W1/W2 live cells and confirmatory live ANOVA (n=1 saturates the "
        "interaction residual). K4 adaptive sharding exists as optional code only — off the "
        "factorial; do not claim K4 “won”."
    )

    g.h("5. Dataset / data (professor cares about this)")
    g.p(
        "Fully synthetic. No real PII. Terraform tags mark data=synthetic."
    )
    g.bullets([
        "Planned catalogue: about 1,000,000 orders over 10,000 customers; Zipfian access "
        "(≈90% of operations hit ≈10% of keys); item sizes 1 KB / 8 KB / 32 KB in the design.",
        "Live key-cell round: 100,000-item seed (not the full 1M) with unique prefixes per "
        "final run; region eu-west-1; orders=100000 in the runner.",
        "Workloads measured live: W3 mixed 50/50 at ~200 ops/s; W4 burst (200↔1000 ops/s). "
        "W1/W2 still placeholders live.",
        "Cost: list-price arithmetic from config/prices.yaml — not Cost Explorer–validated.",
    ])

    g.h("6. Implementation + technologies / AWS services")
    g.bullets([
        "Amazon DynamoDB — six table configs (K1–K3 × on-demand / provisioned).",
        "AWS Lambda — workload generators issuing GetItem / PutItem (batch APIs where used).",
        "Terraform (iac/) — create/destroy tables, Lambda, IAM, CloudWatch, budgets.",
        "Python Zipfian generator + cost model (config/prices.yaml).",
        "CloudWatch — consumed capacity and operational metrics.",
        "S3 — optional result landing in the IaC design.",
        "pytest + moto — plumbing tests only (never cite moto latency as AWS).",
        "Analysis scripts — keycell summary; exploratory n=1 OLS/KW (not confirmatory ANOVA).",
    ])

    g.h("7. End-to-end flow")
    g.bullets([
        "Terraform apply → DynamoDB tables + Lambda generators in eu-west-1.",
        "Seed synthetic orders (100k for the live key-cell round).",
        "Pick a cell: key design K1/K2/K3 × capacity mode × workload W3 or W4.",
        "Warm Lambdas; run measured load; record p99, throughput, throttle, RCU/WCU.",
        "Compute list-price cost per 10k successful ops from prices.yaml.",
        "Write batches.csv / keycell_summary.csv; repeat until all 12 cells are filled.",
        "Terraform destroy (32 resources); verify no leftover ddbpk* tables or Lambda.",
    ])

    g.h("8. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My dataset is synthetic orders — planned one million orders and ten thousand customers "
        "with Zipfian access and one-, eight-, and thirty-two-kilobyte items. The live key-cell "
        "round seeded one hundred thousand items. No real customer data. I implemented three "
        "partition-key designs and two capacity modes as DynamoDB tables driven by Lambda "
        "workload generators, all in Terraform. I measure latency, throttles, consumed capacity, "
        "and list-price cost. Technologies are Python, Terraform, DynamoDB, and Lambda. I did "
        "not re-run Pantelić’s SQL versus NoSQL container bench — I meter DynamoDB configuration "
        "under serverless load. After twelve live cells I destroyed the stack."
    )

    g.h("9. Five likely Q&A (one-liners)")
    g.qa("Did you re-benchmark SQL versus NoSQL like Pantelić?",
         "No — they ranked engines on one node; I meter DynamoDB key × capacity on AWS.")
    g.qa("Is the live data one million rows?",
         "Design target is 1M; live key cells used a 100k seed — say that honestly.")
    g.qa("What are K1, K2, and K3?",
         "K1 = orderId; K2 = customerId + orderTs; K3 = orderId#shard with N=10 write shards.")
    g.qa("Any throttling in the live cells?",
         "throttle_rate = 0.0 on all twelve measured W3/W4 cells (STATUS).")
    g.qa("Is confirmatory ANOVA done on live data?",
         "No — n=1 only; exploratory OLS/KW exist; ANOVA is beyond-CA2 soft work.")

    g.build()
    write_md(out.with_suffix(".md"), title, "Rasool Basha Durbesula", "24205478", [
        ("What is the project?",
         "DynamoDB PK design × capacity mode under serverless Lambda workloads; "
         "12 live W3/W4 cells; stack destroyed."),
        ("Problem + example",
         "Hot partitions + capacity mode drive latency/cost. Warehouse aisle analogy."),
        ("Baseline + SQL/NoSQL",
         "Pantelić et al. 2026 SQL/NoSQL on self-hosted node; gap = no RCU/WCU/throttle/price. "
         "Brief: SQL=joins/fixed schema; DynamoDB=key design + horizontal partitions."),
        ("Dataset",
         "Synthetic Zipfian orders; design 1M/10k customers; live seed 100k; sizes 1/8/32KB."),
        ("AWS / tech", [
            "DynamoDB, Lambda, Terraform, CloudWatch, Python cost model",
        ]),
        ("Speaking script",
         "Synthetic Zipfian orders; 100k live seed; K1–K3 × on-demand/provisioned; "
         "Lambda generators; destroy after 12 cells."),
        ("Q&A", [
            "Re-bench Pantelić SQL/NoSQL? No — DynamoDB-native meters.",
            "Live 1M rows? Design 1M; live seed 100k.",
            "K1/K2/K3? orderId; customerId+ts; sharded orderId.",
            "Throttling? 0.0 on 12 cells.",
            "Live ANOVA? No — n=1 exploratory only.",
        ]),
    ])


# ═══════════════════════════════════════════════════════════
# VIKAS
# ═══════════════════════════════════════════════════════════
def build_vikas(out: Path):
    g = ShortGuide(out, "Vikas Reddy Amanagantti")
    title = (
        "An Empirical Evaluation of Application-Level Idempotency Strategies "
        "for Retry Correctness on AWS Lambda and Amazon DynamoDB"
    )
    g.header(
        title, "Vikas Reddy Amanagantti", "X25178849",
        "Qi et al. Halfmoon (2025) ACM TOCS — DOI 10.1145/3725985",
    )

    g.h("1. What is the project?")
    g.p(
        "This project measures a practical fear: when AWS Lambda is retried, does your "
        "DynamoDB write happen twice? Managed Lambda often gives at-least-once execution, "
        "so the same logical request can run more than once."
    )
    g.p(
        "I compare three application-level write paths on stock AWS Lambda and DynamoDB: "
        "P1 plain Put (unconditional PutItem — the no-guard control), P2 conditional Put "
        "(attribute_not_exists so a second insert fails the condition), and P3 idempotency-key "
        "(claim an IDEMP#request_id token, write the business item, mark COMPLETED). "
        "P4 TransactWrite is quarantined and out of scope for CA2."
    )
    g.p(
        "Live full campaign in eu-west-1: N=1000 × paths {P1,P2,P3} × multiplicities {1,2,5} "
        "= 9000 requests / 24000 deliveries; pre-registered E1–E3 all supported; stack "
        "destroyed afterwards. One-sentence pitch: “I injected known retries into Lambda "
        "writing to DynamoDB three ways and measured duplicate mutations, latency, and capacity.”"
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "If a function times out after the write already committed, the platform may invoke "
        "it again. A plain PutItem applies the side effect twice — duplicate charges, "
        "duplicate orders, or corrupted counters. Runtime research solves this by changing "
        "the runtime. Managed Lambda users cannot swap the runtime; they must use "
        "application-level controls — and those controls have measured costs and residual "
        "failure modes."
    )
    g.p(
        "Real-life example — bank transfer form: you click Submit and the browser spins, so "
        "you click again. P1 = the teller posts the debit every time you click. P2 = the "
        "teller posts only if that slip number does not exist yet. P3 = the teller stamps "
        "your request ID in a log book first, then posts; a second click finds the stamp and "
        "stops. Halfmoon is like rebuilding the bank’s entire ledger machine; I only change "
        "how the teller writes on the existing machine."
    )

    g.h("3. Baseline paper")
    g.p(
        "Qi, Feng, Liu and Jin (2025), “Efficient fault tolerance for stateful serverless "
        "computing with asymmetric logging”, ACM Transactions on Computer Systems "
        "(DOI 10.1145/3725985); SOSP’23 precursor Halfmoon (DOI 10.1145/3600006.3613154). "
        "Halfmoon achieves exactly-once effects with asymmetric logging on a custom serverless "
        "runtime. DynamoDB is used inside that runtime with version-based conditional writes."
    )
    g.p(
        "Their gap for this thesis: you cannot install Halfmoon on stock managed Lambda. We "
        "share the correctness criterion — no duplicate mutation after retry — and measure "
        "what P1, P2, and P3 achieve on unmodified AWS. We do not reimplement Halfmoon and "
        "we do not cite Halfmoon’s logging-overhead numbers as ours."
    )

    g.h("4. How we solve it / research question")
    g.p(
        "Research question: By how much do a conditional write (P2) and an idempotency-key "
        "write (P3) reduce duplicate state mutation relative to a plain write (P1) when an "
        "AWS Lambda function is retried under injected timeouts — and what do they cost in "
        "end-to-end latency and consumed capacity?"
    )
    g.p(
        "Solution: a driver records (request_id, intended_delivery_count) before invoke; "
        "forces timeout after the write has committed; redelivers the same request. DynamoDB "
        "Streams provide mutation ground truth. Pre-registered expectations: E1 — P1 produces "
        "duplicate mutation on a majority of injected retries; E2 — P2 and P3 cut that rate "
        "by >90% relative to P1; E3 — P3 costs more consumed capacity than P2."
    )
    g.p(
        "Live headline (STATUS): P1 dup_rate = 1.0 at multiplicity 2 and 5; P2/P3 dup_rate = "
        "0.0; P3 capacity = P2 + 2 WCU per request. Sensitivity p3_between shows P3 still "
        "fails if you crash between the business write and the COMPLETED mark."
    )

    g.h("5. Dataset / data (professor cares about this)")
    g.p(
        "Fully synthetic request payloads. No real users. No PII."
    )
    g.bullets([
        "Driver schedules known (request_id, intended_delivery_count) before each invoke. "
        "Retries are injected — not inferred from CloudWatch “retry” graphs.",
        "Live campaign: seed 25178849; N=1000 per cell; multiplicities {1,2,5}; workers 6; "
        "region eu-west-1; on-demand DynamoDB; 0 driver errors.",
        "Streams ground truth: 21387 campaign stream records; CloudWatch invocations match.",
        "Sensitivity: 400 requests / 1400 deliveries for P3 p3_between crash window.",
        "Moto factorial is plumbing / correctness only — never cite moto latency or capacity as AWS.",
    ])

    g.h("6. Implementation + technologies / AWS services")
    g.bullets([
        "AWS Lambda — single function with path switch P1 | P2 | P3.",
        "Amazon DynamoDB — business table; idempotency-key items for P3.",
        "DynamoDB Streams — ground-truth mutations versus intended deliveries.",
        "Terraform (infra/) — deploy/destroy (8 resources destroyed after campaign).",
        "Python driver — injects after-commit timeouts; records multiplicity.",
        "CloudWatch — invocation cross-check versus driver counts.",
        "pytest — 63 tests reported; moto for functional plumbing only.",
        "Analysis — z-tests / χ² / Mann–Whitney with Holm–Bonferroni; live figures under results/live/.",
    ])

    g.h("7. End-to-end flow")
    g.bullets([
        "Terraform apply → Lambda + DynamoDB + Streams + IAM in eu-west-1.",
        "Driver picks path (P1/P2/P3) and multiplicity (1/2/5).",
        "First invoke writes; optional after-commit timeout forces a platform retry.",
        "Redeliver the same request_id the planned number of times.",
        "P1 may mutate again; P2 fails the condition; P3 finds the idempotency key and skips.",
        "Streams + driver logs → duplicate rate, latency, consumed WCU/RCU.",
        "Run full factorial N=1000; analyse E1–E3; destroy the stack.",
    ])

    g.h("8. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My dataset is synthetic Lambda requests with known retry counts that I inject myself — "
        "not real users, and not guessed from CloudWatch. I implemented one Lambda that can "
        "write to DynamoDB three ways: plain put, conditional put, and an idempotency-key "
        "pattern. DynamoDB Streams give me ground truth of every mutation. Infrastructure is "
        "Terraform. On the live campaign I ran one thousand requests for each path and each "
        "retry multiplicity in eu-west-1, then destroyed the stack. Technologies are Python, "
        "AWS Lambda, DynamoDB, Streams, and standard statistics. I did not install Halfmoon; "
        "I only share its correctness idea on stock AWS."
    )

    g.h("9. Five likely Q&A (one-liners)")
    g.qa("Did you run Halfmoon?",
         "No — baseline idea only; measurements are on stock managed Lambda and DynamoDB.")
    g.qa("What is P4?",
         "TransactWriteItems — quarantined / out of scope for CA2 (ASSUMPTIONS A12).")
    g.qa("Can I cite moto numbers as AWS results?",
         "No — moto is plumbing only; the live campaign is the research-question answer.")
    g.qa("Did the guarded paths stop duplicates?",
         "Yes in the main campaign: P2 and P3 dup_rate = 0.0; P1 = 1.0 at multiplicity 2 and 5.")
    g.qa("When does P3 still fail?",
         "Sensitivity p3_between: crash between the business write and the COMPLETED mark.")

    g.build()
    write_md(out.with_suffix(".md"), title, "Vikas Reddy Amanagantti", "X25178849", [
        ("What is the project?",
         "P1/P2/P3 idempotency on Lambda+DynamoDB under injected retries; "
         "live N=1000×3×3; Halfmoon as correctness baseline idea only."),
        ("Problem + example",
         "At-least-once retries duplicate side effects. Bank-transfer double-click analogy."),
        ("Baseline",
         "Qi et al. Halfmoon 2025 — exactly-once via custom runtime; gap = not installable on managed Lambda."),
        ("Dataset",
         "Synthetic injected (request_id, delivery_count); Streams ground truth; seed 25178849."),
        ("AWS / tech", [
            "Lambda, DynamoDB, Streams, Terraform, CloudWatch, Python driver/analysis",
        ]),
        ("Speaking script",
         "Synthetic injected retries; P1/P2/P3 on one Lambda; Streams GT; Terraform; "
         "live N=1000×3×3 then destroy; Halfmoon idea only."),
        ("Q&A", [
            "Run Halfmoon? No — idea only on stock AWS.",
            "P4? Quarantined TransactWrite.",
            "Cite moto as AWS? No.",
            "Guarded paths? P2/P3 dup=0; P1=1.0 at mult 2/5.",
            "P3 fail mode? Crash between write and COMPLETED.",
        ]),
    ])


def deploy(name: str, builder):
    pdf_path = OUT_DIR / f"{name}_Explanation_Guide.pdf"
    builder(pdf_path)
    md_path = pdf_path.with_suffix(".md")
    # Overwrite Desktop copies
    (DESKTOP / pdf_path.name).write_bytes(pdf_path.read_bytes())
    if md_path.exists():
        (DESKTOP / md_path.name).write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    pages = len(PdfReader(str(pdf_path)).pages)
    desk_pages = len(PdfReader(str(DESKTOP / pdf_path.name)).pages)
    print(f"{name}: {pages} pages | Desktop={desk_pages} pages | {pdf_path}")
    return pages


def main():
    results = {}
    results["Yashaswini"] = deploy("Yashaswini", build_yashaswini)
    results["Anji"] = deploy("Anji", build_anji)
    results["Rasool"] = deploy("Rasool", build_rasool)
    results["Vikas"] = deploy("Vikas", build_vikas)
    bad = {k: v for k, v in results.items() if v < 5 or v > 6}
    print("RESULTS:", results)
    if bad:
        print("LENGTH_OUT_OF_BAND:", bad)
        raise SystemExit(1)
    print("ALL_OK")


if __name__ == "__main__":
    main()
