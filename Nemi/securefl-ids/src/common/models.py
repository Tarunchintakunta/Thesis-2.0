"""
Neural network models for intrusion detection
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class CNNClassifier(nn.Module):
    """
    CNN-based intrusion detection classifier (Baseline model)
    Based on Saklani et al. (2026)
    """
    def __init__(self, input_dim: int, num_classes: int = 2):
        super(CNNClassifier, self).__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        # Reshape to 2D for CNN (we'll use 1D conv)
        # Input shape: (batch, features) -> (batch, 1, features)
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(32)
        self.pool1 = nn.MaxPool1d(2)
        
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool2 = nn.MaxPool1d(2)
        
        # Calculate flattened size
        conv_output_size = (input_dim // 4) * 64  # After 2 pooling layers
        
        self.fc1 = nn.Linear(conv_output_size, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, num_classes)
    
    def forward(self, x):
        # x shape: (batch, features)
        x = x.unsqueeze(1)  # (batch, 1, features)
        
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool1(x)
        
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool2(x)
        
        x = x.view(x.size(0), -1)  # Flatten
        
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


class CNNLSTMClassifier(nn.Module):
    """
    CNN-LSTM hybrid classifier (Improved model)
    Captures spatial features (CNN) and temporal patterns (LSTM)
    """
    def __init__(self, input_dim: int, num_classes: int = 2, 
                 lstm_hidden: int = 64, lstm_layers: int = 2):
        super(CNNLSTMClassifier, self).__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        # CNN layers
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(32)
        self.pool1 = nn.MaxPool1d(2)
        
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool2 = nn.MaxPool1d(2)
        
        # LSTM layers
        lstm_input_size = input_dim // 4  # After pooling
        self.lstm = nn.LSTM(
            input_size=64,
            hidden_size=lstm_hidden,
            num_layers=lstm_layers,
            batch_first=True,
            dropout=0.3 if lstm_layers > 1 else 0
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(lstm_hidden, 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, num_classes)
    
    def forward(self, x):
        # x shape: (batch, features)
        x = x.unsqueeze(1)  # (batch, 1, features)
        
        # CNN
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.pool1(x)
        
        x = self.conv2(x)
        x = self.bn2(x)
        x = F.relu(x)
        x = self.pool2(x)
        
        # Prepare for LSTM: (batch, channels, seq_len) -> (batch, seq_len, channels)
        x = x.permute(0, 2, 1)
        
        # LSTM
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Use last hidden state
        x = h_n[-1]  # (batch, lstm_hidden)
        
        # FC layers
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


def create_model(model_type: str, input_dim: int, num_classes: int = 2):
    """Factory function to create models"""
    if model_type == "cnn":
        return CNNClassifier(input_dim, num_classes)
    elif model_type == "cnn_lstm":
        return CNNLSTMClassifier(input_dim, num_classes)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
