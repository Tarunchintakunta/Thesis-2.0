#!/usr/bin/env python3
"""
Generate visualizations from experiment results.
Student: Varun Gampa (23398639)
"""

import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 11


def load_results(input_dir):
    """Load all experiment results."""
    input_path = Path(input_dir)
    
    results = {}
    for file in ["pilot_results.json", "baseline_results.json", "improved_results.json"]:
        path = input_path / file
        if path.exists():
            with open(path, 'r') as f:
                results[file.replace("_results.json", "")] = json.load(f)
    
    return results


def plot_cost_comparison(results, output_dir):
    """Plot cost comparison across methods."""
    methods = []
    savings = []
    savings_pct = []
    
    for name, data in results.items():
        if "savings" in data and "our_approach" in data["savings"]:
            methods.append(name.replace("_", " ").title())
            savings.append(data["savings"]["our_approach"]["total_savings_usd_monthly"])
            savings_pct.append(data["savings"]["our_approach"]["total_savings_percent"])
    
    if not methods:
        print("No savings data available")
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Absolute savings
    bars1 = ax1.bar(methods, savings, color=['#3498db', '#2ecc71', '#e74c3c'])
    ax1.set_ylabel('Monthly Savings (USD)', fontsize=12, fontweight='bold')
    ax1.set_title('Absolute Cost Savings', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, max(savings) * 1.2)
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.2f}',
                ha='center', va='bottom', fontweight='bold')
    
    # Percentage savings
    bars2 = ax2.bar(methods, savings_pct, color=['#3498db', '#2ecc71', '#e74c3c'])
    ax2.set_ylabel('Savings (%)', fontsize=12, fontweight='bold')
    ax2.set_title('Percentage Cost Savings', fontsize=14, fontweight='bold')
    ax2.set_ylim(0, max(savings_pct) * 1.2)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    output_path = Path(output_dir) / "cost_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated: {output_path}")


def plot_forecast_accuracy(results, output_dir):
    """Plot forecast accuracy metrics."""
    methods = []
    our_mape = []
    naive_mape = []
    
    for name, data in results.items():
        if "forecasting" in data and data["forecasting"]:
            methods.append(name.replace("_", " ").title())
            
            if "prophet" in data["forecasting"]:
                our_mape.append(data["forecasting"]["prophet"]["errors"]["mape"])
                naive_mape.append(data["forecasting"]["naive_baseline"]["errors"]["mape"])
    
    if not methods:
        print("No forecasting data available")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(methods))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, our_mape, width, label='Prophet Forecast', color='#3498db')
    bars2 = ax.bar(x + width/2, naive_mape, width, label='Naive Baseline', color='#95a5a6')
    
    ax.set_ylabel('MAPE (%)', fontsize=12, fontweight='bold')
    ax.set_title('Forecast Accuracy: Prophet vs Naive Baseline', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend(fontsize=11)
    ax.set_ylim(0, max(our_mape + naive_mape) * 1.2)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    output_path = Path(output_dir) / "forecast_accuracy.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated: {output_path}")


def plot_allocation_accuracy(results, output_dir):
    """Plot storage class allocation accuracy."""
    methods = []
    accuracy = []
    precision = []
    recall = []
    f1 = []
    
    for name, data in results.items():
        if "evaluation" in data and "classification" in data["evaluation"]:
            metrics = data["evaluation"]["classification"]
            methods.append(name.replace("_", " ").title())
            accuracy.append(metrics["accuracy"] * 100)
            precision.append(metrics["precision"] * 100)
            recall.append(metrics["recall"] * 100)
            f1.append(metrics["f1_score"] * 100)
    
    if not methods:
        print("No evaluation data available")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(methods))
    width = 0.2
    
    ax.bar(x - 1.5*width, accuracy, width, label='Accuracy', color='#3498db')
    ax.bar(x - 0.5*width, precision, width, label='Precision', color='#2ecc71')
    ax.bar(x + 0.5*width, recall, width, label='Recall', color='#f39c12')
    ax.bar(x + 1.5*width, f1, width, label='F1-Score', color='#e74c3c')
    
    ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Storage Class Allocation Performance', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    output_path = Path(output_dir) / "allocation_accuracy.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated: {output_path}")


def plot_savings_distribution(results, output_dir):
    """Plot savings distribution by storage class transition."""
    # Extract savings data from improved experiment
    improved = results.get("improved", {})
    
    if "savings" not in improved or "our_approach" not in improved["savings"]:
        print("No detailed savings data available")
        return
    
    individual = improved["savings"]["our_approach"].get("individual_savings", [])
    
    if not individual:
        print("No individual savings data")
        return
    
    # Aggregate by transition
    transitions = {}
    for item in individual[:100]:  # Limit to first 100 for readability
        transition = f"{item['current_class'][:3]} → {item['recommended_class'][:3]}"
        savings = item['savings_usd_monthly']
        if transition not in transitions:
            transitions[transition] = []
        transitions[transition].append(savings)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    labels = list(transitions.keys())
    data = [transitions[k] for k in labels]
    
    bp = ax.boxplot(data, patch_artist=True)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    
    for patch in bp['boxes']:
        patch.set_facecolor('#3498db')
        patch.set_alpha(0.7)
    
    ax.set_ylabel('Savings per Object (USD/month)', fontsize=12, fontweight='bold')
    ax.set_title('Savings Distribution by Storage Class Transition', 
                fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = Path(output_dir) / "savings_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate result visualizations")
    parser.add_argument("--input", required=True, help="Results data directory")
    parser.add_argument("--output", required=True, help="Output figures directory")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load results
    print("Loading results...")
    results = load_results(args.input)
    
    if not results:
        print("No results found!")
        return
    
    print(f"Loaded {len(results)} experiment results")
    
    # Generate plots
    print("\nGenerating figures...")
    plot_cost_comparison(results, output_dir)
    plot_forecast_accuracy(results, output_dir)
    plot_allocation_accuracy(results, output_dir)
    plot_savings_distribution(results, output_dir)
    
    print("\n✓ All figures generated successfully!")


if __name__ == "__main__":
    main()
