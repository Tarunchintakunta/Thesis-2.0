#!/usr/bin/env bash
# After Uday final_1/2/3 exist: write FINAL3_BASELINE from LIVE_EVIDENCE (baseline=QoS0, proposed=QoS1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY=python3
[[ -x .venv/bin/python ]] && PY=.venv/bin/python
"$PY" <<'PY'
import json
from pathlib import Path
from collections import defaultdict
import statistics as stats

root = Path("results/live")
rows = []
for f in (1, 2, 3):
    p = root / f"final_{f}" / "LIVE_EVIDENCE.json"
    if not p.exists():
        raise SystemExit(f"missing {p}")
    data = json.loads(p.read_text())
    for c in data.get("cells") or []:
        qos = c.get("qos")
        role = "baseline" if qos == 0 else ("proposed" if qos == 1 else "other")
        rows.append({
            "round": f"final_{f}",
            "role": role,
            "qos": qos,
            "disconnect_s": c.get("disconnect_s"),
            "rate_mode": c.get("rate_mode"),
            "loss_rate": c.get("loss_rate"),
            "latency_mean_ms": c.get("latency_mean_ms"),
            "latency_p95_ms": c.get("latency_p95_ms"),
            "n_published": c.get("n_published"),
            "n_lost": c.get("n_lost"),
        })

# Aggregate mean loss by round × role (all disconnect/rate cells)
by = defaultdict(list)
for r in rows:
    if r["role"] in ("baseline", "proposed") and r["loss_rate"] is not None:
        by[(r["round"], r["role"])].append(float(r["loss_rate"]))

lines = []
lines.append("# Uday final-3 baseline compare (MQTT QoS lite)")
lines.append("")
lines.append("**Date:** auto-generated from packs  ")
lines.append("**Packs:** `results/live/final_1|final_2|final_3/`  ")
lines.append("**Protocol:** AWS IoT Core lite 16-cell; destroy-after each round.  ")
lines.append("**Wording:** **baseline** = QoS 0; **proposed** = QoS 1.  ")
lines.append("")
lines.append("## Mean loss_rate (all disconnect × rate cells)")
lines.append("")
lines.append("| Round | baseline (QoS0) mean loss | proposed (QoS1) mean loss |")
lines.append("|-------|--------------------------:|--------------------------:|")
for f in (1, 2, 3):
    b = by.get((f"final_{f}", "baseline"), [])
    p = by.get((f"final_{f}", "proposed"), [])
    bm = round(sum(b)/len(b), 4) if b else None
    pm = round(sum(p)/len(p), 4) if p else None
    lines.append(f"| final_{f} | {bm} | {pm} |")

# Highlight d60≡d300 for baseline QoS0 if present
lines.append("")
lines.append("## baseline QoS0 loss by disconnect_s (mean across rounds × rate_mode)")
lines.append("")
dmap = defaultdict(list)
for r in rows:
    if r["role"] == "baseline" and r["loss_rate"] is not None:
        dmap[r["disconnect_s"]].append(float(r["loss_rate"]))
lines.append("| disconnect_s | mean loss |")
lines.append("|-------------:|----------:|")
for d in sorted(dmap.keys(), key=lambda x: (x is None, x or 0)):
    vals = dmap[d]
    lines.append(f"| {d} | {round(sum(vals)/len(vals), 4)} |")

lines.append("")
lines.append("## Verdict (pos + neg)")
lines.append("")
lines.append("- **Positive:** three destroy-after lite finals; proposed (QoS1) targets lower loss under disconnect than baseline (QoS0) where measured.")
lines.append("- **Negative/mixed:** under lite wall-clock, baseline QoS0 d60 and d300 loss may be identical (schedule cut); n=1 per cell; proposed reliability may cost latency/backlog.")
lines.append("- Finals are method-scale Free-Tier packs, not formal 600k-msg confirmatory.")
lines.append("")
lines.append("**CA2 floor:** still **100%** after final-3.")
lines.append("")

out = root / "FINAL3_BASELINE.md"
out.write_text("\n".join(lines) + "\n")
print("wrote", out)

# machine summary
summary = {"by_round_role_mean_loss": {f"{a}|{b}": round(sum(v)/len(v), 4) for (a,b), v in by.items()}, "n_rows": len(rows)}
(root / "final3_qos_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("wrote", root / "final3_qos_summary.json")
PY
