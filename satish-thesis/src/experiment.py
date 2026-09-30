"""Full experiment: tuning, 5-seed training, missingness grid and imputation sensitivity.

    python src/experiment.py              # everything
    python src/experiment.py --quick      # smoke run: 1 seed, 2 epochs

Two tasks share one code path. "estimate" (primary) follows the baseline study (Mahajan et
al., 2024): hourly HVAC energy is predicted from building and weather sensors without the
HVAC meter history. "forecast" (supplementary) predicts the next hour with the meter history
as an extra input. The split follows the baseline: the last six months of 2020 are the test set. The tree family (persistence, seasonal persistence, XGBoost) and the neural
family run in separate processes because xgboost and torch ship different OpenMP runtimes
that crash each other on macOS. Masks depend only on seeds, so every comparison stays paired.
"""
import sys

arg = lambda k, default: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else default
FAMILY, TASK = arg("--family", "all"), arg("--task", "all")
if FAMILY == "tree":
    import xgboost as xgb  # noqa: F401  must be loaded before torch

import argparse  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

from masking import CHANNELS, SENSORS, FeatureBuilder, make_keep, tabular  # noqa: E402
from models import (BNN, WINDOW, Recurrent, Scales, bnn_loss, pick_device, predict, predict_bnn,  # noqa: E402
                    recurrent_loss, train)

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PERIODS = {"train": ("2018-03-01", "2020-03-31 23:00"), "val": ("2020-04-01", "2020-06-30 23:00"),
           "test": ("2020-07-01", "2020-12-31 22:00")}
RATES = [0.1, 0.2, 0.3, 0.4]
TRAIN_SCEN = [("none", 0.0)] + [(p, r) for p in ("mcar", "block") for r in RATES]
VAL_SCEN = [("none", 0.0), ("mcar", 0.2), ("mcar", 0.4), ("block", 0.2), ("block", 0.4)]
EVAL_SCEN = TRAIN_SCEN + [("block_meter", 0.2), ("block_meter", 0.4)]
E = CHANNELS.index("hvac_kwh")
PAPER_SENSORS = [SENSORS.index(c) for c in ("t_in", "t_out", "rh_out", "solar", "q_int")]
NN_GRID = [dict(hidden=64, lr=1e-3, wd=1e-4, dropout=0.1), dict(hidden=128, lr=1e-3, wd=1e-4, dropout=0.1),
           dict(hidden=64, lr=3e-3, wd=1e-4, dropout=0.1), dict(hidden=64, lr=1e-3, wd=1e-3, dropout=0.2),
           dict(hidden=32, lr=1e-3, wd=0.0, dropout=0.0)]
BNN_GRID = [dict(lr=1e-3, bs=64), dict(lr=1e-3, bs=128), dict(lr=1e-4, bs=64), dict(lr=1e-4, bs=128),
            dict(lr=3e-4, bs=128)]
XGB_GRID = [dict(max_depth=6, learning_rate=0.05), dict(max_depth=4, learning_rate=0.05),
            dict(max_depth=8, learning_rate=0.05), dict(max_depth=6, learning_rate=0.1),
            dict(max_depth=6, learning_rate=0.02)]
LAM_GRID = [0.03, 0.1, 0.3, 1.0, 3.0]
NEURAL = {"BNN-paper": dict(kind="bnn", features="paper"),
          "BNN": dict(kind="bnn", features="tabular"),
          "LSTM": dict(cell="lstm", dual=False, physics=False),
          "GRU": dict(cell="gru", dual=False, physics=False),
          "GRU-aux": dict(cell="gru", dual=True, physics=False),
          "PI-GRU": dict(cell="gru", dual=True, physics=True),
          "PI-GRU-nomask": dict(cell="gru", dual=True, physics=True, nomask=True)}
DEVICE = pick_device() if FAMILY == "nn" else torch.device("cpu")
BNN_DEVICE = torch.device("cuda") if DEVICE.type == "cuda" else torch.device("cpu")
torch.set_num_threads(8)


