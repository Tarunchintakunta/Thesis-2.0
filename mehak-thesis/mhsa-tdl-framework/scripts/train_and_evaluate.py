import os
import sys
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# Add parent directory to path to import src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from src.data.telemetry_simulator import TelemetrySimulator, TelemetryDataset
from src.models.mhsa_model import MHSAModel
from src.models.baseline import ThresholdBaseline

def calculate_metrics(y_true, y_pred, y_prob, latency_ms):
    return {
        'Accuracy': round(accuracy_score(y_true, y_pred), 4),
        'Precision': round(precision_score(y_true, y_pred, zero_division=0), 4),
        'Recall': round(recall_score(y_true, y_pred, zero_division=0), 4),
        'F1-Score': round(f1_score(y_true, y_pred, zero_division=0), 4),
        'ROC-AUC': round(roc_auc_score(y_true, y_prob), 4),
        'Latency (ms)': round(latency_ms, 2)
    }

def main():
    print("Initializing Simulation Environment...")
    seq_length = 10
    sim = TelemetrySimulator(num_samples=15000, seq_length=seq_length)
    X, y = sim.generate_data()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    train_dataset = TelemetryDataset(X_train, y_train)
    test_dataset = TelemetryDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    # ----------------------------------------------------
    # Model 1: MHSA-TDL
    # ----------------------------------------------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = MHSAModel(input_dim=4, seq_length=seq_length).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print("Training MHSA-TDL Model...")
    epochs = 15
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")

    print("Evaluating MHSA-TDL Model...")
    model.eval()
    mhsa_preds = []
    mhsa_probs = []

    start_time = time.time()
    with torch.no_grad():
        for X_batch, _ in test_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch)
            mhsa_probs.extend(outputs.cpu().numpy())
            mhsa_preds.extend((outputs.cpu().numpy() > 0.5).astype(int))
    end_time = time.time()

    # In a real environment, you'd calculate latency over single inferences, not a batch,
    # but for benchmark purposes this gives a rough average latency per sample.
    mhsa_latency = (end_time - start_time) * 1000 / len(y_test)
    mhsa_metrics = calculate_metrics(y_test, mhsa_preds, mhsa_probs, mhsa_latency)

    # ----------------------------------------------------
    # Model 2: Traditional Threshold Monitoring
    # ----------------------------------------------------
    print("Evaluating Traditional Threshold Baseline...")
    baseline = ThresholdBaseline(cpu_threshold=0.85, mem_threshold=0.90, disk_threshold=0.90)

    start_time = time.time()
    baseline_preds = baseline.predict(X_test)
    end_time = time.time()

    baseline_latency = (end_time - start_time) * 1000 / len(y_test)
    baseline_metrics = calculate_metrics(y_test, baseline_preds, baseline_preds, baseline_latency)

    # ----------------------------------------------------
    # Save Results
    # ----------------------------------------------------
    results_df = pd.DataFrame([mhsa_metrics, baseline_metrics], index=['MHSA-TDL', 'Threshold Baseline'])
    print("\nEvaluation Results:")
    print(results_df)

    results_dir = os.path.join(parent_dir, 'results')
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, 'results.csv')
    results_df.to_csv(results_path)
    print(f"\nResults saved to {results_path}")

if __name__ == "__main__":
    main()
