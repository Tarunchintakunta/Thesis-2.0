import numpy as np
import pytest

from logad.features.windows import CountView, SemanticView, count_features, line_facts, make_windows, window_labels
from logad.inject.schedule import Injection

REPORT_COLD = ("REPORT RequestId: <RID>\tDuration: 20.00 ms\tBilled Duration: 20 ms\tMemory Size: 256 MB\t"
               "Max Memory Used: 128 MB\tInit Duration: 400.00 ms")
REPORT_WARM = "REPORT RequestId: <RID>\tDuration: 10.00 ms\tBilled Duration: 10 ms\tMemory Size: 256 MB\tMax Memory Used: 64 MB"


def test_line_facts():
    cold = line_facts(REPORT_COLD)
    assert cold["report"] and cold["cold"] and cold["duration"] == 20.0 and cold["mem_ratio"] == 0.5
    assert line_facts("[ERROR]\tts\t<RID>\t{}")["error"]
    assert line_facts("<TS> <RID> Task timed out after 3.00 seconds")["timeout"]
    assert line_facts("RequestId: <RID> Error: Runtime exited with error: signal: killed")["killed"]
    assert not line_facts("START RequestId: <RID> Version: $LATEST")["report"]


def test_make_windows_aggregates_per_minute():
    ts = np.array([0, 10, 70, 75, 130])
    msgs = [REPORT_WARM, REPORT_COLD, REPORT_WARM, "[ERROR]\tx\t<RID>\t{}", "START RequestId: <RID> Version: $LATEST"]
    w = make_windows(ts, msgs, 0, 180, 60)
    assert len(w.starts) == 3
    assert list(w.numeric["invocations"]) == [2, 1, 0]
    assert list(w.numeric["cold_starts"]) == [1, 0, 0]
    assert list(w.numeric["error_lines"]) == [0, 1, 0]
    assert w.numeric.loc[0, "p99_duration_ms"] == pytest.approx(19.9, abs=0.2)


def test_count_view_puts_unknown_templates_in_the_novel_column():
    view = CountView().fit([1, 2, 2])
    mat = view.transform([1, 2, 7, 7], np.array([0, 0, 1, 1]), 2)
    assert mat.shape == (2, 3)
    assert mat.tolist() == [[1, 1, 0], [0, 0, 2]]


def test_count_features_shape(tmp_path):
    ts = np.array([0.0, 1.0])
    w = make_windows(ts, [REPORT_WARM, REPORT_WARM], 0, 60, 60)
    X = count_features(np.ones((1, 3)), w.numeric)
    assert X.shape == (1, 3 + 8)


def test_semantic_view_shares_words_across_systems():
    sv = SemanticView(256)
    lam = sv.window_matrix(["[ERROR] <TS> <RID> error timeout <*>"], np.array([0]), 1)
    bgl = sv.window_matrix(["ciod: error reading message timeout <*>"], np.array([0]), 1)
    other = sv.window_matrix(["instruction cache parity corrected"], np.array([0]), 1)
    def cos(a, b):
        a, b = a.ravel(), b.ravel()
        return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

    assert cos(lam, bgl) > cos(lam, other)
    assert "<" not in SemanticView.clean("a <*> b <TS>")


def test_window_labels_mark_every_overlapping_window():
    starts = np.arange(0, 600, 60.0)
    label, inj, cat = window_labels(starts, 60, [Injection(0, 0, "config_error", 130, 250)])
    assert label.tolist() == [False, False, True, True, True, False, False, False, False, False]
    assert set(cat[label]) == {"config_error"}
    assert set(inj[~label]) == {-1}
