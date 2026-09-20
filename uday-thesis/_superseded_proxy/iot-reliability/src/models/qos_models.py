import numpy as np
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE

RF_PARAMS = dict(n_estimators=200, max_depth=10, min_samples_split=10, min_samples_leaf=1)


def _smote_balance(X, y, seed):
    counts = np.bincount(y, minlength=3)
    if counts.min() < 2:
        return X, y  # SMOTE needs at least 2 samples of the minority class
    k_neighbors = max(1, min(5, counts.min() - 1))
    sm = SMOTE(random_state=seed, k_neighbors=k_neighbors)
    return sm.fit_resample(X, y)


class CentralizedRF:
    """Baseline reproduction of Et-Tousy et al. (2026): all sites' raw
    telemetry is pooled centrally, SMOTE-balanced, and a single Random
    Forest is trained on it -- the model the paper actually deployed."""

    def __init__(self, seed):
        self.seed = seed
        self.model = RandomForestClassifier(random_state=seed, **RF_PARAMS)

    def fit(self, site_frames, feature_cols):
        X = np.concatenate([df[feature_cols].values for df in site_frames.values()])
        y = np.concatenate([df["label"].values for df in site_frames.values()])
        X_bal, y_bal = _smote_balance(X, y, self.seed)
        self.model.fit(X_bal, y_bal)
        return self

    def predict(self, X):
        return self.model.predict(X)


class FederatedEnsembleRF:
    """Improvement: addresses the paper's own stated gap -- 'the system
    currently relies on a centralized learning mechanism, which might not
    scale well or guarantee data privacy in distributed IoT environments'
    -- by training one Random Forest per site, on that site's local data
    only (SMOTE-balanced locally, never pooled with any other site's raw
    telemetry), and combining their predictions by averaging predicted
    class probabilities at inference time. No raw record ever leaves the
    site it was generated on."""

    def __init__(self, seed):
        self.seed = seed
        self.site_models = {}

    def fit(self, site_frames, feature_cols):
        for i, (site, df) in enumerate(site_frames.items()):
            X = df[feature_cols].values
            y = df["label"].values
            X_bal, y_bal = _smote_balance(X, y, self.seed + i)
            model = RandomForestClassifier(random_state=self.seed + i, **RF_PARAMS)
            model.fit(X_bal, y_bal)
            self.site_models[site] = model
        return self

    def predict(self, X):
        probs = np.mean([m.predict_proba(X) for m in self.site_models.values()], axis=0)
        return probs.argmax(axis=1)

    def predict_single_site(self, site, X):
        """A site's own local model in isolation -- no federation at all.
        Used as a lower-bound comparison: this is what a site is stuck
        with if it can't share models or data with anyone else."""
        return self.site_models[site].predict(X)
