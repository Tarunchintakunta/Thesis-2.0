"""
Visualization Module

Generate publication-quality plots from benchmark results.
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
import seaborn as sns

sns.set_style("whitegrid")
sns.set_palette("husl")


class ResultVisualizer:
    """Create visualizations from benchmark results."""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.data_dir = self.results_dir / "data"
        self.figures_dir = self.results_dir / "figures"
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.load_results()
    
    def load_results(self):
        """Load benchmark results from JSON."""
        summary_file = self.data_dir / "summary_statistics.json"
        raw_file = self.data_dir / "benchmark_results.json"
        
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                self.summary_stats = json.load(f)
            self.df_summary = pd.DataFrame(self.summary_stats)
        else:
            print(f"Warning: {summary_file} not found")
            self.summary_stats = []
            self.df_summary = pd.DataFrame()
        
        if raw_file.exists():
            with open(raw_file, 'r') as f:
                self.raw_results = json.load(f)
            self.df_raw = pd.DataFrame(self.raw_results)
        else:
            print(f"Warning: {raw_file} not found")
            self.raw_results = []
            self.df_raw = pd.DataFrame()
    
    def plot_completion_time_vs_size(self):
        """Plot completion time vs matrix size for different configurations."""
        if self.df_summary.empty:
            print("No data to plot")
            return
        
        # Filter for matrix multiplication
        df_matmul = self.df_summary[self.df_summary['operation'] == 'matmul'].copy()
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot 1: Threaded vs Distributed (4 workers)
        ax = axes[0]
        for model in df_matmul['parallelism_model'].unique():
            df_model = df_matmul[
                (df_matmul['parallelism_model'] == model) & 
                (df_matmul['n_workers'] == 4)
            ]
            if not df_model.empty:
                ax.errorbar(
                    df_model['matrix_size'],
                    df_model['mean_time'],
                    yerr=df_model['std_time'],
                    marker='o',
                    label=model.capitalize(),
                    linewidth=2,
                    markersize=8
                )
        
        ax.set_xlabel('Matrix Size (n × n)', fontsize=12)
        ax.set_ylabel('Completion Time (seconds)', fontsize=12)
        ax.set_title('Matrix Multiplication: Completion Time vs Size\n(4 Workers)', 
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Scaling with worker count (size=1000)
        ax = axes[1]
        df_1000 = df_matmul[df_matmul['matrix_size'] == 1000]
        for model in df_1000['parallelism_model'].unique():
            df_model = df_1000[df_1000['parallelism_model'] == model]
            if not df_model.empty:
                ax.errorbar(
                    df_model['n_workers'],
                    df_model['mean_time'],
                    yerr=df_model['std_time'],
                    marker='s',
                    label=model.capitalize(),
                    linewidth=2,
                    markersize=8
                )
        
        ax.set_xlabel('Number of Workers', fontsize=12)
        ax.set_ylabel('Completion Time (seconds)', fontsize=12)
        ax.set_title('Matrix Multiplication: Scaling with Workers\n(Matrix Size 1000×1000)', 
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.figures_dir / "completion_time_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()
    
    def plot_memory_usage(self):
        """Plot peak memory usage comparison."""
        if self.df_summary.empty:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Group by parallelism model and matrix size
        df_matmul = self.df_summary[
            (self.df_summary['operation'] == 'matmul') &
            (self.df_summary['n_workers'] == 4)
        ].copy()
        
        for model in df_matmul['parallelism_model'].unique():
            df_model = df_matmul[df_matmul['parallelism_model'] == model]
            ax.plot(
                df_model['matrix_size'],
                df_model['mean_memory'],
                marker='D',
                label=model.capitalize(),
                linewidth=2,
                markersize=8
            )
        
        ax.set_xlabel('Matrix Size (n × n)', fontsize=12)
        ax.set_ylabel('Peak Memory Usage (MB)', fontsize=12)
        ax.set_title('Peak Memory Usage: Multi-threaded vs Distributed\n(4 Workers, Matrix Multiplication)', 
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.figures_dir / "memory_usage_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()
    
    def plot_cpu_utilization(self):
        """Plot CPU utilization efficiency."""
        if self.df_summary.empty:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Filter for specific size
        df_filtered = self.df_summary[
            (self.df_summary['operation'] == 'matmul') &
            (self.df_summary['matrix_size'] == 1000)
        ].copy()
        
        # Calculate efficiency: actual utilization / (workers * 100)
        # Normalized to show how much of available capacity is used
        df_filtered['efficiency'] = df_filtered['mean_cpu'] / 100.0
        
        for model in df_filtered['parallelism_model'].unique():
            df_model = df_filtered[df_filtered['parallelism_model'] == model]
            ax.plot(
                df_model['n_workers'],
                df_model['efficiency'],
                marker='o',
                label=model.capitalize(),
                linewidth=2,
                markersize=8
            )
        
        ax.set_xlabel('Number of Workers', fontsize=12)
        ax.set_ylabel('CPU Utilization (fraction of capacity)', fontsize=12)
        ax.set_title('CPU Utilization Efficiency\n(Matrix Size 1000×1000, Matrix Multiplication)', 
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.1])
        
        plt.tight_layout()
        output_file = self.figures_dir / "cpu_utilization.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()
    
    def plot_speedup_analysis(self):
        """Plot speedup relative to single-threaded baseline."""
        if self.df_summary.empty:
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Use matrix size 1000 for speedup analysis
        df_filtered = self.df_summary[
            (self.df_summary['operation'] == 'matmul') &
            (self.df_summary['matrix_size'] == 1000)
        ].copy()
        
        # Get baseline (1 worker threaded)
        baseline = df_filtered[
            (df_filtered['parallelism_model'] == 'threaded') &
            (df_filtered['n_workers'] == 1)
        ]['mean_time'].values
        
        if len(baseline) == 0:
            print("No baseline data found for speedup analysis")
            return
        
        baseline_time = baseline[0]
        
        # Calculate speedup for each configuration
        for model in df_filtered['parallelism_model'].unique():
            df_model = df_filtered[df_filtered['parallelism_model'] == model]
            speedup = baseline_time / df_model['mean_time']
            ax.plot(
                df_model['n_workers'],
                speedup,
                marker='^',
                label=model.capitalize(),
                linewidth=2,
                markersize=8
            )
        
        # Plot ideal linear speedup
        workers = sorted(df_filtered['n_workers'].unique())
        ax.plot(workers, workers, 'k--', label='Ideal Linear', linewidth=2, alpha=0.5)
        
        ax.set_xlabel('Number of Workers', fontsize=12)
        ax.set_ylabel('Speedup (vs 1 thread)', fontsize=12)
        ax.set_title('Parallel Speedup Analysis\n(Matrix Size 1000×1000, Matrix Multiplication)', 
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.figures_dir / "speedup_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()
    
    def plot_lu_factorization_comparison(self):
        """Plot LU factorization performance."""
        if self.df_summary.empty:
            return
        
        df_lu = self.df_summary[self.df_summary['operation'] == 'lu'].copy()
        
        if df_lu.empty:
            print("No LU factorization data to plot")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Compare at 4 workers
        df_filtered = df_lu[df_lu['n_workers'] == 4]
        
        for model in df_filtered['parallelism_model'].unique():
            df_model = df_filtered[df_filtered['parallelism_model'] == model]
            ax.errorbar(
                df_model['matrix_size'],
                df_model['mean_time'],
                yerr=df_model['std_time'],
                marker='o',
                label=model.capitalize(),
                linewidth=2,
                markersize=8
            )
        
        ax.set_xlabel('Matrix Size (n × n)', fontsize=12)
        ax.set_ylabel('Completion Time (seconds)', fontsize=12)
        ax.set_title('LU Factorization: Completion Time vs Size\n(4 Workers)', 
                    fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.figures_dir / "lu_factorization_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()
    
    def generate_all_plots(self):
        """Generate all visualization plots."""
        print("Generating visualizations...")
        print("-" * 50)
        
        self.plot_completion_time_vs_size()
        self.plot_memory_usage()
        self.plot_cpu_utilization()
        self.plot_speedup_analysis()
        self.plot_lu_factorization_comparison()
        
        print("-" * 50)
        print(f"All visualizations saved to: {self.figures_dir}")


def main():
    """Main entry point for visualization."""
    import sys
    
    results_dir = "results" if len(sys.argv) < 2 else sys.argv[1]
    
    visualizer = ResultVisualizer(results_dir)
    visualizer.generate_all_plots()


if __name__ == '__main__':
    main()
