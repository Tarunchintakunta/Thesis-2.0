import numpy as np
import pandas as pd
import pytest

from logad.detectors.oneclass_iforest import IforestDetector
from logad.detectors.oneclass_ocsvm import OcsvmDetector
from logad.detectors.thresholds import ThresholdAlarms, metric_windows
from logad.detectors.transfer_elfa import ElfaStyleTransfer, binary_entropy, coral_matrix

RNG = np.random.default_rng(0)
NORMAL = RNG.normal(0, 1, size=(400, 5))
OUTLIERS = RNG.normal(8, 1, size=(20, 5))


@pytest.mark.parametrize("cls", [OcsvmDetector, IforestDetector])
def test_one_class_models_flag_far_points(cls):
    det = cls(threshold_quantile=0.99).fit(NORMAL)
    assert det.predict(NORMAL).mean() <= 0.02  # ~1 % by construction
    assert det.predict(OUTLIERS).mean() > 0.9
    assert det.score(OUTLIERS).mean() > det.score(NORMAL).mean()


def test_iforest_cannot_use_a_feature_that_was_constant_in_training():
    # the blind spot that made "lowest validation FAR" a bad rule for picking D1
    train = np.hstack([NORMAL, np.zeros((len(NORMAL), 1))])
    novel = train[:20].copy()
    novel[:, -1] = 50.0
    assert IforestDetector().fit(train).predict(novel).mean() < 0.2
    assert OcsvmDetector().fit(train).predict(novel).mean() > 0.9


def test_binary_entropy():
    assert binary_entropy(np.array([0.5]))[0] == pytest.approx(np.log(2))
    assert binary_entropy(np.array([0.0001]))[0] < 0.01


def test_coral_matches_target_covariance():
    src = RNG.normal(0, 1, size=(2000, 3))
    tgt = RNG.normal(0, 1, size=(2000, 3)) @ np.array([[3, 0, 0], [1, 1, 0], [0, 0, 0.2]])
    aligned = src @ coral_matrix(src, tgt, eps=1e-6)
    assert np.allclose(np.cov(aligned, rowvar=False), np.cov(tgt, rowvar=False), atol=0.3)


def _words(n, anomalous, rng):
    # bag of words counts: "error" style columns for anomalies, "info" columns otherwise
    X = rng.poisson(1.0, size=(n, 40)).astype(float)
    if anomalous:
        X[:, :5] += rng.poisson(4.0, size=(n, 5))
    return X


def test_transfer_learns_shared_error_words():
    rng = np.random.default_rng(1)
    xs = np.vstack([_words(150, False, rng), _words(50, True, rng)])
    ys = np.array([0] * 150 + [1] * 50)
    xt_train = _words(200, False, rng) * 1.5  # target: different scale, no labels
    model = ElfaStyleTransfer(svd_components=8, rounds=2).fit(xs, ys, xt_train)
    xt_eval = np.vstack([_words(100, False, rng) * 1.5, _words(100, True, rng) * 1.5])
    yt = np.array([0] * 100 + [1] * 100)
    acc = (model.predict(xt_eval) == yt).mean()
    assert acc > 0.7
    assert len(model.history) == 2
    assert model.source_accuracy(xs, ys) > 0.8


def test_transfer_needs_both_classes_in_the_source():
    with pytest.raises(ValueError):
        ElfaStyleTransfer().fit(np.ones((10, 5)), np.zeros(10), np.ones((10, 5)))


def test_metric_windows_and_alarms():
    req = pd.DataFrame({
        "t": [0, 10, 70, 75, 80, 130],
        "throttled": [False, False, False, False, True, False],
        "status": [200, 500, 200, 504, 429, 200],
        "error": [False, False, False, True, False, False],
        "duration_ms": [10, 12, 3000, 3000, 0, 11],
        "timeout": [False, False, False, True, False, False],
        "killed": [False] * 6,
    })
    w = metric_windows(req, 0, 180, 60)
    assert w["api_5xx"].tolist() == [1, 1, 0]
    assert w["lambda_errors"].tolist() == [0, 1, 0]
    assert w["throttles"].tolist() == [0, 1, 0]
    alarms = ThresholdAlarms([{"name": "5xx", "metric": "api_5xx", "floor": 0},
                              {"name": "p99", "metric": "duration_p99_ms", "floor": 100}], 0.99)
    alarms.fit(pd.DataFrame({"api_5xx": [0.0, 0.0], "duration_p99_ms": [20.0, 30.0]}))
    assert alarms.thresholds == {"5xx": 0.0, "p99": 100.0}
    assert alarms.predict(w).tolist() == [True, True, False]
