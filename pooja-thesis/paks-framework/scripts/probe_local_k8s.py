#!/usr/bin/env python3
"""Probe local Kubernetes options (kind / minikube / docker / kubectl).

Never starts a cluster or mutates AWS. Writes results/K8S_LOCAL_PROBE.md.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
OUT_MD = FRAMEWORK_ROOT / "results" / "K8S_LOCAL_PROBE.md"
OUT_JSON = FRAMEWORK_ROOT / "results" / "k8s_local_probe.json"


def _which(name: str) -> str | None:
    return shutil.which(name)


def _run(cmd: list[str], timeout: int = 8) -> dict:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": (proc.stdout or "")[:2000],
            "stderr": (proc.stderr or "")[:2000],
        }
    except Exception as exc:  # noqa: BLE001 — probe must never crash the formal path
        return {"cmd": cmd, "returncode": -1, "error": str(exc)}


def main() -> int:
    probe = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "binaries": {
            "kind": _which("kind"),
            "minikube": _which("minikube"),
            "kubectl": _which("kubectl"),
            "docker": _which("docker"),
        },
        "docker_info": _run(["docker", "info"]),
        "kubectl_cluster": _run(["kubectl", "cluster-info"]),
        "kind_version": _run(["kind", "version"]) if _which("kind") else None,
        "minikube_version": _run(["minikube", "version"]) if _which("minikube") else None,
    }
    docker_ok = probe["docker_info"].get("returncode") == 0
    kind_ok = bool(probe["binaries"]["kind"]) and docker_ok
    minikube_ok = bool(probe["binaries"]["minikube"]) and docker_ok
    live_possible = kind_ok or minikube_ok
    probe["verdict"] = {
        "live_kind_possible": kind_ok,
        "live_minikube_possible": minikube_ok,
        "live_apply_this_pass": False,
        "reason": (
            "kind+docker ready"
            if kind_ok
            else "minikube+docker ready"
            if minikube_ok
            else "kind/minikube missing and/or Docker daemon not running — stay on dry-run"
        ),
    }

    FRAMEWORK_ROOT.joinpath("results").mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(probe, indent=2) + "\n")

    lines = [
        "# Local Kubernetes probe — Pooja PAKS",
        "",
        f"**UTC:** {probe['timestamp_utc']}",
        "",
        "## Verdict",
        "",
        f"- Live kind apply possible: **{kind_ok}**",
        f"- Live minikube apply possible: **{minikube_ok}**",
        f"- Live apply performed this pass: **False**",
        f"- Reason: {probe['verdict']['reason']}",
        "",
        "## Binaries",
        "",
        f"- kind: `{probe['binaries']['kind']}`",
        f"- minikube: `{probe['binaries']['minikube']}`",
        f"- kubectl: `{probe['binaries']['kubectl']}`",
        f"- docker: `{probe['binaries']['docker']}`",
        "",
        "## Docker daemon",
        "",
        "```",
        (probe["docker_info"].get("stderr") or probe["docker_info"].get("stdout") or "")[:800]
        or str(probe["docker_info"].get("error", "")),
        "```",
        "",
        "## kubectl cluster-info",
        "",
        "```",
        (probe["kubectl_cluster"].get("stderr") or probe["kubectl_cluster"].get("stdout") or "")[:800],
        "```",
        "",
        "## Implication for formal CA2",
        "",
        "Formal method still requires a Kubernetes environment (AWS EC2 + S3 + CloudWatch).",
        "This host cannot raise dry-run → live scale patches without kind/minikube **and** a",
        "running Docker (or another container runtime). Adaptive Scale JSON remains recorded",
        "under `formal_k8s_dry_run.json` with `live_apply=false`.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_MD}")
    print(f"live_possible={live_possible} reason={probe['verdict']['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