def load_hourly():
    """Hourly table from src/prepare_data.py, or the bundled compressed copy when raw data is absent."""
    path = ROOT / "data" / "processed" / "bldg59_hourly.csv"
    if not path.exists():
        path = ROOT / "data" / "bldg59_hourly.csv.gz"
    return pd.read_csv(path, parse_dates=["time"], index_col="time")


def rmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)))


def metrics(y, p):
    err = y - p
    nz = y >= 1.0
    return {"MAE": float(np.abs(err).mean()), "RMSE": rmse(y, p),
            "MAPE": float(np.mean(np.abs(err[nz]) / y[nz])),
            "R2": float(1 - (err ** 2).sum() / ((y - y.mean()) ** 2).sum()),
            "NRMSE": rmse(y, p) / float(y.mean()), "neg_pct": float((p < 0).mean() * 100)}


def mask_seed(kind, seed, k):
    return {"train": 50_000, "val": 90_000, "eval": 0}[kind] + 1000 * seed + k


class Data:
    def __init__(self, imputer="locf", task="estimate"):
        df = load_hourly()
        self.df, self.time = df, df.index
        n = len(df)
        period = np.full(n, "", dtype=object)
        for k, (a, b) in PERIODS.items():
            period[(df.index >= a) & (df.index <= b)] = k
        v = df[CHANNELS].to_numpy(float)
        e_next = np.r_[v[1:, E], np.nan]
        t_next = np.r_[v[1:, 0], np.nan]
        same_period = np.r_[period[1:] == period[:-1], False]
        base = (np.arange(n) >= 167) & same_period & ~np.isnan(e_next)
        self.rows = {k: np.where(base & (period == k))[0] for k in PERIODS}
        self.rows["train"] = self.rows["train"][~np.isnan(t_next[self.rows["train"]])]
        self.rows["fit"] = np.r_[self.rows["train"], self.rows["val"][~np.isnan(t_next[self.rows["val"]])]]
        self.fb = FeatureBuilder(df, np.isin(np.arange(n), self.rows["train"]), imputer)
        self.ye, self.yt = e_next, t_next
        nxt = lambda c: np.r_[df[c].to_numpy(float)[1:], np.nan]
        mode = np.tanh((nxt("t_sa") - nxt("t_ra")) / 2.0)
        self.drv = np.column_stack([nxt("t_out"), nxt("q_int"), nxt("solar") / 1000.0, mode])
        self.tnow = v[:, 0]
        self.w = (~np.isnan(self.drv).any(1) & ~np.isnan(self.tnow) & ~np.isnan(t_next)).astype(np.float32)
        hour, dow = df["local_hour"].to_numpy(), df["local_dow"].to_numpy()
        self.duty = ((hour >= 8) & (hour < 17) & (dow < 5)).astype(np.float32)
        tr = self.rows["train"]
        self.sc = Scales(float(np.mean(e_next[tr])), float(np.std(e_next[tr])), float(np.nanmean(t_next[tr])),
                         float(np.nanstd(t_next[tr])), float(np.nanstd((t_next - self.tnow)[tr])))
        log_e = np.log1p(np.clip(e_next[tr], 0, None))
        self.log_mu, self.log_sd = float(log_e.mean()), float(log_e.std())
        fit = self.rows["fit"]
        prof = pd.Series(e_next[fit]).groupby([hour[fit + 1], dow[fit + 1]]).mean()
        self.profile = prof.reindex(pd.MultiIndex.from_arrays([hour, dow])).to_numpy()
        k = len(CHANNELS)
        self.task, self.shift = task, int(task == "estimate")
        month = {3 * k + 4, 3 * k + 5}  # two seasonal cycles are too few to learn month effects
        if task == "estimate":
            self.cols = [i for i in range(3 * k + 7) if (i % k != E or i >= 3 * k) and i not in month]
            self.nomask_cols = [i for i in list(range(E)) + list(range(3 * k, 3 * k + 7)) if i not in month]
        else:
            self.cols = [i for i in range(3 * k + 7) if i not in month]
            self.nomask_cols = [i for i in FeatureBuilder.no_mask_columns() if i not in month]
        self.tab_cols = self.cols + list(range(3 * k + 7, 3 * k + 13))
        self.cache = {}

    def frame(self, pattern, rate, seed):
        key = (pattern, rate, seed)
        if key not in self.cache:
            chans = list(range(len(CHANNELS))) if pattern == "block_meter" else None
            keep = make_keep(self.fb.observed, "block" if pattern == "block_meter" else pattern, rate, seed, chans)
            self.cache[key] = self.fb.frame(keep)
        return self.cache[key]

    def windows(self, frame, rows, cols):
        idx = torch.as_tensor(rows + self.shift)[:, None] + torch.arange(-WINDOW + 1, 1)
        return torch.as_tensor(frame)[idx][..., cols]

    def tab(self, frame, imp, rows):
        if self.task == "forecast":
            return tabular(frame, imp, rows, self.fb.mu[E], self.fb.sd[E])[:, self.tab_cols]
        return np.column_stack([frame[rows + 1][:, self.cols], frame[rows][:, :E]]).astype(np.float32)

    def paper_features(self, frame, rows):
        """Baseline feature set: weather, indoor temperature, other electricity and calendar at the target hour."""
        t = rows + 1
        return np.column_stack([frame[t][:, PAPER_SENSORS], frame[t][:, -7:], self.duty[t]]).astype(np.float32)

    def bnn_features(self, name, frame, imp, rows):
        if NEURAL[name]["features"] == "paper":
            return self.paper_features(frame, rows)
        return self.tab(frame, imp, rows)


