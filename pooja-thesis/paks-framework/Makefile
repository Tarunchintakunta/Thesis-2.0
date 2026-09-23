.PHONY: help install test run run-formal fetch fetch-extended probe-k8s live-aws destroy-aws clean all

# Default target
help:
	@echo "PAKS Framework - Build Automation"
	@echo ""
	@echo "Available targets:"
	@echo "  make install         - Install dependencies from requirements.txt"
	@echo "  make test            - Run test suite with pytest"
	@echo "  make run-formal      - LSTM + GCT/Alibaba samples + K8s dry-run vs HPA"
	@echo "  make fetch           - Download/verify GCT v1 public slice and re-aggregate"
	@echo "  make fetch-extended  - GCT 2011 part-00000 + Alibaba 64MiB RANGE sample"
	@echo "  make probe-k8s       - Record kind/minikube/docker availability (no apply)"
	@echo "  make live-aws        - Free-Tier t3.micro+k3s live scale vs HPA; destroy after"
	@echo "  make destroy-aws     - terraform destroy paks-k8s-live only + verify"
	@echo "  make run             - PROXY synthetic MLP driver (not formal evidence)"
	@echo "  make clean           - Remove generated files and caches"
	@echo "  make all             - Run install, test, and run-formal in sequence"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Run tests
test:
	@echo "Running test suite..."
	pytest tests/ -v --tb=short
	@echo "✓ All tests passed"

run-formal:
	@echo "Running train_lstm_and_evaluate.py (formal, dry-run)..."
	python scripts/train_lstm_and_evaluate.py --dataset gct
	@echo "✓ Formal results generated in results/"

fetch:
	@echo "Fetching/aggregating public GCT v1 slice..."
	python scripts/fetch_public_trace_slice.py
	@echo "✓ traces updated"

fetch-extended:
	@echo "Fetching GCT 2011 part-00000 + Alibaba RANGE sample..."
	python scripts/fetch_extended_trace_samples.py
	@echo "✓ extended traces updated"

probe-k8s:
	@echo "Probing local kind/minikube/docker (no mutate)..."
	python scripts/probe_local_k8s.py
	@echo "✓ wrote results/K8S_LOCAL_PROBE.md"

# Live AWS: 1× t3.micro k3s + S3 + CloudWatch (project=paks-k8s-live). Destroys after.
live-aws:
	@echo "Deploying Free-Tier-safe live k3s + running PAKS vs HPA..."
	python scripts/run_live_aws_k8s.py --steps 16 --max-replicas 3
	@echo "✓ see results/formal_k8s_live_aws.json and aws_destroy_verify.json"

destroy-aws:
	@echo "Destroying paks-k8s-live only (never Venkat matrix-scale)..."
	python scripts/run_live_aws_k8s.py --destroy-only
	@echo "✓ destroy verify written"

run:
	@echo "PROXY: Running train_and_evaluate.py (synthetic MLP)..."
	python scripts/train_and_evaluate.py
	@echo "✓ Proxy results generated in results/"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf src/__pycache__ src/data/__pycache__ src/models/__pycache__ src/lambda_handler/__pycache__
	rm -rf tests/__pycache__
	rm -f results/results_per_seed.csv results/results_summary.csv
	# keep formal_*.csv / RESULTS_PROVENANCE.md / PROXY_NIMBUSGUARD.md
	rm -rf src/lambda_handler/model/*.joblib
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✓ Cleanup complete"

# Run full pipeline
all: install test run-formal
	@echo "✓ Full formal pipeline complete (still NOT live AWS/K8s)"
