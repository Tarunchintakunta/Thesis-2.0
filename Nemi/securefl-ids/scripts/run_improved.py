#!/usr/bin/env python3
"""
Run improved SecureFL-IDS experiment
"""
import os
import sys
import json
import pickle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.improved.securefl_ids import SecureFLIDS


def run_improved_experiment():
    """Run full improved experiment"""
    print("=" * 70)
    print("SecureFL-IDS Experiment (Improved)")
    print("=" * 70)
    
    config = {
        'num_clients': 5,
        'num_rounds': 50,
        'local_epochs': 1,
        'learning_rate': 0.001,
        'base_epsilon': 1.0,
        'communication_efficient': True,
        'compression_ratio': 0.5,
        'sample_size': 25000
    }
    
    print(f"Configuration: {config}\n")
    
    improved = SecureFLIDS(
        num_clients=config['num_clients'],
        base_epsilon=config['base_epsilon'],
        communication_efficient=config['communication_efficient'],
        compression_ratio=config['compression_ratio']
    )
    
    improved.setup(sample_size=config['sample_size'])
    history = improved.train(
        num_rounds=config['num_rounds'],
        local_epochs=config['local_epochs'],
        learning_rate=config['learning_rate']
    )
    
    summary = improved.get_results_summary()
    
    # Save results
    os.makedirs('results/improved', exist_ok=True)
    
    with open('results/improved/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    with open('results/improved/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    with open('results/improved/history.pkl', 'wb') as f:
        pickle.dump(history, f)
    
    print("\n" + "=" * 70)
    print("IMPROVED RESULTS")
    print("=" * 70)
    for key, value in summary.items():
        print(f"{key:<30}: {value}")
    
    print("\nResults saved to: results/improved/")
    print("=" * 70)


if __name__ == '__main__':
    run_improved_experiment()
