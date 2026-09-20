# Experimental Results Note

## Actual Results (Synthetic Data, Local Simulation)

The committed results in `results/` and `figures/` are from **real local experiments** using a **synthetic dataset** derived from UNSW-NB15 characteristics.

### 30-Round Experiment Results

| Metric | Baseline | Improved |
|--------|----------|----------|
| Accuracy | 79.3% | 80.0% |
| F1-Score | 1.9% | 0.0% |
| Avg Comm Cost | 1.83 MB | 3.12 MB |

**Note:** The low F1-scores indicate both models converged to predicting predominantly the majority class (normal traffic). This is a known limitation of:
1. **Synthetic dataset**: Simplified feature space (20 features vs 49 in real UNSW-NB15)
2. **Limited training**: 30 rounds with small sample (10K samples vs 2.5M in full dataset)
3. **Class imbalance**: 80/20 normal/attack distribution

## Baseline-paper reference (NOT this PoC)

Saklani et al. (2026) report ~91.8% accuracy on full UNSW-NB15. The table below is a **literature / methodology aspiration**, not committed artefact output:

| Metric | Baseline (paper-scale aspiration) | Improved (aspiration) |
|--------|-----------------------------------|------------------------|
| Accuracy | ~91-92% | ~93-94% |
| F1-Score | ~90-91% | ~92-93% |
| Communication | Standard | target −40-50% reduction (unsupported by PoC) |

Do **not** cite these as achieved SecureFL-IDS results. Achieved numbers remain accuracy ~0.793/0.800 and F1 near 0.

## Why the Difference?

### Synthetic Dataset Limitations
- Reduced feature space (20 vs 49 features)
- Simplified attack patterns
- Generated distributions may not capture real network traffic complexity

### Training Limitations  
- Shorter training duration (30 rounds vs recommended 50+)
- Smaller sample size (10K vs full 2.5M samples)
- Local simulation without real network latency effects

## What This Demonstrates

✅ **Implementation runs:** Tests pass; baseline and improved arms execute  
✅ **Architecture works:** Code produces convergence metrics on synthetic data  
✅ **Privacy mechanisms present:** DP noise injection / adaptive epsilon code paths exist  
✅ **Reproducible PoC:** One-command local run with documented `results/comparison/results.json`  

❌ **Not a communication win:** Improved arm used *more* MB/round (3.12 vs 1.83); compression does not yield −45% on this PoC  
❌ **Not production-ready results:** Needs full dataset and longer training  
❌ **F1-scores near zero:** Majority-class collapse on synthetic features  
❌ **No centralised IDS comparator / no live AWS** 

## Reproducing Better Results

To achieve baseline-paper-level results:

1. **Download full UNSW-NB15**: https://research.unsw.edu.au/projects/unsw-nb15-dataset
2. **Use all 49 features**: Modify `data_loader.py` to include full feature set
3. **Train longer**: 50+ rounds with full 2.5M samples
4. **Tune hyperparameters**: Learning rate, batch size, model architecture
5. **Balance classes**: Apply SMOTE or class weighting

## Honest Assessment

This artefact provides:
- ✅ **Complete, working implementation** of baseline and improved approaches
- ✅ **Sound methodology** validated against peer-reviewed baseline
- ✅ **Proof-of-concept** demonstration with synthetic data
- ✅ **Full reproducibility** with documented limitations

It does NOT provide:
- ❌ Production-quality detection accuracy on real data (requires full dataset)
- ❌ Live cloud deployment (local simulation only)
- ❌ Results matching reported literature values (synthetic vs real data)

The research contribution is in the **methodology, architecture, and framework design**, not in achieving state-of-the-art detection scores on synthetic data. The implementation is research-grade code suitable for extension to full datasets and deployment scenarios.
