import torch
import torch.nn as nn

NUM_METRICS = 4  # CPU, Mem, Disk, Net
NUM_LEVELS = 3   # None, L1, L2


class SharedBackbone(nn.Module):
    """Shared temporal encoder: linear embedding + positional encoding +
    one self-attention block + FFN. Equivalent to the "Transformer encoder
    backbone" in Fig. 5 of Thapliyal (2026)."""

    def __init__(self, input_dim, seq_length, embed_dim, num_heads, ff_dim, dropout):
        super().__init__()
        self.input_projection = nn.Linear(input_dim, embed_dim)
        self.pos_embedding = nn.Parameter(torch.randn(1, seq_length, embed_dim) * 0.02)
        self.attention = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(embed_dim)
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, embed_dim),
        )
        self.norm2 = nn.LayerNorm(embed_dim)

    def forward(self, x):
        x = self.input_projection(x) + self.pos_embedding
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + attn_out)
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x  # (batch, seq, embed_dim)


class PerMetricHeads(nn.Module):
    """Manual multi-head attention that keeps each head's context vector
    separate instead of merging them with an output projection. Head i is
    dedicated to metric i (CPU/Mem/Disk/Net) -- the "strict 1-to-1
    head-to-rule mapping" the baseline paper uses. Query is the last
    timestep (the prediction point); key/value are the full window."""

    def __init__(self, embed_dim, num_heads):
        super().__init__()
        assert embed_dim % num_heads == 0
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        batch, seq, embed_dim = x.shape
        q = self.q_proj(x[:, -1:, :])
        k = self.k_proj(x)
        v = self.v_proj(x)

        q = q.view(batch, 1, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch, seq, self.num_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch, seq, self.num_heads, self.head_dim).transpose(1, 2)

        scores = (q @ k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        weights = torch.softmax(scores, dim=-1)
        context = (weights @ v).squeeze(2)  # (batch, num_heads, head_dim)
        return context


class CrossHeadFusion(nn.Module):
    """Lets the per-metric head vectors attend to each other before
    classification, so e.g. the CPU head can pick up on what the Net/Disk
    heads are seeing in the same window. This is the fix for the baseline
    paper's reported gap: systematic underprediction on the volatile head
    during high-load transients, caused by heads never exchanging
    information."""

    def __init__(self, head_dim, dropout):
        super().__init__()
        self.attn = nn.MultiheadAttention(head_dim, num_heads=1, dropout=dropout, batch_first=True)
        self.norm = nn.LayerNorm(head_dim)

    def forward(self, context):  # (batch, num_heads, head_dim)
        fused, _ = self.attn(context, context, context)
        return self.norm(context + fused)


class MetricClassifier(nn.Module):
    def __init__(self, head_dim, hidden_dim=16, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(head_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, NUM_LEVELS),
        )

    def forward(self, x):
        return self.net(x)


class MHSAPerHead(nn.Module):
    """Baseline reproduction of Thapliyal (2026): one attention head per
    metric, each head feeding its own independent classifier. No
    cross-metric information sharing after the shared backbone."""

    def __init__(self, input_dim=NUM_METRICS, seq_length=10, embed_dim=32,
                 num_heads=NUM_METRICS, ff_dim=64, dropout=0.1):
        super().__init__()
        self.backbone = SharedBackbone(input_dim, seq_length, embed_dim, num_heads, ff_dim, dropout)
        self.heads = PerMetricHeads(embed_dim, num_heads)
        self.classifiers = nn.ModuleList([
            MetricClassifier(self.heads.head_dim, dropout=dropout) for _ in range(num_heads)
        ])

    def forward(self, x):
        z = self.backbone(x)
        context = self.heads(z)  # (batch, num_heads, head_dim)
        logits = [clf(context[:, i, :]) for i, clf in enumerate(self.classifiers)]
        return torch.stack(logits, dim=1)  # (batch, num_metrics, NUM_LEVELS)


class MHSAFused(nn.Module):
    """Improved model: same backbone and per-metric heads as MHSAPerHead,
    plus a CrossHeadFusion layer that mixes the head vectors before
    classification."""

    def __init__(self, input_dim=NUM_METRICS, seq_length=10, embed_dim=32,
                 num_heads=NUM_METRICS, ff_dim=64, dropout=0.1):
        super().__init__()
        self.backbone = SharedBackbone(input_dim, seq_length, embed_dim, num_heads, ff_dim, dropout)
        self.heads = PerMetricHeads(embed_dim, num_heads)
        self.fusion = CrossHeadFusion(self.heads.head_dim, dropout=dropout)
        self.classifiers = nn.ModuleList([
            MetricClassifier(self.heads.head_dim, dropout=dropout) for _ in range(num_heads)
        ])

    def forward(self, x):
        z = self.backbone(x)
        context = self.heads(z)
        context = self.fusion(context)
        logits = [clf(context[:, i, :]) for i, clf in enumerate(self.classifiers)]
        return torch.stack(logits, dim=1)
