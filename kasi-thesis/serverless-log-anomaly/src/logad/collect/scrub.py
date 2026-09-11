"""Strip request / account identifiers before any analysis (privacy gate).

Request ids, account ids and IP addresses are replaced with fixed tokens. The
masked lines are what the parser sees; raw lines never leave data/raw/.
"""
from __future__ import annotations

import re

_PATTERNS = [
    (re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"), "<RID>"),
    (re.compile(r"(?<![0-9])[0-9]{12}(?![0-9])"), "<ACCT>"),
    (re.compile(r"(?<![0-9.])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9.])"), "<IP>"),
    (re.compile(r"ord-[0-9a-f]{12}"), "<ORDER>"),
]


def scrub(line: str) -> str:
    for pattern, token in _PATTERNS:
        line = pattern.sub(token, line)
    return line


def has_identifiers(line: str) -> bool:
    return any(p.search(line) for p, _ in _PATTERNS)
