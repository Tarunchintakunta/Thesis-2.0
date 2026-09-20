#!/usr/bin/env python3
"""
Run centralised IDS comparator on the same data path as FL arms.
"""
import json
import os
import pickle
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.centralised.centralised_ids import CentralisedIDS


def run_centralised_experiment(
    data_path: str = "data/UNSW_NB15_training-set.csv",
    sample_size: int = 10000,
    epochs: int = 30,
    out_dir: str = "results/centralised",
):
    """Train centralised CNN and write summary JSON."""
    print("=" * 70)
    print("Centralised IDS Comparator (CA2 traditional baseline)")
    print("=" * 70)

    config = {
        "mode": "centralised",
        "epochs": epochs,
        "learning_rate": 0.001,
        "batch_size": 64,
        "sample_size": sample_size,
        "data_path": data_path,
        "model": "cnn",
    }
    print(f"Configuration: {config}\n")

    trainer = CentralisedIDS()
    trainer.setup(data_path=data_path, sample_size=sample_size)
    history = trainer.train(
        epochs=config["epochs"],
        learning_rate=config["learning_rate"],
        batch_size=config["batch_size"],
    )
    summary = trainer.get_results_summary()

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(out_dir, "history.pkl"), "wb") as f:
        pickle.dump(history, f)

    print("\n" + "=" * 70)
    print("CENTRALISED RESULTS")
    print("=" * 70)
    for key, value in summary.items():
        print(f"{key:<30}: {value}")
    print(f"\nResults saved to: {out_dir}/")
    print("=" * 70)
    return summary


if __name__ == "__main__":
    run_centralised_experiment()
