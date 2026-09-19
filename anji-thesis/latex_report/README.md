# LaTeX Report - Compilation Instructions

## Report Details

**Title:** Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures  
**Student:** Anjaneya Reddy Gurram (24288853)  
**Programme:** MSc in Cloud Computing  
**Institution:** National College of Ireland

## Files

- `projectReport.tex` - Main LaTeX document
- `titlepage.tex` - Title page layout
- `refs.bib` - Bibliography with 20+ verified references
- `text/` - Individual chapter files:
  - `abstract.tex` - Abstract (~300 words)
  - `introduction.tex` - Introduction (~8 pages)
  - `relatedwork.tex` - Literature Review (~15 pages)
  - `methodology.tex` - Research Methodology (~8 pages)
  - `design.tex` - Design and Implementation Specifications (~6 pages)
  - `implementation.tex` - Implementation (~4 pages)
  - `evaluation.tex` - Evaluation (~6 pages)
  - `conclusion.tex` - Conclusions and Future Work (~5 pages)
- `figures/` - Placeholder for figures (actual figures in `../sqs-reliability-recovery/results/figures/`)
- `logos/` - NCI logo

## Compilation Instructions

### Using pdflatex (Recommended)

```bash
cd latex_report

# First pass: generate aux files
pdflatex projectReport.tex

# Generate bibliography
bibtex projectReport

# Second pass: resolve citations
pdflatex projectReport.tex

# Third pass: resolve cross-references
pdflatex projectReport.tex
```

The output PDF will be `projectReport.pdf`.

### Using latexmk (Automated)

```bash
cd latex_report
latexmk -pdf projectReport.tex
```

### Using Overleaf

1. Create a new project in Overleaf
2. Upload all files preserving directory structure
3. Set main document to `projectReport.tex`
4. Click "Recompile"

## Dependencies

Required LaTeX packages (usually included in TeX distributions):
- babel
- geometry
- cite / natbib
- graphicx
- adjustbox
- textpos
- tikz
- algorithm / algorithmic
- amsmath, amsfonts, amssymb
- lastpage
- datetime
- hyperref

## Figures

Note: The report references figures from `../sqs-reliability-recovery/results/figures/`. 
To compile successfully, either:
1. Copy figures from `../sqs-reliability-recovery/results/figures/*.png` to `figures/`
2. Adjust the `\graphicspath` in `projectReport.tex` to point to the results directory
3. Or comment out figure references for a text-only preview

## Bibliography Style

The report uses Harvard (dcu) style with natbib. All references are in `refs.bib` with verified DOIs from 2020-2025 research.

## Report Statistics

- Total pages: ~50-55 (estimated)
- Literature review: ~15 pages with 20+ references
- Abstract: ~300 words
- Total word count: ~18,000-20,000 words

## Troubleshooting

**Missing package errors:** Install full TeX distribution (TeX Live, MiKTeX, MacTeX)

**Bibliography not appearing:** Ensure you run bibtex after first pdflatex pass

**Cross-references showing ??:** Run pdflatex multiple times (3 passes recommended)

**Figure not found:** Check `\graphicspath` and ensure figures exist in specified directory

## Contact

For questions about the report content, refer to:
- Main artefact: `../sqs-reliability-recovery/`
- Configuration manual: `../sqs-reliability-recovery/docs/CONFIGURATION_MANUAL.md`
- Status disclosure: `../sqs-reliability-recovery/STATUS.md`
