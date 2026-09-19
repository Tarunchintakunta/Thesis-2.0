"""
Main entry point for matrix scaling benchmarks.

Addresses the research question from Sabir & Alebrahim (2025):
How do multi-threaded and distributed parallel processing compare for matrix workloads?
"""

import argparse
import sys
from pathlib import Path

from benchmark import run_full_benchmark_suite


def main():
    """Main entry point for benchmarking suite."""
    parser = argparse.ArgumentParser(
        description='Matrix Scaling Benchmark Suite - Venkat Bora Thesis Project'
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'quick', 'custom'],
        default='full',
        help='Benchmark mode: full (all sizes), quick (small subset), custom'
    )
    
    parser.add_argument(
        '--sizes',
        type=int,
        nargs='+',
        default=None,
        help='Matrix sizes to test (for custom mode)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        nargs='+',
        default=None,
        help='Worker counts to test (for custom mode)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=5,
        help='Number of iterations per configuration (default: 5)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Output directory for results (default: results/)'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='Shortcut for full benchmark mode'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Shortcut for quick benchmark mode'
    )
    
    args = parser.parse_args()
    
    # Determine configuration
    if args.quick or args.mode == 'quick':
        # Quick test: smaller subset
        matrix_sizes = [200, 500, 1000]
        worker_counts = [1, 2, 4]
        print("\nRunning QUICK benchmark suite")
        print("Using reduced matrix sizes and worker counts")
    
    elif args.full or args.mode == 'full':
        # Full benchmark: all sizes from CA requirements
        matrix_sizes = [200, 500, 1000, 1500, 2000]
        worker_counts = [1, 2, 4, 8]
        print("\nRunning FULL benchmark suite")
        print("This will take significant time (30-60 minutes depending on hardware)")
    
    else:  # custom
        if not args.sizes or not args.workers:
            print("Error: --sizes and --workers required for custom mode")
            sys.exit(1)
        matrix_sizes = args.sizes
        worker_counts = args.workers
        print("\nRunning CUSTOM benchmark suite")
    
    print(f"Matrix sizes: {matrix_sizes}")
    print(f"Worker counts: {worker_counts}")
    print(f"Iterations per config: {args.iterations}")
    print(f"Output directory: {args.output}")
    print()
    
    # Run benchmark suite
    try:
        harness = run_full_benchmark_suite(
            matrix_sizes=matrix_sizes,
            worker_counts=worker_counts,
            n_iterations=args.iterations,
            output_dir=args.output
        )
        
        print("\n" + "=" * 70)
        print("BENCHMARK COMPLETE")
        print(f"Total configurations tested: {len(set((r.config_name, r.matrix_size) for r in harness.results))}")
        print(f"Total runs: {len(harness.results)}")
        print(f"Results saved to: {args.output}/")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run 'make visualize' to generate charts")
        print("  2. Check results/data/ for JSON and CSV files")
        print("  3. Check results/figures/ for visualizations")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
