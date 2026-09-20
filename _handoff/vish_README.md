# Hybrid IaC Misconfiguration Detection

Vishvaksen's MSc Cloud Computing thesis codebase. Reproduces the central
ablation finding of War, Rawass, Kabore, Samhi, Klein & Bissyandé (2025),
*"Detection of Security Smells in IaC Scripts through Semantics-Aware Code
and Language Processing"* (University of Luxembourg, arXiv:2509.18790),
and builds a fix for the specific weakness it exposes.

**Scope note:** this arXiv paper was the best-verified match for the
topic within a 6-12 month recency window, but I could not confirm it has
been accepted at a peer-reviewed venue (unlike the baselines used for the
other three projects in this thesis series) — it is cited and treated
here as a preprint, not a confirmed peer-reviewed publication.

## The baseline paper's gap
The paper fine-tunes CodeBERT (Ansible) and LongFormer (Puppet) to detect
IaC misconfigurations, using both code and natural-language context
(comments, task descriptions). Its own ablation study removes that
natural-language context and finds precision collapses sharply while
recall holds or rises — e.g. CodeBERT on Ansible: precision 0.92 → 0.46,
F1 0.90 → 0.58. Their own words: *"without sufficient semantic context...
models over-flag and lose precision, undermining practical usability."*
No fix for this is built in the paper.

## What this project does
1. **Reproduces the gap** on a synthetic IaC benchmark deliberately split into "easy" patterns (safe/unsafe distinguishable from code tokens alone, e.g. file mode 0777 vs 0640) and "hard" patterns (the code line is lexically identical either way — a credential *reference* token — and only an explanatory comment reveals whether it resolves to a hardcoded fallback secret or a managed vault lookup). A TF-IDF + logistic regression classifier (`MLDetector`) trained and evaluated with comments scores 1.00/1.00/1.00 (precision/recall/F1); without comments it drops to 0.77/0.71/0.73 — the same qualitative collapse the paper reports.
2. **Builds a fix**: `HybridDetector` combines a comment-independent rule layer (regex signatures for the four enumerable "easy" patterns) with the ML classifier gated at a stricter confidence threshold, rather than a naive OR (which would only add false positives on top of an already-unreliable model).
3. **Reports the fix honestly**: the hybrid detector restores perfect precision (1.00, matching the rich-context ideal) in the code-only setting, but at a real recall cost (0.48 vs. the noisier plain classifier's 0.71) — because the "hard" pattern genuinely cannot be resolved without the missing comment, by construction. No amount of rule/ML combination recovers information that was never in the code to begin with.

## Project Structure
- `src/data/iac_dataset.py` — synthetic IaC snippet generator with paired easy/hard, with/without-comment variants.
- `src/models/detectors.py` — `MLDetector` (baseline), `RULE_PATTERNS` + `rule_based_flag` (comment-independent), `HybridDetector` (improvement).
- `scripts/train_and_evaluate.py` — trains/evaluates all variants over 5 seeds, saves results, exports the deployable ML detector.
- `src/lambda_handler/app.py` — real-time inference over a Kinesis stream of submitted IaC snippets, applying the hybrid detector.
- `template.yaml` — AWS SAM template (Kinesis stream + Lambda).
- `.github/workflows/deploy.yml` (repo root) — CI: trains + deploys the SAM stack on push to `main`.

## Usage
```bash
pip install -r requirements.txt
python scripts/train_and_evaluate.py
```
Results land in `results/results_per_seed.csv` and `results/results_summary.csv`.

## Known scope limitation
The baseline paper fine-tunes CodeBERT/LongFormer (transformer models
requiring GPU + model downloads). This project reproduces the qualitative
phenomenon (precision collapse without comments) with a much lighter
TF-IDF + logistic regression classifier instead, consistent with keeping
this codebase simple and runnable without special hardware. The "hard"
pattern category is also a deliberately small, synthetic stand-in for the
kind of genuinely context-dependent misconfiguration real IaC scripts
contain — see `final_report.md` for the full discussion.
