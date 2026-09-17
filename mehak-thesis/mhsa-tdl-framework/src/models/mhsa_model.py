import torch
import torch.nn as nn

class MHSAModel(nn.Module):
    def __init__(self, input_dim=4, seq_length=10, embed_dim=32, num_heads=4, ff_dim=64, dropout=0.1):
        super(MHSAModel, self).__init__()

        # Linear embedding
        self.input_projection = nn.Linear(input_dim, embed_dim)

        # Positional Encoding (learned parameter)
        self.pos_embedding = nn.Parameter(torch.randn(1, seq_length, embed_dim))

        # MHSA Layer
        self.attention = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)

        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)

        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, ff_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(ff_dim, embed_dim)
        )

        # Classification head
        self.flatten = nn.Flatten()
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim * seq_length, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        # x is (batch_size, seq_length, input_dim)
        x = self.input_projection(x)
        x = x + self.pos_embedding

        # MHSA setup
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + attn_out)

        # FFN setup
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)

        # Classification output
        x = self.flatten(x)
        out = self.classifier(x)
        return out.squeeze(-1)
