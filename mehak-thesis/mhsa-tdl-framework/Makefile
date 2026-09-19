.PHONY: help install test train evaluate clean lint format all

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies from requirements.txt"
	@echo "  test        - Run pytest tests"
	@echo "  train       - Train and evaluate all models"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code"
	@echo "  clean       - Remove generated files"
	@echo "  all         - Install dependencies, run tests, and train models"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install pytest pytest-cov

# Run tests
test:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Train and evaluate models
train:
	python scripts/train_and_evaluate.py

# Shorthand for train_and_evaluate
evaluate: train

# Lint code
lint:
	@echo "Checking Python code style..."
	@python -m py_compile src/data/telemetry_simulator.py
	@python -m py_compile src/models/mhsa_model.py
	@python -m py_compile src/models/baseline.py
	@python -m py_compile scripts/train_and_evaluate.py
	@echo "All Python files compile successfully!"

# Format code (basic - could add black/isort)
format:
	@echo "Code formatting not configured. Consider adding black or autopep8."

# Clean generated files
clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/data/__pycache__
	rm -rf src/models/__pycache__
	rm -rf src/lambda_handler/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

# Run all steps: install, test, train
all: install test train
	@echo "All steps completed successfully!"
