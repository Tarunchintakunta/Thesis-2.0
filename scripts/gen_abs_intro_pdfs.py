#!/usr/bin/env python3
"""Generate four Abstract+Introduction PDFs with ONE shared Times New Roman style via pandoc."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

BASE = Path("/Users/tarunchintakunta/Desktop/Thesis2.0")
DESKTOP = Path("/Users/tarunchintakunta/Desktop")
NEXT_WEEK = BASE / "rewrites_next_week"
PANDOC = "/opt/anaconda3/bin/pandoc"
CSS = BASE / "scripts" / "abs_intro_shared.css"

STUDENTS = [
    {
        "key": "anji",
        "md": BASE / "anji-thesis/rewrites/Abstract_Introduction_CA2_revised.md",
        "pdf_name": "Anji_Abstract_Introduction_revised.pdf",
        "local_dir": BASE / "anji-thesis/rewrites",
    },
    {
        "key": "mehak",
        "md": BASE / "mehak-thesis/rewrites/Abstract_Introduction_CA2_revised.md",
        "pdf_name": "Mehak_Abstract_Introduction_revised.pdf",
        "local_dir": BASE / "mehak-thesis/rewrites",
    },
    {
        "key": "pooja",
        "md": BASE / "pooja-thesis/rewrites/Abstract_Introduction_CA2_revised.md",
        "pdf_name": "Pooja_Abstract_Introduction_revised.pdf",
        "local_dir": BASE / "pooja-thesis/rewrites",
    },
    {
        "key": "yashaswini",
        "md": BASE / "yashaswini-thesis/rewrites/Abstract_Introduction_CA2_revised.md",
        "pdf_name": "Yashaswini_Abstract_Introduction_revised.pdf",
        "local_dir": BASE / "yashaswini-thesis/rewrites",
    },
]


def abstract_word_count(md_path: Path) -> int:
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"^## Abstract\s*\n+(.*?)(?=\n## |\Z)", text, re.S | re.M)
    if not m:
        raise ValueError(f"No Abstract section in {md_path}")
    body = m.group(1).strip()
    if "\n\n" in body:
        raise ValueError(f"Abstract must be one continuous paragraph: {md_path}")
    return len(body.split())


def build_pdf(md: Path, out: Path) -> None:
    cmd = [
        PANDOC,
        str(md),
        "-o",
        str(out),
        "--pdf-engine=xelatex",
        "-V",
        "mainfont=Times New Roman",
        "-V",
        "monofont=Times New Roman",
        "-V",
        "geometry:margin=1in",
        "-V",
        "fontsize=12pt",
        "-V",
        "linestretch=1.5",
        "-V",
        "colorlinks=false",
        f"--css={CSS}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"pandoc failed for {md}:\n{r.stderr}")


def main() -> None:
    NEXT_WEEK.mkdir(parents=True, exist_ok=True)
    for s in STUDENTS:
        n = abstract_word_count(s["md"])
        if n > 180:
            raise SystemExit(f"{s['key']} abstract has {n} words (>180)")
        print(f"=== {s['key']} abstract={n} words ===", flush=True)
        primary = DESKTOP / s["pdf_name"]
        build_pdf(s["md"], primary)
        for t in [NEXT_WEEK / s["pdf_name"], s["local_dir"] / s["pdf_name"]]:
            shutil.copy2(primary, t)
        print(f"  wrote {s['pdf_name']} ({primary.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
