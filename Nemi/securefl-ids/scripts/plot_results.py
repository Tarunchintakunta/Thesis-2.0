#!/usr/bin/env python3
"""
Plot experimental results
"""
import os
import sys
import pickle
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def plot_convergence(baseline_hist, improved_hist, output_dir):
    """Plot accuracy and F1 convergence"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Accuracy
    axes[0].plot(baseline_hist['rounds'], baseline_hist['test_accuracy'], 
                label='Baseline', marker='o', markersize=3)
    axes[0].plot(improved_hist['rounds'], improved_hist['test_accuracy'], 
                label='SecureFL-IDS', marker='s', markersize=3)
    axes[0].set_xlabel('Federated Round')
    axes[0].set_ylabel('Test Accuracy')
    axes[0].set_title('Model Convergence: Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # F1-Score
    axes[1].plot(baseline_hist['rounds'], baseline_hist['test_f1'], 
                label='Baseline', marker='o', markersize=3)
    axes[1].plot(improved_hist['rounds'], improved_hist['test_f1'], 
                label='SecureFL-IDS', marker='s', markersize=3)
    axes[1].set_xlabel('Federated Round')
    axes[1].set_ylabel('Test F1-Score')
    axes[1].set_title('Model Convergence: F1-Score')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'convergence.png'), dpi=300)
    print(f"Saved: {output_dir}/convergence.png")


def plot_communication_cost(baseline_hist, improved_hist, output_dir):
    """Plot communication cost over rounds"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    ax.plot(baseline_hist['rounds'], baseline_hist['communication_cost'],
           label='Baseline', marker='o', markersize=3)
    ax.plot(improved_hist['rounds'], improved_hist['communication_cost'],
           label='SecureFL-IDS (Compressed)', marker='s', markersize=3)
    ax.set_xlabel('Federated Round')
    ax.set_ylabel('Communication Cost (MB)')
    ax.set_title('Communication Efficiency Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'communication_cost.png'), dpi=300)
    print(f"Saved: {output_dir}/communication_cost.png")


def plot_comparison_bar(baseline_sum, improved_sum, output_dir):
    """Bar chart comparison"""
    metrics = ['Accuracy', 'F1-Score', 'Avg Comm\nCost (MB)']
    baseline_vals = [
        baseline_sum['accuracy'],
        baseline_sum['f1_score'],
        baseline_sum['avg_communication_cost']
    ]
    improved_vals = [
        improved_sum['accuracy'],
        improved_sum['f1_score'],
        improved_sum['avg_communication_cost']
    ]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, baseline_vals, width, label='Baseline', alpha=0.8)
    ax.bar(x + width/2, improved_vals, width, label='SecureFL-IDS', alpha=0.8)
    
    ax.set_ylabel('Value')
    ax.set_title('Performance Comparison: Baseline vs SecureFL-IDS')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_bar.png'), dpi=300)
    print(f"Saved: {output_dir}/comparison_bar.png")


def main():
    print("=" * 70)
    print("Generating Figures")
    print("=" * 70)
    
    # Load results
    with open('results/baseline/history.pkl', 'rb') as f:
        baseline_hist = pickle.load(f)
    
    with open('results/improved/history.pkl', 'rb') as f:
        improved_hist = pickle.load(f)
    
    import json
    with open('results/baseline/summary.json', 'r') as f:
        baseline_sum = json.load(f)
    
    with open('results/improved/summary.json', 'r') as f:
        improved_sum = json.load(f)
    
    # Create output directory
    output_dir = 'figures'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate plots
    plot_convergence(baseline_hist, improved_hist, output_dir)
    plot_communication_cost(baseline_hist, improved_hist, output_dir)
    plot_comparison_bar(baseline_sum, improved_sum, output_dir)
    
    print("\nAll figures saved to: figures/")
    print("=" * 70)


if __name__ == '__main__':
    main()
