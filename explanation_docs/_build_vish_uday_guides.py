#!/usr/bin/env python3
"""Build Vishvaksen + Uday SHORT (target 5–6 page) explanation guides. A4, ~11pt, 1-inch margins."""
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


def write_md(path: Path, title: str, name: str, sid: str, blocks: list):
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
# VISHVAKSEN
# ═══════════════════════════════════════════════════════════
def build_vishvaksen(out: Path):
    g = ShortGuide(out, "Vishvaksen Machana")
    title = (
        "Terraform / IaC Security Scanner Benchmark "
        "on Labelled AWS Terraform Modules"
    )
    g.header(
        title, "Vishvaksen Machana", "25173421",
        "Verdet et al. (2025) Empir. Softw. Eng. — DOI 10.1007/s10664-024-10610-0",
    )

    g.h("1. What is the project?")
    g.p(
        "This project benchmarks how well popular Infrastructure-as-Code (IaC) security "
        "tools find known misconfigurations in AWS Terraform modules. The formal artefact "
        "is terraform-scanner-benchmark/ only — not the quarantined proxy under "
        "_superseded_proxy/iac-security/."
    )
    g.p(
        "I built a labelled corpus of N=240 AWS Terraform modules (60 per category × 4 "
        "categories; about 60% defective). Each module has a published secure/insecure "
        "ground-truth label. I score three detection stages against those labels: (1) a "
        "deterministic label-oracle checklist, (2) static scanners Checkov 3.3.19 and "
        "tfsec v1.28.14 (plus their union), and (3) an OPA/Rego 1.4.2 policy-as-code CI "
        "gate. Ethics: evaluation-only — no terraform apply and no live AWS infrastructure."
    )
    g.p(
        "One-sentence pitch: “I measure precision, recall, and F1 of Checkov, tfsec, and "
        "an OPA gate against labelled AWS Terraform defects — without ever applying the "
        "modules to a real cloud account.”"
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "Teams ship cloud infrastructure as Terraform code. Misconfigurations — public "
        "storage, over-permissive IAM, missing encryption, weak logging — create real "
        "breaches. Security scanners (Checkov, tfsec) and policy-as-code (OPA) are meant "
        "to catch them in CI before deploy. But how many labelled defects do they actually "
        "find? Prior Terraform studies often report alert conflicts or accuracy only on "
        "disputed cases, not recall/F1 against a full labelled ground truth."
    )
    g.p(
        "Real-life example — building inspection: Terraform files are the blueprints for "
        "a cloud building. Checkov and tfsec are two different inspectors with printed "
        "checklists. OPA is the city permit gate that blocks the build if a policy fails. "
        "My labelled corpus is a street of 240 houses where I already know which ones "
        "have faulty wiring. I ask: what fraction of those known faults does each "
        "inspector catch? Verdet studied how often developers adopt security policies "
        "across clouds; I measure scanner recall on known AWS Terraform defects."
    )
    g.p(
        "Why it is hard: scanners disagree; high precision can hide low recall; and "
        "applying insecure modules to live AWS would be unethical for a thesis — so "
        "scoring must stay local against labels."
    )

    g.h("3. Baseline paper")
    g.p(
        "Verdet, Hamdaqa, Da Silva and Khomh (2025), “Assessing the adoption of security "
        "policies by developers in Terraform across different cloud providers”, Empirical "
        "Software Engineering 30(3), 74 (DOI 10.1007/s10664-024-10610-0). They study "
        "security-policy adoption in Terraform across cloud providers and report accuracy "
        "mainly on disputed Checkov/tfsec cases."
    )
    g.p(
        "Their gap for this thesis: no published Terraform study reports recall/F1 against "
        "labelled ground truth across manual/oracle review, Checkov/tfsec, and an OPA gate "
        "on the same modules. Rahman/GLITCH-style labelled benchmarks are the oracle "
        "methodology anchors — not a different Terraform scanner baseline. The older War "
        "et al. proxy is superseded and must not be cited as this CA2’s baseline."
    )

    g.h("4. How we solve it / research question")
    g.p(
        "Research question: What percentage of the labelled AWS misconfigurations will be "
        "identified by Terraform security scanners and an enforced policy-as-code gate?"
    )
    g.p(
        "Solution: fix pinned tool versions; score every stage against corpus/labels.csv; "
        "report precision / recall / F1 / false-negative rate per category; record scan "
        "time and remediation LOC (secure↔insecure diff). Compare Checkov vs tfsec with "
        "McNemar + Holm–Bonferroni on pre-registered pairs (docs/VERDET_COMPARISON.md)."
    )
    g.p(
        "Honest STATUS numbers (do not invent others): label-oracle checklist F1 = 0.876 "
        "(precision 0.951, recall 0.812); Checkov F1 = 0.651 (recall 0.562); tfsec F1 = "
        "0.693 (recall 0.618); static union F1 = 0.718 (recall 0.708); OPA gate F1 = 0.753 "
        "(precision 1.000, recall 0.604). High OPA precision ≠ complete coverage."
    )

    g.h("5. Dataset / data (professor cares about this)")
    g.p(
        "Purpose-built labelled Terraform modules. No live cloud data. No customer PII. "
        "No terraform apply."
    )
    g.bullets([
        "N=240 AWS Terraform modules: 60 per category × 4 categories; ≈60% labelled defective.",
        "Categories: public_storage; overpermissive_access; encryption_at_rest; weak_logging.",
        "Ground truth: corpus/labels.csv written with the modules (Rahman/GLITCH-style oracle).",
        "Stages scored on identical inputs: checklist, Checkov, tfsec, static union, OPA gate.",
        "Evidence under terraform-scanner-benchmark/results/ (metrics_per_category.csv, "
        "scan_times.csv, remediation_loc.csv, tool_versions.json).",
        "Ethics: evaluation-only corpus; AWS apply forbidden.",
    ])

    g.h("6. Implementation + technologies / AWS services")
    g.bullets([
        "Checkov 3.3.19 — static IaC security scanner (shipped defaults).",
        "tfsec v1.28.14 — second static scanner; McNemar vs Checkov on same modules.",
        "OPA 1.4.2 + Rego — category-scoped policy-as-code CI gate under policies/rego/.",
        "Python 3 + python-hcl2 — corpus generate, evaluate, pytest harness.",
        "Terraform CLI present for syntax context only — never applied.",
        "Four AWS misconfiguration themes in HCL modules (S3/IAM/encryption/logging patterns).",
        "No live AWS account required for the formal CA2 floor.",
    ])

    g.h("7. End-to-end flow")
    g.bullets([
        "Generate or load the labelled corpus (scripts/generate_corpus.py → corpus/).",
        "Run label-oracle checklist rules vs labels.csv.",
        "Batch-scan corpus/ with pinned Checkov and tfsec; build static union.",
        "Evaluate OPA/Rego policies as a CI gate on the same modules.",
        "Compute per-category P/R/F1/FN; write metrics_per_category.csv.",
        "Record scan times and remediation LOC diffs.",
        "Run McNemar + Holm–Bonferroni pairs for Verdet-aligned comparison.",
        "Keep results local — never terraform apply.",
    ])

    g.h("8. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My dataset is two hundred and forty labelled AWS Terraform modules I built for "
        "this thesis — about sixty per misconfiguration category, with known secure or "
        "insecure labels. I never applied them to a real AWS account. I implemented three "
        "detection stages: a label-oracle checklist, the static scanners Checkov and tfsec "
        "at pinned versions, and an OPA Rego policy gate. I score every stage against the "
        "same labels and report precision, recall, and F1 per category, plus scan time and "
        "remediation lines of code. Technologies are Python, Checkov, tfsec, and OPA. The "
        "baseline is Verdet et al. 2025; my gap is labelled recall on Terraform, not just "
        "alert conflicts. The War hybrid proxy is not my evidence."
    )

    g.h("9. Five likely Q&A (one-liners)")
    g.qa("Did you terraform apply these modules?",
         "No — ethics forbid apply; scoring is local against labelled ground truth.")
    g.qa("Is iac-security/ your artefact?",
         "No — that is the superseded proxy. Formal evidence is terraform-scanner-benchmark/.")
    g.qa("Which scanners and versions?",
         "Checkov 3.3.19, tfsec v1.28.14, OPA 1.4.2 — pinned in tool_versions.json.")
    g.qa("Did Checkov catch everything?",
         "No — Checkov recall is 0.562; static union recall 0.708; OPA precision 1.0 but recall 0.604.")
    g.qa("What is the baseline gap?",
         "Verdet lacks labelled recall/F1 across checklist, Checkov/tfsec, and OPA on the same modules.")

    g.build()
    write_md(out.with_suffix(".md"), title, "Vishvaksen Machana", "25173421", [
        ("What is the project?",
         "Labelled N=240 AWS Terraform benchmark; Checkov + tfsec + OPA vs label oracle; "
         "no terraform apply. Artefact: terraform-scanner-benchmark/ only."),
        ("Problem + example",
         "Scanners may miss labelled defects; Verdet focuses on policy adoption / disputed "
         "cases. Building-inspection analogy for Checkov/tfsec/OPA."),
        ("Baseline",
         "Verdet et al. 2025 Empir. Softw. Eng. DOI 10.1007/s10664-024-10610-0; "
         "gap = labelled recall/F1 + OPA gate on same modules."),
        ("RQ / solution",
         "What % of labelled AWS misconfigs do scanners + OPA identify? "
         "Oracle F1=0.876; Checkov 0.651; tfsec 0.693; union 0.718; OPA 0.753."),
        ("Dataset",
         "N=240 modules; 4 categories; labels.csv oracle; results under "
         "terraform-scanner-benchmark/results/; no PII; no apply."),
        ("AWS / tech", [
            "Checkov 3.3.19, tfsec v1.28.14, OPA 1.4.2 + Rego",
            "Python + HCL2; Terraform CLI never applied",
        ]),
        ("Speaking script",
         "240 labelled modules; checklist + Checkov/tfsec + OPA; score vs labels; "
         "no apply; Verdet gap = labelled recall."),
        ("Q&A", [
            "Apply? No — ethics.",
            "iac-security artefact? No — proxy only.",
            "Versions? Checkov 3.3.19, tfsec v1.28.14, OPA 1.4.2.",
            "Checkov complete? No — recall 0.562.",
            "Baseline gap? Labelled recall/F1 + OPA on same modules.",
        ]),
    ])