# ----------------------------------------------------------------------------- neural family
class Pool:
    """Training pool: the 9 training scenarios (clean + 4 MCAR + 4 block rates) stacked on the device."""

    def __init__(self, data, seed, cols, rows):
        frames = [data.frame(p, r, mask_seed("train", seed, k))[0] for k, (p, r) in enumerate(TRAIN_SCEN)]
        self.F = torch.as_tensor(np.stack(frames), device=DEVICE)
        self.rows, self.cols = rows, cols
        t = lambda a: torch.as_tensor(np.nan_to_num(a), dtype=torch.float32, device=DEVICE)
        self.ye, self.yt, self.tnow, self.drv, self.w = t(data.ye), t(data.yt), t(data.tnow), t(data.drv), t(data.w)
        self.offsets = torch.arange(-WINDOW + 1 + data.shift, 1 + data.shift, device=DEVICE)

    def batch(self, rng, bs=256):
        c = torch.as_tensor(rng.integers(0, len(self.F), bs), device=DEVICE)
        h = torch.as_tensor(rng.choice(self.rows, bs), device=DEVICE)
        x = self.F[c[:, None], h[:, None] + self.offsets][..., self.cols]
        return x, self.ye[h], self.yt[h], self.tnow[h], self.drv[h], self.w[h]


def refit(fit_once, epochs, do_refit):
    """Early-stop on validation, then (final runs) retrain on train + validation for the chosen epoch count."""
    model, info = fit_once("train", epochs, True)
    if do_refit:
        t0 = info["train_s"]
        model, info2 = fit_once("fit", info["best_epoch"], False)
        info = {**info, "train_s": t0 + info2["train_s"]}
    return model, info


def fit_recurrent(data, name, cfg, lam, seed, epochs, do_refit=False):
    spec = NEURAL[name]
    cols = data.nomask_cols if spec.get("nomask") else data.cols
    rows = data.rows["val"]
    xs = [data.windows(data.frame(p, r, mask_seed("val", 0, k))[0], rows, cols) for k, (p, r) in enumerate(VAL_SCEN)]
    val = lambda m: float(np.mean([rmse(data.ye[rows], predict(m, x, data.sc)[0]) for x in xs]))
    lam = lam if spec["physics"] else 0.0

    def fit_once(rows_key, n_epochs, early):
        pool = Pool(data, seed, cols, data.rows[rows_key])
        torch.manual_seed(seed)
        model = Recurrent(len(cols), cfg["hidden"], cfg["dropout"], spec["cell"], spec["dual"], spec["physics"]).to(DEVICE)
        info = train(model, pool.batch, lambda m, b: recurrent_loss(m, b, data.sc, lam), val if early else None,
                     lr=cfg["lr"], wd=cfg["wd"], epochs=n_epochs, seed=seed)
        return model, info

    model, info = refit(fit_once, epochs, do_refit)
    return Predictor(data, "nn", model, cols), model, info


