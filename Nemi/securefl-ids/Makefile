.PHONY: help install pilot test experiment stats figures clean

help:
	@echo "SecureFL-IDS Makefile"
	@echo "====================="
	@echo "make install    - Create venv and install dependencies"
	@echo "make pilot      - Run quick pilot experiment (3 clients, 10 rounds)"
	@echo "make test       - Run all tests"
	@echo "make experiment - Run full experiment (baseline + improved)"
	@echo "make stats      - Generate statistical analysis"
	@echo "make figures    - Create evaluation figures"
	@echo "make clean      - Remove generated files and cache"

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Virtual environment ready. Activate with: source .venv/bin/activate"

pilot: install
	@echo "Running pilot experiment..."
	.venv/bin/python scripts/download_data.py --sample
	.venv/bin/python scripts/run_pilot.py
	@echo "Pilot complete. Results in results/pilot/"

test:
	@echo "Running tests..."
	.venv/bin/pytest tests/ -v --cov=src --cov-report=term-missing

experiment: install
	@echo "Running full experiment (this may take 10-15 minutes)..."
	.venv/bin/python scripts/download_data.py
	.venv/bin/python scripts/run_baseline.py
	.venv/bin/python scripts/run_improved.py
	@echo "Experiments complete. Results in results/"

stats:
	@echo "Generating statistical analysis..."
	.venv/bin/python scripts/analyze_results.py
	@echo "Analysis complete. See results/analysis/"

figures:
	@echo "Creating evaluation figures..."
	.venv/bin/python scripts/plot_results.py
	@echo "Figures saved to figures/"

clean:
	rm -rf .venv
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf results/* figures/*
	find . -type f -name "*.pyc" -delete
	@echo "Cleaned generated files"
