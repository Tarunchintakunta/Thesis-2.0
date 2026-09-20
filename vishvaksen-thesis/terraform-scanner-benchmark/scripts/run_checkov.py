#!/usr/bin/env python3
"""Run Checkov (shipped defaults) over the labelled corpus. No terraform apply."""

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

from src.io_util import RESULTS, CORPUS, load_id_map, load_labels, module_dir  # noqa: E402


def find_checkov() -> str:
    env = os.environ.get("CHECKOV_BIN")
    if env:
        return env
    found = shutil.which("checkov")
    if found:
        return found
    extra = Path.home() / "Library/Python/3.14/bin/checkov"
    if extra.exists():
        return str(extra)
    raise SystemExit("checkov not found on PATH; set CHECKOV_BIN")


def checkov_version(bin_path: str) -> str:
    out = subprocess.check_output([bin_path, "--version"], text=True).strip()
    return out.splitlines()[0]


def run_batch(bin_path: str) -> dict:
    RESULTS.mkdir(parents=True, exist_ok=True)
    raw_path = RESULTS / "raw" / "checkov_batch.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        bin_path,
        "-d",
        str(CORPUS),
        "--framework",
        "terraform",
        "--download-external-modules",
        "false",
        "--quiet",
        "-o",
        "json",
        "--compact",
        "--soft-fail",
    ]
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.perf_counter() - t0
    payload = proc.stdout
    if not payload.strip():
        payload = proc.stderr
    raw_path.write_text(payload, encoding="utf-8")
    try:
        data = json.loads(payload) if payload.strip() else {}
    except json.JSONDecodeError:
        data = {"parse_error": True, "stdout_head": payload[:4000]}
    return {"elapsed_s": elapsed, "returncode": proc.returncode, "data": data}


def _failed_checks(data) -> list[dict]:
    checks = []
    if isinstance(data, list):
        for item in data:
            checks.extend(_failed_checks(item))
        return checks
    if not isinstance(data, dict):
        return checks
    results = data.get("results") or {}
    failed = results.get("failed_checks") or data.get("failed_checks") or []
    checks.extend(failed)
    for key in ("check_type",):
        _ = key
    for nested in data.values():
        if isinstance(nested, dict) and nested is not data:
            if "results" in nested:
                checks.extend(_failed_checks(nested))
        if isinstance(nested, list):
            for item in nested:
                if isinstance(item, dict) and "results" in item:
                    checks.extend(_failed_checks(item))
    return checks


def index_by_module(data, rows: list[dict]) -> dict[str, list[dict]]:
    by_mod = {r["module_id"]: [] for r in rows}
    path_to_id = {}
    for r in rows:
        path_to_id[str(module_dir(r).resolve())] = r["module_id"]
        path_to_id[str((module_dir(r) / "main.tf").resolve())] = r["module_id"]
    seen = set()
    for chk in _failed_checks(data):
        ident = id(chk)
        if ident in seen:
            continue
        seen.add(ident)
        fpath = chk.get("file_abs_path") or chk.get("file_path") or ""
        fpath = str(Path(fpath).resolve()) if fpath else ""
        module_id = None
        for prefix, mid in path_to_id.items():
            if fpath == prefix or fpath.startswith(str(Path(prefix).parent)):
                if Path(prefix).name == "main.tf" and fpath.endswith(mid + "/main.tf"):
                    module_id = mid
                    break
                if Path(prefix).name != "main.tf" and f"/{mid}/" in fpath:
                    module_id = mid
                    break
        if module_id is None:
            for r in rows:
                if f"/{r['module_id']}/" in fpath or fpath.endswith(f"/{r['module_id']}/main.tf"):
                    module_id = r["module_id"]
                    break
        if module_id is None:
            continue
        by_mod[module_id].append(
            {
                "check_id": chk.get("check_id") or chk.get("id") or "",
                "check_name": chk.get("check_name") or chk.get("name") or "",
                "severity": chk.get("severity") or "",
                "resource": chk.get("resource") or "",
            }
        )
    return by_mod


def verdicts(rows, by_mod, id_map) -> list[dict]:
    out = []
    unmatched: dict[str, int] = {}
    for r in rows:
        cat = r["category"]
        mapped = id_map.get(cat, set())
        hits = []
        for chk in by_mod.get(r["module_id"], []):
            cid = chk["check_id"]
            if cid in mapped:
                hits.append(chk)
            else:
                unmatched[cid] = unmatched.get(cid, 0) + 1
        out.append(
            {
                "module_id": r["module_id"],
                "category": cat,
                "label": r["label"],
                "predicted": 1 if hits else 0,
                "n_mapped_findings": len(hits),
                "n_all_findings": len(by_mod.get(r["module_id"], [])),
                "mapped_check_ids": sorted({h["check_id"] for h in hits}),
            }
        )
    return out, unmatched


def sample_times(bin_path: str, rows: list[dict], n_per_category: int = 3) -> list[dict]:
    """Individual-module timings on a stratified sample (accuracy uses batch)."""
    sample = []
    by_cat: dict[str, list[dict]] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    for cat, items in by_cat.items():
        insecure = [x for x in items if x["label"] == "insecure"][:2]
        secure = [x for x in items if x["label"] == "secure"][:1]
        sample.extend(insecure + secure)
    timed = []
    for r in sample[: n_per_category * 4]:
        cmd = [
            bin_path,
            "-d",
            str(module_dir(r)),
            "--framework",
            "terraform",
            "--download-external-modules",
            "false",
            "--quiet",
            "-o",
            "json",
            "--compact",
            "--soft-fail",
        ]
        t0 = time.perf_counter()
        subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - t0
        timed.append(
            {
                "module_id": r["module_id"],
                "category": r["category"],
                "label": r["label"],
                "seconds": elapsed,
            }
        )
    return timed


def main() -> int:
    bin_path = find_checkov()
    rows = load_labels()
    id_map = load_id_map("checkov_ids.json")
    batch = run_batch(bin_path)
    by_mod = index_by_module(batch["data"], rows)
    verd, unmatched = verdicts(rows, by_mod, id_map)
    times = sample_times(bin_path, rows)
    payload = {
        "tool": "checkov",
        "version": checkov_version(bin_path),
        "defaults": "shipped",
        "batch_seconds": batch["elapsed_s"],
        "n_modules": len(rows),
        "verdicts": verd,
        "unmatched_check_ids": unmatched,
        "sample_times": times,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "checkov_verdicts.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"checkov {payload['version']} batch {batch['elapsed_s']:.1f}s "
        f"flagged {sum(v['predicted'] for v in verd)}/{len(verd)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
