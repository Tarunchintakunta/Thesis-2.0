"""Shared command line for invoke_idle.py / invoke_steady.py / invoke_burst.py."""
from __future__ import annotations

import argparse
import re
import sys

from .backends import data_mode, get_backend
from .config import load_config
from .driver import run_phase


def parse_duration_h(text: str) -> float:
    """'2h' -> 2.0, '90m' -> 1.5, '1.5' -> 1.5"""
    m = re.fullmatch(r"\s*([\d.]+)\s*([hm]?)\s*", text)
    if not m:
        raise argparse.ArgumentTypeError(f"bad duration {text!r}")
    value = float(m.group(1))
    return value / 60 if m.group(2) == "m" else value


def build_parser(description: str, default_phases: str) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--config", default="configs/experiment.yaml")
    ap.add_argument("--phase", default=default_phases, help="comma list of phases from the config")
    ap.add_argument("--out", required=True, help="output root; each phase gets its own folder")
    ap.add_argument("--reps", type=int, help="override reps")
    ap.add_argument("--memories", help="override memories, e.g. 128,512,1024,3008")
    ap.add_argument("--runtime", help="override runtimes, e.g. python or python,java")
    ap.add_argument("--variant", help="override variants, e.g. default")
    ap.add_argument("--duration", type=parse_duration_h, help="warming phase length, e.g. 2h")
    ap.add_argument("--warming", default="on,off", help="kept for the documented command; both arms always run")
    ap.add_argument("--seed", type=int)
    return ap


def apply_overrides(ph: dict, args) -> dict:
    ph = dict(ph)
    if args.reps:
        ph["reps"] = args.reps
    if args.memories:
        ph["memories"] = [int(x) for x in args.memories.split(",")]
        ph.pop("cells", None)
        ph.setdefault("variants", ["optimised"])
    if args.runtime:
        ph["runtimes"] = args.runtime.split(",")
    if args.variant:
        ph["variants"] = args.variant.split(",")
    if args.duration:
        ph["duration_h"] = args.duration
    return ph


def main(description: str, allowed_kinds: set[str], argv=None) -> int:
    args = build_parser(description, "").parse_args(argv)
    cfg = load_config(args.config)
    if args.phase:
        names = [p for p in args.phase.split(",") if p]
    else:  # no --phase: every phase of the right kind in the config
        names = [n for n, ph in cfg["phases"].items() if ph["kind"] in allowed_kinds]
    for n in names:
        if n not in cfg["phases"]:
            print(f"unknown phase {n}; config has {', '.join(cfg['phases'])}", file=sys.stderr)
            return 2
        if cfg["phases"][n]["kind"] not in allowed_kinds:
            print(f"phase {n} is a {cfg['phases'][n]['kind']} phase, not for this script", file=sys.stderr)
            return 2
        cfg["phases"][n] = apply_overrides(cfg["phases"][n], args)
    seed = args.seed if args.seed is not None else int(cfg["seed"])
    mode = data_mode()
    print(f"DATA_MODE={mode}" + ("  (SYNTHETIC - not measured)" if mode == "mock" else ""))
    backend = get_backend(cfg, seed)
    code = 0
    for n in names:
        info = run_phase(backend, cfg, n, args.out, seed)
        print(f"  {n:16s} {info['invocations']:6d} invocations  {info['status']}")
        code = code or (0 if info["status"] == "complete" else 3)
    return code
