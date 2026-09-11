"""60 s windows -> feature vectors.

Two views of the same window:

* **count view** (D1): event count vector over the templates seen in the
  training period, one extra column for lines of never-seen templates, plus a
  few numbers read from the logs themselves (REPORT durations, memory,
  cold starts, timeouts, crashes, ERROR lines). log1p + standardisation.
* **semantic view** (D2): each template is turned into hashed word features
  and a window is the sum over its lines. Words (not template ids) are the
  only thing a Blue Gene/L supercomputer log and a Lambda log can share, which
  is why the transfer detector needs this view.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import HashingVectorizer

REPORT_RE = re.compile(
    r"Duration: ([\d.]+) ms.*?Memory Size: (\d+) MB\s+Max Memory Used: (\d+) MB(?:\s+Init Duration: ([\d.]+) ms)?"
)
NUMERIC_FEATURES = ["invocations", "error_lines", "p50_duration_ms", "p99_duration_ms", "max_mem_ratio",
                    "cold_starts", "timeouts", "killed"]
_TOKEN = r"(?u)\b[a-zA-Z][a-zA-Z]+\b"


def line_facts(message: str) -> dict:
    """Numbers and flags we can read straight off one scrubbed log line."""
    facts = {"report": False, "duration": math.nan, "mem_ratio": math.nan, "cold": False,
             "error": False, "timeout": False, "killed": False}
    if message.startswith("REPORT"):
        m = REPORT_RE.search(message)
        if m:
            facts["report"] = True
            facts["duration"] = float(m.group(1))
            facts["mem_ratio"] = float(m.group(3)) / max(1.0, float(m.group(2)))
            facts["cold"] = m.group(4) is not None
    elif message.startswith("[ERROR]"):
        facts["error"] = True
    elif "Task timed out" in message:
        facts["timeout"] = True
        facts["error"] = True
    elif "Runtime exited with error" in message:
        facts["killed"] = True
        facts["error"] = True
    return facts


@dataclass
class Windows:
    starts: np.ndarray           # window start times
    line_window: np.ndarray      # window index of every line
    numeric: pd.DataFrame        # NUMERIC_FEATURES per window
    window_s: float


def make_windows(ts: np.ndarray, messages: list[str], t0: float, t1: float, window_s: float) -> Windows:
    n = int(math.ceil((t1 - t0) / window_s))
    starts = t0 + np.arange(n) * window_s
    idx = np.clip(((np.asarray(ts) - t0) // window_s).astype(int), 0, n - 1)
    facts = pd.DataFrame([line_facts(m) for m in messages])
    facts["w"] = idx
    g = facts.groupby("w")
    numeric = pd.DataFrame(index=range(n))
    numeric["invocations"] = g["report"].sum()
    numeric["error_lines"] = g["error"].sum()
    dur = facts[facts["report"]].groupby("w")["duration"]
    numeric["p50_duration_ms"] = dur.quantile(0.5)
    numeric["p99_duration_ms"] = dur.quantile(0.99)
    numeric["max_mem_ratio"] = facts[facts["report"]].groupby("w")["mem_ratio"].max()
    numeric["cold_starts"] = g["cold"].sum()
    numeric["timeouts"] = g["timeout"].sum()
    numeric["killed"] = g["killed"].sum()
    numeric = numeric.fillna(0.0).astype(float)
    return Windows(starts=starts, line_window=idx, numeric=numeric, window_s=window_s)


class CountView:
    """Event count vectors over a vocabulary fixed on the training windows."""

    def __init__(self) -> None:
        self.vocab: dict[int, int] = {}

    def fit(self, cluster_ids) -> "CountView":
        for cid in sorted(set(int(c) for c in cluster_ids)):
            self.vocab[cid] = len(self.vocab)
        return self

    def transform(self, cluster_ids, line_window: np.ndarray, n_windows: int) -> np.ndarray:
        mat = np.zeros((n_windows, len(self.vocab) + 1), dtype=float)
        novel = len(self.vocab)
        cols = np.array([self.vocab.get(int(c), novel) for c in cluster_ids], dtype=int)
        np.add.at(mat, (line_window, cols), 1.0)
        return mat


def count_features(counts: np.ndarray, numeric: pd.DataFrame) -> np.ndarray:
    return np.hstack([np.log1p(counts), np.log1p(numeric[NUMERIC_FEATURES].to_numpy(dtype=float))])


class SemanticView:
    """Hashed bag of words of the templates; shared by source and target."""

    def __init__(self, n_features: int = 1024) -> None:
        self.vectorizer = HashingVectorizer(n_features=n_features, alternate_sign=False, norm=None,
                                            token_pattern=_TOKEN, lowercase=True)
        self._cache: dict[str, int] = {}
        self._rows: list[str] = []

    @staticmethod
    def clean(template: str) -> str:
        # drop the masks (<*>, <TS>, <RID> ...) - they carry no meaning across systems
        return re.sub(r"<[^>]*>", " ", template)

    def window_matrix(self, templates: list[str], line_window: np.ndarray, n_windows: int) -> np.ndarray:
        keys = []
        for tpl in templates:
            key = self._cache.get(tpl)
            if key is None:
                key = len(self._rows)
                self._cache[tpl] = key
                self._rows.append(self.clean(tpl))
            keys.append(key)
        tpl_vectors = self.vectorizer.transform(self._rows)  # sparse [n_templates x n_features]
        counts = np.zeros((n_windows, len(self._rows)), dtype=float)
        np.add.at(counts, (np.asarray(line_window, dtype=int), np.asarray(keys, dtype=int)), 1.0)
        return np.asarray((tpl_vectors.T @ counts.T).T)


def window_labels(starts: np.ndarray, window_s: float, schedule) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For every window: anomalous?, injection id (-1), category ('' if normal).

    A window is anomalous if it overlaps an injected interval at all.
    """
    n = len(starts)
    label = np.zeros(n, dtype=bool)
    inj_id = np.full(n, -1, dtype=int)
    cat = np.array([""] * n, dtype=object)
    for inj in schedule:
        lo = int(max(0, math.floor((inj.start - starts[0]) / window_s)))
        hi = int(min(n, math.ceil((inj.end - starts[0]) / window_s)))
        label[lo:hi] = True
        inj_id[lo:hi] = inj.injection_id
        cat[lo:hi] = inj.category
    return label, inj_id, cat
