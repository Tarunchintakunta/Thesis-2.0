"""Neural forecasters, the RC thermal-balance physics term and the Bayesian baseline.

Physics-informed residual (first-order RC balance, dt = 1 h):

    T[h+1] - T[h] = a (T_out[h+1] - T[h]) + b m[h+1] E[h+1] + c Q_int[h+1] + d S[h+1] + e

a = UA/C, b = eta/C, c = beta/C, d = gamma/C are positive (softplus), m = tanh((T_sa - T_ra)/2)
is the HVAC mode (+ heating, - cooling).
"""
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

WINDOW = 24


def pick_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def inv_softplus(x):
    return float(np.log(np.expm1(x)))


class RCPhysics(nn.Module):
    def __init__(self):
        super().__init__()
        self.raw = nn.Parameter(torch.tensor([inv_softplus(1 / 24), inv_softplus(1e-3),
                                              inv_softplus(1e-2), inv_softplus(1e-2)]))
        self.e = nn.Parameter(torch.zeros(1))

    def coefs(self):
        a, b, c, d = F.softplus(self.raw)
        return a, b, c, d, self.e[0]

    def rhs(self, t_now, drv, e_next):
        """drv columns: t_out, q_int, solar (kW/m2), mode, all at h+1."""
        a, b, c, d, e = self.coefs()
        return a * (drv[:, 0] - t_now) + b * drv[:, 3] * e_next + c * drv[:, 1] + d * drv[:, 2] + e

    def describe(self):
        a, b, c, d, e = [float(v.detach().cpu()) for v in self.coefs()]
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


class BayesLinear(nn.Module):
    """Mean-field Gaussian linear layer (Bayes by backprop) with a N(0, prior^2) prior."""

    def __init__(self, n_in, n_out, prior=1.0):
        super().__init__()
        bound = 1 / np.sqrt(n_in)
        self.w_mu = nn.Parameter(torch.empty(n_out, n_in).uniform_(-bound, bound))
        self.w_rho = nn.Parameter(torch.full((n_out, n_in), -6.0))
        self.b_mu = nn.Parameter(torch.zeros(n_out))
        self.b_rho = nn.Parameter(torch.full((n_out,), -6.0))
        self.prior = prior

    def forward(self, x):
        w = self.w_mu + F.softplus(self.w_rho) * torch.randn_like(self.w_mu)
        b = self.b_mu + F.softplus(self.b_rho) * torch.randn_like(self.b_mu)
        return F.linear(x, w, b)

    def kl(self):
        total = 0.0
        for mu, rho in ((self.w_mu, self.w_rho), (self.b_mu, self.b_rho)):
            s = F.softplus(rho)
            total = total + (torch.log(self.prior / s) + (s ** 2 + mu ** 2) / (2 * self.prior ** 2) - 0.5).sum()
        return total


class BNN(nn.Module):
    """Re-implementation of the Mahajan et al. (2024) BNN: 512-512-128 ReLU, softplus scale, NLL + KL."""

    def __init__(self, n_in):
        super().__init__()
        self.layers = nn.ModuleList([BayesLinear(n_in, 512), BayesLinear(512, 512), BayesLinear(512, 128)])
        self.out = BayesLinear(128, 2)

    def forward(self, x):
        for layer in self.layers:
            x = F.relu(layer(x))
        mu, s = self.out(x).unbind(-1)
        return mu, F.softplus(s) + 1e-3

    def kl(self):
        return sum(m.kl() for m in [*self.layers, self.out])


class Scales:
    def __init__(self, mu_e, sd_e, mu_t, sd_t, sd_dt):
        self.mu_e, self.sd_e, self.mu_t, self.sd_t, self.sd_dt = mu_e, sd_e, mu_t, sd_t, sd_dt


def recurrent_loss(model, batch, sc, lam, alpha=1.0):
    x, ye, yt, tnow, drv, w = batch
    pe, pt = model(x)
    loss = F.huber_loss(pe, (ye - sc.mu_e) / sc.sd_e)
    if pt is not None:
        loss = loss + alpha * F.huber_loss(pt, (yt - sc.mu_t) / sc.sd_t)
        if model.physics is not None and lam > 0:
            e_hat = pe * sc.sd_e + sc.mu_e
            t_hat = pt * sc.sd_t + sc.mu_t
            r = ((t_hat - tnow) - model.physics.rhs(tnow, drv, e_hat)) / sc.sd_dt
            phys = (w * F.huber_loss(r, torch.zeros_like(r), reduction="none")).sum() / w.sum().clamp(min=1)
            loss = loss + lam * phys
    return loss


def bnn_loss(model, batch, n_train):
    x, y = batch
    mu, s = model(x)
    return F.gaussian_nll_loss(mu, y, s ** 2) + model.kl() / n_train


def train(model, sample_batch, loss_fn, val_fn, lr=1e-3, wd=1e-4, epochs=40, steps=120, patience=6, seed=0):
    """sample_batch(rng) -> batch; loss_fn(model, batch) -> loss; val_fn(model) -> validation RMSE (kWh)."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    best, best_state, bad, history = np.inf, None, 0, []
    t0 = time.time()
    for ep in range(epochs):
        model.train()
        for _ in range(steps):
            loss = loss_fn(model, sample_batch(rng))
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
    dev = next(model.parameters()).device
    es, ts = [], []
    for i in range(0, len(x), bs):
        e, t = model(x[i:i + bs].to(dev))
        es.append((e * sc.sd_e + sc.mu_e).cpu())
        if t is not None:
            ts.append((t * sc.sd_t + sc.mu_t).cpu())
    return torch.cat(es).numpy(), (torch.cat(ts).numpy() if ts else None)


@torch.no_grad()
def predict_bnn(model, x, mu_y, sd_y, samples=30):
    """Posterior-mean forecast in kWh; the model works on standardised log1p(kWh) as in the paper."""
    dev = next(model.parameters()).device
    x = torch.as_tensor(x, device=dev)
    draws = torch.stack([torch.expm1(model(x)[0] * sd_y + mu_y) for _ in range(samples)])
    return draws.mean(0).clamp(min=0).cpu().numpy()


def demo():
    torch.manual_seed(0)
    phys = RCPhysics()
    n = 64
    tnow = 22 + torch.randn(n)
    drv = torch.stack([15 + 5 * torch.randn(n), torch.rand(n) * 10, torch.rand(n), -torch.rand(n)], 1)
    e = 30 + 5 * torch.rand(n)
    t_next = tnow + phys.rhs(tnow, drv, e)
    assert ((t_next - tnow) - phys.rhs(tnow, drv, e)).abs().max() < 1e-5
    pe, pt = Recurrent(34, dual=True, physics=True)(torch.randn(8, WINDOW, 34))
    assert pe.shape == (8,) and pt.shape == (8,)
    b = BNN(40)
    mu, s = b(torch.randn(8, 40))
    assert mu.shape == (8,) and (s > 0).all() and b.kl() > 0
    print("models demo ok on", pick_device())


if __name__ == "__main__":
    demo()
