"""
Data loading and preprocessing for UNSW-NB15 dataset
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Tuple, List, Dict
import pickle
import os


class UNSWDataLoader:
    """Load and preprocess UNSW-NB15 intrusion detection dataset"""
    
    def __init__(self, data_path: str = "data/UNSW_NB15_training-set.csv"):
        self.data_path = data_path
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Feature columns (exclude label, attack_cat, id)
        self.feature_cols = None
        
    def load_data(self, binary=True, sample_size=None):
        """
        Load and preprocess dataset
        
        Args:
            binary: If True, binary classification (normal vs attack)
                   If False, multi-class (normal + attack types)
            sample_size: Number of samples to load (None = all)
        
        Returns:
            X, y: Features and labels
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(
                f"Dataset not found at {self.data_path}. "
                "Run scripts/download_data.py first."
            )
        
        df = pd.read_csv(self.data_path)
        
        if sample_size:
            df = df.sample(n=min(sample_size, len(df)), random_state=42)
        
        # Remove non-feature columns
        label_col = 'label' if 'label' in df.columns else 'Label'
        attack_col = 'attack_cat' if 'attack_cat' in df.columns else 'attack_cat'
        
        # Handle missing values
        df = df.fillna(0)
        
        # Extract features and labels
        exclude_cols = [label_col]
        if attack_col in df.columns:
            exclude_cols.append(attack_col)
        if 'id' in df.columns:
            exclude_cols.append('id')
        
        # Select only numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        X = df[feature_cols].values
        
        if binary:
            # Binary: 0=normal, 1=attack
            y = df[label_col].values
        else:
            # Multi-class: encode attack types
            if attack_col in df.columns:
                y = self.label_encoder.fit_transform(df[attack_col].values)
            else:
                y = df[label_col].values
        
        self.feature_cols = feature_cols
        return X, y
    
    def normalize(self, X_train, X_test=None):
        """Normalize features using StandardScaler"""
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def create_non_iid_split(self, X, y, num_clients: int, 
                            alpha: float = 0.5) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Create non-IID data splits for federated clients
        
        Args:
            X, y: Dataset
            num_clients: Number of clients
            alpha: Dirichlet concentration parameter (lower = more non-IID)
        
        Returns:
            List of (X_client, y_client) tuples
        """
        num_classes = len(np.unique(y))
        num_samples = len(y)
        
        # Dirichlet non-IID split with a hard floor so no client is empty
        # (empty clients break DataLoader / RandomSampler).
        if num_samples < num_clients:
            raise ValueError(
                f"Need at least {num_clients} samples for {num_clients} clients; "
                f"got {num_samples}"
            )

        client_sample_nums = np.random.dirichlet([alpha] * num_clients, 1)[0]
        client_sample_nums = (client_sample_nums * num_samples).astype(int)
        # Guarantee ≥1 sample per client, then redistribute remainder
        client_sample_nums = np.maximum(client_sample_nums, 1)
        while client_sample_nums.sum() > num_samples:
            # Trim from the largest client that still has >1
            donors = np.where(client_sample_nums > 1)[0]
            if len(donors) == 0:
                break
            client_sample_nums[donors[np.argmax(client_sample_nums[donors])]] -= 1
        diff = num_samples - int(client_sample_nums.sum())
        if diff > 0:
            client_sample_nums[np.argmax(client_sample_nums)] += diff

        indices = list(range(num_samples))
        np.random.shuffle(indices)

        client_data = []
        start_idx = 0
        for i in range(num_clients):
            end_idx = start_idx + int(client_sample_nums[i])
            client_indices = indices[start_idx:end_idx]
            client_data.append((X[client_indices], y[client_indices]))
            start_idx = end_idx

        return client_data
    
    def get_test_set(self, test_size=0.2, random_state=42):
        """Load full dataset and create test set"""
        X, y = self.load_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        return X_train, X_test, y_train, y_test


def create_federated_data(num_clients: int = 5, 
                         data_path: str = "data/UNSW_NB15_training-set.csv",
                         alpha: float = 0.5,
                         binary: bool = True,
                         sample_size: int = None) -> Dict:
    """
    Create federated data splits
    
    Returns:
        dict with keys: 'train_clients', 'test_set', 'scaler'
    """
    loader = UNSWDataLoader(data_path)
    # When sample_size is set, subsample the full CSV first so train/test
    # both come from the same capped pool (avoids 175k test + tiny clients).
    X, y = loader.load_data(binary=binary, sample_size=sample_size)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Normalize
    X_train, X_test = loader.normalize(X_train, X_test)

    # Create non-IID splits
    client_data = loader.create_non_iid_split(X_train, y_train, num_clients, alpha)

    return {
        'train_clients': client_data,
        'test_set': (X_test, y_test),
        'scaler': loader.scaler,
        'num_features': X_train.shape[1]
    }
