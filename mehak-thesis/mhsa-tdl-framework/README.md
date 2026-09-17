# MHSA-TDL: Multi-Head Self-Attention-based Telemetry-Driven Deep Learning Framework for Cluster Health Prediction and Failure Detection

This directory contains the simulation codebase for Mehak's MSc Cloud Computing thesis.

## Overview
As cloud clusters grow in scale, traditional threshold-based monitoring systems fail to capture complex, non-linear relationships among telemetry metrics (CPU, Memory, Disk I/O, Network traffic), leading to false positives and delayed failure detection. This project proposes **MHSA-TDL**, a Deep Learning framework utilizing Multi-Head Self-Attention to dynamically weigh the importance of different telemetry metrics over time to predict cluster health and detect impending failures.

The project models data similar to the Google Cluster Trace dataset by generating synthetic multivariate time-series telemetry. 

## Approach
1. **Telemetry Capture:** CloudWatch (simulated here) aggregates node-level metrics (CPU, Mem, Disk, Net). In production, this data streams through Kinesis to a central inference service.
2. **Multi-Head Self-Attention (MHSA):** Extracts temporal and feature-wise correlations from the telemetry stream.
3. **Threshold Baseline:** A traditional monitoring system triggering alerts when metrics exceed fixed limits.

## Project Structure
- `src/data/telemetry_simulator.py`: Generates synthetic cluster telemetry.
- `src/models/mhsa_model.py`: PyTorch implementation of the MHSA-TDL network.
- `src/models/baseline.py`: Traditional threshold monitoring implementation.
- `scripts/train_and_evaluate.py`: Training loop, evaluation against baseline, and metric calculation.
- `results/`: Output directory for generated CSV performance metrics.
- `template.yaml`: AWS SAM template defining Kinesis stream and Lambda inference pipeline.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the simulation:
   ```bash
   python scripts/train_and_evaluate.py
   ```
3. Check `results/results.csv` for comparison metrics.
