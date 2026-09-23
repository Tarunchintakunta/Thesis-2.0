.PHONY: help install pilot test experiment centralised unsw-real stats figures clean live-cloud-fl

help:
	@echo "SecureFL-IDS Makefile"
	@echo "====================="
	@echo "make install      - Create venv and install dependencies"
	@echo "make pilot        - Run quick pilot experiment (synthetic sample)"
	@echo "make test         - Run all tests"
	@echo "make centralised  - centralised IDS comparator (synthetic PoC data)"
	@echo "make experiment   - Federated baseline + improved (synthetic)"
	@echo "make unsw-real    - Real UNSW training-partition sample (central+FL)"
	@echo "make stats        - Generate statistical analysis"
	@echo "make figures      - Create evaluation figures"
	@echo "make clean        - Remove generated files and cache"
	@echo "make live-cloud-fl - Free-Tier EC2+S3+CW lite FL, then destroy"

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Virtual environment ready. Activate with: source .venv/bin/activate"

pilot: install
	@echo "Running pilot experiment..."
	.venv/bin/python scripts/download_data.py --synthetic --sample
	.venv/bin/python scripts/run_pilot.py
	@echo "Pilot complete. Results in results/pilot/"

test:
	@echo "Running tests..."
	.venv/bin/pytest tests/ -v --cov=src --cov-report=term-missing

centralised: install
	@echo "Running centralised IDS comparator on synthetic PoC data..."
	.venv/bin/python scripts/download_data.py --synthetic
	.venv/bin/python scripts/run_centralised.py
	.venv/bin/python scripts/merge_centralised_comparison.py
	@echo "Centralised results in results/centralised/ (merged into comparison/)"

experiment: install
	@echo "Running federated experiment (baseline + improved)..."
	.venv/bin/python scripts/download_data.py --synthetic
	.venv/bin/python scripts/run_baseline.py
	.venv/bin/python scripts/run_improved.py
	@echo "Experiments complete. Results in results/"

unsw-real: install
	@echo "Downloading real UNSW-NB15 training partition and running sample campaign..."
	.venv/bin/python scripts/download_data.py --real --force
	.venv/bin/python scripts/run_unsw_real.py
	@echo "Real-UNSW results in results/unsw_real/ (synthetic PoC JSON unchanged)"

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

live-cloud-fl:
	@chmod +x scripts/run_live_cloud_fl.sh scripts/bootstrap_cloud.sh
	@bash scripts/run_live_cloud_fl.sh

