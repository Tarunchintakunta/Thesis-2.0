#!/usr/bin/env bash
# Setup script for S3 Predictive Cost Optimization Framework
# Student: Varun Gampa (23398639)

set -euo pipefail

echo "=== S3 Predictive Cost Optimization Framework Setup ==="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
    echo "ERROR: Python 3.11+ required, found $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate and install dependencies
echo "Installing dependencies..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements-dev.txt

echo "✓ Dependencies installed"

# Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
fi

# Ensure results directories exist
mkdir -p results/data results/figures

echo ""
echo "=== Setup Complete ==="
echo "Run 'make test' to verify installation"
echo "Run 'make pilot' for a quick experiment"
