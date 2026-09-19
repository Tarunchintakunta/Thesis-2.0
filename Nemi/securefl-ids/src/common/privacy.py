"""
Differential privacy mechanisms
"""
import torch
import numpy as np
from typing import Dict


class DifferentialPrivacy:
    """
    Differential privacy implementation via gradient clipping + Gaussian noise
    Based on Saklani et al. (2026) and standard DP-SGD
    """
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5, 
                 clip_norm: float = 1.0):
        """
        Args:
            epsilon: Privacy budget (lower = more privacy)
            delta: Privacy parameter (typically 1/n^2)
            clip_norm: Maximum gradient norm (C in DP-SGD)
        """
        self.epsilon = epsilon
        self.delta = delta
        self.clip_norm = clip_norm
        
        # Calculate noise scale using DP-SGD formula
        # σ = (C * sqrt(2 * ln(1.25/δ))) / ε
        self.noise_scale = (clip_norm * np.sqrt(2 * np.log(1.25 / delta))) / epsilon
    
    def clip_gradients(self, model: torch.nn.Module) -> float:
        """
        Clip gradients to bound sensitivity
        Returns: gradient norm before clipping
        """
        total_norm = torch.nn.utils.clip_grad_norm_(
            model.parameters(), 
            self.clip_norm
        )
        return total_norm.item()
    
    def add_noise_to_gradients(self, model: torch.nn.Module):
        """Add calibrated Gaussian noise to gradients"""
        with torch.no_grad():
            for param in model.parameters():
                if param.grad is not None:
                    noise = torch.randn_like(param.grad) * self.noise_scale
                    param.grad += noise
    
    def privatize_model_update(self, model_params: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """
        Apply DP to model parameters directly (alternative to gradient noise)
        Used during federated aggregation
        """
        privatized_params = {}
        
        for name, param in model_params.items():
            # Clip parameter update
            param_norm = torch.norm(param)
            if param_norm > self.clip_norm:
                param = param * (self.clip_norm / param_norm)
            
            # Add noise
            noise = torch.randn_like(param) * self.noise_scale
            privatized_params[name] = param + noise
        
        return privatized_params


class AdaptiveDifferentialPrivacy(DifferentialPrivacy):
    """
    Adaptive DP with client-specific privacy budgets
    Enhanced version for SecureFL-IDS
    """
    def __init__(self, base_epsilon: float = 1.0, delta: float = 1e-5,
                 clip_norm: float = 1.0, adaptive: bool = True):
        super().__init__(base_epsilon, delta, clip_norm)
        self.base_epsilon = base_epsilon
        self.adaptive = adaptive
    
    def get_client_epsilon(self, client_id: int, total_clients: int, 
                          data_quality: float = 1.0) -> float:
        """
        Calculate client-specific epsilon based on data quality
        
        Args:
            client_id: Client identifier
            total_clients: Total number of clients
            data_quality: Quality score [0, 1] (higher = better quality)
        
        Returns:
            Adjusted epsilon for this client
        """
        if not self.adaptive:
            return self.base_epsilon
        
        # Clients with better data can afford lower epsilon (more privacy)
        # Clients with poor data need higher epsilon (less noise) to contribute
        epsilon_factor = 1.0 / (data_quality + 0.1)  # Avoid division by zero
        
        client_epsilon = self.base_epsilon * epsilon_factor
        
        # Bound epsilon to reasonable range [0.5 * base, 2.0 * base]
        client_epsilon = np.clip(client_epsilon, 
                                self.base_epsilon * 0.5, 
                                self.base_epsilon * 2.0)
        
        return client_epsilon
    
    def update_noise_scale(self, epsilon: float):
        """Update noise scale for new epsilon"""
        self.epsilon = epsilon
        self.noise_scale = (self.clip_norm * np.sqrt(2 * np.log(1.25 / self.delta))) / epsilon
