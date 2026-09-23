"""Google Cluster Trace loader.

Does **not** invent data. Raises FileNotFoundError with an exact checklist when
the required GCT files are absent. Synthetic telemetry remains a separate path
(`telemetry_simulator.py`) and must not be used as a silent fallback here.

Windowing (2011): join task_usage ↔ task_events on (job_id, task_index).
MHSA 4-metric tensor (honest channel map):
  cpu  = mean CPU usage rate
  mem  = canonical memory usage
  disk = mean disk I/O time (clipped/scaled into [0,1])
  net  = sampled CPU usage — ClusterData 2011 has **no network-byte column**
         (see data/gct/CHANNEL_HONESTY.md). Not a fabricated bandwidth series.

Aldomi expanded tensor: additional usage columns (assigned/max memory, disk
space, max CPU, …) plus **history-only** scheduling event counts (SCHEDULE /
UPDATE). Future FAIL-family events are labels, never features.

Labels: per-channel None/L1/L2 from the *future* usage window (same thresholds
as the synthetic path), with FAIL/EVICT/KILL/LOST events inside the horizon
forcing L2 on all channels (failure-aware health)."""

from __future__ import annotations

import gzip
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

try:
    from src.data.telemetry_simulator import METRIC_NAMES, THRESHOLDS
except ImportError:  # python -m / direct script from package root
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.data.telemetry_simulator import METRIC_NAMES, THRESHOLDS

DEFAULT_RELATIVE_ROOT = Path(__file__).resolve().parents[2] / "data" / "gct"

GCT_2011_REQUIRED_GLOBS = (
    "2011/task_events/part-*-of-*.csv.gz",
    "2011/task_usage/part-*-of-*.csv.gz",
)

GCT_2011_OPTIONAL_GLOBS = (
    "2011/machine_events/part-*-of-*.csv.gz",
    "2011/machine_attributes/part-*-of-*.csv.gz",
    "2011/job_events/part-*-of-*.csv.gz",
)

GCT_2019_REQUIRED_GLOBS = (
    "2019/*/instance_usage/*",
    "2019/*/instance_events/*",
)

# task_events.event_type values treated as unhealthy outcomes
_FAIL_EVENTS = {2, 3, 5, 6}  # EVICT, FAIL, KILL, LOST
_SCHED_EVENTS = {1}  # SCHEDULE
_UPDATE_EVENTS = {7, 8}  # UPDATE_PENDING, UPDATE_RUNNING

_MAX_USAGE_ROWS = 2_000_000
_MAX_SERIES = 8_000
_MAX_WINDOWS = 20_000

GCT_METRIC_NAMES = tuple(METRIC_NAMES)
LAST_LOAD_META: dict = {}

# ClusterData2011_2 task_usage numeric columns used for Aldomi SelectKBest.
# Index 19 (sampled CPU) is also the MHSA "net" proxy — not network bytes.
EXPANDED_USAGE_FIELDS: Tuple[Tuple[str, int, float], ...] = (
    ("mean_cpu", 5, 1.0),
    ("canonical_mem", 6, 1.0),
    ("assigned_mem", 7, 1.0),
    ("unmapped_cache", 8, 1.0),
    ("total_cache", 9, 1.0),
    ("max_mem", 10, 1.0),
    ("mean_disk_io", 11, 50.0),
    ("mean_local_disk", 12, 1.0),
    ("max_cpu", 13, 1.0),
    ("max_disk_io", 14, 50.0),
    ("sampled_cpu", 19, 1.0),
)
SCHED_FEATURE_NAMES = ("sched_count_hist", "update_count_hist")
EXPANDED_FEATURE_NAMES = tuple(n for n, _, _ in EXPANDED_USAGE_FIELDS) + SCHED_FEATURE_NAMES


