"""
Integration tests for the full training and evaluation pipeline.
"""
import numpy as np
import torch
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.telemetry_simulator import TelemetrySimulator, TelemetryDataset
from src.models.mhsa_model import MHSAPerHead, MHSAFused
from src.models.baseline import ThresholdBaseline
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader


class TestIntegration:
    """Integration tests for complete pipeline."""

    def test_end_to_end_data_to_prediction(self):
        """Test complete pipeline from data generation to prediction."""
        # Generate data
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        # Create dataset
        dataset = TelemetryDataset(X, y, is_transient)
        
        # Create model
        model = MHSAPerHead(seq_length=10)
        
        # Make predictions
        model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X[:10])
            predictions = model(X_tensor)
        
        # Check predictions shape
        assert predictions.shape == (10, 4, 3)
        
    def test_training_reduces_loss(self):
        """Test that training actually reduces loss."""
        # Generate small dataset
        sim = TelemetrySimulator(num_samples=200, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        # Create dataset and dataloader
        dataset = TelemetryDataset(X, y)
        dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # Create model and optimizer
        torch.manual_seed(42)
        model = MHSAPerHead(seq_length=10)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.CrossEntropyLoss()
        
        # Train for a few epochs
        model.train()
        initial_loss = None
        final_loss = None
        
        for epoch in range(5):
            epoch_loss = 0.0
            for X_batch, y_batch, _ in dataloader:
                optimizer.zero_grad()
                logits = model(X_batch)
                
                # Compute loss per metric
                loss = sum(
                    criterion(logits[:, i, :], y_batch[:, i]) 
                    for i in range(4)
                )
                
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(dataloader)
            if initial_loss is None:
                initial_loss = avg_loss
            final_loss = avg_loss
        
        # Loss should decrease with training
        assert final_loss < initial_loss

    def test_baseline_vs_attention_difference(self):
        """Test that attention models perform differently than threshold baseline."""
        # Generate data
        sim = TelemetrySimulator(num_samples=100, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, is_transient = sim.generate_data()
        
        # Baseline predictions
        baseline = ThresholdBaseline()
        baseline_preds = baseline.predict(X)
        
        # Attention model predictions
        model = MHSAPerHead(seq_length=10)
        model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X)
            logits = model(X_tensor)
            attention_preds = logits.argmax(dim=-1).numpy()
        
        # Predictions should be different (not all the same)
        assert not np.array_equal(baseline_preds, attention_preds)

    def test_reproducibility_with_seed(self):
        """Test that fixing seed produces reproducible results."""
        # Run 1
        torch.manual_seed(42)
        sim1 = TelemetrySimulator(num_samples=50, seq_length=10, transient_ratio=0.4, seed=42)
        X1, y1, _ = sim1.generate_data()
        
        model1 = MHSAPerHead(seq_length=10)
        model1.eval()
        with torch.no_grad():
            pred1 = model1(torch.FloatTensor(X1)).argmax(dim=-1).numpy()
        
        # Run 2 with same seed
        torch.manual_seed(42)
        sim2 = TelemetrySimulator(num_samples=50, seq_length=10, transient_ratio=0.4, seed=42)
        X2, y2, _ = sim2.generate_data()
        
        model2 = MHSAPerHead(seq_length=10)
        model2.eval()
        with torch.no_grad():
            pred2 = model2(torch.FloatTensor(X2)).argmax(dim=-1).numpy()
        
        # Data should be identical
        np.testing.assert_array_equal(X1, X2)
        np.testing.assert_array_equal(y1, y2)
        
        # Predictions should be identical
        np.testing.assert_array_equal(pred1, pred2)

    def test_fusion_has_different_gradients(self):
        """Test that fusion layer actually participates in backprop."""
        # Generate data
        sim = TelemetrySimulator(num_samples=32, seq_length=10, transient_ratio=0.4, seed=42)
        X, y, _ = sim.generate_data()
        
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.LongTensor(y)
        
        # Create fused model
        torch.manual_seed(42)
        model = MHSAFused(seq_length=10)
        
        # Check that fusion layer has parameters
        fusion_params = list(model.fusion.parameters())
        assert len(fusion_params) > 0
        
        # Forward pass
        model.train()
        logits = model(X_tensor)
        
        # Compute loss
        criterion = torch.nn.CrossEntropyLoss()
        loss = sum(criterion(logits[:, i, :], y_tensor[:, i]) for i in range(4))
        
        # Backward pass
        loss.backward()
        
        # Check that fusion layer has gradients
        for param in fusion_params:
            if param.requires_grad:
                assert param.grad is not None
                # Grad should be non-zero (fusion layer should participate)
                assert param.grad.abs().sum() > 0
