"""End-to-end run: logs -> scrub -> fixed Drain -> windows -> D1/D2/D3 -> window predictions.

    python -m logad.pipeline --config configs/experiment.yaml
    python -m logad.pipeline --config configs/smoke.yaml --out results_smoke

Per seed:
  1. generate phases A/B/C with the Lambda emulator (unless data/raw/seed_X exists)
  2. strip identifiers (data/interim), parse A -> B -> C online with the fixed parser
  3. certify phase A clean (no injection overlaps it, no fault signatures in it)
  4. D1: OC-SVM + Isolation Forest on phase A count features; chronological
     80/20 split inside A picks the primary model, then both are refit on all of A
  5. D2: ELFA-Log style transfer, labelled Loghub BGL source -> unlabelled phase A
  6. D3: threshold alarms calibrated on phase A metrics
  7. score phases B and C -> results/metrics/windows_<phase>_seed_<seed>.csv

All metrics / statistics / figures are computed afterwards from those CSVs by
``python -m logad.eval.report``.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from logad.collect.generate import generate
from logad.collect.scrub import has_identifiers, scrub
from logad.config import CONFIG_DIR, PROJECT_ROOT, load_experiment, load_yaml
from logad.detectors.oneclass_iforest import IforestDetector
from logad.detectors.oneclass_ocsvm import OcsvmDetector
from logad.detectors.thresholds import ThresholdAlarms, metric_windows
from logad.detectors.transfer_elfa import ElfaStyleTransfer
from logad.eval.metrics import false_alarm_rate, window_blocks
from logad.features.windows import CountView, SemanticView, count_features, make_windows, window_labels
from logad.inject.schedule import read_ground_truth
from logad.parse.drain_parser import FixedDrainParser, check_or_write_fingerprint
from logad.source.loghub_bgl import read_bgl, window_labels as bgl_window_labels, window_line_index

FAULT_SIGNATURES = ("AccessDeniedException", "ResourceNotFoundException", "DownstreamTimeout",
                    "Task timed out", "Runtime exited with error")


class TrainingWindowNotClean(RuntimeError):
    pass


def read_phase(path: Path) -> tuple[np.ndarray, list[str]]:
    import datetime as dt

    ts, msgs = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            stamp, message = line.rstrip("\n").split("\t", 1)
            ts.append(dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp())
            msgs.append(message)
    return np.asarray(ts), msgs


def certify_clean(msgs_a: list[str], metrics_a: pd.DataFrame, schedule, a_end: float) -> dict:
    """Albert (2024): source-free training is only as good as its clean window."""
    signature_hits = {sig: sum(sig in m for m in msgs_a) for sig in FAULT_SIGNATURES}
    overlapping = [inj.injection_id for inj in schedule if inj.start < a_end]
    server_errors = int((pd.to_numeric(metrics_a["status"]) >= 500).sum())
    certified = not overlapping and not any(signature_hits.values()) and server_errors == 0
    return {"certified": certified, "injections_overlapping_A": overlapping,
            "fault_signature_lines": signature_hits, "http_5xx_in_A": server_errors, "lines_in_A": len(msgs_a)}


def _write_interim(folder: Path, phase: str, ts: np.ndarray, msgs: list[str]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / f"phase_{phase}.log", "w", encoding="utf-8") as fh:
        for t, m in zip(ts, msgs):
            fh.write(f"{t:.3f}\t{m}\n")


def bgl_source(drain_cfg: dict, det_cfg: dict, semantic: SemanticView) -> tuple[np.ndarray, np.ndarray, dict]:
    bgl = read_bgl()
    parser = FixedDrainParser(drain_cfg)  # same fixed config, own template store
    parsed = parser.parse(bgl.contents)
    size, step = det_cfg["source_window_lines"], det_cfg["source_step_lines"]
    rows, wins = window_line_index(len(bgl.contents), size, step)
    n_win = int(wins.max()) + 1
    X = semantic.window_matrix([parsed.template[i] for i in rows], wins, n_win)
    y = bgl_window_labels(bgl.labels, size, step)
    info = {"lines": len(bgl.contents), "alert_lines": int(bgl.labels.sum()), "windows": int(n_win),
            "anomalous_windows": int(y.sum()), "templates": len(parser.templates())}
    return X, y, info


def run_seed(cfg: dict, seed: int, det_cfg: dict, alarm_cfg: dict, drain_cfg: dict, out: Path,
             raw_root: Path, interim_root: Path, regenerate: bool = False) -> dict:
    t_begin = time.time()
    raw = raw_root / f"seed_{seed}"
    if regenerate or not (raw / "meta.json").exists():
        generate(cfg, seed, raw_root)
    meta = json.loads((raw / "meta.json").read_text())
    schedule = read_ground_truth(raw / "ground_truth.csv")
    window_s = float(cfg["window_s"])

    # -- scrub + parse (online, chronological) ----------------------------------------
    parser = FixedDrainParser(drain_cfg)
    phases = {}
    for ph in "ABC":
        ts, msgs = read_phase(raw / f"phase_{ph}.log")
        msgs = [scrub(m) for m in msgs]
        leaked = sum(has_identifiers(m) for m in msgs)
        if leaked:
            raise RuntimeError(f"{leaked} lines still carry identifiers after scrubbing")
        _write_interim(interim_root / f"seed_{seed}", ph, ts, msgs)
        parsed = parser.parse(msgs, ts)
        t0, t1 = meta["phases"][ph]["start"], meta["phases"][ph]["end"]
        wins = make_windows(ts, msgs, t0, t1, window_s)
        requests = pd.read_csv(raw / f"metrics_{ph}.csv")
        phases[ph] = {"ts": ts, "msgs": msgs, "parsed": parsed, "win": wins, "requests": requests,
                      "metrics": metric_windows(requests, t0, t1, window_s)}

    templates = pd.DataFrame(parser.templates())
    templates.to_csv(out / "tables" / f"templates_seed_{seed}.csv", index=False)

    # -- clean window certification ------------------------------------------------
    a = phases["A"]
    cert = certify_clean(a["msgs"], a["requests"], schedule, meta["phases"]["A"]["end"])
    cert.update({"seed": seed, "identifier_lines_after_scrub": 0})
    (out / "certification").mkdir(parents=True, exist_ok=True)
    (out / "certification" / f"seed_{seed}.json").write_text(json.dumps(cert, indent=2) + "\n")
    if not cert["certified"]:
        raise TrainingWindowNotClean(f"seed {seed}: phase A is not clean: {cert}")

    # -- D1 source-free ---------------------------------------------------------------
    n_a = len(a["win"].starts)
    n_train = int(n_a * cfg["split"]["train_fraction"])
    split_t = a["win"].starts[n_train]
    line_is_train = a["ts"] < split_t
    assert a["ts"][line_is_train].max() < split_t <= phases["B"]["ts"].min(), "chronological split violated"

    def d1_matrix(view: CountView, ph: str) -> np.ndarray:
        p = phases[ph]
        return count_features(view.transform(p["parsed"].cluster_id, p["win"].line_window, len(p["win"].starts)),
                              p["win"].numeric)

    d1 = det_cfg["d1_source_free"]
    q = d1["threshold_quantile"]
    sel_view = CountView().fit(np.asarray(a["parsed"].cluster_id)[line_is_train])
    xa_sel = d1_matrix(sel_view, "A")
    candidates = {"d1_ocsvm": OcsvmDetector(threshold_quantile=q, **d1["ocsvm"]),
                  "d1_iforest": IforestDetector(threshold_quantile=q, **d1["iforest"])}
    val_far = {}
    for name, det in candidates.items():
        det.fit(xa_sel[:n_train])
        val_far[name] = false_alarm_rate(det.predict(xa_sel[n_train:]))
    if d1["primary"] == "auto":
        primary = min(val_far, key=lambda k: (val_far[k], 0 if k == "d1_iforest" else 1))
    else:
        primary = d1["primary"]

    view = CountView().fit(a["parsed"].cluster_id)
    xa = d1_matrix(view, "A")
    finals = {"d1_ocsvm": OcsvmDetector(threshold_quantile=q, **d1["ocsvm"]).fit(xa),
              "d1_iforest": IforestDetector(threshold_quantile=q, **d1["iforest"]).fit(xa)}
    (out / "models").mkdir(parents=True, exist_ok=True)
    for name, det in finals.items():
        joblib.dump(det, out / "models" / f"{name}_seed_{seed}.joblib")

    # -- D2 transfer --------------------------------------------------------------------
    d2 = det_cfg["d2_transfer"]
    semantic = SemanticView(d2["hashing_features"])
    xs, ys, src_info = bgl_source(drain_cfg, d2, semantic)

    def d2_matrix(ph: str) -> np.ndarray:
        p = phases[ph]
        return semantic.window_matrix(p["parsed"].template, p["win"].line_window, len(p["win"].starts))

    transfer = ElfaStyleTransfer(svd_components=d2["svd_components"], coral_eps=d2["coral_eps"],
                                 rounds=d2["pseudo_label_rounds"], entropy_threshold=d2["entropy_threshold"],
                                 pseudo_weight=d2["pseudo_weight"], decision_threshold=d2["decision_threshold"],
                                 **d2["classifier"]).fit(xs, ys, d2_matrix("A"))

    # -- D3 thresholds ---------------------------------------------------------------
    alarms = ThresholdAlarms(alarm_cfg["alarms"], alarm_cfg["calibration_quantile"]).fit(a["metrics"])

    # -- score B and C ------------------------------------------------------------------
    for ph in ("B", "C"):
        p = phases[ph]
        starts = p["win"].starts
        x1 = d1_matrix(view, ph)
        x2 = d2_matrix(ph)
        df = pd.DataFrame({"seed": seed, "phase": ph, "window": np.arange(len(starts)), "start": starts})
        if ph == "B":
            label, inj, cat = window_labels(starts, window_s, schedule)
            df["label"], df["injection_id"], df["category"] = label, inj, cat
            df["block"] = window_blocks(starts, schedule)
        else:
            df["label"], df["injection_id"], df["category"], df["block"] = False, -1, "", -1
        bursts = pd.read_csv(raw / f"bursts_{ph}.csv")
        in_burst = np.zeros(len(starts), dtype=bool)
        for _, b in bursts.iterrows():
            in_burst |= (starts + window_s > b["start"]) & (starts < b["start"] + b["length"])
        df["burst"] = in_burst
        df["cold_starts"] = p["win"].numeric["cold_starts"].to_numpy()
        df["invocations"] = p["win"].numeric["invocations"].to_numpy()
        df["throttles"] = p["metrics"]["throttles"].to_numpy()
        for name, det in finals.items():
            df[f"score_{name}"] = det.score(x1)
            df[f"pred_{name}"] = det.predict(x1)
        df["score_d1_primary"] = df[f"score_{primary}"]
        df["pred_d1_primary"] = df[f"pred_{primary}"]
        df["score_d2_transfer"] = transfer.score(x2)
        df["pred_d2_transfer"] = transfer.predict(x2)
        df["score_d3_thresholds"] = alarms.score(p["metrics"])
        df["pred_d3_thresholds"] = alarms.predict(p["metrics"])
        df.to_csv(out / "metrics" / f"windows_{ph}_seed_{seed}.csv", index=False)

    info = {
        "seed": seed,
        "lines": {ph: len(phases[ph]["msgs"]) for ph in "ABC"},
        "windows": {ph: len(phases[ph]["win"].starts) for ph in "ABC"},
        "templates": len(templates),
        "d1": {"primary": primary, "validation_far": val_far, "train_windows": n_train,
               "validation_windows": n_a - n_train, "vocab": len(view.vocab),
               "thresholds": {k: v.threshold for k, v in finals.items()}},
        "d2": {"source": src_info, "pseudo_label_history": transfer.history,
               "source_fit_accuracy": transfer.source_accuracy(xs, ys)},
        "d3": {"thresholds": alarms.thresholds},
        "certification": cert["certified"],
        "seconds": round(time.time() - t_begin, 1),
    }
    return info


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="run the whole detection pipeline")
    p.add_argument("--config", default=str(CONFIG_DIR / "experiment.yaml"))
    p.add_argument("--out", default=str(PROJECT_ROOT / "results"))
    p.add_argument("--raw", default=str(PROJECT_ROOT / "data" / "raw"))
    p.add_argument("--interim", default=str(PROJECT_ROOT / "data" / "interim"))
    p.add_argument("--seed", type=int, action="append")
    p.add_argument("--regenerate", action="store_true", help="regenerate raw logs even if they exist")
    args = p.parse_args(argv)

    cfg = load_experiment(args.config)
    det_cfg = load_yaml(CONFIG_DIR / "detectors.yaml")
    alarm_cfg = load_yaml(CONFIG_DIR / "alarms.yaml")
    drain_cfg = load_yaml(CONFIG_DIR / "drain.yaml")
    out = Path(args.out)
    for sub in ("metrics", "tables", "stats", "figures"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    fp = check_or_write_fingerprint(out / "parser_fingerprint.json")

    runs = []
    for seed in args.seed or cfg["seeds"]:
        info = run_seed(cfg, seed, det_cfg, alarm_cfg, drain_cfg, out, Path(args.raw) / cfg["name"],
                        Path(args.interim) / cfg["name"], regenerate=args.regenerate)
        runs.append(info)
        print(f"seed {seed}: {info['lines']} lines, {info['templates']} templates, D1 primary {info['d1']['primary']}, "
              f"{info['seconds']} s")
    run_info = {"config": cfg.get("name"), "parser_fingerprint": fp, "runs": runs,
                "note": "logs produced by the local Lambda runtime emulator (not live AWS / LocalStack)"}
    (out / "run_info.json").write_text(json.dumps(run_info, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
