"""Centralised IDS comparator ( traditional baseline).

Trains a single CNN on the pooled training set (no federated split, no DP).
Uses the same model family and data path as the FL arms for a fair local PoC
comparison on detection metrics. Communication cost is not applicable (raw
features stay local to one trainer); reported as 0.0 MB/round."""
import time
from typing import Dict, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from src.common.data_loader import UNSWDataLoader
from src.common.metrics import calculate_metrics
from src.common.models import create_model


class CentralisedIDS:
    """Traditional centralised intrusion detection (non-federated comparator)."""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model: Optional[nn.Module] = None
        self.history = {
            "epochs": [],
            "train_loss": [],
            "test_accuracy": [],
            "test_f1": [],
            "epoch_time": [],
        }
        self.test_X = None
        self.test_y = None
        self.train_X = None
        self.train_y = None
        self.num_features = None

    def setup(
        self,
        data_path: str = "data/UNSW_NB15_training-set.csv",
        sample_size: Optional[int] = None,
        test_size: float = 0.2,
        random_state: int = 42,
    ):
        """Load pooled train/test split (same CSV path as FL arms)."""
        print("Setting up centralised IDS (pooled training, no FL)...")
        loader = UNSWDataLoader(data_path)
        X, y = loader.load_data(binary=True, sample_size=sample_size)
        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        X_train, X_test = loader.normalize(X_train, X_test)

        self.train_X, self.train_y = X_train, y_train
        self.test_X, self.test_y = X_test, y_test
        self.num_features = X_train.shape[1]

        self.model = create_model("cnn", self.num_features, num_classes=2)
        self.model.to(self.device)
        print(
            f"Setup complete. Features: {self.num_features}, "
            f"Train: {len(y_train)}, Test: {len(y_test)}"
        )

    def train(
        self,
        epochs: int = 30,
        learning_rate: float = 0.001,
        batch_size: int = 64,
    ):
        """Train centralised model for a fixed number of epochs."""
        if self.model is None:
            raise RuntimeError("Call setup() before train()")

        print(f"\nTraining centralised IDS for {epochs} epochs...")
        dataset = TensorDataset(
            torch.FloatTensor(self.train_X),
            torch.LongTensor(self.train_y),
        )
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

        for epoch in range(epochs):
            epoch_start = time.time()
            self.model.train()
            running_loss = 0.0
            batches = 0
            for data, target in loader:
                data, target = data.to(self.device), target.to(self.device)
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()
                batches += 1

            avg_loss = running_loss / max(batches, 1)
            test_metrics = self.evaluate(self.test_X, self.test_y)
            epoch_time = time.time() - epoch_start

            self.history["epochs"].append(epoch + 1)
            self.history["train_loss"].append(avg_loss)
            self.history["test_accuracy"].append(test_metrics["accuracy"])
            self.history["test_f1"].append(test_metrics["f1_score"])
            self.history["epoch_time"].append(epoch_time)

            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(
                    f"Epoch {epoch + 1}/{epochs} | "
                    f"Loss: {avg_loss:.4f} | "
                    f"Acc: {test_metrics['accuracy']:.4f} | "
                    f"F1: {test_metrics['f1_score']:.4f} | "
                    f"Time: {epoch_time:.2f}s"
                )

        print("\nCentralised training complete!")
        return self.history

    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """Evaluate centralised model on a hold-out set."""
        self.model.eval()
        X_tensor = torch.FloatTensor(X_test).to(self.device)
        with torch.no_grad():
            outputs = self.model(X_tensor)
            probas = torch.softmax(outputs, dim=1)
            predictions = torch.argmax(outputs, dim=1).cpu().numpy()
            probas_np = probas[:, 1].cpu().numpy()
        return calculate_metrics(y_test, predictions, probas_np, binary=True)

    def get_results_summary(self) -> Dict:
        """Summary aligned with FL arm keys for comparison tables."""
        return {
            "accuracy": self.history["test_accuracy"][-1],
            "f1_score": self.history["test_f1"][-1],
            # Centralised IDS does not exchange model updates across clients.
            "avg_communication_cost": 0.0,
            "total_communication_cost": 0.0,
            "convergence_rounds": len(self.history["epochs"]),
            "avg_round_time": float(np.mean(self.history["epoch_time"])),
            "mode": "centralised",
        }
