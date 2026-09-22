#!/usr/bin/env bash
# Nemi Docker FL regression for rounds listed (default 1 2 3).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT_ROOT="$ROOT/results/docker_fl"
mkdir -p "$OUT_ROOT"
ROUNDS=("$@")
if [[ ${#ROUNDS[@]} -eq 0 ]]; then ROUNDS=(1 2 3); fi
LOG="$OUT_ROOT/regression_continue.log"
exec > >(tee -a "$LOG") 2>&1

need() { command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }; }
need docker

echo "=== Nemi Docker rounds ${ROUNDS[*]} $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
for r in "${ROUNDS[@]}"; do
  dest="$OUT_ROOT/final_$r"
  mkdir -p "$dest"
  echo "=== round $r → $dest ==="
  docker compose down -v --remove-orphans || true
  rm -f "$OUT_ROOT/docker_fl_summary.json"
  docker compose up --build -d
  for _w in $(seq 1 240); do
    if [[ -f "$OUT_ROOT/docker_fl_summary.json" ]]; then
      echo "summary ready after ${_w}s"
      break
    fi
    sleep 1
  done
  if [[ -f "$OUT_ROOT/docker_fl_summary.json" ]]; then
    cp -f "$OUT_ROOT/docker_fl_summary.json" "$dest/docker_fl_summary.json"
  else
    docker cp securefl-orchestrator:/shared/docker_fl_summary.json "$dest/docker_fl_summary.json" \
      || docker cp securefl-orchestrator:/out/docker_fl_summary.json "$dest/docker_fl_summary.json"
  fi
  docker compose down -v --remove-orphans || true
  test -f "$dest/docker_fl_summary.json"
  python3 - "$dest/docker_fl_summary.json" "$r" <<'PY'
import json, sys
from datetime import datetime, timezone
p, r = sys.argv[1], int(sys.argv[2])
d = json.load(open(p))
d["regression_round"] = r
d["collected_at"] = datetime.now(timezone.utc).isoformat()
open(p, "w").write(json.dumps(d, indent=2) + "\n")
print(json.dumps({k: d.get(k) for k in ("regression_round","accuracy","f1","elapsed_s")}, indent=2))
PY
done

python3 - "$OUT_ROOT" <<'PY'
import json
from pathlib import Path
from datetime import datetime, timezone
root = Path(sys.argv[1])
rows = []
for r in (1, 2, 3):
    p = root / f"final_{r}" / "docker_fl_summary.json"
    if p.exists():
        rows.append(json.loads(p.read_text()))
lines = [
    "# Nemi Docker FL final-3 baseline (multi-container)",
    "",
    f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
    "**Artefact:** docker-compose.yml + scripts/run_docker_fl_worker.py",
    "**Note:** Not Kubernetes; separate containers + FedAvg via shared volume.",
    "",
    "| Round | accuracy | F1 | elapsed_s | clients |",
    "|------:|---------:|---:|----------:|--------:|",
]
for d in rows:
    lines.append(
        f"| {d.get('regression_round')} | {d.get('accuracy'):.4f} | {d.get('f1'):.4f} | "
        f"{d.get('elapsed_s'):.3f} | {d.get('num_clients')} |"
    )
if rows:
    accs = [d["accuracy"] for d in rows]
    f1s = [d["f1"] for d in rows]
    lines += ["", "## Verdict", f"- Rounds present: {len(rows)}/3",
              f"- Accuracy range: {min(accs):.4f}–{max(accs):.4f}",
              f"- F1 range: {min(f1s):.4f}–{max(f1s):.4f}",
              "- Residual: Kubernetes still Not met if CA2 requires K8s.", ""]
(root / "DOCKER_FINAL3_BASELINE.md").write_text("\n".join(lines) + "\n")
print((root / "DOCKER_FINAL3_BASELINE.md").read_text())
PY
echo "NEMI_DOCKER_CONTINUE_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)"
