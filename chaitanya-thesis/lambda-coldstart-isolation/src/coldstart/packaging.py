"""Deterministic deployment zips + the package manifest.

Package size is one of the independent variables, so every variant's size and
hash is recorded in build/package_manifest.json (and copied into the results).
Zips are built with sorted entries and a fixed timestamp so the same source
always gives the same sha256.

    python -m coldstart.packaging build/
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

FIXED_TIME = (2024, 1, 1, 0, 0, 0)


def deterministic_zip(src_dir: str | Path, zip_path: str | Path) -> Path:
    src_dir, zip_path = Path(src_dir), Path(zip_path)
    files = sorted(p for p in src_dir.rglob("*") if p.is_file())
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(src_dir).as_posix(), date_time=FIXED_TIME)
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, p.read_bytes(), compresslevel=9)
    return zip_path


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def describe_zip(path: str | Path) -> dict:
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
    return {
        "artifact": path.name,
        "zip_bytes": path.stat().st_size,
        "unzipped_bytes": sum(i.file_size for i in infos),
        "files": len(infos),
        "sha256": sha256_file(path),
    }


def build_manifest(build_dir: str | Path) -> dict:
    """Zip every <runtime>-<variant>/ folder (java ships its jar as-is) and describe it."""
    build_dir = Path(build_dir)
    entries = []
    for d in sorted(p for p in build_dir.iterdir() if p.is_dir()):
        if "-" not in d.name:
            continue
        runtime, variant = d.name.split("-", 1)
        jar = d / "function.jar"
        artifact = jar if jar.exists() else deterministic_zip(d, build_dir / f"{d.name}.zip")
        entries.append({"runtime": runtime, "variant": variant, **describe_zip(artifact)})
    manifest = {"variants": entries}
    (build_dir / "package_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    m = build_manifest(sys.argv[1] if len(sys.argv) > 1 else "build")
    for e in m["variants"]:
        print(f"{e['runtime']:8s} {e['variant']:10s} {e['zip_bytes']:>12,d} B zipped  "
              f"{e['unzipped_bytes']:>12,d} B unzipped  {e['files']:>6d} files")
