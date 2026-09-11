"""Daily spend cap (ethics/budget gate).

Every invocation's estimated cost is appended to a spend log CSV. Before each
invocation the guard adds the worst case of the next call (timeout x memory)
to today's total (UTC day) and stops the run if that would pass the cap.
"""
from __future__ import annotations

import csv
import datetime as dt
from pathlib import Path

from .cost_model import invocation_cost, load_prices

FIELDS = ["utc_day", "t", "mode", "function", "memory_mb", "billed_ms", "usd"]


class BudgetExceeded(RuntimeError):
    pass


def _day(t: float) -> str:
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")


class BudgetGuard:
    def __init__(self, daily_usd: float, log_path: str | Path, mode: str, arch: str = "arm64",
                 prices: dict | None = None, timeout_s: float = 30.0):
        self.daily_usd = float(daily_usd)
        self.log_path = Path(log_path)
        self.mode = mode
        self.arch = arch
        self.prices = prices or load_prices(None)
        self.timeout_ms = timeout_s * 1000
        self._totals: dict[str, float] = {}
        if self.log_path.exists():
            with open(self.log_path, newline="") as fh:
                for row in csv.DictReader(fh):
                    self._totals[row["utc_day"]] = self._totals.get(row["utc_day"], 0.0) + float(row["usd"])

    def spent(self, t: float) -> float:
        return self._totals.get(_day(t), 0.0)

    def check(self, t: float, memory_mb: int) -> None:
        worst = invocation_cost(self.timeout_ms, memory_mb, self.arch, self.prices)
        if self.spent(t) + worst > self.daily_usd:
            raise BudgetExceeded(f"daily cap ${self.daily_usd:.2f} reached "
                                 f"(spent ${self.spent(t):.4f} on {_day(t)})")

    def charge(self, t: float, function: str, memory_mb: int, billed_ms: float) -> float:
        usd = invocation_cost(billed_ms, memory_mb, self.arch, self.prices)
        day = _day(t)
        self._totals[day] = self._totals.get(day, 0.0) + usd
        new = not self.log_path.exists()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            if new:
                w.writeheader()
            w.writerow({"utc_day": day, "t": round(t, 3), "mode": self.mode, "function": function,
                        "memory_mb": memory_mb, "billed_ms": round(billed_ms, 3), "usd": f"{usd:.10f}"})
        return usd
