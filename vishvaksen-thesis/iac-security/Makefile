.PHONY: help install test train clean lint format all

help:
	@echo "Available targets:"
	@echo "  install    - Install Python dependencies"
	@echo "  test       - Run pytest test suite"
	@echo "  train      - Train and evaluate all detector variants"
	@echo "  clean      - Remove generated files and caches"
	@echo "  lint       - Run code quality checks (flake8, if available)"
	@echo "  format     - Format code with black (if available)"
	@echo "  all        - Install, test, and train"

install:
	pip install -r requirements.txt

test:
	python3 -m pytest tests/ -v --tb=short

train:
	python3 scripts/train_and_evaluate.py

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache
	rm -f src/lambda_handler/model/ml_detector.joblib

lint:
	@command -v flake8 >/dev/null 2>&1 && flake8 src/ tests/ scripts/ || echo "flake8 not installed, skipping lint"

format:
	@command -v black >/dev/null 2>&1 && black src/ tests/ scripts/ || echo "black not installed, skipping format"

all: install test train
