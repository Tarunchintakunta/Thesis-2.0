.PHONY: install test train clean lint help

help:  ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

test:  ## Run pytest unit tests
	pytest -v --cov=src --cov-report=term-missing tests/

train:  ## Train and evaluate all models (5 seeds)
	python scripts/train_and_evaluate.py

clean:  ## Remove generated files
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.coverage' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '.coverage' -delete

lint:  ## Run code quality checks
	@which pylint > /dev/null 2>&1 || (echo "pylint not installed; skipping lint" && exit 0)
	pylint src/ scripts/ || echo "Linting completed with warnings"

pdf:  ## Compile LaTeX report to PDF
	cd latex_report && pdflatex -interaction=nonstopmode projectReport.tex && bibtex projectReport && pdflatex -interaction=nonstopmode projectReport.tex && pdflatex -interaction=nonstopmode projectReport.tex

all: install test train  ## Install, test, and train
