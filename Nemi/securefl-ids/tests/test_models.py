"""
Test neural network models
"""
import pytest
import torch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.common.models import CNNClassifier, CNNLSTMClassifier, create_model


def test_cnn_classifier():
    """Test CNN classifier forward pass"""
    model = CNNClassifier(input_dim=20, num_classes=2)
    
    # Test forward pass
    batch_size = 8
    x = torch.randn(batch_size, 20)
    output = model(x)
    
    assert output.shape == (batch_size, 2)
    
    # Test with different batch size
    x2 = torch.randn(16, 20)
    output2 = model(x2)
    assert output2.shape == (16, 2)


def test_cnn_lstm_classifier():
    """Test CNN-LSTM classifier forward pass"""
    model = CNNLSTMClassifier(input_dim=20, num_classes=2)
    
    batch_size = 8
    x = torch.randn(batch_size, 20)
    output = model(x)
    
    assert output.shape == (batch_size, 2)


def test_model_training():
    """Test basic model training"""
    model = CNNClassifier(input_dim=10, num_classes=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.CrossEntropyLoss()
    
    # Dummy data
    x = torch.randn(16, 10)
    y = torch.randint(0, 2, (16,))
    
    # Training step
    optimizer.zero_grad()
    output = model(x)
    loss = criterion(output, y)
    loss.backward()
    optimizer.step()
    
    # Check that loss is computed
    assert loss.item() > 0


def test_model_factory():
    """Test model creation via factory function"""
    cnn = create_model('cnn', input_dim=10, num_classes=2)
    assert isinstance(cnn, CNNClassifier)
    
    cnn_lstm = create_model('cnn_lstm', input_dim=10, num_classes=2)
    assert isinstance(cnn_lstm, CNNLSTMClassifier)
    
    with pytest.raises(ValueError):
        create_model('invalid_model', input_dim=10)
