"""
Baseline: Privacy-Preserving FL-IDS (Saklani et al. 2026)
Replication of PP-FL-DP-IDS from:
Saklani, S., Chohan, D.K., and Sharma, R. (2026) 'Privacy Preserving Cloud Native 
Intrusion Detection Using Federated Learning and Differential Privacy'
"""
import torch
import numpy as np
from typing import Dict, List
import time

from src.common.models import create_model
from src.common.federated import FederatedClient, FederatedServer, federated_learning_round
from src.common.privacy import DifferentialPrivacy
from src.common.metrics import calculate_metrics
from src.common.data_loader import create_federated_data


class BaselineFLIDS:
    """
    Baseline Federated Learning IDS with Differential Privacy
    
    Configuration matches Saklani et al. (2026):
    - CNN-based binary classifier
    - FedAvg aggregation
    - Differential Privacy (ε=1.0, δ=1e-5, clip=1.0)
    - Non-IID data distribution across clients
    """
    
    def __init__(self, 
                 num_clients: int = 5,
                 epsilon: float = 1.0,
                 delta: float = 1e-5,
                 clip_norm: float = 1.0,
                 device: str = 'cpu'):
        
        self.num_clients = num_clients
        self.device = device
        
        # Privacy parameters (from Saklani et al.)
        self.privacy = DifferentialPrivacy(
            epsilon=epsilon,
            delta=delta,
            clip_norm=clip_norm
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
        print(f"Setting up baseline FL-IDS with {self.num_clients} clients...")
        
        # Load and distribute data
        fed_data = create_federated_data(
            num_clients=self.num_clients,
            data_path=data_path,
            alpha=0.5,  # Non-IID parameter
            binary=True,
            sample_size=sample_size
        )
        
        self.test_X, self.test_y = fed_data['test_set']
        num_features = fed_data['num_features']
        
        # Create global model
        self.global_model = create_model('cnn', num_features, num_classes=2)
        self.global_model.to(self.device)
        
        # Create server
        self.server = FederatedServer(self.global_model, aggregation_method='fedavg')
        
        # Create clients
        self.clients = []
        for client_id, (X_train, y_train) in enumerate(fed_data['train_clients']):
            model_copy = create_model('cnn', num_features, num_classes=2)
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
    
    def train(self, num_rounds: int = 50, local_epochs: int = 1, 
             learning_rate: float = 0.001):
        """
        Train federated model
        
        Args:
            num_rounds: Number of federated rounds
            local_epochs: Local epochs per client per round
            learning_rate: Learning rate
        """
        print(f"\nTraining baseline FL-IDS for {num_rounds} rounds...")
        
        for round_idx in range(num_rounds):
            round_start = time.time()
            
            # Federated learning round
            round_result = federated_learning_round(
                server=self.server,
                clients=self.clients,
                local_epochs=local_epochs,
                learning_rate=learning_rate,
                privacy_mechanism=self.privacy,
                communication_efficient=False  # Baseline uses standard FedAvg
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
            probas_np = probas[:, 1].cpu().numpy()  # Probability of attack class
        
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
