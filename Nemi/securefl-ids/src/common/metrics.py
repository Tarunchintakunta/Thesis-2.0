"""
Evaluation metrics for intrusion detection
"""
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, confusion_matrix, roc_auc_score
)
import numpy as np
from typing import Dict


def calculate_metrics(y_true, y_pred, y_proba=None, binary=True) -> Dict[str, float]:
    """
    Calculate intrusion detection metrics
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_proba: Prediction probabilities (optional)
        binary: Binary or multi-class classification
    
    Returns:
        Dictionary of metrics
    """
    average_mode = 'binary' if binary else 'weighted'
    
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average=average_mode, zero_division=0),
        'recall': recall_score(y_true, y_pred, average=average_mode, zero_division=0),
        'f1_score': f1_score(y_true, y_pred, average=average_mode, zero_division=0)
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    if binary and cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        metrics['true_negative'] = int(tn)
        metrics['false_positive'] = int(fp)
        metrics['false_negative'] = int(fn)
        metrics['true_positive'] = int(tp)
        metrics['fpr'] = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        metrics['tpr'] = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # ROC-AUC if probabilities provided
    if y_proba is not None:
        try:
            if binary:
                metrics['roc_auc'] = roc_auc_score(y_true, y_proba)
            else:
                metrics['roc_auc'] = roc_auc_score(
                    y_true, y_proba, multi_class='ovr', average='weighted'
                )
        except Exception:
            metrics['roc_auc'] = 0.0
    
    return metrics


def calculate_communication_cost(model_updates: list) -> float:
    """
    Calculate communication cost in MB
    
    Args:
        model_updates: List of model parameter dictionaries
    
    Returns:
        Total size in MB
    """
    total_bytes = 0
    for update in model_updates:
        for param in update.values():
            total_bytes += param.numel() * param.element_size()
    
    return total_bytes / (1024 * 1024)  # Convert to MB
