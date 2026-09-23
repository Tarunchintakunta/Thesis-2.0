# Makefile for S3 Predictive Cost Optimization Framework
# Student: Varun Gampa (23398639)
# Default: DRY_RUN=0 (live AWS)

PY ?= .venv/bin/python
PYTEST ?= .venv/bin/pytest
export DRY_RUN ?= 0

.PHONY: help setup test lint pilot baseline improved experiments stats figures gates clean pdf

help:
	@echo "Available targets:"
	@echo "  setup       - Create venv and install dependencies"
	@echo "  test        - Run pytest test suite"
	@echo "  lint        - Run code quality checks"
	@echo "  pilot       - Quick pilot experiment (synthetic data)"
	@echo "  baseline    - Run baseline (rule-based) experiment"
	@echo "  improved    - Run improved (ML+forecast) experiment"
	@echo "  experiments - Run all experiments (pilot, baseline, improved)"
	@echo "  stats       - Generate statistics and hypothesis tests"
	@echo "  figures     - Generate result visualizations"
	@echo "  gates       - Run all quality gates (test, results check)"
	@echo "  pdf         - Compile LaTeX report to PDF"
	@echo "  clean       - Remove generated files and cache"
	@echo ""
	@echo "Environment variables:"
	@echo "  DRY_RUN=1   - Local simulator mode (default, no AWS)"
	@echo "  DRY_RUN=0   - Live AWS mode (requires credentials)"

setup:
	@echo "Setting up environment..."
	@bash scripts/scaffold.sh

test:
	@echo "Running tests..."
	$(PYTEST) tests/ -v --tb=short

lint:
	@echo "Running linter..."
	$(PY) -m ruff check src tests analysis || true
	$(PY) -m pylint src tests analysis --exit-zero || true

pilot:
	@echo "Running pilot experiment (DRY_RUN=$(DRY_RUN))..."
	$(PY) src/runner/experiment.py --config configs/pilot.yaml --output results/data/pilot_results.json

baseline:
	@echo "Running baseline experiment (DRY_RUN=$(DRY_RUN))..."
	$(PY) src/runner/experiment.py --config configs/baseline.yaml --output results/data/baseline_results.json

improved:
	@echo "Running improved framework experiment (DRY_RUN=$(DRY_RUN))..."
	$(PY) src/runner/experiment.py --config configs/improved.yaml --output results/data/improved_results.json

experiments: pilot baseline improved
	@echo "All experiments complete!"

stats:
	@echo "Generating statistics..."
	$(PY) analysis/statistics.py --input results/data/ --output results/statistics.json

figures:
	@echo "Generating figures..."
	$(PY) analysis/plotting.py --input results/data/ --output results/figures/

gates: test
	@echo "Checking quality gates..."
	@test -f results/data/pilot_results.json || (echo "ERROR: Missing pilot results" && exit 1)
	@test -f results/data/baseline_results.json || (echo "ERROR: Missing baseline results" && exit 1)
	@test -f results/data/improved_results.json || (echo "ERROR: Missing improved results" && exit 1)
	@test -f results/figures/cost_comparison.png || (echo "ERROR: Missing cost comparison figure" && exit 1)
	@test -f results/figures/forecast_accuracy.png || (echo "ERROR: Missing forecast accuracy figure" && exit 1)
	@test -f docs/ARCHITECTURE.md || (echo "ERROR: Missing ARCHITECTURE.md" && exit 1)
	@test -f docs/CONFIGURATION_MANUAL.md || (echo "ERROR: Missing CONFIGURATION_MANUAL.md" && exit 1)
	@test -f ../latex_report/projectReport.pdf || (echo "ERROR: Missing projectReport.pdf" && exit 1)
	@echo "✓ All quality gates passed!"

pdf:
	@echo "Compiling LaTeX report..."
	cd ../latex_report && pdflatex projectReport.tex
	@echo "✓ PDF generated at ../latex_report/projectReport.pdf"

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache __pycache__ .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete (results/ preserved)"

