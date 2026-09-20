#!/usr/bin/env python3
"""Run tfsec (shipped defaults) over the labelled corpus. No terraform apply."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.io_util import CORPUS, RESULTS, load_id_map, load_labels, module_dir  # noqa: E402


def find_tfsec() -> str:
    env = os.environ.get("TFSEC_BIN")
    if env:
        return env
    found = shutil.which("tfsec")
    if found:
        return found
    extra = Path.home() / ".local/bin/tfsec"
    if extra.exists():
        return str(extra)
    raise SystemExit("tfsec not found on PATH; set TFSEC_BIN")


def tfsec_version(bin_path: str) -> str:
    return subprocess.check_output([bin_path, "--version"], text=True).strip()


def run_batch(bin_path: str) -> dict:
    RESULTS.mkdir(parents=True, exist_ok=True)
    raw_path = RESULTS / "raw" / "tfsec_batch.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        bin_path,
        str(CORPUS),
        "--format",
        "json",
        "--soft-fail",
        "--no-colour",
        "--exclude-downloaded-modules",
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - t0
    payload = proc.stdout or proc.stderr
    raw_path.write_text(payload, encoding="utf-8")
    try:
        data = json.loads(payload) if payload.strip() else {}
    except json.JSONDecodeError:
        data = {"parse_error": True, "stdout_head": payload[:4000]}
    return {"elapsed_s": elapsed, "returncode": proc.returncode, "data": data}


def index_by_module(data, rows) -> dict[str, list[dict]]:
    by_mod = {r["module_id"]: [] for r in rows}
    results = []
    if isinstance(data, dict):
        results = data.get("results") or data.get("issues") or []
    for item in results:
        loc = item.get("location") or {}
        fpath = loc.get("filename") or item.get("location_filename") or ""
        rule = (
            item.get("rule_id")
            or item.get("long_id")
            or item.get("rule_id".upper(), "")
            or ""
        )
        long_id = item.get("long_id") or ""
        ids = {rule, long_id, item.get("rule_description", "")}
        module_id = None
        for r in rows:
            token = f"/{r['module_id']}/"
            if token in fpath.replace("\\", "/"):
                module_id = r["module_id"]
                break
        if module_id is None:
            continue
        by_mod[module_id].append(
            {
                "check_id": long_id or rule,
                "ids": [x for x in ids if x],
                "severity": item.get("severity") or "",
                "resource": (item.get("resource") or loc.get("resource") or ""),
            }
        )
    return by_mod


def verdicts(rows, by_mod, id_map):
    out = []
    unmatched: dict[str, int] = {}
    for r in rows:
        mapped = id_map.get(r["category"], set())
        hits = []
        for chk in by_mod.get(r["module_id"], []):
            candidates = set(chk.get("ids") or []) | {chk.get("check_id")}
            if candidates & mapped:
                hits.append(chk)
            else:
                key = chk.get("check_id") or "unknown"
                unmatched[key] = unmatched.get(key, 0) + 1
        out.append(
            {
                "module_id": r["module_id"],
                "category": r["category"],
                "label": r["label"],
                "predicted": 1 if hits else 0,
                "n_mapped_findings": len(hits),
                "n_all_findings": len(by_mod.get(r["module_id"], [])),
                "mapped_check_ids": sorted({h["check_id"] for h in hits}),
            }
        )
    return out, unmatched


def sample_times(bin_path: str, rows: list[dict]) -> list[dict]:
    sample = []
    by_cat: dict[str, list] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    for items in by_cat.values():
        sample.extend([x for x in items if x["label"] == "insecure"][:2])
        sample.extend([x for x in items if x["label"] == "secure"][:1])
    timed = []
    for r in sample:
        cmd = [
            bin_path,
            str(module_dir(r)),
            "--format",
            "json",
            "--soft-fail",
            "--no-colour",
        ]
        t0 = time.perf_counter()
        subprocess.run(cmd, capture_output=True, text=True)
        timed.append(
            {
                "module_id": r["module_id"],
                "category": r["category"],
                "label": r["label"],
                "seconds": time.perf_counter() - t0,
            }
        )
    return timed


def main() -> int:
    bin_path = find_tfsec()
    rows = load_labels()
    id_map = load_id_map("tfsec_ids.json")
    batch = run_batch(bin_path)
    by_mod = index_by_module(batch["data"], rows)
    verd, unmatched = verdicts(rows, by_mod, id_map)
    times = sample_times(bin_path, rows)
    payload = {
        "tool": "tfsec",
        "version": tfsec_version(bin_path),
        "defaults": "shipped",
        "batch_seconds": batch["elapsed_s"],
        "n_modules": len(rows),
        "verdicts": verd,
        "unmatched_check_ids": unmatched,
        "sample_times": times,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "tfsec_verdicts.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"tfsec {payload['version']} batch {batch['elapsed_s']:.1f}s "
        f"flagged {sum(v['predicted'] for v in verd)}/{len(verd)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
