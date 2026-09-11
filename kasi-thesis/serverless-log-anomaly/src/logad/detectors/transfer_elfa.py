"""D2 - ELFA-Log style cross-system transfer (Zhao et al., 2025), re-implemented.

The baseline removes the need for *target* labels but still needs a
*labelled source*. What is reproduced here from the paper's description:

1. a classifier trained on a labelled source system (Loghub BGL windows),
2. distance-based **feature alignment** between source and target - done with
   CORAL (the source features are re-coloured so their covariance matches the
   target's, which minimises the distance between the two second-order
   statistics),
3. **enhanced pseudo-labelling** - unlabelled target windows the classifier is
   confident about (low prediction entropy) are added to the training set with
   their predicted label, for a few rounds.

Deliberate simplifications (must be stated when reporting D2): a linear
classifier instead of a neural encoder, hashed bag-of-words template features
instead of pretrained embeddings, CORAL instead of the paper's exact alignment
loss. This is a faithful *operational* replication of the procedure, not the
authors' code. The unlabelled target data is phase A only, so the
chronological protocol holds (no evaluation logs are seen during training).
"""
from __future__ import annotations

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, normalize


def _sqrtm(mat: np.ndarray, inverse: bool = False) -> np.ndarray:
    vals, vecs = np.linalg.eigh(mat)
    vals = np.clip(vals, 1e-12, None)
    power = -0.5 if inverse else 0.5
    return (vecs * vals**power) @ vecs.T


def coral_matrix(source: np.ndarray, target: np.ndarray, eps: float = 1.0) -> np.ndarray:
    """A such that source @ A has (roughly) the target covariance (Sun et al. CORAL)."""
    d = source.shape[1]
    cs = np.cov(source, rowvar=False) + eps * np.eye(d)
    ct = np.cov(target, rowvar=False) + eps * np.eye(d)
    return _sqrtm(cs, inverse=True) @ _sqrtm(ct)


def binary_entropy(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return -(p * np.log(p) + (1 - p) * np.log(1 - p))


class ElfaStyleTransfer:
    name = "d2_transfer"

    def __init__(self, svd_components: int = 32, coral_eps: float = 1.0, C: float = 1.0,
                 class_weight: str | None = "balanced", max_iter: int = 2000, rounds: int = 3,
                 entropy_threshold: float = 0.3, pseudo_weight: float = 0.5,
                 decision_threshold: float = 0.5, random_state: int = 0) -> None:
        self.svd_components = svd_components
        self.coral_eps = coral_eps
        self.clf_params = {"C": C, "class_weight": class_weight, "max_iter": max_iter}
        self.rounds = rounds
        self.entropy_threshold = entropy_threshold
        self.pseudo_weight = pseudo_weight
        self.decision_threshold = decision_threshold
        self.random_state = random_state
        self.history: list[dict] = []

    # -- shared, unsupervised preprocessing ---------------------------------------
    def _embed(self, X: np.ndarray) -> np.ndarray:
        return self.svd.transform(normalize(self.tfidf.transform(X)))

    def fit(self, Xs: np.ndarray, ys: np.ndarray, Xt: np.ndarray) -> "ElfaStyleTransfer":
        ys = np.asarray(ys, dtype=int)
        if len(set(ys)) < 2:
            raise ValueError("the labelled source needs both normal and anomalous windows")
        both = np.vstack([Xs, Xt])
        self.tfidf = TfidfTransformer(sublinear_tf=True).fit(both)
        k = max(2, min(self.svd_components, both.shape[1] - 1, both.shape[0] - 1))
        self.svd = TruncatedSVD(n_components=k, random_state=self.random_state)
        self.svd.fit(normalize(self.tfidf.transform(both)))

        es, et = self._embed(Xs), self._embed(Xt)
        self.scaler_s = StandardScaler().fit(es)
        self.scaler_t = StandardScaler().fit(et)
        ss, st = self.scaler_s.transform(es), self.scaler_t.transform(et)

        # feature alignment: bring the source into the target's covariance structure
        self.A = coral_matrix(ss, st, self.coral_eps)
        sa = ss @ self.A

        X, y, w = sa, ys, np.ones(len(ys))
        self.history = []
        clf = LogisticRegression(**self.clf_params).fit(X, y, sample_weight=w)
        for rnd in range(self.rounds):
            p = clf.predict_proba(st)[:, 1]
            confident = binary_entropy(p) < self.entropy_threshold
            pseudo = (p[confident] >= 0.5).astype(int)
            self.history.append({"round": rnd, "target_windows": int(len(st)), "pseudo_labelled": int(confident.sum()),
                                 "pseudo_anomalous": int(pseudo.sum())})
            X = np.vstack([sa, st[confident]])
            y = np.concatenate([ys, pseudo])
            w = np.concatenate([np.ones(len(ys)), np.full(int(confident.sum()), self.pseudo_weight)])
            clf = LogisticRegression(**self.clf_params).fit(X, y, sample_weight=w)
        self.clf = clf
        return self

    def _target(self, Xt: np.ndarray) -> np.ndarray:
        return self.scaler_t.transform(self._embed(Xt))

    def score(self, Xt: np.ndarray) -> np.ndarray:
        return self.clf.predict_proba(self._target(Xt))[:, 1]

    def predict(self, Xt: np.ndarray) -> np.ndarray:
        return self.score(Xt) >= self.decision_threshold

    def source_accuracy(self, Xs: np.ndarray, ys: np.ndarray) -> float:
        """Sanity check: how well the final model fits its own (aligned) source."""
        sa = self.scaler_s.transform(self._embed(Xs)) @ self.A
        return float((self.clf.predict(sa) == np.asarray(ys, dtype=int)).mean())