def fit_bnn(data, name, cfg, seed, epochs, do_refit=False):
    rows = data.rows["val"]
    xv = [data.bnn_features(name, *data.frame(p, r, mask_seed("val", 0, k)), rows) for k, (p, r) in enumerate(VAL_SCEN)]
    pred = lambda m, x: predict_bnn(m, x, data.log_mu, data.log_sd, samples=10)
    val = lambda m: float(np.mean([rmse(data.ye[rows], pred(m, x)) for x in xv]))

    def fit_once(rows_key, n_epochs, early):
        tr = data.rows[rows_key]
        X = np.concatenate([data.bnn_features(name, *data.frame(p, r, mask_seed("train", seed, k)), tr)
                            for k, (p, r) in enumerate(TRAIN_SCEN)])
        y = np.tile((np.log1p(np.clip(data.ye[tr], 0, None)) - data.log_mu) / data.log_sd, len(TRAIN_SCEN))
        X, y = torch.as_tensor(X, device=BNN_DEVICE), torch.as_tensor(y, dtype=torch.float32, device=BNN_DEVICE)

        def batch(rng):
            i = torch.as_tensor(rng.integers(0, len(X), cfg["bs"]), device=BNN_DEVICE)
            return X[i], y[i]

        torch.manual_seed(seed)
        model = BNN(X.shape[1]).to(BNN_DEVICE)
        info = train(model, batch, lambda m, b: bnn_loss(m, b, len(X)), val if early else None, lr=cfg["lr"], wd=0.0,
                     epochs=n_epochs, seed=seed)
        return model, info

    model, info = refit(fit_once, epochs, do_refit)
    return Predictor(data, "bnn", model, name=name), model, info


def fit_neural(data, name, chosen, seed, epochs):
    if NEURAL[name].get("kind") == "bnn":
        return fit_bnn(data, name, chosen["BNN"], seed, epochs, do_refit=True)
    cfg = chosen["LSTM"] if name == "LSTM" else chosen["GRU"]
    return fit_recurrent(data, name, cfg, chosen.get("lambda", 0.0), seed, epochs, do_refit=True)


# ----------------------------------------------------------------------------- tree family
def fit_xgb(data, cfg, seed, do_refit=False):
    def design(scen, kind, rows):
        parts = [(data.frame(p, r, mask_seed(kind, 0 if kind == "val" else seed, k)), rows) for k, (p, r) in enumerate(scen)]
        X = np.concatenate([data.tab(f, i, rw) for (f, i), rw in parts])
        return X, np.tile(data.ye[rows], len(scen))

    Xtr, ytr = design(TRAIN_SCEN, "train", data.rows["train"])
    Xva, yva = design(VAL_SCEN, "val", data.rows["val"])
    t0 = time.time()
    m = xgb.XGBRegressor(n_estimators=3000, subsample=0.8, colsample_bytree=0.8, tree_method="hist", n_jobs=8,
                         early_stopping_rounds=100, random_state=seed, **cfg)
    m.fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
    info = {"val_rmse": rmse(yva, m.predict(Xva)), "epochs": int(m.best_iteration) + 1, "train_s": time.time() - t0}
    if do_refit:
        Xf, yf = design(TRAIN_SCEN, "train", data.rows["fit"])
        m = xgb.XGBRegressor(n_estimators=info["epochs"], subsample=0.8, colsample_bytree=0.8, tree_method="hist",
                             n_jobs=8, random_state=seed, **cfg).fit(Xf, yf)
        info["train_s"] = time.time() - t0
    return Predictor(data, "xgb", m), m, info


