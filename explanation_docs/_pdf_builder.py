#!/usr/bin/env python3
"""Shared reportlab builder for speakable explanation guides (A4, ~11pt, 1-inch margins)."""
from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted,
    Table, TableStyle, KeepTogether, ListFlowable, ListItem, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

MARGIN = inch


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "GuideTitle", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "GuideSub", parent=base["Normal"], fontName="Helvetica",
            fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=6,
        ),
        "meta": ParagraphStyle(
            "GuideMeta", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "GuideH1", parent=base["Heading1"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, spaceBefore=16, spaceAfter=8,
            textColor=colors.HexColor("#1a1a1a"),
        ),
        "h2": ParagraphStyle(
            "GuideH2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=12, leading=16, spaceBefore=12, spaceAfter=6,
            textColor=colors.HexColor("#222222"),
        ),
        "h3": ParagraphStyle(
            "GuideH3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "GuideBody", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=15, alignment=TA_JUSTIFY, spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "GuideBullet", parent=base["Normal"], fontName="Helvetica",
            fontSize=11, leading=15, leftIndent=18, spaceAfter=3,
        ),
        "script": ParagraphStyle(
            "GuideScript", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=11, leading=15, leftIndent=12, rightIndent=12,
            spaceBefore=4, spaceAfter=8, backColor=colors.HexColor("#f5f5f5"),
            borderPadding=6,
        ),
        "code": ParagraphStyle(
            "GuideCode", parent=base["Code"], fontName="Courier",
            fontSize=8.5, leading=11, leftIndent=6, spaceBefore=4, spaceAfter=8,
            backColor=colors.HexColor("#f0f0f0"),
        ),
        "caption": ParagraphStyle(
            "GuideCap", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=9, leading=12, alignment=TA_CENTER, spaceAfter=10,
        ),
        "footer": ParagraphStyle(
            "GuideFooter", parent=base["Normal"], fontName="Helvetica",
            fontSize=8, leading=10, alignment=TA_CENTER,
        ),
        "cheat": ParagraphStyle(
            "GuideCheat", parent=base["Normal"], fontName="Helvetica",
            fontSize=10, leading=13, spaceAfter=4,
        ),
    }
    return styles


class GuideDoc:
    def __init__(self, path: Path, student: str):
        self.path = Path(path)
        self.student = student
        self.styles = _styles()
        self.story = []
        self._page_count = 0

    def title_page(self, name, sid, title, extra_lines=None):
        s = self.styles
        self.story.append(Spacer(1, 1.5 * inch))
        self.story.append(Paragraph("Explanation Guide", s["title"]))
        self.story.append(Paragraph("for viva / weekly explanation", s["subtitle"]))
        self.story.append(Spacer(1, 0.4 * inch))
        self.story.append(HRFlowable(width="80%", thickness=1, color=colors.grey, spaceBefore=4, spaceAfter=12))
        self.story.append(Paragraph(self._esc(title), s["title"]))
        self.story.append(Spacer(1, 0.35 * inch))
        self.story.append(Paragraph(self._esc(name), s["meta"]))
        self.story.append(Paragraph(f"Student ID: {sid}", s["meta"]))
        self.story.append(Paragraph("MSc Cloud Computing — National College of Ireland", s["meta"]))
        self.story.append(Paragraph("Research Project — Speakable Explanation Pack", s["meta"]))
        if extra_lines:
            self.story.append(Spacer(1, 0.25 * inch))
            for line in extra_lines:
                self.story.append(Paragraph(self._esc(line), s["meta"]))
        self.story.append(Spacer(1, 0.5 * inch))
        self.story.append(Paragraph(
            "How to use this guide: read it aloud in simple English. "
            "Every number here is taken from STATUS.md / results files in the repo. "
            "If a number is not in those files, this guide says “planned” or “measured as …”. "
            "Do not invent live AWS metrics in class.",
            s["body"],
        ))
        self.story.append(PageBreak())

    def h1(self, text):
        self.story.append(Paragraph(self._esc(text), self.styles["h1"]))

    def h2(self, text):
        self.story.append(Paragraph(self._esc(text), self.styles["h2"]))

    def h3(self, text):
        self.story.append(Paragraph(self._esc(text), self.styles["h3"]))

    def p(self, text):
        self.story.append(Paragraph(self._esc(text), self.styles["body"]))

    def script(self, text):
        # italic speakable script
        self.story.append(Paragraph(f"<i>“{self._esc(text)}”</i>", self.styles["body"]))

    def bullets(self, items):
        for it in items:
            self.story.append(Paragraph(f"• {self._esc(it)}", self.styles["bullet"]))
        self.story.append(Spacer(1, 4))

    def code(self, text, label=None):
        if label:
            self.story.append(Paragraph(f"<b>{self._esc(label)}</b>", self.styles["caption"]))
        self.story.append(Preformatted(text.rstrip() + "\n", self.styles["code"]))

    def table(self, headers, rows, col_widths=None):
        s = self.styles
        data = [[Paragraph(f"<b>{self._esc(h)}</b>", s["cheat"]) for h in headers]]
        for row in rows:
            data.append([Paragraph(self._esc(str(c)), s["cheat"]) for c in row])
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        self.story.append(t)
        self.story.append(Spacer(1, 10))

    def pagebreak(self):
        self.story.append(PageBreak())

    def spacer(self, h=8):
        self.story.append(Spacer(1, h))

    @staticmethod
    def _esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )

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
                A4[0] / 2, 0.55 * inch,
                f"{student} — Explanation Guide — page {doc_.page}",
            )
            canvas.restoreState()

        doc.build(self.story, onFirstPage=_footer, onLaterPages=_footer)
        return self.path
