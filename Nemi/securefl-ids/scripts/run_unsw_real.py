#!/usr/bin/env python3
"""
Run a documented real-UNSW experiment (stratified sample of the training partition).

Does NOT overwrite the locked synthetic PoC at results/comparison/results.json.
Writes evidence under results/unsw_real/.
"""
import json
import os
import pickle
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.baseline.baseline_fl_ids import BaselineFLIDS
from src.centralised.centralised_ids import CentralisedIDS
from src.improved.securefl_ids import SecureFLIDS


def _load_provenance():
    path = "data/DATA_PROVENANCE.json"
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} missing — run: python scripts/download_data.py --real"
        )
    with open(path) as f:
        prov = json.load(f)
    if prov.get("kind") != "real":
        raise RuntimeError(
            f"DATA_PROVENANCE kind={prov.get('kind')!r}; need kind='real' "
            "before claiming a real-UNSW run."
        )
    return prov


def run_unsw_real(
    sample_size: int = 25000,
    num_rounds: int = 30,
    epochs_central: int = 30,
):
    print("=" * 70)
    print("Real UNSW-NB15 experiment (stratified sample of training partition)")
    print("=" * 70)

    provenance = _load_provenance()
    data_path = provenance.get("local_path", "data/UNSW_NB15_training-set.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(data_path)

    config = {
        "dataset_kind": "real_unsw_nb15_training_partition",
        "data_path": data_path,
        "sample_size": sample_size,
        "num_clients": 5,
        "num_rounds": num_rounds,
        "epochs_centralised": epochs_central,
        "local_epochs": 1,
        "learning_rate": 0.001,
        "note": (
            "Stratified sample of the official training-set CSV — not the full "
            "2.5M-flow corpus and not a 50-round full-feature campaign."
        ),
        "provenance": provenance,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(f"Configuration: sample_size={sample_size}, rounds={num_rounds}\n")

    results = {}

    # Centralised
    print("\n[1/3] Centralised IDS...")
    print("-" * 70)
    central = CentralisedIDS()
    central.setup(data_path=data_path, sample_size=sample_size)
    central.train(epochs=epochs_central, learning_rate=config["learning_rate"])
    results["centralised"] = central.get_results_summary()

    # FL baseline
    print("\n[2/3] Federated baseline (Saklani-style)...")
    print("-" * 70)
    baseline = BaselineFLIDS(num_clients=config["num_clients"])
    baseline.setup(data_path=data_path, sample_size=sample_size)
    baseline.train(
        num_rounds=num_rounds,
        local_epochs=config["local_epochs"],
        learning_rate=config["learning_rate"],
    )
    results["baseline_fl"] = baseline.get_results_summary()

    # Improved FL
    print("\n[3/3] SecureFL-IDS improved...")
    print("-" * 70)
    improved = SecureFLIDS(
        num_clients=config["num_clients"],
        communication_efficient=True,
        compression_ratio=0.5,
    )
    improved.setup(data_path=data_path, sample_size=sample_size)
    improved.train(
        num_rounds=num_rounds,
        local_epochs=config["local_epochs"],
        learning_rate=config["learning_rate"],
    )
    results["improved_fl"] = improved.get_results_summary()

    config["finished_at_utc"] = datetime.now(timezone.utc).isoformat()

    out_dir = "results/unsw_real"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)
    with open(os.path.join(out_dir, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    with open(os.path.join(out_dir, "history_centralised.pkl"), "wb") as f:
        pickle.dump(central.history, f)
    with open(os.path.join(out_dir, "history_baseline.pkl"), "wb") as f:
        pickle.dump(baseline.history, f)
    with open(os.path.join(out_dir, "history_improved.pkl"), "wb") as f:
        pickle.dump(improved.history, f)

    print("\n" + "=" * 70)
    print("REAL UNSW RESULTS (stratified sample)")
    print("=" * 70)
    for arm, summary in results.items():
        print(
            f"{arm:<16} acc={summary['accuracy']:.4f} "
            f"f1={summary['f1_score']:.4f} "
            f"comm={summary['avg_communication_cost']:.2f} MB"
        )
    print(f"\nSaved under {out_dir}/ (synthetic PoC JSON left unchanged).")
    print("=" * 70)
    return results


if __name__ == "__main__":
    run_unsw_real()
