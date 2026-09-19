#!/usr/bin/env python3
"""
Run pilot experiment (quick test)
"""
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.baseline.baseline_fl_ids import BaselineFLIDS
from src.improved.securefl_ids import SecureFLIDS


def run_pilot():
    """Run quick pilot with both baseline and improved"""
    print("=" * 70)
    print("SecureFL-IDS Pilot Experiment")
    print("=" * 70)
    print("Quick test with 3 clients, 10 rounds, 1000 samples\n")
    
    config = {
        'num_clients': 3,
        'num_rounds': 10,
        'local_epochs': 1,
        'learning_rate': 0.001,
        'sample_size': 3000
    }
    
    results = {}
    
    # Baseline
    print("\n[1/2] Running Baseline (Saklani et al. 2026)...")
    print("-" * 70)
    baseline = BaselineFLIDS(num_clients=config['num_clients'])
    baseline.setup(sample_size=config['sample_size'])
    baseline.train(
        num_rounds=config['num_rounds'],
        local_epochs=config['local_epochs'],
        learning_rate=config['learning_rate']
    )
    results['baseline'] = baseline.get_results_summary()
    
    # Improved
    print("\n[2/2] Running Improved (SecureFL-IDS)...")
    print("-" * 70)
    improved = SecureFLIDS(
        num_clients=config['num_clients'],
        communication_efficient=True,
        compression_ratio=0.5
    )
    improved.setup(sample_size=config['sample_size'])
    improved.train(
        num_rounds=config['num_rounds'],
        local_epochs=config['local_epochs'],
        learning_rate=config['learning_rate']
    )
    results['improved'] = improved.get_results_summary()
    
    # Summary
    print("\n" + "=" * 70)
    print("PILOT RESULTS SUMMARY")
    print("=" * 70)
    print(f"{'Metric':<30} {'Baseline':<15} {'Improved':<15} {'Δ':<10}")
    print("-" * 70)
    
    metrics = ['accuracy', 'f1_score', 'avg_communication_cost']
    for metric in metrics:
        baseline_val = results['baseline'][metric]
        improved_val = results['improved'][metric]
        delta = improved_val - baseline_val
        delta_pct = (delta / baseline_val * 100) if baseline_val != 0 else 0
        
        if 'cost' in metric:
            print(f"{metric:<30} {baseline_val:>10.2f} MB   {improved_val:>10.2f} MB   {delta_pct:>6.1f}%")
        else:
            print(f"{metric:<30} {baseline_val:>10.4f}     {improved_val:>10.4f}     {delta_pct:>6.1f}%")
    
    # Save results
    os.makedirs('results/pilot', exist_ok=True)
    with open('results/pilot/pilot_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to: results/pilot/pilot_results.json")
    print("=" * 70)


if __name__ == '__main__':
    run_pilot()
