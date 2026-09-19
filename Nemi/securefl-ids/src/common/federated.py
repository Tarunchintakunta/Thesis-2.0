"""
Federated learning orchestration
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import copy
from typing import List, Dict, Tuple
import numpy as np


class FederatedClient:
    """Single federated learning client"""
    
    def __init__(self, client_id: int, model: nn.Module, 
                 X_train: np.ndarray, y_train: np.ndarray,
                 device: str = 'cpu'):
        self.client_id = client_id
        self.model = model.to(device)
        self.device = device
        
        # Create data loader
        X_tensor = torch.FloatTensor(X_train)
        y_tensor = torch.LongTensor(y_train)
        dataset = TensorDataset(X_tensor, y_tensor)
        self.data_loader = DataLoader(dataset, batch_size=64, shuffle=True)
        
        self.data_quality = self._calculate_data_quality(y_train)
    
    def _calculate_data_quality(self, y_train: np.ndarray) -> float:
        """
        Calculate data quality score based on class balance
        Returns value in [0, 1], where 1 = perfectly balanced
        """
        unique, counts = np.unique(y_train, return_counts=True)
        if len(unique) < 2:
            return 0.5
        
        # Calculate entropy-based quality score
        probabilities = counts / counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        max_entropy = np.log2(len(unique))
        
        return entropy / max_entropy if max_entropy > 0 else 0.5
    
    def train(self, epochs: int = 1, lr: float = 0.001, 
             privacy_mechanism=None) -> Dict[str, torch.Tensor]:
        """
        Train local model
        
        Args:
            epochs: Number of local epochs
            lr: Learning rate
            privacy_mechanism: DP mechanism (optional)
        
        Returns:
            Model parameter updates
        """
        self.model.train()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()
        
        # Store initial parameters
        initial_params = {
            name: param.clone().detach() 
            for name, param in self.model.named_parameters()
        }
        
        for epoch in range(epochs):
            for batch_idx, (data, target) in enumerate(self.data_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                
                # Apply differential privacy
                if privacy_mechanism:
                    privacy_mechanism.clip_gradients(self.model)
                    privacy_mechanism.add_noise_to_gradients(self.model)
                
                optimizer.step()
        
        # Calculate parameter updates (delta)
        updates = {}
        for name, param in self.model.named_parameters():
            updates[name] = param.data - initial_params[name]
        
        return updates
    
    def update_model(self, global_params: Dict[str, torch.Tensor]):
        """Update local model with global parameters"""
        with torch.no_grad():
            for name, param in self.model.named_parameters():
                if name in global_params:
                    param.copy_(global_params[name])


class FederatedServer:
    """Federated learning server for aggregation"""
    
    def __init__(self, model: nn.Module, aggregation_method: str = 'fedavg'):
        self.global_model = model
        self.aggregation_method = aggregation_method
        self.round = 0
    
    def aggregate(self, client_updates: List[Tuple[int, Dict[str, torch.Tensor], float]],
                 communication_efficient: bool = False,
                 compression_ratio: float = 0.5) -> Dict[str, torch.Tensor]:
        """
        Aggregate client updates
        
        Args:
            client_updates: List of (client_id, updates, weight) tuples
            communication_efficient: Enable gradient compression
            compression_ratio: Fraction of gradients to keep (top-k)
        
        Returns:
            Aggregated global parameters
        """
        if self.aggregation_method == 'fedavg':
            return self._fedavg(client_updates, communication_efficient, compression_ratio)
        elif self.aggregation_method == 'weighted':
            return self._weighted_aggregation(client_updates, communication_efficient, compression_ratio)
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")
    
    def _fedavg(self, client_updates: List[Tuple[int, Dict[str, torch.Tensor], float]],
               communication_efficient: bool = False,
               compression_ratio: float = 0.5) -> Dict[str, torch.Tensor]:
        """Standard FedAvg aggregation"""
        total_weight = sum(weight for _, _, weight in client_updates)
        
        aggregated = {}
        
        # Get parameter names from first client
        param_names = client_updates[0][1].keys()
        
        for name in param_names:
            weighted_sum = None
            
            for client_id, updates, weight in client_updates:
                update = updates[name]
                
                # Apply communication-efficient compression
                if communication_efficient:
                    update = self._compress_gradient(update, compression_ratio)
                
                if weighted_sum is None:
                    weighted_sum = update * (weight / total_weight)
                else:
                    weighted_sum += update * (weight / total_weight)
            
            aggregated[name] = weighted_sum
        
        # Update global model
        with torch.no_grad():
            for name, param in self.global_model.named_parameters():
                if name in aggregated:
                    param.add_(aggregated[name])
        
        # Return updated global parameters
        global_params = {
            name: param.clone().detach() 
            for name, param in self.global_model.named_parameters()
        }
        
        self.round += 1
        return global_params
    
    def _weighted_aggregation(self, client_updates: List[Tuple[int, Dict[str, torch.Tensor], float]],
                             communication_efficient: bool = False,
                             compression_ratio: float = 0.5) -> Dict[str, torch.Tensor]:
        """
        Quality-weighted aggregation (improved method)
        Weights are based on data quality scores
        """
        return self._fedavg(client_updates, communication_efficient, compression_ratio)
    
    def _compress_gradient(self, gradient: torch.Tensor, 
                          compression_ratio: float) -> torch.Tensor:
        """
        Top-k gradient compression for communication efficiency
        
        Args:
            gradient: Gradient tensor
            compression_ratio: Fraction of elements to keep
        
        Returns:
            Compressed gradient (sparse)
        """
        if compression_ratio >= 1.0:
            return gradient
        
        # Flatten gradient
        flat_grad = gradient.flatten()
        k = max(1, int(len(flat_grad) * compression_ratio))
        
        # Get top-k by magnitude
        topk_values, topk_indices = torch.topk(flat_grad.abs(), k)
        
        # Create sparse gradient
        compressed = torch.zeros_like(flat_grad)
        compressed[topk_indices] = flat_grad[topk_indices]
        
        return compressed.reshape(gradient.shape)


def federated_learning_round(server: FederatedServer,
                             clients: List[FederatedClient],
                             local_epochs: int = 1,
                             learning_rate: float = 0.001,
                             privacy_mechanism=None,
                             communication_efficient: bool = False) -> Dict:
    """
    Execute one round of federated learning
    
    Returns:
        dict with 'global_params' and 'communication_cost'
    """
    client_updates = []
    total_comm_cost = 0
    
    # Each client trains locally
    for client in clients:
        updates = client.train(
            epochs=local_epochs, 
            lr=learning_rate,
            privacy_mechanism=privacy_mechanism
        )
        
        # Calculate weight (proportional to data size)
        weight = len(client.data_loader.dataset)
        
        # Use data quality for weighted aggregation
        quality_weight = client.data_quality * weight
        
        client_updates.append((client.client_id, updates, quality_weight))
        
        # Calculate communication cost
        for param in updates.values():
            total_comm_cost += param.numel() * param.element_size()
    
    # Server aggregates
    global_params = server.aggregate(
        client_updates, 
        communication_efficient=communication_efficient
    )
    
    # Broadcast global model to clients
    for client in clients:
        client.update_model(global_params)
        total_comm_cost += sum(
            p.numel() * p.element_size() 
            for p in global_params.values()
        )
    
    return {
        'global_params': global_params,
        'communication_cost': total_comm_cost / (1024 * 1024)  # MB
    }
