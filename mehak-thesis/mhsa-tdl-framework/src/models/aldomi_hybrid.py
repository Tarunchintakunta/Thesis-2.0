"""Aldomi et al. (2026) hybrid: SelectKBest → GRU extractor → RF/KNN/SVM.

Paper (Systems and Soft Computing 8:200442): SelectKBest feature pre-selection,
GRU as a sequence-level feature extractor, then RF/KNN/SVM on GRU hidden states.
Best reported configuration is GRU-RF.

This is a same-split, same-label implementation on the GCT windows in this
artefact — not a line-by-line clone of the paper's 2019 Borg preprocessing
or hyperparameters. Feature set: expanded 2011 usage columns + history-only
scheduling counts (see gct_loader.EXPANDED_FEATURE_NAMES). The 2011 schema
has no network-byte field.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC


class AldomiStyleHybrid(nn.Module):
    """Retained lightweight GRU+gate scaffold (unit-test / ablation).

    The CA2 comparison path uses ``run_aldomi_hybrid`` (SelectKBest+GRU+RF).
    """

    def __init__(
        self,
        input_dim: int = 4,
        seq_length: int = 10,
        hidden: int = 48,
        dropout: float = 0.1,
        num_metrics: int = 4,
        num_classes: int = 3,
    ):
        super().__init__()
        self.seq_length = seq_length
        self.feature_logit = nn.Parameter(torch.zeros(input_dim))
        self.gru = nn.GRU(input_dim, hidden, num_layers=1, batch_first=True)
        self.drop = nn.Dropout(dropout)
        self.classifiers = nn.ModuleList(
            [nn.Linear(hidden, num_classes) for _ in range(num_metrics)]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = torch.sigmoid(self.feature_logit)
        z = x * gate
        _, h = self.gru(z)
        h = self.drop(h[-1])
        logits = [clf(h) for clf in self.classifiers]
        return torch.stack(logits, dim=1)


class _GRUExtractor(nn.Module):
    def __init__(self, input_dim: int, hidden: int = 48, n_classes: int = 3):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden, num_layers=1, batch_first=True)
        self.head = nn.Linear(hidden, n_classes)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        out, h = self.gru(x)
        emb = h[-1]
        return self.head(emb), emb


def _select_channels(
    X_train: np.ndarray,
    y_train: np.ndarray,
    k: int,
) -> np.ndarray:
    """SelectKBest on mean-pooled channels vs max-label (healthy/L1/L2)."""
    pooled = X_train.mean(axis=1)
    target = y_train.max(axis=1)
    n_feat = pooled.shape[1]
    k_use = max(1, min(k, n_feat))
    # Drop near-constant columns so f_classif does not warn/NaN.
    var = pooled.var(axis=0)
    keep = var > 1e-12
    if keep.sum() == 0:
        return np.arange(n_feat)
    selector = SelectKBest(f_classif, k=min(k_use, int(keep.sum())))
    masked = pooled[:, keep]
    try:
        selector.fit(masked, target)
        support_masked = selector.get_support()
    except ValueError:
        support_masked = np.ones(masked.shape[1], dtype=bool)
    idx = np.where(keep)[0][support_masked]
    if len(idx) == 0:
        idx = np.arange(min(k_use, n_feat))
    return np.sort(idx)


def _train_gru_extractor(
    X_sel: np.ndarray,
    y_max: np.ndarray,
    *,
    seed: int,
    epochs: int,
    hidden: int,
    device: torch.device,
) -> _GRUExtractor:
    torch.manual_seed(seed)
    model = _GRUExtractor(X_sel.shape[-1], hidden=hidden, n_classes=3).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    counts = np.bincount(y_max, minlength=3).astype(np.float32)
    counts[counts == 0] = 1.0
    w = torch.tensor(counts.sum() / (3.0 * counts), dtype=torch.float32, device=device)
    crit = nn.CrossEntropyLoss(weight=w)
    ds = torch.utils.data.TensorDataset(
        torch.from_numpy(X_sel),
        torch.from_numpy(y_max.astype(np.int64)),
    )
    loader = torch.utils.data.DataLoader(ds, batch_size=64, shuffle=True)
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            logits, _ = model(xb)
            loss = crit(logits, yb)
            loss.backward()
            opt.step()
    model.eval()
    return model


@torch.no_grad()
def _embed(model: _GRUExtractor, X_sel: np.ndarray, device: torch.device) -> np.ndarray:
    xt = torch.from_numpy(X_sel).to(device)
    _, emb = model(xt)
    return emb.cpu().numpy()


def run_aldomi_hybrid(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    *,
    k: int = 14,
    seed: int = 0,
    epochs: int = 12,
    hidden: int = 48,
    heads: Optional[List[str]] = None,
) -> Dict[str, Tuple[np.ndarray, np.ndarray, float, dict]]:
    """Fit SelectKBest + GRU extractor + ML heads.

    Returns name -> (preds, scores[N,M,3], latency_ms, info).
    Primary CA2 row is ``Aldomi GRU-RF``.
    """
    heads = heads or ["Aldomi GRU-RF", "Aldomi GRU-KNN"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    idx = _select_channels(X_train, y_train, k=k)
    Xtr = X_train[:, :, idx].astype(np.float32)
    Xte = X_test[:, :, idx].astype(np.float32)
    y_max = y_train.max(axis=1)
    gru = _train_gru_extractor(Xtr, y_max, seed=seed, epochs=epochs, hidden=hidden, device=device)
    emb_tr = _embed(gru, Xtr, device)
    t0 = time.time()
    emb_te = _embed(gru, Xte, device)
    embed_ms = (time.time() - t0) * 1000 / max(len(X_test), 1)

    scaler = StandardScaler()
    emb_tr_s = scaler.fit_transform(emb_tr)
    emb_te_s = scaler.transform(emb_te)

    factories = {
        "Aldomi GRU-RF": lambda: RandomForestClassifier(
            n_estimators=80, max_depth=12, random_state=seed, n_jobs=-1
        ),
        "Aldomi GRU-KNN": lambda: KNeighborsClassifier(n_neighbors=15),
        "Aldomi GRU-SVM": lambda: LinearSVC(max_iter=2000, dual=False),
    }
    info = {
        "selected_channel_indices": idx.tolist(),
        "k_requested": k,
        "k_used": int(len(idx)),
        "gru_hidden": hidden,
        "paper": "Aldomi et al. 2026 SelectKBest+GRU+ML (GRU-RF best in paper)",
        "clone": False,
        "net_channel_is_network_bytes": False,
    }
    n_metrics = y_train.shape[1]
    out: Dict[str, Tuple[np.ndarray, np.ndarray, float, dict]] = {}
    for name in heads:
        factory = factories[name]
        preds = np.zeros((X_test.shape[0], n_metrics), dtype=np.int64)
        scores = np.zeros((X_test.shape[0], n_metrics, 3), dtype=np.float64)
        t1 = time.time()
        for m in range(n_metrics):
            clf = factory()
            clf.fit(emb_tr_s, y_train[:, m])
            preds[:, m] = clf.predict(emb_te_s)
            if hasattr(clf, "predict_proba"):
                proba = clf.predict_proba(emb_te_s)
                full = np.zeros((X_test.shape[0], 3), dtype=np.float64)
                for i, c in enumerate(clf.classes_):
                    full[:, int(c)] = proba[:, i]
                scores[:, m, :] = full
            elif hasattr(clf, "decision_function"):
                dec = clf.decision_function(emb_te_s)
                full = np.zeros((X_test.shape[0], 3), dtype=np.float64)
                if dec.ndim == 1:
                    full[:, 1] = dec
                else:
                    for i, c in enumerate(clf.classes_):
                        full[:, int(c)] = dec[:, i]
                scores[:, m, :] = full
            else:
                scores[np.arange(X_test.shape[0]), m, preds[:, m]] = 1.0
        head_ms = (time.time() - t1) * 1000 / max(len(X_test), 1)
        out[name] = (preds, scores, float(embed_ms + head_ms), dict(info))
    return out
