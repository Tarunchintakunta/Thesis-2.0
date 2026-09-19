#!/usr/bin/env python3
"""
Run baseline experiment (full)
"""
import os
import sys
import json
import pickle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.baseline.baseline_fl_ids import BaselineFLIDS


def run_baseline_experiment():
    """Run full baseline experiment"""
    print("=" * 70)
    print("Baseline FL-IDS Experiment (Saklani et al. 2026)")
    print("=" * 70)
    
    config = {
        'num_clients': 5,
        'num_rounds': 50,
        'local_epochs': 1,
        'learning_rate': 0.001,
        'epsilon': 1.0,
        'sample_size': 25000
    }
    
    print(f"Configuration: {config}\n")
    
    baseline = BaselineFLIDS(
        num_clients=config['num_clients'],
        epsilon=config['epsilon']
    )
    
    baseline.setup(sample_size=config['sample_size'])
    history = baseline.train(
        num_rounds=config['num_rounds'],
        local_epochs=config['local_epochs'],
        learning_rate=config['learning_rate']
    )
    
    summary = baseline.get_results_summary()
    
    # Save results
    os.makedirs('results/baseline', exist_ok=True)
    
    with open('results/baseline/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    with open('results/baseline/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    with open('results/baseline/history.pkl', 'wb') as f:
        pickle.dump(history, f)
    
    print("\n" + "=" * 70)
    print("BASELINE RESULTS")
    print("=" * 70)
    for key, value in summary.items():
        print(f"{key:<30}: {value}")
    
    print("\nResults saved to: results/baseline/")
    print("=" * 70)


if __name__ == '__main__':
    run_baseline_experiment()
