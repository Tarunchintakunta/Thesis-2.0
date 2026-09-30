"""Controlled sensor loss, causal imputation and feature construction.

All functions work on the full hourly timeline. A "keep" matrix says which (hour, channel)
readings a model is allowed to see. Natural gaps are always missing; controlled masks remove
a further fraction of the readings that were observed.
"""
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.tree import DecisionTreeRegressor

SENSORS = ["t_in", "t_out", "rh_out", "solar", "q_int", "t_sa", "t_ra", "fan"]
CHANNELS = SENSORS + ["hvac_kwh"]   # the meter history is a channel too, masked only in the stress test
TSL_CAP = 168                        # hours; "time since last observation" is capped at one week


def mcar_mask(observed, rate, rng, channels):
    keep = observed.copy()
    drop = rng.random(observed.shape) < rate
    keep[:, channels] &= ~drop[:, channels]
    return keep


def block_mask(observed, rate, rng, channels, min_len=6, max_len=72, max_width=3):
    """Contiguous outages of 6-72 h hitting 1-3 channels at once (e.g. a BAS controller dropping)."""
    keep = observed.copy()
    target = rate * observed[:, channels].sum()
    removed, n = 0, len(observed)
    while removed < target:
        length = int(rng.integers(min_len, max_len + 1))
        start = int(rng.integers(0, n - length))
        width = int(rng.integers(1, min(max_width, len(channels)) + 1))
        chans = rng.choice(channels, size=width, replace=False)
        block = keep[start:start + length][:, chans]
        removed += int(block.sum())
        keep[start:start + length, chans] = False
    return keep


def make_keep(observed, pattern, rate, seed, channels=None):
    """pattern: 'mcar' | 'block'. channels: column indices of CHANNELS that may be removed."""
    if channels is None:
        channels = list(range(len(SENSORS)))
    if rate == 0:
        return observed.copy()
    rng = np.random.default_rng(seed)
    fn = mcar_mask if pattern == "mcar" else block_mask
    return fn(observed, rate, rng, np.asarray(channels))


def time_since_last(keep):
    n = len(keep)
    idx = np.where(keep, np.arange(n)[:, None], -10 ** 9)
    last = np.maximum.accumulate(idx, axis=0)
    return np.minimum(np.arange(n)[:, None] - last, TSL_CAP)


class Imputer:
    """Causal imputers fitted on training rows only. 'locf' = last observation carried forward,
    'mean' = training mean, 'cart' = iterative CART regression on the other channels at the same hour."""

    def __init__(self, kind, values, train_rows):
        self.kind = kind
        self.mean = np.nanmean(values[train_rows], axis=0)
        if kind == "cart":
            self.model = IterativeImputer(DecisionTreeRegressor(max_depth=8, min_samples_leaf=20, random_state=0),
                                          max_iter=5, random_state=0, skip_complete=True)
            self.model.fit(values[train_rows])

    def __call__(self, values, keep):
        v = np.where(keep, values, np.nan)
        if self.kind == "locf":
            out = pd.DataFrame(v).ffill().to_numpy()
        elif self.kind == "cart":
            out = self.model.transform(v)
        else:
            out = v
        return np.where(np.isnan(out), self.mean, out)


def calendar(df):
    h, d, m = df["local_hour"].to_numpy(), df["local_dow"].to_numpy(), df["local_month"].to_numpy()
    tau = 2 * np.pi
    return np.column_stack([np.sin(tau * h / 24), np.cos(tau * h / 24), np.sin(tau * d / 7), np.cos(tau * d / 7),
                            np.sin(tau * m / 12), np.cos(tau * m / 12), (d >= 5).astype(float)])


class FeatureBuilder:
    """Turns (timeline, keep) into the per-hour feature matrix shared by every model.

    Per-hour layout: 9 standardised imputed values | 9 observation masks | 9 scaled
    time-since-last-observation | 7 calendar terms  -> 34 columns.
    """

    def __init__(self, df, train_rows, imputer="locf"):
        self.df = df
        self.values = df[CHANNELS].to_numpy(dtype=float)
        self.observed = ~np.isnan(self.values)
        self.cal = calendar(df)
        self.imputer = Imputer(imputer, self.values, train_rows)
        self.mu = np.nanmean(self.values[train_rows], axis=0)
        self.sd = np.nanstd(self.values[train_rows], axis=0)

    def frame(self, keep):
        imp = self.imputer(self.values, keep)
        z = (imp - self.mu) / self.sd
        tsl = np.log1p(time_since_last(keep)) / np.log1p(TSL_CAP)
        return np.column_stack([z, keep.astype(float), tsl, self.cal]).astype(np.float32), imp

    @staticmethod
    def no_mask_columns():
        k = len(CHANNELS)
        return list(range(k)) + list(range(3 * k, 3 * k + 7))


def tabular(frame, imp, rows, mu_e, sd_e):
    """Features for XGBoost at hour h: the hour-h frame plus meter lags and a 24 h mean."""
    e = (imp[:, CHANNELS.index("hvac_kwh")] - mu_e) / sd_e
    tin = imp[:, 0]
    roll = pd.Series(e).rolling(24, min_periods=1).mean().to_numpy()
    extra = np.column_stack([e[rows - 1], e[rows - 2], e[rows - 23], e[rows - 167], roll[rows],
                             tin[rows] - tin[rows - 1]])
    return np.column_stack([frame[rows], extra]).astype(np.float32)


def demo():
    """Self-check: rates are hit, natural gaps stay missing, features are causal."""
    rng = np.random.default_rng(0)
    obs = rng.random((5000, 9)) > 0.05
    for pattern in ("mcar", "block"):
        keep = make_keep(obs, pattern, 0.3, 1)
        lost = 1 - keep[:, :8].sum() / obs[:, :8].sum()
        assert 0.27 < lost < 0.36, (pattern, lost)
        assert not (keep & ~obs).any()
        assert (keep[:, 8] == obs[:, 8]).all()          # meter untouched by default
    tsl = time_since_last(np.array([[1], [0], [0], [1]], bool))
    assert tsl[:, 0].tolist() == [0, 1, 2, 0]
    print("masking demo ok")


if __name__ == "__main__":
    demo()