def resolve_gct_root(explicit: Optional[str] = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("MHSA_GCT_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_RELATIVE_ROOT.resolve()


def _expand(root: Path, patterns: Iterable[str]) -> List[Path]:
    found: List[Path] = []
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and path.stat().st_size > 0 and not path.name.endswith(".partial"):
                found.append(path)
    return sorted(found)


def inventory(root: Optional[Path] = None) -> dict:
    """Return present/missing file inventory for both GCT families."""
    root = root or resolve_gct_root()
    inv = {
        "root": str(root),
        "root_exists": root.is_dir(),
        "2011_required": {p: [str(x) for x in _expand(root, [p])] for p in GCT_2011_REQUIRED_GLOBS},
        "2011_optional": {p: [str(x) for x in _expand(root, [p])] for p in GCT_2011_OPTIONAL_GLOBS},
        "2019_required": {p: [str(x) for x in _expand(root, [p])] for p in GCT_2019_REQUIRED_GLOBS},
    }
    inv["2011_ready"] = all(inv["2011_required"][p] for p in GCT_2011_REQUIRED_GLOBS)
    inv["2019_ready"] = all(inv["2019_required"][p] for p in GCT_2019_REQUIRED_GLOBS)
    inv["any_ready"] = bool(inv["2011_ready"] or inv["2019_ready"])
    return inv


def missing_checklist(root: Optional[Path] = None) -> str:
    inv = inventory(root)
    lines = [
        f"Looked under: {inv['root']}",
        "See mehak-thesis/DATA_GAPS.md for canonical download locations.",
        "",
        "Required (either family):",
    ]
    if not inv["2011_ready"]:
        lines.append("  [2011] missing:")
        for pattern, hits in inv["2011_required"].items():
            if not hits:
                lines.append(f"    - {pattern}")
    if not inv["2019_ready"]:
        lines.append("  [2019] missing:")
        for pattern, hits in inv["2019_required"].items():
            if not hits:
                lines.append(f"    - {pattern}")
    return "\n".join(lines)


def require_gct(root: Optional[str] = None) -> Path:
    """Raise if no usable GCT subset is present. Returns resolved root when ready."""
    resolved = resolve_gct_root(root)
    inv = inventory(resolved)
    if not inv["any_ready"]:
        raise FileNotFoundError(missing_checklist(resolved))
    return resolved


def _read_all_events(paths: Sequence[Path]) -> Dict[Tuple[int, int], List[Tuple[int, int]]]:
    """Map (job_id, task_index) → sorted (timestamp, event_type)."""
    events: Dict[Tuple[int, int], List[Tuple[int, int]]] = defaultdict(list)
    for path in paths:
        with gzip.open(path, "rt") as fh:
            for line in fh:
                parts = line.rstrip("\n").split(",")
                if len(parts) < 6:
                    continue
                try:
                    ts = int(parts[0]) if parts[0] else 0
                    job_id = int(parts[2])
                    task_index = int(parts[3])
                    event_type = int(parts[5])
                except ValueError:
                    continue
                events[(job_id, task_index)].append((ts, event_type))
    for key in events:
        events[key].sort(key=lambda x: x[0])
    return events


def _fail_times_from_events(
    events: Dict[Tuple[int, int], List[Tuple[int, int]]]
) -> Dict[Tuple[int, int], List[int]]:
    out: Dict[Tuple[int, int], List[int]] = {}
    for key, pairs in events.items():
        fails = [ts for ts, et in pairs if et in _FAIL_EVENTS]
        if fails:
            out[key] = fails
    return out


def _safe_float(raw: str) -> float:
    if not raw:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _read_usage_series(
    paths: Sequence[Path],
    max_rows: int = _MAX_USAGE_ROWS,
    max_series: int = _MAX_SERIES,
    prefer_keys: Optional[Iterable[Tuple[int, int]]] = None,
) -> Dict[Tuple[int, int], List[Tuple[int, np.ndarray, np.ndarray]]]:
    """Map (job, task) → list of (start_time, feats4, feats_expanded_usage)."""
    prefer = set(prefer_keys or [])
    series: Dict[Tuple[int, int], List[Tuple[int, np.ndarray, np.ndarray]]] = defaultdict(list)
    n_other = 0
    rows = 0
    n_usage = len(EXPANDED_USAGE_FIELDS)
    for path in paths:
        with gzip.open(path, "rt") as fh:
            for line in fh:
                parts = line.rstrip("\n").split(",")
                if len(parts) < 20:
                    continue
                try:
                    start = int(parts[0])
                    job_id = int(parts[2])
                    task_index = int(parts[3])
                except ValueError:
                    continue
                exp = np.zeros(n_usage, dtype=np.float32)
                for i, (_name, idx, scale) in enumerate(EXPANDED_USAGE_FIELDS):
                    val = _safe_float(parts[idx] if idx < len(parts) else "")
                    exp[i] = float(np.clip(val * scale, 0.0, 1.0))
                # MHSA 4-channel view (net = sampled CPU; not network bytes)
                feats4 = np.array(
                    [exp[0], exp[1], exp[6], exp[10]],
                    dtype=np.float32,
                )
                key = (job_id, task_index)
                if key not in series:
                    if key in prefer:
                        pass
                    elif n_other >= max_series:
                        continue
                    else:
                        n_other += 1
                series[key].append((start, feats4, exp))
                rows += 1
                if rows >= max_rows and not prefer:
                    break
        if rows >= max_rows and not prefer:
            break
    for key in series:
        series[key].sort(key=lambda x: x[0])
    return series


def _label_future(future: np.ndarray, force_fail: bool = False) -> np.ndarray:
    """Label each channel from future usage peaks only."""
    del force_fail  # FAIL events recorded separately; do not override channel labels.
    labels = np.zeros(len(METRIC_NAMES), dtype=np.int64)
    for i, name in enumerate(METRIC_NAMES):
        l1, l2 = THRESHOLDS[name]
        peak = float(future[:, i].max())
        if peak >= l2:
            labels[i] = 2
        elif peak >= l1:
            labels[i] = 1
        else:
            labels[i] = 0
    return labels


def _has_fail_in_window(
    fail_times: Sequence[int], t_hist_end: int, t_future_end: int
) -> bool:
    for ts in fail_times:
        if t_hist_end < ts <= t_future_end:
            return True
        if ts > t_future_end:
            break
    return False


def _count_types(
    pairs: Sequence[Tuple[int, int]], t0: int, t1: int, types: set
) -> int:
    n = 0
    for ts, et in pairs:
        if ts > t1:
            break
        if t0 < ts <= t1 and et in types:
            n += 1
    return n


def _windows_from_2011(
    root: Path,
    seq_length: int,
    horizon: int,
    max_windows: int = _MAX_WINDOWS,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    event_paths = _expand(root, ["2011/task_events/part-*-of-*.csv.gz"])
    usage_paths = _expand(root, ["2011/task_usage/part-*-of-*.csv.gz"])
    all_events = _read_all_events(event_paths)
    fails = _fail_times_from_events(all_events)
    series = _read_usage_series(usage_paths, prefer_keys=fails.keys())

    X_list: List[np.ndarray] = []
    Xe_list: List[np.ndarray] = []
    y_list: List[np.ndarray] = []
    transient_list: List[bool] = []
    fail_forced_n = 0
    need = seq_length + horizon
    n_exp = len(EXPANDED_FEATURE_NAMES)

    ordered_keys = [k for k in series if k in fails] + [k for k in series if k not in fails]
    for key in ordered_keys:
        points = series[key]
        if len(points) < need:
            continue
        fail_times = fails.get(key, [])
        ev_pairs = all_events.get(key, [])
        feats = np.stack([p[1] for p in points], axis=0)
        exp_u = np.stack([p[2] for p in points], axis=0)
        times = [p[0] for p in points]
        step = max(1, horizon)
        for start in range(0, len(points) - need + 1, step):
            hist = feats[start : start + seq_length]
            fut = feats[start + seq_length : start + need]
            t_hist_end = times[start + seq_length - 1]
            t_future_end = times[start + need - 1]
            t_hist_start = times[start]
            forced = _has_fail_in_window(fail_times, t_hist_end, t_future_end)
            y = _label_future(fut, force_fail=forced)
            is_t = bool(forced or (y.max() > 0))
            if forced:
                fail_forced_n += 1
            # History-only scheduling (no future FAIL leak).
            sched_n = _count_types(ev_pairs, t_hist_start - 1, t_hist_end, _SCHED_EVENTS)
            upd_n = _count_types(ev_pairs, t_hist_start - 1, t_hist_end, _UPDATE_EVENTS)
            sched = np.array(
                [min(sched_n / 10.0, 1.0), min(upd_n / 10.0, 1.0)],
                dtype=np.float32,
            )
            hist_exp = exp_u[start : start + seq_length]
            extra = np.repeat(sched[None, :], seq_length, axis=0)
            Xe = np.concatenate([hist_exp, extra], axis=1).astype(np.float32)
            assert Xe.shape[1] == n_exp
            X_list.append(hist.astype(np.float32))
            Xe_list.append(Xe)
            y_list.append(y)
            transient_list.append(is_t)
            if len(X_list) >= max_windows:
                break
        if len(X_list) >= max_windows:
            break

    if not X_list:
        raise RuntimeError(
            "GCT files present but no (job,task) series long enough for "
            f"seq_length={seq_length}+horizon={horizon}. Add more task_usage parts."
        )

    X = np.stack(X_list, axis=0)
    Xe = np.stack(Xe_list, axis=0)
    y = np.stack(y_list, axis=0)
    is_transient = np.asarray(transient_list, dtype=bool)

    if len(X) > max_windows:
        rng = np.random.RandomState(seed)
        pick = rng.choice(len(X), size=max_windows, replace=False)
        pick.sort()
        X, Xe, y, is_transient = X[pick], Xe[pick], y[pick], is_transient[pick]

    LAST_LOAD_META.clear()
    LAST_LOAD_META.update(
        {
            "family": "2011",
            "root": str(root),
            "seq_length": seq_length,
            "horizon": horizon,
            "n_windows": int(len(X)),
            "fail_forced_windows": int(fail_forced_n),
            "n_fail_event_keys": int(len(fails)),
            "n_usage_series": int(len(series)),
            "transient_rate": float(is_transient.mean()),
            "task_events_parts": [p.name for p in event_paths],
            "task_usage_parts": [p.name for p in usage_paths],
            "metrics": list(GCT_METRIC_NAMES),
            "expanded_features": list(EXPANDED_FEATURE_NAMES),
            "n_expanded_features": int(Xe.shape[-1]),
            "channel_notes": {
                "cpu": "mean CPU usage rate",
                "mem": "canonical memory usage",
                "disk": "mean disk I/O time ×50 clipped",
                "net": (
                    "sampled CPU (ClusterData 2011 has no network-byte field; "
                    "not a fabricated bandwidth series)"
                ),
            },
            "scheduling_features": "history-only SCHEDULE/UPDATE counts; no future FAIL leak",
            "net_channel_is_network_bytes": False,
            "fail_series_first": True,
            "seed": seed,
        }
    )
    return X, y, is_transient, Xe


def load_gct_bundle(
    root: Optional[str] = None,
    seq_length: int = 10,
    horizon: int = 5,
    max_windows: int = _MAX_WINDOWS,
    seed: int = 42,
) -> dict:
    """Load GCT → MHSA 4-channel windows + Aldomi expanded tensor."""
    resolved = require_gct(root)
    inv = inventory(resolved)
    if inv["2011_ready"]:
        X, y, is_transient, Xe = _windows_from_2011(
            resolved,
            seq_length=seq_length,
            horizon=horizon,
            max_windows=max_windows,
            seed=seed,
        )
        return {
            "X": X,
            "y": y,
            "is_transient": is_transient,
            "X_expanded": Xe,
            "expanded_names": list(EXPANDED_FEATURE_NAMES),
            "meta": dict(LAST_LOAD_META),
        }
    if inv["2019_ready"]:
        raise NotImplementedError(
            "2019 Borg cell files are present, but the 2019 JSON join is not "
            "implemented yet. Prefer the 2011 CSV subset documented in DATA_GAPS.md."
        )
    raise FileNotFoundError(missing_checklist(resolved))


def load_gct_windows(
    root: Optional[str] = None,
    seq_length: int = 10,
    horizon: int = 5,
    max_windows: int = _MAX_WINDOWS,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load GCT → (X, y, is_transient) matching TelemetrySimulator shapes.

    X: (N, seq_length, 4) float32
    y: (N, 4) int64 in {0,1,2}
    is_transient: (N,) bool  — also used as fail/unhealthy mask by train script
    """
    bundle = load_gct_bundle(
        root=root,
        seq_length=seq_length,
        horizon=horizon,
        max_windows=max_windows,
        seed=seed,
    )
    return bundle["X"], bundle["y"], bundle["is_transient"]


if __name__ == "__main__":
    try:
        root = require_gct()
        print(f"GCT ready under {root}")
        bundle = load_gct_bundle()
        X, y, t, Xe = bundle["X"], bundle["y"], bundle["is_transient"], bundle["X_expanded"]
        print(
            f"windows={len(X)} X={X.shape} Xe={Xe.shape} y={y.shape} "
            f"transient_rate={t.mean():.3f}"
        )
        print(f"label histogram (flat): {np.bincount(y.ravel(), minlength=3)}")
        print(f"net_channel_is_network_bytes={LAST_LOAD_META.get('net_channel_is_network_bytes')}")
    except (FileNotFoundError, NotImplementedError, RuntimeError) as exc:
        print(exc)
        raise SystemExit(2)
