#!/usr/bin/env python3
"""Build Sriraj SHORT (target 5–6 page) explanation guide — verbose like Anji/Vish packs."""
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
            fontSize=13, leading=16, alignment=TA_CENTER, spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "M", parent=base["Normal"], fontName="Helvetica",
            fontSize=9.5, leading=12, alignment=TA_CENTER, spaceAfter=2,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=11.5, leading=14, spaceBefore=10, spaceAfter=5,
            textColor=colors.HexColor("#1a1a1a"),
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=14, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bu", parent=base["Normal"], fontName="Helvetica",
            fontSize=10.5, leading=13.5, leftIndent=12, spaceAfter=2,
        ),
        "script": ParagraphStyle(
            "Sc", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10, leading=13.5, leftIndent=6, rightIndent=6,
            spaceBefore=3, spaceAfter=5,
        ),
        "qa": ParagraphStyle(
            "QA", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=13, spaceAfter=5,
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
    def __init__(self, path: Path):
        self.path = Path(path)
        self.s = styles()
        self.story = []

    def header(self, title: str, name: str, sid: str, baseline: str):
        s = self.s
        self.story.append(Paragraph(esc(title), s["title"]))
        self.story.append(Paragraph(
            f"<b>{esc(name)}</b> &nbsp;|&nbsp; Student ID: {esc(sid)}", s["meta"]))
        self.story.append(Paragraph(
            "MSc Cloud Computing — National College of Ireland — Short Explanation Guide",
            s["meta"]))
        self.story.append(Paragraph(f"Baseline: {esc(baseline)}", s["meta"]))
        self.story.append(Spacer(1, 4))
        self.story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#333")))

    def h(self, text: str):
        self.story.append(Paragraph(esc(text), self.s["h1"]))

    def p(self, text: str):
        self.story.append(Paragraph(esc(text), self.s["body"]))

    def bullets(self, items: list[str]):
        for it in items:
            self.story.append(Paragraph("• " + esc(it), self.s["bullet"]))

    def script(self, text: str):
        self.story.append(Paragraph(esc(text), self.s["script"]))

    def qa(self, q: str, a: str):
        self.story.append(Paragraph(
            f"<b>Q:</b> {esc(q)}<br/><b>A:</b> {esc(a)}", self.s["qa"]))

    def build(self):
        doc = SimpleDocTemplate(
            str(self.path), pagesize=A4,
            leftMargin=MARGIN, rightMargin=MARGIN,
            topMargin=0.85 * inch, bottomMargin=0.85 * inch,
        )
        doc.build(self.story)


def write_md(path: Path, title: str, name: str, sid: str, sections: list):
    lines = [
        f"# {title}", "",
        f"**Student:** {name}  ",
        f"**Student ID:** {sid}  ",
        "**Programme:** MSc Cloud Computing, National College of Ireland  ",
        "**Format:** Short explanation guide (target 5–6 pages)", "",
    ]
    for heading, body in sections:
        lines.append(f"## {heading}")
        lines.append("")
        if isinstance(body, list):
            for b in body:
                lines.append(f"- {b}")
        else:
            lines.append(body)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_sriraj(path: Path):
    g = ShortGuide(path)
    title = "Serverless Webhook Processing with Retry, Dead-Letter Queue, and Idempotency"
    g.header(
        title,
        "Sriraj Gannavaram",
        "x23431873",
        "Qi et al. 2025 Halfmoon (ACM TOCS) — DOI 10.1145/3725985",
    )

    g.h("1. What is the project?")
    g.p(
        "Modern SaaS, payments, and CI systems notify each other with webhooks — HTTP callbacks "
        "that must arrive even when networks blip or consumers crash. Serverless (AWS Lambda) "
        "is a natural place to run those consumers, but FaaS is stateless and platforms usually "
        "give at-least-once delivery, not exactly-once. This project builds an integrated "
        "reliability pipeline that joins three mechanisms the literature usually studies apart: "
        "(1) SQS-style exponential backoff with full jitter, (2) dead-letter queue capture and "
        "automated replay, and (3) Redis-style idempotency keys with TTL. Ingestion is protected "
        "with HMAC-SHA256. Infrastructure is sketched in Terraform."
    )
    g.p(
        "The floor artefact is Sriraj/webhook-reliability-eval/. It is a runnable local simulator "
        "with pytest, configs B/R/RD/RDI, committed LOCAL_SIM JSON results, and Terraform stubs "
        "for SQS+DLQ. Live AWS apply (API Gateway, Lambda, ElastiCache) is explicitly not claimed "
        "in STATUS.md. One-sentence pitch: I measure how much joint retry + DLQ + idempotency "
        "improves webhook delivery success and duplicate control under controlled faults."
    )

    g.h("2. Problem statement + real-life example")
    g.p(
        "Without structured reliability, three bad outcomes appear together. Transient timeouts "
        "drop events. Provider retries and queue redeliveries apply the same business effect twice "
        "(double charge, duplicate ticket). Poison payloads loop forever on the main queue or "
        "vanish without an audit trail. Surveys catalogue FaaS challenges and microservice "
        "resilience patterns, but they rarely evaluate an integrated serverless webhook stack "
        "under a controlled fault grid."
    )
    g.p(
        "Courier analogy: the driver retries the doorbell with longer waits and random jitter "
        "(retry + backoff). Parcels that still fail go to a depot cage for a supervisor to replay "
        "after the road is fixed (DLQ). The handheld scanner refuses to mark the same tracking "
        "ID delivered twice (idempotency). HMAC is the tamper-evident seal on the parcel label. "
        "Baseline-only designs are like delivering once with no seal, no cage, and no scanner."
    )
    g.bullets([
        "Independent variable — config: B (none), R (retry), RD (retry+DLQ), RDI (full).",
        "Independent variable — fault rate: 0%, 10%, 25%, 50% (CA2).",
        "Dependent variables: delivery success, duplicate suppression, P50/P95/P99, DLQ recovery.",
    ])

    g.h("3. Why this matters")
    g.p(
        "Webhook reliability is an industry SLA problem, not only an academic taxonomy. Payment "
        "providers, Git forges, and CRM platforms all redeliver. Copying a throughput blog post "
        "into a Lambda consumer without DLQ alarms or idempotency keys is a common production "
        "incident pattern. This work gives practitioners an ablation (B→R→RD→RDI) so they can "
        "see marginal value of each mechanism, plus a Terraform starting point."
    )
    g.p(
        "What this project does NOT claim: LOCAL_SIM numbers are not AWS p99 SLOs; cold starts, "
        "ElastiCache RTT, and API Gateway authorizer cost need a live campaign; results do not "
        "automatically transfer to Azure Queue or GCP Pub/Sub parameter-for-parameter."
    )

    g.h("4. Baseline paper (problem / solution / gap / metrics)")
    g.p(
        "Primary baseline: Qi, S., Feng, H., Liu, X. and Jin, X. (2025). Efficient Fault Tolerance "
        "for Stateful Serverless Computing with Asymmetric Logging. ACM Transactions on Computer "
        "Systems, 43(1–2), Article 3. DOI 10.1145/3725985. Online AM 28 March 2025. OA PDF stored "
        "in Sriraj/baseline_papers/Qi_et_al_2025_Halfmoon_TOCS_baseline.pdf."
    )
    g.p(
        "Halfmoon’s problem is that naive retries on stateful serverless functions can corrupt "
        "shared state with duplicate updates, while symmetric logging for exactly-once is "
        "expensive. Their solution is asymmetric (read- or write-only) logging protocols that "
        "are log-optimal versus prior systems such as Boki. Metrics emphasise latency and "
        "logging overhead."
    )
    g.p(
        "Gap this CA2 closes: Halfmoon is a runtime logging design for stateful SSFs. It does "
        "not implement webhook HMAC ingestion, SQS exponential-backoff+jitter, DLQ capture/"
        "replay, or Redis TTL idempotency as a joint application architecture, and it does not "
        "run a B/R/RD/RDI fault-rate grid reporting delivery success and DLQ recovery. Zhang et "
        "al. (2025) TOSEM failure-diagnosis survey (DOI 10.1145/3715005) remains related CA2 "
        "literature for controlled-fault method language but falls outside the primary 6–7 month "
        "recency window (Online AM January 2025), so it is not the primary baseline."
    )

    g.h("5. Research question and how we solve it")
    g.p(
        "RQ: To what extent does an integrated retry, dead-letter queue, and idempotency "
        "framework enhance reliability in serverless webhook processing under faults? "
        "Sub-questions cover success uplift at 10/25/50% faults (RQ1), duplicate suppression "
        "(RQ2), and happy-path latency overhead (RQ3)."
    )
    g.p(
        "Solution: implement the four configs in one harness; inject transient and permanent "
        "faults plus duplicate ingestions; replay DLQ after a simulated root-cause fix; write "
        "metrics JSON. Floor evidence (LOCAL_SIM, 200 events/cell, duplicate_rate=0.10): at 50% "
        "fault, B delivery success ≈0.57 while R ≈0.94 and RD/RDI ≈1.00 after replay; RDI "
        "duplicate suppression ratio = 1.0; happy-path P50 rises modestly B→RDI (~2.5→~3.2 "
        "simulator milliseconds). Direction matches CA2 hypotheses; confirmatory live AWS stats "
        "are future work."
    )

    g.h("6. Dataset")
    g.p(
        "Synthetic webhook JSON only — fields event_id, source, type, amount_cents, currency, "
        "poison, synthetic. Generator: sim.runner.make_event. No personal data, no production "
        "customer traffic. Fault mass splits into transient vs permanent (default 85/15 of the "
        "configured fault rate). Duplicate injection default 10%. Aggregates stored under "
        "results/local_sim/ with mode explicitly labelled local_sim."
    )

    g.h("7. Implementation, AWS mapping, technologies")
    g.bullets([
        "Python 3.11+ packages: ingestion (HMAC-SHA256), retry (full jitter backoff), dlq "
        "(maxReceiveCount redrive + replay), idempotency (SET NX EX stand-in), fault injector, "
        "pipeline, metrics, sim runner.",
        "AWS mapping (live phase): API Gateway, Lambda, SQS + DLQ, ElastiCache Redis, Terraform, "
        "optional AWS FIS / Locust harness (CA2).",
        "Floor commands: make setup && make test && make pilot — 16 pytest cases green.",
        "Terraform stubs ship SQS main+DLQ only; never commit HMAC secrets or AWS keys.",
    ])

    g.h("8. End-to-end flow")
    g.bullets([
        "Build synthetic event; HMAC-sign body+timestamp; reject bad signatures.",
        "Enqueue to main queue; optionally enqueue a duplicate event_id.",
        "Worker path depends on config: B single-attempt drop; R retry until maxReceiveCount; "
        "RD/RDI redrive to DLQ; RDI claims idempotency key (COMPLETE suppresses, PROCESSING retries).",
        "After campaign, replay DLQ with root cause cleared; count recovered unique event_ids.",
        "Emit pilot_results.json; destroy any future live stack; quote only labelled evidence.",
    ])

    g.h("9. Exact speaking script (dataset + implementation + technologies)")
    g.script(
        "My dataset is synthetic payment-style webhooks — event IDs, amounts, HMAC signatures — "
        "with no personal data. I compare four reliability configs: baseline, retry with "
        "exponential backoff and jitter, retry plus dead-letter queue, and the full stack with "
        "Redis-style idempotency. I inject faults at zero, ten, twenty-five, and fifty percent, "
        "plus about ten percent duplicate deliveries. The floor artefact runs locally with "
        "in-memory queues and store, sixteen unit tests green, and committed local_sim JSON. "
        "Technologies map to API Gateway, Lambda, SQS, ElastiCache, and Terraform, but I do not "
        "claim live AWS numbers yet. My baseline is Qi et al. 2025 Halfmoon in ACM TOCS; their "
        "gap is runtime asymmetric logging, while I evaluate the joint application mechanisms "
        "my CA2 required under controlled fault injection."
    )

    g.h("10. Five likely Q&A")
    g.qa("Is the evaluation live on AWS?",
         "No. STATUS says LOCAL_SIM floor; Terraform stubs exist; live apply is future work.")
    g.qa("Why is Halfmoon the baseline instead of Zhang 2025?",
         "Halfmoon is inside the Mar 2025–Sep 2026 window and targets FaaS exactly-once; Zhang "
         "is a Jan 2025 diagnosis survey kept as related.")
    g.qa("Do you process real customer webhooks?",
         "No — synthetic payloads only; ethics scenario is secondary synthetic data.")
    g.qa("What does RDI add over RD?",
         "Idempotency keys so duplicate deliveries and DLQ replays cannot double-apply effects.")
    g.qa("Where is the artefact and how do I run it?",
         "Sriraj/webhook-reliability-eval/ — run make test and make pilot.")

    g.h("11. Validity, STATUS, and honesty rules")
    g.p(
        "Internal validity: shared generator, seeds, and fault model; only reliability mechanisms "
        "change across B/R/RD/RDI. External validity: simulator milliseconds omit cold starts and "
        "real Redis RTT. Construct validity: delivery success uses unique event_id sink membership; "
        "duplicate suppression counts COMPLETE-key hits against injected duplicate ingestions."
    )
    g.p(
        "STATUS one-liner: FLOOR COMPLETE — runnable local artefact, 16 tests passed, Qi et al. "
        "2025 baseline documented, evaluation LOCAL_SIM only (LIVE_AWS=not_run). Never invent "
        "AWS dollar costs or CloudWatch percentiles. Never force-push. Never commit secrets."
    )

    g.build()
    write_md(path.with_suffix(".md"), title, "Sriraj Gannavaram", "x23431873", [
        ("What is the project?",
         "Integrated serverless webhook retry+DLQ+idempotency; artefact webhook-reliability-eval/; LOCAL_SIM floor."),
        ("Problem + example",
         "Transient faults/duplicates/poison; courier retry + depot cage + scanner analogy."),
        ("Baseline",
         "Qi et al. 2025 Halfmoon TOCS DOI 10.1145/3725985; gap = joint webhook mechanisms under faults."),
        ("RQ / solution",
         "RDI vs B at 10/25/50%; local_sim B≈0.57 vs RDI≈1.00 @50%; dup suppress≈1.0."),
        ("Dataset",
         "Synthetic webhooks; no PII; fault rates 0/10/25/50; results/local_sim/."),
        ("AWS / tech", [
            "Mapped API GW, Lambda, SQS/DLQ, ElastiCache, Terraform stubs",
            "Python simulator; pytest 16 passed",
        ]),
        ("Speaking script",
         "Four configs × fault rates; synthetic HMAC webhooks; Halfmoon gap; local_sim only."),
        ("Q&A", [
            "Live AWS? Not yet.",
            "Zhang primary? No — related only.",
            "Real webhooks? No.",
            "RDI vs RD? Idempotency.",
            "Path? webhook-reliability-eval/.",
        ]),
    ])


def main():
    pdf_path = OUT_DIR / "Sriraj_Explanation_Guide.pdf"
    build_sriraj(pdf_path)
    md_path = pdf_path.with_suffix(".md")
    (DESKTOP / pdf_path.name).write_bytes(pdf_path.read_bytes())
    (DESKTOP / md_path.name).write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
    pages = len(PdfReader(str(pdf_path)).pages)
    print(f"Sriraj: {pages} pages | {pdf_path}")
    print(f"Desktop: {DESKTOP / pdf_path.name}")
    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf_path)).pages)
    print(f"words≈{len(text.split())}")
    if pages < 5 or pages > 6:
        print("LENGTH_OUT_OF_BAND:", pages)
        raise SystemExit(1)
    print("ALL_OK")


if __name__ == "__main__":
    main()