# ----------------------------------------------------------------------------- tuning
def tune(data, family, quick):
    tag = f"{data.task}_{family}"
    path = RES / f"chosen_{tag}.json"
    if path.exists() and not quick:
        return json.loads(path.read_text(encoding="utf-8"))
    rows, ep = [], (2 if quick else 40)
    strip = lambda r, keys: {k: r[k] for k in keys}
    best = lambda name: min((r for r in rows if r["model"] == name), key=lambda r: r["val_rmse"])
    first = lambda grid: grid[:1] if quick else grid

    def log(model, cfg, info, **extra):
        rows.append({"model": model, **cfg, "val_rmse": info["val_rmse"], "train_s": info["train_s"], **extra})
        print(rows[-1], flush=True)

    if family == "tree":
        for cfg in first(XGB_GRID):
            log("XGBoost", cfg, fit_xgb(data, cfg, 0)[2])
        chosen = {"XGBoost": strip(best("XGBoost"), ("max_depth", "learning_rate"))}
    else:
        for cfg in first(BNN_GRID):
            log("BNN-paper", cfg, fit_bnn(data, "BNN-paper", cfg, 0, ep)[2])
        for cfg in first(NN_GRID):
            log("LSTM", cfg, fit_recurrent(data, "LSTM", cfg, 0.0, 0, ep)[2])
        for cfg in first(NN_GRID):
            log("GRU-aux", cfg, fit_recurrent(data, "GRU-aux", cfg, 0.0, 0, ep)[2])
        gru = strip(best("GRU-aux"), ("hidden", "lr", "wd", "dropout"))
        for lam in LAM_GRID[2:3] if quick else LAM_GRID:
            _, m, info = fit_recurrent(data, "PI-GRU", gru, lam, 0, ep)
            log("PI-GRU", gru, info, **{"lambda": lam, **m.physics.describe()})
        chosen = {"BNN": strip(best("BNN-paper"), ("lr", "bs")),
                  "LSTM": strip(best("LSTM"), ("hidden", "lr", "wd", "dropout")), "GRU": gru,
                  "lambda": best("PI-GRU")["lambda"]}
    pd.DataFrame(rows).to_csv(RES / f"tuning_{tag}{'_quick' if quick else ''}.csv", index=False)
    if not quick:
        path.write_text(json.dumps(chosen, indent=2), encoding="utf-8")
    return chosen


# ----------------------------------------------------------------------------- evaluation
def ref_rc(data):
    """Grey-box RC fitted by least squares on clean training rows: the physics yard-stick for every model."""
    r = data.rows["train"][data.w[data.rows["train"]] > 0]
    T, d = data.tnow[r], data.drv[r]
    A = np.column_stack([d[:, 0] - T, d[:, 3] * data.ye[r], d[:, 1], d[:, 2], np.ones(len(r))])
    coef, *_ = np.linalg.lstsq(A, data.yt[r] - T, rcond=None)
    return coef


def rc_residual(coef, data, rows, e_hat, t_hat):
    T, d = data.tnow[rows], data.drv[rows]
    rhs = coef[0] * (d[:, 0] - T) + coef[1] * d[:, 3] * e_hat + coef[2] * d[:, 1] + coef[3] * d[:, 2] + coef[4]
    r = ((t_hat - T) - rhs)[data.w[rows] > 0]
    return float(np.sqrt(np.mean(r ** 2)))


class Predictor:
    """Uniform predict(frame, imp, rows) -> (energy, temperature or None) over all model kinds."""

    def __init__(self, data, kind, obj=None, cols=None, name=None):
        self.d, self.kind, self.obj, self.cols, self.name = data, kind, obj, cols, name

    def __call__(self, frame, imp, rows):
        d = self.d
        if self.kind == "profile":
            return d.profile[rows + 1], None
        if self.kind == "persistence":
            return imp[rows, E], None
        if self.kind == "seasonal":
            return imp[rows - 23, E], None
        if self.kind == "xgb":
            return self.obj.predict(d.tab(frame, imp, rows)), None
        if self.kind == "bnn":
            return predict_bnn(self.obj, d.bnn_features(self.name, frame, imp, rows), d.log_mu, d.log_sd), None
        return predict(self.obj, d.windows(frame, rows, self.cols), d.sc)


