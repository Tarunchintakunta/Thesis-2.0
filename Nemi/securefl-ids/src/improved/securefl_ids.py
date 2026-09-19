"""
Improved: SecureFL-IDS with Adaptive DP and Communication Efficiency
Enhanced version with:
1. Adaptive differential privacy (client-specific epsilon)
2. Communication-efficient aggregation (gradient compression)
3. CNN-LSTM hybrid model
4. Quality-weighted aggregation
"""
import torch
import numpy as np
from typing import Dict, List
import time

from src.common.models import create_model
from src.common.federated import FederatedClient, FederatedServer, federated_learning_round
from src.common.privacy import AdaptiveDifferentialPrivacy
from src.common.metrics import calculate_metrics
from src.common.data_loader import create_federated_data


class SecureFLIDS:
    """
    Improved Federated Learning IDS with:
    - Adaptive differential privacy
    - Communication-efficient aggregation
    - Enhanced CNN-LSTM model
    """
    
    def __init__(self, 
                 num_clients: int = 5,
                 base_epsilon: float = 1.0,
                 delta: float = 1e-5,
                 clip_norm: float = 1.0,
                 communication_efficient: bool = True,
                 compression_ratio: float = 0.5,
                 device: str = 'cpu'):
        
        self.num_clients = num_clients
        self.device = device
        self.communication_efficient = communication_efficient
        self.compression_ratio = compression_ratio
        
        # Adaptive privacy
        self.privacy = AdaptiveDifferentialPrivacy(
            base_epsilon=base_epsilon,
            delta=delta,
            clip_norm=clip_norm,
            adaptive=True
        )
        
        self.clients = []
        self.server = None
        self.global_model = None
        
        # Metrics tracking
        self.history = {
            'rounds': [],
            'train_accuracy': [],
            'test_accuracy': [],
            'test_f1': [],
            'communication_cost': [],
            'round_time': []
        }
    
    def setup(self, data_path: str = "data/UNSW_NB15_training-set.csv",
             sample_size: int = None):
        """Initialize federated setup with data"""
        print(f"Setting up SecureFL-IDS with {self.num_clients} clients...")
        
        # Load and distribute data
        fed_data = create_federated_data(
            num_clients=self.num_clients,
            data_path=data_path,
            alpha=0.5,
            binary=True,
            sample_size=sample_size
        )
        
        self.test_X, self.test_y = fed_data['test_set']
        num_features = fed_data['num_features']
        
        # Create global model (CNN-LSTM hybrid)
        self.global_model = create_model('cnn_lstm', num_features, num_classes=2)
        self.global_model.to(self.device)
        
        # Create server with weighted aggregation
        self.server = FederatedServer(self.global_model, aggregation_method='weighted')
        
        # Create clients
        self.clients = []
        for client_id, (X_train, y_train) in enumerate(fed_data['train_clients']):
            model_copy = create_model('cnn_lstm', num_features, num_classes=2)
            model_copy.load_state_dict(self.global_model.state_dict())
            
            client = FederatedClient(
                client_id=client_id,
                model=model_copy,
                X_train=X_train,
                y_train=y_train,
                device=self.device
            )
            self.clients.append(client)
        
        print(f"Setup complete. Features: {num_features}, Test samples: {len(self.test_y)}")
        print(f"Communication efficient: {self.communication_efficient} "
              f"(compression: {self.compression_ratio})")
    
    def train(self, num_rounds: int = 50, local_epochs: int = 1, 
             learning_rate: float = 0.001):
        """
        Train federated model with adaptive privacy
        
        Args:
            num_rounds: Number of federated rounds
            local_epochs: Local epochs per client per round
            learning_rate: Learning rate
        """
        print(f"\nTraining SecureFL-IDS for {num_rounds} rounds...")
        
        for round_idx in range(num_rounds):
            round_start = time.time()
            
            # Adapt privacy budget per client based on data quality
            for client in self.clients:
                client_epsilon = self.privacy.get_client_epsilon(
                    client_id=client.client_id,
                    total_clients=self.num_clients,
                    data_quality=client.data_quality
                )
                # Update privacy mechanism for this client
                adapted_privacy = AdaptiveDifferentialPrivacy(
                    base_epsilon=client_epsilon,
                    delta=self.privacy.delta,
                    clip_norm=self.privacy.clip_norm,
                    adaptive=False
                )
                client.privacy = adapted_privacy
            
            # Federated learning round with communication efficiency
            round_result = federated_learning_round(
                server=self.server,
                clients=self.clients,
                local_epochs=local_epochs,
                learning_rate=learning_rate,
                privacy_mechanism=self.privacy,
                communication_efficient=self.communication_efficient
            )
            
            round_time = time.time() - round_start
            
            # Evaluate on test set
            test_metrics = self.evaluate(self.test_X, self.test_y)
            
            # Record metrics
            self.history['rounds'].append(round_idx + 1)
            self.history['test_accuracy'].append(test_metrics['accuracy'])
            self.history['test_f1'].append(test_metrics['f1_score'])
            self.history['communication_cost'].append(round_result['communication_cost'])
            self.history['round_time'].append(round_time)
            
            if (round_idx + 1) % 10 == 0 or round_idx == 0:
                print(f"Round {round_idx + 1}/{num_rounds} | "
                      f"Acc: {test_metrics['accuracy']:.4f} | "
                      f"F1: {test_metrics['f1_score']:.4f} | "
                      f"Comm: {round_result['communication_cost']:.2f} MB | "
                      f"Time: {round_time:.2f}s")
        
        print("\nTraining complete!")
        return self.history
    
    def evaluate(self, X_test, y_test) -> Dict[str, float]:
        """Evaluate global model"""
        self.global_model.eval()
        
        X_tensor = torch.FloatTensor(X_test).to(self.device)
        y_tensor = torch.LongTensor(y_test)
        
        with torch.no_grad():
            outputs = self.global_model(X_tensor)
            probas = torch.softmax(outputs, dim=1)
            predictions = torch.argmax(outputs, dim=1).cpu().numpy()
            probas_np = probas[:, 1].cpu().numpy()
        
        metrics = calculate_metrics(y_test, predictions, probas_np, binary=True)
        return metrics
    
    def get_results_summary(self) -> Dict:
        """Get summary of results for comparison"""
        final_metrics = {
            'accuracy': self.history['test_accuracy'][-1],
            'f1_score': self.history['test_f1'][-1],
            'avg_communication_cost': np.mean(self.history['communication_cost']),
            'total_communication_cost': np.sum(self.history['communication_cost']),
            'convergence_rounds': len(self.history['rounds']),
            'avg_round_time': np.mean(self.history['round_time'])
        }
        return final_metrics
