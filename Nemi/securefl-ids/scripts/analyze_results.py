#!/usr/bin/env python3
"""
Analyze experimental results
"""
import os
import sys
import json
import pickle
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def load_results():
    """Load baseline and improved results"""
    with open('results/baseline/summary.json', 'r') as f:
        baseline_summary = json.load(f)
    
    with open('results/improved/summary.json', 'r') as f:
        improved_summary = json.load(f)
    
    with open('results/baseline/history.pkl', 'rb') as f:
        baseline_history = pickle.load(f)
    
    with open('results/improved/history.pkl', 'rb') as f:
        improved_history = pickle.load(f)
    
    return baseline_summary, improved_summary, baseline_history, improved_history


def calculate_improvements(baseline, improved):
    """Calculate percentage improvements"""
    improvements = {}
    
    for key in ['accuracy', 'f1_score']:
        delta = improved[key] - baseline[key]
        pct = (delta / baseline[key]) * 100 if baseline[key] != 0 else 0
        improvements[key] = {
            'delta': delta,
            'percentage': pct
        }
    
    # Communication cost (reduction is improvement)
    comm_delta = baseline['avg_communication_cost'] - improved['avg_communication_cost']
    comm_pct = (comm_delta / baseline['avg_communication_cost']) * 100
    improvements['communication_reduction'] = {
        'delta': -comm_delta,
        'percentage': comm_pct
    }
    
    return improvements


def statistical_significance(baseline_values, improved_values):
    """Perform t-test for statistical significance"""
    t_stat, p_value = stats.ttest_ind(baseline_values, improved_values)
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }


def main():
    print("=" * 70)
    print("SecureFL-IDS Results Analysis")
    print("=" * 70)
    
    baseline_sum, improved_sum, baseline_hist, improved_hist = load_results()
    
    # Calculate improvements
    improvements = calculate_improvements(baseline_sum, improved_sum)
    
    print("\nCOMPARATIVE ANALYSIS")
    print("-" * 70)
    print(f"{'Metric':<30} {'Baseline':<15} {'Improved':<15} {'Δ%':<10}")
    print("-" * 70)
    
    print(f"{'Accuracy':<30} {baseline_sum['accuracy']:.4f}         "
          f"{improved_sum['accuracy']:.4f}         "
          f"{improvements['accuracy']['percentage']:+.2f}%")
    
    print(f"{'F1-Score':<30} {baseline_sum['f1_score']:.4f}         "
          f"{improved_sum['f1_score']:.4f}         "
          f"{improvements['f1_score']['percentage']:+.2f}%")
    
    print(f"{'Avg Comm Cost (MB)':<30} {baseline_sum['avg_communication_cost']:.2f}           "
          f"{improved_sum['avg_communication_cost']:.2f}           "
          f"{improvements['communication_reduction']['percentage']:+.2f}%")
    
    print(f"{'Total Comm Cost (MB)':<30} {baseline_sum['total_communication_cost']:.2f}          "
          f"{improved_sum['total_communication_cost']:.2f}          ")
    
    print(f"{'Avg Round Time (s)':<30} {baseline_sum['avg_round_time']:.2f}            "
          f"{improved_sum['avg_round_time']:.2f}")
    
    # Statistical tests
    print("\nSTATISTICAL SIGNIFICANCE")
    print("-" * 70)
    
    acc_test = statistical_significance(
        baseline_hist['test_accuracy'],
        improved_hist['test_accuracy']
    )
    print(f"Accuracy improvement: p-value = {acc_test['p_value']:.4f} "
          f"({'Significant' if acc_test['significant'] else 'Not significant'})")
    
    # Save analysis
    os.makedirs('results/analysis', exist_ok=True)
    
    analysis = {
        'baseline': baseline_sum,
        'improved': improved_sum,
        'improvements': improvements,
        'statistical_tests': {
            'accuracy': acc_test
        }
    }
    
    with open('results/analysis/comparative_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print("\nAnalysis saved to: results/analysis/comparative_analysis.json")
    print("=" * 70)


if __name__ == '__main__':
    main()
