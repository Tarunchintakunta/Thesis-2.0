# Final Report: Hybrid IaC Misconfiguration Detection

## Abstract
War, Rawass, Kabore, Samhi, Klein & Bissyandé (2025), "Detection of Security Smells in IaC Scripts through Semantics-Aware Code and Language Processing" (University of Luxembourg, arXiv:2509.18790 — **a preprint; peer-review status could not be confirmed**), fine-tune CodeBERT/LongFormer on IaC scripts, beating prior TF-IDF baselines. Their own ablation study shows precision collapsing when natural-language context (comments) is stripped: CodeBERT on Ansible drops from precision 0.92 to 0.46 (F1 0.90→0.58). This project reproduces that collapse on a synthetic benchmark split into "easy" (code-alone-solvable) and "hard" (comment-dependent, lexically identical code either way) misconfiguration patterns, then builds a hybrid rule+ML detector. The hybrid restores perfect precision (1.00) in the code-only setting but at a real recall cost (0.48 vs. the plain classifier's 0.71) — the hard pattern is unsolvable without the missing comment, full stop. A threshold sweep shows this is a tunable trade-off, not a fixed number.

## 1. Introduction
See `latex_report/text/introduction.tex` for the full introduction, research question, and objectives.

## 2. Literature Review Summary
(Refers to `/latex_report/text/relatedwork.tex`.) Baseline: War, A. et al. (2025). *Detection of Security Smells in IaC Scripts through Semantics-Aware Code and Language Processing.* arXiv:2509.18790, University of Luxembourg. **Scope note: cited as a preprint — its acceptance at a peer-reviewed venue could not be confirmed**, unlike the baselines used for the other three projects in this thesis series. CodeBERT/LongFormer for Ansible/Puppet misconfiguration detection; ablation shows severe precision loss without natural-language context.

## 3. Methodology
Synthetic IaC snippet generator (`src/data/iac_dataset.py`): 4 "easy" patterns (enumerable literal values, e.g. file mode 0777 vs 0640) + 2 "hard" patterns (an opaque reference token, identical in code either way — only a comment reveals the true label). Paired with/without-comment renderings from identical underlying random choices. `MLDetector` (TF-IDF + logistic regression, standing in for the paper's fine-tuned transformers given no GPU budget); `RULE_PATTERNS`/`rule_based_flag` (regex, comment-independent, covers only the easy patterns); `HybridDetector` (rule OR ML-above-strict-threshold). 5 seeds (42-46), 70/30 stratified split.

## 4. Experimental Results
| Model | Precision | Recall | F1 |
|---|---|---|---|
| ML Detector (rich context) | 1.000 ± 0.000 | 1.000 ± 0.000 | 1.000 ± 0.000 |
| ML Detector (code-only, baseline gap) | 0.768 ± 0.045 | 0.708 ± 0.064 | 0.733 ± 0.019 |
| Rule-Based Only (reference) | 1.000 ± 0.000 | 0.483 ± 0.028 | 0.651 ± 0.025 |
| Hybrid Detector (improved, code-only) | 1.000 ± 0.000 | 0.483 ± 0.028 | 0.651 ± 0.025 |

Threshold sweep (hybrid detector's ML-fallback confidence cutoff):

| Threshold | Precision | Recall | F1 |
|---|---|---|---|
| 0.5 (= plain ML) | 0.768 | 0.708 | 0.733 |
| 0.6 | 0.928 | 0.528 | 0.672 |
| 0.7 | 0.998 | 0.485 | 0.652 |
| 0.8 | 1.000 | 0.483 | 0.651 |
| 0.9 | 1.000 | 0.483 | 0.651 |

Raw per-seed and summary CSVs: `iac-security/results/results_per_seed.csv`, `results_summary.csv`. Reproduce with `python scripts/train_and_evaluate.py` inside `iac-security/`.

## 5. Conclusion
The hybrid detector fully restores precision without natural-language context, but recall is capped at whatever the comment-independent rule layer alone can catch — the "hard," comment-dependent misconfigurations are unsolvable by construction once the comment is gone, confirming the baseline paper's own framing that semantic context is load-bearing, not a nice-to-have. See `latex_report/text/conclusion.tex` for full discussion and future work (real datasets, a fuller rule engine, routing low-confidence cases to human review).

## Bibliography
See `latex_report/refs.bib` (`War25` entry).
