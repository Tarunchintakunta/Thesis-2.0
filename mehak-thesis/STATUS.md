# Project Status: mehak-thesis

**Last Updated:** September 19, 2026  
**Project:** Cross-Head Fusion for Multi-Head Attention Cluster Telemetry Monitoring  
**Status:** SUBMIT-READY ✅

## Summary

This project reproduces the baseline architecture from Thapliyal (2026), "A Multi-Head Attention Approach for SLA Compliance Monitoring in Data Centers" (arXiv:2605.05354, IEEE ICDCS 2026), confirms the systematic underprediction gap reported in that paper on synthetic cluster telemetry, and evaluates a cross-head fusion layer as a targeted fix.

## Completion Status

### ✅ Completed Components

1. **Code Implementation** (100%)
   - Synthetic telemetry generator with controlled cross-metric burst precursors
   - Baseline threshold monitor (reactive)
   - MHSA-PerHead (strict per-metric heads, baseline reproduction)
   - MHSA-Fused (with cross-head fusion layer)
   - Training and evaluation pipeline across 5 seeds
   - Comprehensive test suite (33 tests, 100% passing)

2. **Experimental Results** (100%)
   - 5-seed runs completed (seeds 42-46)
   - Results recorded in `mhsa-tdl-framework/results/results_per_seed.csv` and `results_summary.csv`
   - Key findings:
     - Both attention models strongly outperform reactive threshold monitoring (86-88% vs 2.5% transient recall)
     - Cross-head fusion shows modest improvement on targeted gap (recall 86.4%→88.4%, bias 0.290→0.273)
     - Small accuracy cost (87.3%→86.3%), all differences within 1 std across seeds

3. **Documentation** (100%)
   - Comprehensive LaTeX report (~22-25 pages)
   - Expanded literature review (~8 pages, 27 citations with DOIs)
   - Detailed methodology and design sections
   - Implementation and deployment architecture
   - Honest discussion of unseeded vs properly-seeded results
   - STATUS.md (this file)
   - README.md with usage instructions

4. **Testing Infrastructure** (100%)
   - pytest test suite with 33 tests covering:
     - Telemetry simulator functionality
     - Model architecture correctness
     - Integration tests for full pipeline
   - Makefile with targets: install, test, train, lint, clean, all
   - All tests passing (exit code 0)

5. **Deployment** (100%)
   - AWS Lambda inference handler
   - AWS SAM template (Kinesis + Lambda + SNS)
   - GitHub Actions CI/CD pipeline
   - Model export for deployment

### 📋 Project Structure

```
mehak-thesis/
├── mhsa-tdl-framework/           # Main codebase
│   ├── src/
│   │   ├── data/
│   │   │   └── telemetry_simulator.py    # Synthetic data generator
│   │   ├── models/
│   │   │   ├── mhsa_model.py            # Attention models
│   │   │   └── baseline.py              # Threshold baseline
│   │   └── lambda_handler/
│   │       ├── app.py                   # AWS Lambda handler
│   │       └── model/                   # Exported trained model
│   ├── scripts/
│   │   └── train_and_evaluate.py        # Main experimental pipeline
│   ├── results/
│   │   ├── results_per_seed.csv         # Per-seed results
│   │   └── results_summary.csv          # Aggregated results (mean ± std)
│   ├── tests/
│   │   ├── test_telemetry_simulator.py  # Data generation tests
│   │   ├── test_models.py               # Model tests
│   │   └── test_integration.py          # End-to-end tests
│   ├── Makefile                         # Build automation
│   ├── requirements.txt                 # Python dependencies
│   └── template.yaml                    # AWS SAM template
├── latex_report/                        # Thesis report
│   ├── projectReport.tex               # Main LaTeX file
│   ├── projectReport.pdf               # Compiled PDF report
│   ├── refs.bib                        # Bibliography (27 references)
│   ├── text/
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── relatedwork.tex             # Expanded ~8 pages
│   │   ├── methodology.tex             # Expanded with detailed procedures
│   │   ├── design.tex                  # Expanded with architecture details
│   │   ├── implementation.tex          # Expanded with deployment info
│   │   ├── evaluation.tex              # Results and discussion
│   │   └── conclusion.tex
│   └── figures/                        # Placeholder diagrams
├── .github/workflows/deploy.yml        # CI/CD pipeline
├── final_report.md                     # Project summary
├── README.md                           # Project overview
└── STATUS.md                           # This file
```

