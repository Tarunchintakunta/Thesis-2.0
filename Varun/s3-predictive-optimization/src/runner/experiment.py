#!/usr/bin/env python3
"""
Main experiment runner for S3 Predictive Cost Optimization Framework.
Student: Varun Gampa (23398639)
"""

import sys
import os
import json
import argparse
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.simulator.workload_generator import WorkloadGenerator
from src.simulator.s3_simulator import S3Simulator
from src.pricing.s3_pricing import S3Pricing
from src.recommendation.baseline import BaselineRecommender
from src.recommendation.ml_recommender import MLRecommender
from src.forecasting.naive_baseline import NaiveBaseline
from src.forecasting.time_series import TimeSeriesForecaster
from src.savings.estimator import SavingsEstimator
from src.evaluation.metrics import MetricsCalculator


class ExperimentRunner:
    """Main experiment orchestrator."""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.experiment_name = self.config["experiment"]["name"]
        self.mode = self.config["experiment"]["mode"]
        
        # Initialize components
        self.pricing = S3Pricing()
        self.generator = WorkloadGenerator()
        self.simulator = S3Simulator()
        self.metrics = MetricsCalculator()
        
        # Results
        self.results = {
            "experiment": self.config["experiment"],
            "timestamp": datetime.now().isoformat(),
            "config": self.config
        }
    
    def generate_workload(self):
        """Generate synthetic S3 workload."""
        print(f"Generating workload ({self.config['workload']['num_objects']} objects)...")
        
        objects = self.generator.generate_objects(
            self.config["workload"]["num_objects"],
            self.config["workload"]
        )
        
        access_log = self.generator.generate_access_log(
            objects,
            self.config["workload"]["duration_days"]
        )
        
        # Load into simulator
        self.simulator.load_objects_from_generator(objects)
        self.simulator.load_access_log(access_log)
        
        self.results["workload"] = {
            "num_objects": len(objects),
            "duration_days": self.config["workload"]["duration_days"],
            "access_log_entries": len(access_log),
            "metrics": self.simulator.get_bucket_metrics()
        }
        
        return objects, access_log
    
    def run_baseline_recommendation(self, objects):
        """Run TierBase-inspired baseline recommender."""
        print("Running baseline (TierBase) recommender...")
        
        recommender = BaselineRecommender(self.config["recommendation"], self.pricing)
        recommendations = recommender.recommend_batch(objects)
        
        self.results["baseline_recommendation"] = {
            "metadata": recommender.get_metadata(),
            "num_recommendations": len(recommendations),
            "recommendations": recommendations
        }
        
        return recommendations
    
    def run_ml_recommendation(self, objects):
        """Run ML-based recommender."""
        print("Running ML (XGBoost) recommender...")
        
        try:
            recommender = MLRecommender(self.config["recommendation"], self.pricing)
            
            # Train model
            train_info = recommender.train(objects)
            print(f"  Trained: accuracy={train_info['train_accuracy']:.2%}")
            
            # Generate recommendations
            recommendations = recommender.recommend_batch(objects)
            
            self.results["ml_recommendation"] = {
                "metadata": recommender.get_metadata(),
                "training": train_info,
                "num_recommendations": len(recommendations),
                "recommendations": recommendations
            }
            
            return recommendations
        
        except ImportError as e:
            print(f"  Warning: {e}")
            print("  Falling back to baseline recommender")
            return self.run_baseline_recommendation(objects)
    
    def generate_cost_history(self, objects, days=60):
        """Generate synthetic cost history for forecasting.

        Preserve float precision: rounding to 4 d.p. can collapse
        sub-cent daily costs (~1e-3) into a flat series, making Prophet
        identical to naive persistence.
        """
        history = []
        current_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            date = current_date + timedelta(days=day)
            
            daily_cost = sum(
                self.pricing.get_storage_cost_per_month(
                    obj.get("current_storage_class", "STANDARD"),
                    obj.get("size_mb", 0) / 1024
                ) / 30
                for obj in objects
            )
            
            # Weekly seasonality noise (series must vary for forecast eval)
            noise = daily_cost * 0.05 * (0.5 - abs(day % 7 - 3) / 10)
            daily_cost += noise
            
            history.append({
                "date": date.isoformat(),
                "cost": float(daily_cost)
            })
        
        return history
    
    def run_forecasting(self, cost_history):
        """Run Prophet vs naive on a temporal holdout of the cost series.

        Prior bug: compared both forecasts to a synthetic growing 'actual'
        never present in history, while rounded costs were flat — MAPEs
        matched exactly and beats_naive was always false.
        """
        if not self.config.get("forecasting", {}).get("enabled", False):
            return None
        
        print("Running cost forecasting...")
        
        naive = NaiveBaseline()
        horizon = self.config["forecasting"].get("horizon_days", 30)

        if len(cost_history) <= horizon + 2:
            horizon = max(1, len(cost_history) // 3)
        train_history = cost_history[:-horizon]
        holdout = cost_history[-horizon:]
        actual_future = [h["cost"] for h in holdout]
        train_costs = [h["cost"] for h in train_history]
        naive_forecast = naive.forecast(train_costs, horizon)
        
        try:
            forecaster = TimeSeriesForecaster(self.config["forecasting"])
            forecast_result = forecaster.forecast_cost(train_history, horizon)
            
            prophet_forecast = [f["yhat"] for f in forecast_result["forecast"]]
            n = min(len(actual_future), len(prophet_forecast), len(naive_forecast))
            actual_future = actual_future[:n]
            prophet_forecast = prophet_forecast[:n]
            naive_forecast = naive_forecast[:n]
            
            naive_error = naive.calculate_error(actual_future, naive_forecast)
            prophet_error = forecaster.calculate_error(actual_future, prophet_forecast)
            beats = prophet_error["mape"] < naive_error["mape"]
            
            self.results["forecasting"] = {
                "method": "prophet",
                "eval_protocol": "temporal_holdout",
                "horizon_days": horizon,
                "historical_points": len(cost_history),
                "train_points": len(train_history),
                "holdout_points": n,
                "naive_baseline": {
                    "forecast": naive_forecast[:5],
                    "errors": naive_error,
                    "metadata": naive.get_metadata()
                },
                "prophet": {
                    "forecast": forecast_result["forecast"][:5],
                    "errors": prophet_error,
                    "metadata": forecaster.get_metadata()
                },
                "beats_naive_baseline": beats
            }
            
            return {
                "actual": actual_future,
                "predicted": prophet_forecast,
                "naive": naive_forecast
            }
        
        except ImportError as e:
            print(f"  Warning: {e}")
            self.results["forecasting"] = {
                "error": str(e),
                "naive_baseline_only": True
            }
            return None
    
    def run_savings_estimation(self, objects, recommendations):
        """Estimate cost savings."""
        if not self.config.get("savings", {}).get("enabled", True):
            return None
        
        print("Estimating cost savings...")
        
        estimator = SavingsEstimator(self.pricing)
        
        # Individual savings
        savings = estimator.estimate_savings_batch(objects, recommendations)
        
        # Compare against AWS baselines
        comparison = estimator.comprehensive_comparison(objects, recommendations)
        
        self.results["savings"] = {
            "our_approach": savings,
            "comparison_vs_aws": comparison,
            "metadata": estimator.get_metadata()
        }
        
        return savings
    
    def run_evaluation(self, objects, recommendations, forecast_data):
        """Run comprehensive evaluation."""
        print("Running evaluation...")
        
        # Generate "optimal" labels for evaluation
        optimal_labels = []
        for obj in objects:
            # Simplified optimal class determination
            age = obj.get("age_days", 0)
            freq = obj.get("access_frequency", 0)
            
            if freq > 10:
                optimal = "STANDARD"
            elif age < 30:
                optimal = "STANDARD"
            elif age < 90:
                optimal = "STANDARD_IA"
            elif age < 180:
                optimal = "GLACIER_INSTANT"
            else:
                optimal = "GLACIER_DEEP_ARCHIVE"
            
            optimal_labels.append(optimal)
        
        # Classification metrics
        predicted = [r["recommended_storage_class"] for r in recommendations]
        classification = self.metrics.classification_metrics(optimal_labels, predicted)
        
        # Forecast comparison (if available)
        forecast_metrics = None
        if forecast_data:
            forecast_metrics = {
                "mape": self.metrics.forecast_mape(
                    forecast_data["actual"], forecast_data["predicted"]
                ),
                "rmse": self.metrics.forecast_rmse(
                    forecast_data["actual"], forecast_data["predicted"]
                ),
                "naive_mape": self.metrics.forecast_mape(
                    forecast_data["actual"], forecast_data["naive"]
                ),
                "beats_naive": self.metrics.forecast_mape(
                    forecast_data["actual"], forecast_data["predicted"]
                ) < self.metrics.forecast_mape(
                    forecast_data["actual"], forecast_data["naive"]
                )
            }
        
        self.results["evaluation"] = {
            "classification": classification,
            "forecasting": forecast_metrics
        }
    
    def run(self):
        """Run complete experiment."""
        print(f"\n{'='*60}")
        print(f"S3 Predictive Cost Optimization - {self.experiment_name}")
        print(f"{'='*60}\n")
        
        # Step 1: Generate workload
        objects, access_log = self.generate_workload()
        
        # Step 2: Run recommendation engine
        method = self.config["recommendation"]["method"]
        if method == "baseline":
            recommendations = self.run_baseline_recommendation(objects)
        elif method == "ml":
            recommendations = self.run_ml_recommendation(objects)
        else:  # both
            self.run_baseline_recommendation(objects)
            recommendations = self.run_ml_recommendation(objects)
        
        # Step 3: Generate cost history and forecast
        cost_history = self.generate_cost_history(objects)
        forecast_data = self.run_forecasting(cost_history)
        
        # Step 4: Estimate savings
        self.run_savings_estimation(objects, recommendations)
        
        # Step 5: Evaluation
        self.run_evaluation(objects, recommendations, forecast_data)
        
        print(f"\n{'='*60}")
        print("Experiment complete!")
        print(f"{'='*60}\n")
        
        return self.results
    
    def save_results(self, output_path: str):
        """Save results to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run S3 Predictive Cost Optimization experiment"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to experiment configuration YAML"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to save results JSON"
    )
    
    args = parser.parse_args()
    
    # Run experiment
    runner = ExperimentRunner(args.config)
    results = runner.run()
    runner.save_results(args.output)
    
    # Print summary
    if "evaluation" in results:
        eval_results = results["evaluation"]
        
        print("\n=== SUMMARY ===")
        
        if "classification" in eval_results:
            print(f"\nAllocation Accuracy: {eval_results['classification']['accuracy']:.2%}")
            print(f"Precision: {eval_results['classification']['precision']:.2%}")
            print(f"Recall: {eval_results['classification']['recall']:.2%}")
            print(f"F1-Score: {eval_results['classification']['f1_score']:.2%}")
        
        if "forecasting" in eval_results and eval_results["forecasting"]:
            fc = eval_results["forecasting"]
            print(f"\nForecast MAPE: {fc['mape']:.2f}%")
            print(f"Naive MAPE: {fc['naive_mape']:.2f}%")
            print(f"Beats Naive Baseline: {fc['beats_naive']}")
        
        if "savings" in results:
            sav = results["savings"]["our_approach"]
            print(f"\nCost Savings: ${sav['total_savings_usd_monthly']:.2f}/month")
            print(f"Savings Percent: {sav['total_savings_percent']:.1f}%")


if __name__ == "__main__":
    main()
