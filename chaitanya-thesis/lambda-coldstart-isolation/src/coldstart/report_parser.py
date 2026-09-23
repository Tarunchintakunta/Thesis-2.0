"""Parse Lambda REPORT lines (the isolation gate: Init Duration present or not).

    REPORT RequestId: 3f5a...  Duration: 12.34 ms  Billed Duration: 13 ms  Memory Size: 512 MB
    Max Memory Used: 71 MB  Init Duration: 245.67 ms  [XRAY TraceId: ...]

Classification rule : an invocation is COLD if and only if
its REPORT line carries an ``Init Duration``. What the invoker *intended*
(an idle gap meant to force a cold start) does not matter - platform reuse is
outside the experimenter's control, so intended-cold invocations that came
back warm are counted and reported, not analysed as cold.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass

REPORT_RE = re.compile(
    r"REPORT RequestId:\s*(?P<request_id>[0-9a-fA-F-]+)\s+"
    r"Duration:\s*(?P<duration>[\d.]+)\s*ms\s+"
    r"Billed Duration:\s*(?P<billed>\d+)\s*ms\s+"
    r"Memory Size:\s*(?P<memory>\d+)\s*MB\s+"
    r"Max Memory Used:\s*(?P<max_used>\d+)\s*MB"
    r"(?:\s+Init Duration:\s*(?P<init>[\d.]+)\s*ms)?"
)


@dataclass(frozen=True)
class Report:
    request_id: str
    duration_ms: float
    billed_ms: int
    memory_mb: int
    max_memory_used_mb: int
    init_ms: float | None

    @property
    def cold(self) -> bool:
        return self.init_ms is not None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["cold"] = self.cold
        return d


def parse_report(line: str) -> Report | None:
    m = REPORT_RE.search(line)
    if not m:
        return None
    init = m.group("init")
    return Report(
        request_id=m.group("request_id"),
        duration_ms=float(m.group("duration")),
        billed_ms=int(m.group("billed")),
        memory_mb=int(m.group("memory")),
        max_memory_used_mb=int(m.group("max_used")),
        init_ms=float(init) if init is not None else None,
    )


def parse_log_text(text: str) -> list[Report]:
    """All REPORT lines in a block of log text (e.g. the base64-decoded LogResult)."""
    out = []
    for line in text.splitlines():
        rep = parse_report(line)
        if rep is not None:
            out.append(rep)
    return out
