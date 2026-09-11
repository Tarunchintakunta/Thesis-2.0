#!/usr/bin/env python
"""Citation check for bib/references.bib.

    python scripts/check_bib.py            # resolves every DOI / URL (needs internet)
    python scripts/check_bib.py --offline  # structure only (CI)

Rules from the master prompt section 4: the 21 listed scholarly items
(2022-2026), the 3 AWS documentation pages, and at most the two optional
pre-2022 items (Wang et al. 2021, Burckhardt et al. 2021). Every entry has a
DOI or URL, and the baseline Qi et al. (2025) TOCS paper is present.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

BIB = Path(__file__).resolve().parents[1] / "bib" / "references.bib"
BASELINE_DOI = "10.1145/3725985"
OPTIONAL = {"wang2021kafka", "burckhardt2021durable"}


def parse_bib(text: str) -> list[dict]:
    out = []
    for chunk in re.split(r"\n(?=@)", text):
        m = re.match(r"\s*@(\w+)\{([^,]+),", chunk)
        if not m:
            continue
        fields = dict(re.findall(r"(\w+)=\{((?:[^{}]|\{[^{}]*\})*)\}", chunk))
        out.append({"type": m.group(1), "key": m.group(2), **{k.lower(): v for k, v in fields.items()}})
    return out


def _words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3}


def resolve(e: dict) -> tuple[bool, str]:
    if e.get("doi"):
        req = urllib.request.Request(f"https://doi.org/{e['doi']}",
                                     headers={"Accept": "application/vnd.citationstyles.csl+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            meta = json.load(r)
        title = meta.get("title", "")
        title = " ".join([title[0] if isinstance(title, list) else title, *meta.get("subtitle", [])])
    else:
        req = urllib.request.Request(e["url"], headers={"User-Agent": "Mozilla/5.0 (citation check)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.headers.get_content_type() == "application/pdf":
                return r.status == 200, "pdf reachable"
            title = r.read().decode("utf-8", "replace")
    want = _words(e["title"].replace("{", "").replace("}", ""))
    share = len(want & _words(title)) / max(1, len(want))
    return share >= 0.8, f"title overlap {share:.0%}"


def check(entries: list[dict]) -> list[str]:
    problems = []
    docs = [e for e in entries if e["key"].startswith("aws")]
    optional = [e for e in entries if e["key"] in OPTIONAL]
    scholarly = [e for e in entries if e not in docs and e not in optional]
    if len({e["key"] for e in entries}) != len(entries):
        problems.append("duplicate keys")
    if len(scholarly) != 21:
        problems.append(f"{len(scholarly)} scholarly entries, the master prompt lists 21")
    if len(docs) != 3:
        problems.append(f"{len(docs)} AWS documentation entries, the master prompt lists 3")
    if any(not 2022 <= int(e.get("year", 0)) <= 2026 for e in scholarly):
        problems.append("a scholarly entry is outside 2022-2026")
    if not any(e.get("doi", "").lower() == BASELINE_DOI for e in entries):
        problems.append("baseline Qi et al. (2025) missing")
    for e in entries:
        if not (e.get("doi") or e.get("url")):
            problems.append(f"{e['key']}: no DOI or URL")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args(argv)
    entries = parse_bib(BIB.read_text())
    problems = check(entries)
    n_opt = sum(e["key"] in OPTIONAL for e in entries)
    n_docs = sum(e["key"].startswith("aws") for e in entries)
    print(f"{len(entries)} entries ({len(entries) - n_opt - n_docs} scholarly 2022-2026 + {n_docs} AWS docs"
          f" + {n_opt} optional pre-2022)")
    if not args.offline:
        for e in entries:
            try:
                ok, why = resolve(e)
            except Exception as exc:  # noqa: BLE001
                ok, why = False, f"error {exc}"
            print(f"  {'ok ' if ok else 'BAD'} {e['key']:26s} {why}")
            if not ok:
                problems.append(f"{e['key']}: {why}")
    for p in problems:
        print("PROBLEM:", p)
    print("citation check:", "PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
