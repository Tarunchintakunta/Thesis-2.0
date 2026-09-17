# Predictive Adaptive Kubernetes Scaling (PAKS)

**Author:** Pooja
**Thesis:** A Machine Learning-Based Framework for Dynamic Workload Prediction in Cloud

## Overview
This repository contains the simulation and architecture components for **PAKS** (Predictive Adaptive Kubernetes Scaling), a framework designed to proactively scale Kubernetes workloads (like AWS EKS) using Machine Learning, replacing the traditional, fully reactive Horizontal Pod Autoscaler (HPA).

By anticipating workload demands before they spike, PAKS significantly reduces Service Level Agreement (SLA) violations and improves overall cluster efficiency compared to standard HPA. 

## Features
- **Workload Simulation:** Generates synthetic, cyclical cloud workload data with random traffic spikes.
- **Classic HPA Mock:** Simulates traditional CloudWatch/Prometheus-based scaling, which scales reactively on a delay.
- **PAKS ML Engine:** Uses a TensorFlow/Keras-based Artificial Neural Network (Feed Forward / LSTM) trained on historical time series data to anticipate the required pod count for the immediate future.
- **Metrics Evaluator:** Compares both approaches calculating Latency gaps, SLA Violations, and Resource Over-provisioning statistics.

## Architecture

1. **Prediction Model (`TensorFlow/Keras`)**: Consumes metric history (e.g. past CPU usage, request counts).
2. **Decision Engine**: Computes target replicasets based on `predicted_load / target_utilization`.
3. **EKS Cluster**: Mimicked locally for simulation, but the SAM template `template.yaml` describes real deployment bindings to AWS CloudWatch and Auto Scaling.

## Getting Started

1. **Install Dependencies**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run the Simulation**:
```bash
python scripts/run_simulation.py
```

The output will be exported to the `results/` folder as a CSV, directly comparing the HPA replicas vs PAKS replicas against the actual workload demand.