def evaluate(data, preds, seed, coef, scen_list):
    out, store = [], {}
    rows = data.rows["test"]
    y = data.ye[rows]
    for p, r in scen_list:
        if p == "block_meter" and data.task == "estimate":
            continue
        frame, imp = data.frame(p, r, mask_seed("eval", seed, EVAL_SCEN.index((p, r))))
        for name, pr in preds.items():
            e_hat, t_hat = pr(frame, imp, rows)
            row = {"model": name, "seed": seed, "pattern": p, "rate": r, **metrics(y, e_hat)}
            if t_hat is not None:
                okt = ~np.isnan(data.yt[rows])
                row["temp_RMSE"] = rmse(data.yt[rows][okt], t_hat[okt])
                row["rc_residual"] = rc_residual(coef, data, rows, e_hat, t_hat)
            out.append(row)
            store[f"{name}|{seed}|{p}|{r}"] = e_hat.astype(np.float32)
    return out, store


def plausibility(data, preds, seed):
    """+1 degC outdoor temperature at every input step. In cooling hours HVAC energy should not fall."""
    frame, imp = data.frame("none", 0.0, mask_seed("eval", seed, 0))
    j = SENSORS.index("t_out")
    f2, i2 = frame.copy(), imp.copy()
    f2[:, j] += 1.0 / data.fb.sd[j]
    i2[:, j] += 1.0
    rows = data.rows["test"]
    cooling = data.drv[rows, 3] < -0.2
    out = []
    for name, pr in preds.items():
        if name in ("Persistence", "Seasonal", "Profile"):
            continue
        d = pr(f2, i2, rows)[0] - pr(frame, imp, rows)[0]
        out.append({"model": name, "seed": seed, "mean_dE_per_degC": float(d.mean()),
                    "cooling_mean_dE": float(d[cooling].mean()), "implausible_pct": float((d[cooling] < 0).mean() * 100)})
    return out


def infer_us_per_sample(pr, data, seed):
    frame, imp = data.frame("none", 0.0, mask_seed("eval", seed, 0))
    rows = data.rows["test"]
    t0 = time.time()
    pr(frame, imp, rows)
    return (time.time() - t0) / len(rows) * 1e6


def fit_family(data, family, chosen, seed, quick, names=tuple(NEURAL)):
    preds, cost, coefs, hist = {}, [], [], {}
    if family == "tree":
        if data.task == "forecast":
            preds = {"Persistence": Predictor(data, "persistence"), "Seasonal": Predictor(data, "seasonal")}
        else:
            preds = {"Profile": Predictor(data, "profile")}
        preds["XGBoost"], _, info = fit_xgb(data, chosen["XGBoost"], seed, do_refit=True)
        cost.append({"model": "XGBoost", "seed": seed, "train_s": info["train_s"], "epochs_or_trees": info["epochs"]})
        return preds, cost, coefs, hist
    for name in names:
        preds[name], model, info = fit_neural(data, name, chosen, seed, 2 if quick else 40)
        cost.append({"model": name, "seed": seed, "train_s": info["train_s"], "epochs_or_trees": info["best_epoch"]})
        hist[f"{name}|{seed}"] = info["history"]
        if getattr(model, "physics", None) is not None:
            coefs.append({"model": name, "seed": seed, "lambda": chosen["lambda"], **model.physics.describe()})
        print(f"seed {seed} {name}: val {info['val_rmse']:.3f} in {info['train_s']:.0f}s ({info['epochs']} ep)", flush=True)
    return preds, cost, coefs, hist


