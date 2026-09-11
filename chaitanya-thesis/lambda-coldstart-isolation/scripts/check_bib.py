#!/usr/bin/env python
"""Citation gate: every entry in bib/references.bib must resolve.

    python scripts/check_bib.py            # needs internet
    python scripts/check_bib.py --offline  # only structure checks (used in CI)

DOI entries are resolved through doi.org content negotiation and the returned
title is compared with the one in the file. URL-only entries (USENIX) must
return HTTP 200 and contain the title words.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIB = ROOT / "bib" / "references.bib"


def parse_bib(text: str) -> list[dict]:
    entries = []
    for chunk in re.split(r"\n(?=@)", text):
        m = re.match(r"\s*@(\w+)\{([^,]+),", chunk)
        if not m:
            continue
        fields = dict(re.findall(r"(\w+)=\{((?:[^{}]|\{[^{}]*\})*)\}", chunk))
        entries.append({"type": m.group(1), "key": m.group(2), **{k.lower(): v for k, v in fields.items()}})
    return entries


def _words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3}


def check_online(entry: dict) -> tuple[bool, str]:
    if entry.get("doi"):
        req = urllib.request.Request(f"https://doi.org/{entry['doi']}",
                                     headers={"Accept": "application/vnd.citationstyles.csl+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            meta = json.load(r)
        title = meta.get("title", "")
        title = title[0] if isinstance(title, list) else title
        # ACM splits "SeBS: a serverless benchmark ..." into title + subtitle
        title = " ".join([title, *meta.get("subtitle", [])])
    else:
        # usenix.org answers 403 to the default python user agent
        req = urllib.request.Request(entry["url"], headers={"User-Agent": "Mozilla/5.0 (citation check)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            title = r.read().decode("utf-8", "replace") if r.status == 200 else ""
    want = _words(entry["title"])
    overlap = len(want & _words(title)) / max(1, len(want))
    return overlap >= 0.8, f"title overlap {overlap:.0%}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args(argv)
    entries = parse_bib(BIB.read_text())
    keys = [e["key"] for e in entries]
    recent = [e for e in entries if 2022 <= int(e.get("year", 0)) <= 2026]
    problems = []
    if len(set(keys)) != len(keys):
        problems.append("duplicate keys")
    if len(recent) < 20:
        problems.append(f"only {len(recent)} entries from 2022-2026 (need >= 20)")
    for e in entries:
        if not (e.get("doi") or e.get("url")):
            problems.append(f"{e['key']}: no DOI or URL")
    if not any(e.get("doi", "").lower() == "10.24425/ijet.2025.153619" for e in entries):
        problems.append("baseline paper missing")
    print(f"{len(entries)} entries, {len(recent)} from 2022-2026")
    if not args.offline:
        for e in entries:
            try:
                ok, why = check_online(e)
            except Exception as exc:  # noqa: BLE001 - report and carry on
                ok, why = False, f"error {exc}"
            print(f"  {'ok ' if ok else 'BAD'} {e['key']:28s} {why}")
            if not ok:
                problems.append(f"{e['key']}: {why}")
    for p in problems:
        print("PROBLEM:", p)
    print("citation gate:", "PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
