"""Neural forecasters and the RC thermal-balance physics term.

All recurrent models read the same 24 h window of per-hour features and forecast
HVAC energy for the next hour. Dual-head models also forecast next-hour indoor
temperature; the physics-informed model adds a soft first-order RC residual:

    T[h+1] - T[h] = a (T_out[h+1] - T[h]) + b m[h+1] E[h+1] + c Q_int[h+1] + d S[h+1] + e

with a = UA/C, b = eta/C, c = beta/C, d = gamma/C all constrained positive (softplus),
m = tanh((T_sa - T_ra)/2) the HVAC mode (+ heating, - cooling), and dt = 1 h.
"""
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

WINDOW = 24


def inv_softplus(x):
    return float(np.log(np.expm1(x)))


class RCPhysics(nn.Module):
    def __init__(self):
        super().__init__()
        # start at tau = 24 h and small gains; everything is learned from data
        self.raw = nn.Parameter(torch.tensor([inv_softplus(1 / 24), inv_softplus(1e-3),
                                              inv_softplus(1e-2), inv_softplus(1e-2)]))
        self.e = nn.Parameter(torch.zeros(1))

    def coefs(self):
        a, b, c, d = F.softplus(self.raw)
        return a, b, c, d, self.e[0]

    def rhs(self, t_now, drv, e_next):
        """drv columns: t_out, q_int, solar (kW/m2), mode at h+1."""
        a, b, c, d, e = self.coefs()
        return a * (drv[:, 0] - t_now) + b * drv[:, 3] * e_next + c * drv[:, 1] + d * drv[:, 2] + e

    def describe(self):
        a, b, c, d, e = [float(v.detach()) for v in self.coefs()]
        return {"a_UA_over_C": a, "tau_h": 1 / a, "b_eta_over_C": b, "c_beta_over_C": c,
                "d_gamma_over_C": d, "e_offset": e}


class Recurrent(nn.Module):
    def __init__(self, n_in, hidden=64, dropout=0.1, cell="gru", dual=False, physics=False):
        super().__init__()
        rnn = nn.GRU if cell == "gru" else nn.LSTM
        self.rnn = rnn(n_in, hidden, batch_first=True)
        self.drop = nn.Dropout(dropout)
        self.body = nn.Sequential(nn.Linear(hidden, hidden), nn.ReLU())
        self.head_e = nn.Linear(hidden, 1)
        self.head_t = nn.Linear(hidden, 1) if dual else None
        self.physics = RCPhysics() if physics else None

    def forward(self, x):
        out, _ = self.rnn(x)
        z = self.body(self.drop(out[:, -1]))
        e = self.head_e(z).squeeze(-1)
        t = self.head_t(z).squeeze(-1) if self.head_t is not None else None
        return e, t


class Scales:
    """Target scaling (train statistics) shared by the loss and the physics term."""

    def __init__(self, mu_e, sd_e, mu_t, sd_t, sd_dt):
        self.mu_e, self.sd_e, self.mu_t, self.sd_t, self.sd_dt = mu_e, sd_e, mu_t, sd_t, sd_dt


def losses(model, batch, sc, lam, alpha=1.0):
    x, ye, yt, tnow, drv, w = batch
    pe, pt = model(x)
    loss_e = F.huber_loss(pe, (ye - sc.mu_e) / sc.sd_e)
    total, parts = loss_e, {"energy": float(loss_e)}
    if pt is not None:
        loss_t = F.huber_loss(pt, (yt - sc.mu_t) / sc.sd_t)
        total = total + alpha * loss_t
        parts["temp"] = float(loss_t)
        if model.physics is not None and lam > 0:
            e_hat = pe * sc.sd_e + sc.mu_e
            t_hat = pt * sc.sd_t + sc.mu_t
            r = ((t_hat - tnow) - model.physics.rhs(tnow, drv, e_hat)) / sc.sd_dt
            # mask-aware: the residual only counts where every physical driver was really measured
            loss_p = (w * F.huber_loss(r, torch.zeros_like(r), reduction="none")).sum() / w.sum().clamp(min=1)
            total = total + lam * loss_p
            parts["physics"] = float(loss_p)
    return total, parts


def train(model, sample_batch, val_fn, sc, lam=0.0, lr=1e-3, wd=1e-4, epochs=40, steps=120, patience=6, seed=0):
    """sample_batch(rng) -> tensors; val_fn(model) -> validation RMSE (kWh). Early stopping on val_fn."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    best, best_state, bad, history = np.inf, None, 0, []
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        for _ in range(steps):
            loss, _ = losses(model, sample_batch(rng), sc, lam)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        model.eval()
        v = val_fn(model)
        history.append(v)
        if v < best - 1e-4:
            best, bad = v, 0
            best_state = {k: t.detach().clone() for k, t in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    model.eval()
    return {"val_rmse": best, "epochs": ep + 1, "train_s": time.time() - t0, "history": history}


@torch.no_grad()
def predict(model, x, sc, bs=4096):
    es, ts = [], []
    for i in range(0, len(x), bs):
        e, t = model(x[i:i + bs])
        es.append(e * sc.sd_e + sc.mu_e)
        if t is not None:
            ts.append(t * sc.sd_t + sc.mu_t)
    e = torch.cat(es).numpy()
    t = torch.cat(ts).numpy() if ts else None
    return e, t


def demo():
    """Self-check: the physics residual is zero for data generated by the RC equation."""
    torch.manual_seed(0)
    phys = RCPhysics()
    n = 64
    tnow = 22 + torch.randn(n)
    drv = torch.stack([15 + 5 * torch.randn(n), torch.rand(n) * 10, torch.rand(n), -torch.rand(n)], 1)
    e = 30 + 5 * torch.rand(n)
    t_next = tnow + phys.rhs(tnow, drv, e)
    r = (t_next - tnow) - phys.rhs(tnow, drv, e)
    assert r.abs().max() < 1e-5
    m = Recurrent(34, dual=True, physics=True)
    pe, pt = m(torch.randn(8, WINDOW, 34))
    assert pe.shape == (8,) and pt.shape == (8,)
    print("models demo ok", phys.describe()["tau_h"])


if __name__ == "__main__":
    demo()
