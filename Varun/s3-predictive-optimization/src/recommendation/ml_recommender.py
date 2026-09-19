"""
ML-based storage class recommender using XGBoost.
Builds on Yang et al. (2025) ML-driven storage placement methodology.
"""

from typing import Dict, List
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    xgb = None

from src.pricing.s3_pricing import S3Pricing


class MLRecommender:
    """
    ML-based storage class recommender using XGBoost.
    
    Features:
    - Object size, age, access frequency, recency
    - Trained on labeled optimal storage class data
    - Provides probability scores for each class
    """
    
    def __init__(self, config: Dict, pricing: S3Pricing = None):
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not available. Install with: pip install xgboost")
        
        self.config = config.get("ml", {})
        self.pricing = pricing or S3Pricing()
        
        self.features = self.config.get("features", [
            "object_size_mb", "age_days", "access_frequency",
            "access_recency", "days_since_creation"
        ])
        
        self.hyperparams = self.config.get("hyperparameters", {
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "objective": "multi:softmax"
        })
        
        self.model = None
        self.label_encoder = LabelEncoder()
        self.trained = False
    
    def _prepare_features(self, objects: List[Dict]) -> pd.DataFrame:
        """Prepare feature matrix from objects."""
        data = []
        
        for obj in objects:
            features = {
                "object_size_mb": obj.get("size_mb", 0),
                "age_days": obj.get("age_days", 0),
                "access_frequency": obj.get("access_frequency", 0),
                "access_recency": obj.get("last_access_days", obj.get("age_days", 0)),
                "days_since_creation": obj.get("age_days", 0),
                "size_kb": obj.get("size_kb", 0)
            }
            data.append(features)
        
        return pd.DataFrame(data)
    
    def _generate_optimal_labels(self, objects: List[Dict]) -> List[str]:
        """
        Generate optimal storage class labels based on cost analysis.
        This simulates the ground truth for training.
        """
        labels = []
        
        for obj in objects:
            age = obj.get("age_days", 0)
            freq = obj.get("access_frequency", 0)
            size_kb = obj.get("size_kb", 0)
            
            # Calculate cost for each storage class over 1 month
            costs = {}
            for storage_class in ["STANDARD", "STANDARD_IA", "GLACIER_INSTANT", 
                                 "GLACIER_FLEXIBLE", "GLACIER_DEEP_ARCHIVE"]:
                if self.pricing.is_valid_for_class(storage_class, size_kb, age):
                    size_gb = obj.get("size_mb", 0) / 1024
                    costs[storage_class] = self.pricing.get_total_cost(
                        storage_class, size_gb, freq, months=1
                    )
            
            # Select class with minimum cost
            if costs:
                optimal_class = min(costs.items(), key=lambda x: x[1])[0]
            else:
                optimal_class = "STANDARD"
            
            labels.append(optimal_class)
        
        return labels
    
    def train(self, objects: List[Dict]) -> Dict:
        """Train the ML model on object data."""
        # Prepare features
        X = self._prepare_features(objects)
        
        # Generate optimal labels
        y_labels = self._generate_optimal_labels(objects)
        y = self.label_encoder.fit_transform(y_labels)
        
        # Split train/test
        train_fraction = self.config.get("train_fraction", 0.7)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, train_size=train_fraction, random_state=42
        )
        
        # Train XGBoost
        self.model = xgb.XGBClassifier(**self.hyperparams, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = self.model.score(X_train, y_train)
        test_acc = self.model.score(X_test, y_test)
        
        self.trained = True
        
        return {
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "train_size": len(X_train),
            "test_size": len(X_test),
            "num_classes": len(self.label_encoder.classes_),
            "classes": list(self.label_encoder.classes_)
        }
    
    def recommend_storage_class(self, obj: Dict) -> str:
        """Recommend storage class for a single object."""
        if not self.trained:
            raise ValueError("Model not trained. Call train() first.")
        
        X = self._prepare_features([obj])
        pred_encoded = self.model.predict(X)[0]
        return self.label_encoder.inverse_transform([pred_encoded])[0]
    
    def recommend_batch(self, objects: List[Dict]) -> List[Dict]:
        """Recommend storage classes for a batch of objects."""
        if not self.trained:
            raise ValueError("Model not trained. Call train() first.")
        
        X = self._prepare_features(objects)
        pred_encoded = self.model.predict(X)
        pred_proba = self.model.predict_proba(X)
        
        recommended_classes = self.label_encoder.inverse_transform(pred_encoded)
        
        recommendations = []
        for i, obj in enumerate(objects):
            current_class = obj.get("current_storage_class", "STANDARD")
            recommended_class = recommended_classes[i]
            
            # Get confidence scores
            class_probas = {
                cls: float(prob)
                for cls, prob in zip(self.label_encoder.classes_, pred_proba[i])
            }
            
            recommendations.append({
                "object_id": obj["object_id"],
                "key": obj["key"],
                "current_storage_class": current_class,
                "recommended_storage_class": recommended_class,
                "confidence": float(pred_proba[i].max()),
                "class_probabilities": class_probas,
                "reason": f"ML prediction (confidence: {pred_proba[i].max():.2%})"
            })
        
        return recommendations
    
    def get_metadata(self) -> Dict:
        """Return recommender metadata."""
        return {
            "method": "ml_xgboost",
            "reference": "Yang et al. (2025), MLSys 2025",
            "arxiv": "2501.05651",
            "model": "XGBoost",
            "hyperparameters": self.hyperparams,
            "features": self.features,
            "trained": self.trained,
            "num_classes": len(self.label_encoder.classes_) if self.trained else 0
        }
