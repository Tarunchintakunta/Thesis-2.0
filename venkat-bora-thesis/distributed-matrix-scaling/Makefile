.PHONY: help install test benchmark clean lint format aws-verify

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
SRC_DIR := src
TEST_DIR := tests
RESULTS_DIR := results

help:
	@echo "Venkat Bora - Matrix Scaling Workloads Project"
	@echo ""
	@echo "Available targets:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run test suite"
	@echo "  make benchmark    - Run full benchmark suite (takes time!)"
	@echo "  make quick-test   - Run quick benchmark (smaller matrices)"
	@echo "  make visualize    - Generate plots from existing results"
	@echo "  make clean        - Remove generated files"
	@echo "  make lint         - Check code quality"
	@echo "  make all          - Install, test, and run benchmarks"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully"

test:
	$(PYTEST) $(TEST_DIR) -v --timeout=60
	@echo "All tests passed"

benchmark:
	@echo "Running full benchmark suite (this will take several minutes)..."
	$(PYTHON) $(SRC_DIR)/main.py --full
	@echo "Benchmark complete. Results saved to $(RESULTS_DIR)/"

quick-test:
	@echo "Running quick benchmark with smaller matrices..."
	$(PYTHON) $(SRC_DIR)/main.py --quick
	@echo "Quick test complete"

visualize:
	$(PYTHON) $(SRC_DIR)/visualize_results.py
	@echo "Visualizations generated in $(RESULTS_DIR)/figures/"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned up temporary files"

lint:
	@echo "Checking code quality..."
	@$(PYTHON) -m py_compile $(SRC_DIR)/*.py
	@echo "Code quality check passed"

all: install test benchmark visualize

aws-verify:
	@bash ../../scripts/aws-verify/venkat-matrix.sh

.DEFAULT_GOAL := help