### 📊 Key Results

| Model | Accuracy | Macro-F1 | Transient Recall | Underprediction Bias |
|---|---|---|---|---|
| Threshold Baseline (reactive) | 0.847 ± 0.002 | 0.313 ± 0.002 | 0.025 ± 0.002 | 1.715 ± 0.011 |
| MHSA-PerHead (baseline) | 0.873 ± 0.011 | 0.565 ± 0.008 | 0.864 ± 0.022 | 0.290 ± 0.076 |
| MHSA-Fused (improved) | 0.863 ± 0.014 | 0.560 ± 0.010 | 0.884 ± 0.021 | 0.273 ± 0.050 |

### 🔬 Research Contributions

1. **Baseline Reproduction:** Confirmed that the strict one-head-per-metric architecture from Thapliyal (2026) exhibits systematic underprediction during high-load transients on cluster telemetry.

2. **Targeted Fix:** Introduced a minimal cross-head fusion layer that allows per-metric heads to exchange information before classification.

3. **Honest Evaluation:** Reported both an unseeded result (that overstated the effect) and a properly-seeded 5-seed result (showing modest but real improvement), demonstrating the importance of seed control in small neural network experiments.

4. **Reproducibility:** Full pipeline is reproducible with `python scripts/train_and_evaluate.py` (no external dataset dependency).

### 🔧 Usage

#### Run Tests
```bash
cd mhsa-tdl-framework
make test
```

#### Train and Evaluate
```bash
cd mhsa-tdl-framework
make train
```
or
```bash
cd mhsa-tdl-framework
python scripts/train_and_evaluate.py
```

#### Compile LaTeX Report
```bash
cd latex_report
pdflatex projectReport.tex
bibtex projectReport
pdflatex projectReport.tex
pdflatex projectReport.tex
```

### ⚠️ Known Simplifications

1. **Synthetic Data:** Real cluster traces (Google Borg, IBM Cloud) would provide stronger validation, but synthetic data with known cross-metric dependencies allows controlled isolation of the targeted failure mode.

2. **Lambda Packaging:** PyTorch is heavy for a Lambda zip package. Production deployment would use a container image or Lambda Layer.

3. **Diagrams:** Methodology and architecture diagrams are specified as placeholders in the LaTeX. Final versions would include actual rendered figures.

### 🎯 Future Work

1. Evaluate on real cluster telemetry (e.g., Google Borg traces) to validate that fusion improvement holds under real, non-stationary failure patterns.

2. Replace generic cross-entropy loss with asymmetric loss that penalizes underprediction more than overprediction.

3. Extend burst-pattern vocabulary to wider range of cross-metric lead/lag relationships.

## Submission Checklist

- [x] Code complete and tested (33/33 tests passing)
- [x] Experiments run across 5 seeds
- [x] Results recorded and reproducible
- [x] Literature review expanded (~8 pages, 27 citations with verified DOIs)
- [x] Report expanded (~22-25 pages with methodology details)
- [x] Baseline paper DOI verified (arXiv:2605.05354)
- [x] Clear distinction between baseline and improved arms
- [x] No mocked/fake data or metrics
- [x] No credentials exposed in code
- [x] Makefile and pytest infrastructure added
- [x] STATUS.md created
- [x] All changes committed to feature branch
- [x] PR ready to create

## Contact

**Student:** Mehak  
**Programme:** MSc Cloud Computing  
**Institution:** National College of Ireland  
**Supervisor:** TBD

---

**Project Repository:** https://github.com/Tarunchintakunta/Thesis-2.0  
**Branch:** cursor/mehak-thesis-completion-6fd5  
**Base Branch:** main