def run_main(data, family, chosen, seeds, quick):
    coef = ref_rc(data)
    mrows, store, coefs, plaus, cost, hist = [], {}, [], [], [], {}
    for seed in seeds:
        preds, c, pc, h = fit_family(data, family, chosen, seed, quick)
        for row in c:
            row["infer_us_per_sample"] = infer_us_per_sample(preds[row["model"]], data, seed)
        cost, coefs = cost + c, coefs + pc
        hist.update(h)
        rows, st = evaluate(data, preds, seed, coef, EVAL_SCEN)
        mrows += rows
        store.update(st)
        plaus += plausibility(data, preds, seed)
        data.cache.clear()
        print(f"[{family}] seed {seed} evaluated", flush=True)
    tag = f"_{data.task}_{family}" + ("_quick" if quick else "")
    pd.DataFrame(mrows).to_csv(RES / f"metrics{tag}.csv", index=False)
    pd.DataFrame(plaus).to_csv(RES / f"plausibility{tag}.csv", index=False)
    pd.DataFrame(cost).to_csv(RES / f"cost{tag}.csv", index=False)
    if coefs:
        pd.DataFrame(coefs).to_csv(RES / f"physics_coefs{tag}.csv", index=False)
        (RES / f"train_history{tag}.json").write_text(json.dumps(hist), encoding="utf-8")
    extra = {}
    if family == "tree":
        r = data.rows["test"]
        extra = {"y": data.ye[r], "t": data.time[r + 1].astype("int64").to_numpy(), "drv": data.drv[r],
                 "local_hour": data.df["local_hour"].to_numpy()[r + 1], "local_dow": data.df["local_dow"].to_numpy()[r + 1]}
        (RES / f"ref_rc_{data.task}.json").write_text(json.dumps(dict(zip("abcde", map(float, coef))), indent=2), encoding="utf-8")
    np.savez_compressed(RES / f"predictions{tag}.npz", **store, **extra)


def run_imputation(task, family, chosen, seeds, quick):
    out = []
    keep = {"tree": ["XGBoost"], "nn": ["GRU-aux", "PI-GRU"]}[family]
    for imputer in ("mean", "cart"):
        data = Data(imputer, task)
        coef = ref_rc(data)
        for seed in seeds:
            preds, *_ = fit_family(data, family, chosen, seed, quick, names=keep)
            rows, _ = evaluate(data, {k: preds[k] for k in keep}, seed, coef, VAL_SCEN)
            out += [{"imputer": imputer, **r} for r in rows]
            data.cache.clear()
            print(f"[{family}] imputer {imputer} seed {seed} done", flush=True)
    pd.DataFrame(out).to_csv(RES / f"imputation_{task}_{family}{'_quick' if quick else ''}.csv", index=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--family", default="all", choices=["all", "tree", "nn"])
    ap.add_argument("--task", default="all", choices=["all", "estimate", "forecast"])
    ap.add_argument("--stage", default="all", choices=["all", "main", "imputation"])
    a = ap.parse_args()
    RES.mkdir(exist_ok=True)
    if a.family == "all" or a.task == "all":
        for task in (("estimate", "forecast") if a.task == "all" else (a.task,)):
            for fam in (("tree", "nn") if a.family == "all" else (a.family,)):
                cmd = [sys.executable, str(Path(__file__).resolve()), "--family", fam, "--task", task, "--stage", a.stage]
                subprocess.run(cmd + (["--quick"] if a.quick else []), check=True)
        return
    data = Data("locf", a.task)
    meta = {"task": a.task, "family": a.family, "device": str(DEVICE), **{k: int(len(v)) for k, v in data.rows.items()},
            "periods": PERIODS, "started": time.strftime("%Y-%m-%d %H:%M"), "torch": torch.__version__}
    print(meta, flush=True)
    chosen = tune(data, a.family, a.quick)
    print("chosen", chosen, flush=True)
    seeds = [0] if a.quick else [0, 1, 2, 3, 4]
    if a.stage in ("all", "main"):
        run_main(data, a.family, chosen, seeds, a.quick)
    if a.stage in ("all", "imputation") and a.task == "estimate":
        run_imputation(a.task, a.family, chosen, [0] if a.quick else [0, 1, 2], a.quick)
    meta["finished"] = time.strftime("%Y-%m-%d %H:%M")
    (RES / f"run_meta_{a.task}_{a.family}{'_quick' if a.quick else ''}.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
