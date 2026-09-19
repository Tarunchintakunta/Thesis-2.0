.PHONY: help install test run clean all

# Default target
help:
	@echo "Stability-Aware PAKS Framework - Build Automation"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install dependencies from requirements.txt"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make run        - Execute train_and_evaluate.py to reproduce results"
	@echo "  make clean      - Remove generated files and caches"
	@echo "  make all        - Run install, test, and run in sequence"
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

# Run experiments
run:
	@echo "Running train_and_evaluate.py..."
	python scripts/train_and_evaluate.py
	@echo "✓ Results generated in results/"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf src/__pycache__ src/data/__pycache__ src/models/__pycache__ src/lambda_handler/__pycache__
	rm -rf tests/__pycache__
	rm -rf results/*.csv
	rm -rf src/lambda_handler/model/*.joblib
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✓ Cleanup complete"

# Run full pipeline
all: install test run
	@echo "✓ Full pipeline complete"
