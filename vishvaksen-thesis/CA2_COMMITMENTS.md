# CA2 Commitments (proxy) — Vishvaksen

**Status:** Formal CA2 file **NOT FOUND** in-repo. This document is the **binding research contract** until a real CA2 is added.  
**AWS deploy:** **Not required** for research alignment (local synthetic IaC ablation). Lambda/SAM is packaging only — **do not deploy AWS**.

## Research question
Can a hybrid detector — rule layer + conservatively gated ML — recover precision lost when natural-language context (comments) is unavailable, and at what recall cost?

## Objectives (must evidence)
1. Reproduce War et al. comment-ablation precision collapse on a controlled synthetic benchmark.
2. Design easy (code-alone) vs hard (comment-required) patterns so the ablation is non-trivial.
3. Build hybrid rule+ML detector; report precision/recall/F1 trade-offs and threshold sweep honestly.

## Baseline
War et al. (2025), arXiv:2509.18790 (preprint; peer-review not confirmed). Operational baseline for gap. Cite Rahman/GLITCH as published anchors without replacing War.

## Variables / metrics (eval↔CSV)
| Metric | Artefact |
|--------|----------|
| Precision, Recall, F1 | `iac-security/results/results_summary.csv` |
| Threshold sweep | evaluation table + `results_per_seed.csv` |
| Seeds | 42–46 |

## Non-goals (honest)
- Fine-tuned CodeBERT/LongFormer replication of War’s full stack
- Real Ansible Galaxy / Puppet Forge corpora
- Live AWS Lambda deploy
- Claiming peer-reviewed venue for War until VoR exists
