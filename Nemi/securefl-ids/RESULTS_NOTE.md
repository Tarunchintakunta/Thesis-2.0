# Experimental Results Note

## Synthetic PoC (locked FL + centralised comparator)

Authoritative file: `results/comparison/results.json` (synthetic UNSW-derived, 20 features, sample 10k, 30 rounds/epochs).

| Metric | Centralised | Baseline FL | Improved FL |
|--------|-------------|-------------|-------------|
| Accuracy | 0.7975 | 0.793 | 0.800 |
| F1-Score | ≈0.015 | ≈0.019 | 0.0 |
| Avg Comm (MB/round) | 0.0 (N/A) | 1.83 | 3.12 |

Near-zero F1 on synthetic data reflects majority-class collapse on a simplified feature space.

## Real UNSW-NB15 training-partition sample

Authoritative file: `results/unsw_real/results.json`  
Provenance: `results/unsw_real/DATA_PROVENANCE.json` (`kind=real`, ≈175341 rows, 45 cols — official training-set mirror).

Stratified sample: 25k rows, 39 numeric features, 5 clients, 30 rounds/epochs.

| Metric | Centralised | Baseline FL | Improved FL |
|--------|-------------|-------------|-------------|
| Accuracy | **0.9452** | **0.8934** | **0.6800** |
| F1-Score | **0.9603** | **0.9262** | **0.8095** |
| Avg Comm (MB/round) | 0.0 (N/A) | 3.08 | 3.12 |

This is **not** the full 2.5M-flow corpus. Improved FL plateaued — reported honestly; do not invent a win.

## Baseline-paper reference (NOT this artefact)

Saklani et al. (2026) report ~91.8% accuracy on full UNSW-NB15. Literature aspiration only.

## What This Demonstrates

✅ Centralised IDS comparator implemented and measured  
✅ Real UNSW training-partition sample campaign committed  
✅ Synthetic PoC FL metrics still locked and reproducible  
✅ Tests include centralised unit coverage  

❌ Improved arm does not beat baseline FL on the real sample  
❌ No −45% communication win  
❌ No live AWS / Docker / Kubernetes evidence  
❌ Full 2.5M-flow corpus not run (optional depth)

## Reproducing

```bash
make centralised   # synthetic + merge into comparison/
make unsw-real     # real training-partition sample
make test
```
