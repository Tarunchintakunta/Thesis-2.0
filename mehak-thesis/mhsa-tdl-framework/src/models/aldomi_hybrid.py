"""Aldomi-style hybrid scaffold: GRU + learned feature gate.

Formal CA2 names Aldomi et al. (2026) GRU+feature-selection hybrid as a
baseline family. This is a same-split scaffold on GCT windows, not a
line-by-line reproduction of that paper's architecture or hyperparameters.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class AldomiStyleHybrid(nn.Module):
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
        # Learned per-channel gate (feature selection analogue).
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
