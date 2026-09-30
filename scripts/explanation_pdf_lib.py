#!/usr/bin/env python3
"""Shared reportlab helpers for thesis explanation guides (~40-45 pages)."""
from __future__ import annotations
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, Preformatted,
)

PAGE = A4
LEFT = RIGHT = TOP = BOTTOM = 0.95 * inch


def styles():
    base = getSampleStyleSheet()
    s = {}
    s["title"] = ParagraphStyle("TTitle", parent=base["Title"], fontName="Times-Bold",
        fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=10)
    s["subtitle"] = ParagraphStyle("TSub", parent=base["Normal"], fontName="Times-Roman",
        fontSize=11, leading=14, alignment=TA_CENTER, spaceAfter=5)
    s["h1"] = ParagraphStyle("TH1", parent=base["Heading1"], fontName="Times-Bold",
        fontSize=13, leading=16, spaceBefore=12, spaceAfter=8)
    s["h2"] = ParagraphStyle("TH2", parent=base["Heading2"], fontName="Times-Bold",
        fontSize=11.5, leading=14, spaceBefore=11, spaceAfter=5)
    s["h3"] = ParagraphStyle("TH3", parent=base["Heading3"], fontName="Times-Bold",
        fontSize=10.5, leading=13, spaceBefore=6, spaceAfter=3)
    s["body"] = ParagraphStyle("TBody", parent=base["Normal"], fontName="Times-Roman",
        fontSize=11, leading=15.8, alignment=TA_JUSTIFY, spaceAfter=9)
    s["bullet"] = ParagraphStyle("TBullet", parent=s["body"], leftIndent=12, spaceAfter=3)
    s["script"] = ParagraphStyle("TScript", parent=s["body"], leftIndent=6, rightIndent=6,
        fontName="Times-Italic", spaceBefore=3, spaceAfter=5, leading=13)
    s["qa_q"] = ParagraphStyle("TQAQ", parent=s["body"], fontName="Times-Bold", spaceBefore=6, spaceAfter=1)
    s["qa_a"] = ParagraphStyle("TQAA", parent=s["body"], leftIndent=6, spaceAfter=4)
    s["code"] = ParagraphStyle("TCode", parent=base["Code"], fontName="Courier", fontSize=7.5,
        leading=9.5, leftIndent=4, spaceBefore=3, spaceAfter=6, backColor=colors.HexColor("#f0f0f0"))
    s["caption"] = ParagraphStyle("TCap", parent=base["Normal"], fontName="Times-Italic",
        fontSize=8.5, leading=10, alignment=TA_CENTER, spaceBefore=1, spaceAfter=8)
    s["toc"] = ParagraphStyle("TToc", parent=s["body"], fontSize=10.5, leading=15, spaceAfter=2)
    s["cheat"] = ParagraphStyle("TCheat", parent=s["body"], fontSize=9.5, leading=13, spaceAfter=2)
    return s


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 8)
    canvas.drawCentredString(PAGE[0] / 2, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def make_doc(path: Path, title: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    return SimpleDocTemplate(str(path), pagesize=PAGE, leftMargin=LEFT, rightMargin=RIGHT,
        topMargin=TOP, bottomMargin=BOTTOM, title=title,
        author="Thesis explanation guide (outsourcing lane)")


def P(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def simple_table(rows, col_widths=None):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 11.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#888888")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def hr():
    return HRFlowable(width="100%", thickness=0.55, color=colors.HexColor("#aaaaaa"),
                      spaceBefore=3, spaceAfter=6)


def code_block(text, st):
    return Preformatted(text.rstrip() + "\n", st["code"])


def title_page(story, st, meta):
    story.append(Spacer(1, 0.9 * inch))
    story.append(P(meta["doc_label"], st["subtitle"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(P(meta["title"], st["title"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(hr())
    for line in [
        f"<b>Student:</b> {meta['student']}",
        f"<b>Student ID:</b> {meta['student_id']}",
        f"<b>Programme:</b> MSc in Cloud Computing, National College of Ireland (NCI)",
        f"<b>Artefact folder:</b> <font face='Courier'>{meta['artefact']}</font>",
        f"<b>Baseline:</b> {meta['baseline']}",
        f"<b>Purpose:</b> Speakable simple-English guide so a friend can brief a professor.",
        f"<b>Rule:</b> Numbers come only from STATUS / live results — nothing invented.",
    ]:
        story.append(P(line, st["subtitle"]))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 0.25 * inch))
    story.append(P("How to use this document", st["h2"]))
    story.append(P(
        "Sections 1–5 are the story. Section 6 is vocabulary with analogies. "
        "Sections 12–13 are speaking scripts and exact professor answers. "
        "Section 14 is honest STATUS. Section 15 is a one-page cheat sheet for the viva.",
        st["body"]))
    story.append(PageBreak())


def toc_page(story, st, sections):
    story.append(P("Contents", st["h1"]))
    story.append(hr())
    for i, name in enumerate(sections, 1):
        story.append(P(f"{i}. {name}", st["toc"]))
    story.append(PageBreak())


def add_qa(story, st, pairs):
    for q, a in pairs:
        story.append(P(f"Q. {q}", st["qa_q"]))
        story.append(P(f"A. {a}", st["qa_a"]))