# ═══════════════════════════════════════════════════════════
# UDAY
# ═══════════════════════════════════════════════════════════
def build_uday(out: Path):
    g = ShortGuide(out, "Uday Kiran Reddy Dodda")
    title = (
        "MQTT QoS 0 vs 1 Message Loss under Controlled Disconnect "
        "on AWS IoT Core"
    )
    g.header(
        title, "Uday Kiran Reddy Dodda", "X25166484",
        "Shvaika et al. (2025) J. Big Data — TBMQ — DOI 10.1186/s40537-025-01271-x",
    )

    g.h("1. What is the project?")
    g.p(
        "This project measures how MQTT Quality-of-Service (QoS) level 0 versus level 1 "
        "affects telemetry message loss on AWS IoT Core when the publishing device is "
        "deliberately disconnected for controlled periods. The formal artefact is "
        "mqtt-qos-iot-core/ only — not the proxy iot-reliability/ federated-RF tree."
    )
    g.p(
        "Simulated devices publish synthetic telemetry. A device-side ID log is written "
        "before each publish. IoT Core rules forward messages to Lambda, which stores "
        "delivered records in DynamoDB. Loss, duplicates, and end-to-end latency come from "
        "matching the device log to DynamoDB. Factors: QoS ∈ {0,1} × disconnect ∈ "
        "{0, 15s, 1m, 5m} × rate ∈ {steady, bursty}. Lite live: 16 cells in eu-west-1 "
        "(≈6 000 IoT messages upper), then destroy. Formal-scale (~600 k msgs) is "
        "beyond the free-tier floor."
    )
    g.p(
        "One-sentence pitch: “I disconnect publishers on purpose on AWS IoT Core and "
        "measure whether MQTT QoS 1 really loses fewer messages than QoS 0 — with "
        "per-message ground truth.”"
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "IoT devices often drop off Wi-Fi or cellular for seconds to minutes. MQTT QoS 0 "
        "is fire-and-forget: if the link is down, the message can vanish. QoS 1 asks the "
        "broker to acknowledge delivery and may retransmit — so you expect less loss but "
        "more latency and possible duplicates. Teams need measured loss under disconnect "
        "on a managed broker they do not operate themselves."
    )
    g.p(
        "Real-life example — courier and warehouse desk: each telemetry message is a "
        "parcel with a tracking ID stamped in the driver’s book before leaving "
        "(device-side log). QoS 0 = toss the parcel toward the desk and drive away — if "
        "the road is closed, it never arrives. QoS 1 = wait for a signed receipt; if the "
        "road reopens, backlog can still flush. AWS IoT Core is the public warehouse "
        "desk you do not own. Shvaika’s TBMQ paper studies a self-hosted desk under "
        "steady load and leaves disconnect and multi-QoS as future work — that is my gap."
    )
    g.p(
        "Industry angle: smart factories, fleets, and home IoT all use MQTT through "
        "managed clouds. Copying “QoS 1 is safer” without measuring loss under cut links "
        "is a guess."
    )

    g.h("3. Baseline paper")
    g.p(
        "Shvaika, Shvaika, Landiak and Artemchuk (2025), “A distributed architecture for "
        "MQTT messaging: the case of TBMQ”, Journal of Big Data 12(1), 224 "
        "(DOI 10.1186/s40537-025-01271-x). They characterise a self-hosted, "
        "Kafka/Redis-backed MQTT broker under steady high load. Companion work covers "
        "architectural enhancements and replay while clients stay connected."
    )
    g.p(
        "Their gap: they name as future work varying QoS, intermittent connectivity, and "
        "varying client conditions. No reviewed study jointly has managed broker + client "
        "disconnection + more than one service level + per-message device-side log. This "
        "thesis fills that niche on AWS IoT Core. Do not use Et-Tousy federated-RF as "
        "this CA2 baseline — that belonged to the quarantined proxy."
    )

    g.h("4. How we solve it / research question")
    g.p(
        "Research question: To what extent does publishing at MQTT QoS level 1 rather "
        "than level 0 reduce telemetry message loss in AWS IoT Core when the publishing "
        "device undergoes controlled disconnections of varying duration?"
    )
    g.p(
        "Solution: hold the managed broker fixed (IoT Core); inject controlled publisher "
        "disconnect windows; match device IDs to DynamoDB deliveries; measure loss "
        "(primary), duplicate-id rate, E2E latency (mean/p95/p99), reconnection/backlog, "
        "and estimated USD from published unit prices × counted ops."
    )
    g.p(
        "Lite live numbers from STATUS / BASELINE_PAPER (do not invent others): no "
        "disconnect → QoS0 and QoS1 loss 0.00; 15 s disconnect → QoS0 loss 0.30, QoS1 "
        "loss 0.00; 60 s / 300 s under the lite schedule → QoS0 loss 0.68, QoS1 loss "
        "0.00 (with latency/backlog cost on QoS1). n=1 replication per cell — directional, "
        "not formal Holm power."
    )

    g.h("5. Dataset / data (professor cares about this)")
    g.p(
        "Fully synthetic device telemetry. No real sensors. No PII. Formal CA2 explicitly "
        "allows synthetic devices."
    )
    g.bullets([
        "Device-side ID log written before each publish = ground truth of intent.",
        "Lite live (2026-09-21): 16 cells; 5 devices × 50 msgs; ≈6 000 IoT msgs upper "
        "(~2.4% of monthly free tier); region eu-west-1; stack destroyed (43 resources).",
        "Smoke archive: 4 cells, 2×8 msgs — harness proof only.",
        "Mock dry-run under results/mock/ is harness proof — not AWS evidence.",
        "Formal design scale (5 devices × 1000 msgs × 5 reps ≈ 600 k) remains free-tier "
        "blocked as a single-month apply — beyond floor.",
        "Evidence pointer: mqtt-qos-iot-core/results/live/ (lite campaign).",
    ])

    g.h("6. Implementation + technologies / AWS services")
    g.bullets([
        "AWS IoT Core — managed MQTT broker (tenant does not operate the broker).",
        "IoT Rules — route telemetry to the ingest path.",
        "AWS Lambda — ingest function writing delivered records.",
        "Amazon DynamoDB — delivered-message store for matching.",
        "Terraform (terraform/) — provision/destroy; enable_apply gate; project tags.",
        "Python simulator — synthetic devices, disconnect windows, steady/bursty rates.",
        "Matching + analysis — loss/dup/latency; cost surface; Holm on mock.",
        "eu-west-1 lite campaign then mandatory destroy.",
    ])

    g.h("7. End-to-end flow")
    g.bullets([
        "Terraform apply IoT Core + rule + Lambda + DynamoDB (lite/smoke vars only).",
        "Start simulated devices; stamp message IDs in the device log.",
        "Publish at QoS 0 or 1 under steady or bursty rate.",
        "Inject controlled disconnect (0 / 15 s / 1 m / 5 m); then reconnect.",
        "IoT rule → Lambda → DynamoDB for each delivered message.",
        "Match device log ↔ DynamoDB → loss, duplicates, latency, backlog.",
        "Write live evidence; Terraform destroy; keep results under results/live/.",
    ])

    g.h("8. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My data is synthetic IoT telemetry from simulated devices — no real sensors and "
        "no personal data. Before each publish I write the message ID on the device side, "
        "then match it to what lands in DynamoDB through IoT Core rules and Lambda. I ran "
        "a lite sixteen-cell live campaign in eu-west-1 — about six thousand messages — "
        "then destroyed the stack. I compare MQTT QoS 0 versus QoS 1 under controlled "
        "disconnects of zero, fifteen seconds, one minute, and five minutes. Technologies "
        "are Python, Terraform, AWS IoT Core, Lambda, and DynamoDB. My baseline is Shvaika "
        "et al. 2025 on self-hosted TBMQ; my gap is managed broker plus disconnect plus "
        "multi-QoS with per-message ground truth. The old federated-RF proxy is not this "
        "project."
    )

    g.h("9. Five likely Q&A (one-liners)")
    g.qa("Is this the same as Shvaika’s TBMQ paper?",
         "No — they self-host under steady load; I measure managed IoT Core under controlled disconnect at QoS 0 and 1.")
    g.qa("Do you use real device data?",
         "No — synthetic telemetry only; formal CA2 allows it.")
    g.qa("Is lite 16 cells the formal 600k-message study?",
         "No — lite is the free-tier floor; formal scale is beyond floor / free-tier blocked.")
    g.qa("Did QoS 1 remove loss in the lite run?",
         "In the lite cells, QoS1 loss stayed 0.00 while QoS0 rose under disconnect — paid for with latency/backlog.")
    g.qa("Is iot-reliability/ your artefact?",
         "No — that proxy is quarantined. Formal artefact is mqtt-qos-iot-core/.")

    g.build()
    write_md(out.with_suffix(".md"), title, "Uday Kiran Reddy Dodda", "X25166484", [
        ("What is the project?",
         "MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core; "
         "device-log ↔ DynamoDB match; lite 16 cells then destroy. "
         "Artefact: mqtt-qos-iot-core/ only."),
        ("Problem + example",
         "Disconnect drops QoS0 messages; QoS1 should survive with latency cost. "
         "Courier tracking-book analogy."),
        ("Baseline",
         "Shvaika et al. 2025 TBMQ (DOI 10.1186/s40537-025-01271-x); "
         "gap = managed broker + disconnect + multi-QoS + per-message GT."),
        ("RQ / solution",
         "Does QoS1 cut loss vs QoS0 under controlled disconnect on IoT Core? "
         "Lite: QoS0 loss 0.30@15s / 0.68@60–300s; QoS1 loss 0.00."),
        ("Dataset",
         "Synthetic devices; device ID log; lite ≈6k msgs / 16 cells / eu-west-1; "
         "destroyed; mock ≠ AWS."),
        ("AWS / tech", [
            "IoT Core, Rules, Lambda, DynamoDB, Terraform, Python simulator",
        ]),
        ("Speaking script",
         "Synthetic telemetry; device ID log matched via IoT→Lambda→DynamoDB; "
         "lite 16 cells then destroy; Shvaika gap = managed+disconnect+multi-QoS."),
        ("Q&A", [
            "Same as Shvaika? No — managed + disconnect.",
            "Real devices? No — synthetic.",
            "Lite = formal 600k? No — floor only.",
            "QoS1 loss in lite? 0.00; QoS0 rises under cut.",
            "iot-reliability artefact? No — proxy only.",
        ]),
    ])


def deploy(name: str, builder):
    pdf_path = OUT_DIR / f"{name}_Explanation_Guide.pdf"
    builder(pdf_path)
    md_path = pdf_path.with_suffix(".md")
    (DESKTOP / pdf_path.name).write_bytes(pdf_path.read_bytes())
    if md_path.exists():
        (DESKTOP / md_path.name).write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    pages = len(PdfReader(str(pdf_path)).pages)
    desk_pages = len(PdfReader(str(DESKTOP / pdf_path.name)).pages)
    print(f"{name}: {pages} pages | Desktop={desk_pages} pages | {pdf_path}")
    print(f"  Desktop PDF: {DESKTOP / pdf_path.name}")
    print(f"  Desktop MD:  {DESKTOP / md_path.name}" if md_path.exists() else "")
    return pages


def main():
    results = {}
    results["Vishvaksen"] = deploy("Vishvaksen", build_vishvaksen)
    results["Uday"] = deploy("Uday", build_uday)
    bad = {k: v for k, v in results.items() if v < 5 or v > 6}
    print("RESULTS:", results)
    if bad:
        print("LENGTH_OUT_OF_BAND:", bad)
        raise SystemExit(1)
    print("ALL_OK")


if __name__ == "__main__":
    main()
