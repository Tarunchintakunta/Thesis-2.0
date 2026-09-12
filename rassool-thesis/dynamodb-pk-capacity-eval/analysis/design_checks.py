"""Design-time checks worked out from the workload definition and AWS's documented limits.

These are **predictions from arithmetic, not measurements**:

* capacity plan - RCU/WCU each key design needs at the base rate, which sizes
  the provisioned (C2) tables and their auto-scaling bounds
* hot-key load - units per second on the hottest partition-key value, compared
  with the documented per-partition maximum (3,000 RCU / 1,000 WCU per second)

    python analysis/design_checks.py            # writes analysis/design_checks/*.csv + .md
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from workloads.generator import keys  # noqa: E402
from workloads.generator.profiles import PROFILES  # noqa: E402
from workloads.generator.zipf import Zipf  # noqa: E402

PER_PARTITION_RCU = 3000  # AWS DynamoDB developer guide, partition throughput limits
PER_PARTITION_WCU = 1000


def load_config(path=ROOT / "config/experiment.yaml") -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def rcu_per_read(item_kb: float, consistency: str, design: str, shards: int) -> float:
    units = math.ceil(item_kb / 4) * (0.5 if consistency == "eventual" else 1.0)
    # K3 reads every shard key; a missing item still costs the minimum read unit
    if design == "K3":
        return units * shards
    # For K4, average read cost is weighted: 90% of traffic on top 10% (hot, 10 shards)
    # But wait, capacity plan is based on worst case or average? Average required RCU/s.
    if design == "K4":
        # Hot items (top 1000) take ~ 50% of traffic, cost is N=10. Rest cost N=1.
        # This is a simplification for capacity planning.
        return units * (0.50 * shards + 0.50 * 1)
    return units

def wcu_per_write(item_kb: float) -> float:
    return float(math.ceil(item_kb))

def capacity_plan(cfg: dict) -> pd.DataFrame:
    prov, kb, shards = cfg["provisioned"], cfg["dataset"]["item_size_kb"], cfg["k3_shards"]
    rows = []
    for d in keys.DESIGNS:
        need_r = need_w = 0.0
        for w in prov["sizing_profiles"]:
            p = PROFILES[w]
            base_rate = p["cycle"][0][0]
            need_r = max(need_r, base_rate * p["read_fraction"] * rcu_per_read(kb, cfg["consistency"], d, shards))
            need_w = max(need_w, base_rate * (1 - p["read_fraction"]) * wcu_per_write(kb))
        t = prov["target_utilisation"] / 100
        rmin = int(math.ceil(need_r / t / 10) * 10)
        wmin = int(math.ceil(need_w / t / 10) * 10)
        rows.append({"key_design": d, "read_need_rcu_s": need_r, "write_need_wcu_s": need_w,
                     "read_min": rmin, "read_max": rmin * prov["max_multiplier"],
                     "write_min": wmin, "write_max": wmin * prov["max_multiplier"]})
    return pd.DataFrame(rows)

def hottest_shares(z: Zipf, n_shards: int) -> dict:
    pmf = np.diff(np.concatenate([[0.0], z.cdf]))
    by_order = np.empty(z.n)
    by_order[z.perm] = pmf  # probability of each order index
    cust = np.array([(i * 7919 + 13) % keys.N_CUSTOMERS for i in range(z.n)])
    by_customer = np.bincount(cust, weights=by_order, minlength=keys.N_CUSTOMERS)
    return {"order": float(by_order.max()), "customer": float(by_customer.max()), "shards": n_shards}

def hot_key_load(cfg: dict, z: Zipf, item_sizes=(1, 8, 32)) -> pd.DataFrame:
    sh = hottest_shares(z, cfg["k3_shards"])
    rows = []
    for d in keys.DESIGNS:
        for w, p in PROFILES.items():
            for kb in item_sizes:
                peak = max(r for r, _ in p["cycle"])
                share = sh["customer"] if d == "K2" else sh["order"]
                reads = peak * p["read_fraction"] * share
                writes = peak * (1 - p["read_fraction"]) * share
                # K3/K4: hottest key is spread. K4 spreads hot keys identical to K3.
                w_units = writes * wcu_per_write(kb) / (sh["shards"] if d in ("K3", "K4") else 1)

                # For capacity checking, r_units of the hottest key:
                if d in ("K3", "K4"):
                    r_units = reads * math.ceil(kb / 4) * (0.5 if cfg["consistency"] == "eventual" else 1)
                else:
                    r_units = reads * math.ceil(kb / 4) * (0.5 if cfg["consistency"] == "eventual" else 1)
                rows.append({"key_design": d, "workload": w, "item_kb": kb, "peak_ops_s": peak,
                             "hottest_key_share": share, "hot_key_rcu_s": r_units, "hot_key_wcu_s": w_units,
                             "over_partition_limit": bool(r_units > PER_PARTITION_RCU or w_units > PER_PARTITION_WCU)})
    return pd.DataFrame(rows)


def md_table(df: pd.DataFrame) -> str:
    """Small markdown table writer (keeps `tabulate` out of the dependencies)."""
    def fmt(v):
        return f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "---|" * len(df.columns)
    body = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def main() -> int:
    cfg = load_config()
    out = ROOT / "analysis/design_checks"
    out.mkdir(parents=True, exist_ok=True)
    cap = capacity_plan(cfg)
    z = Zipf(cfg["dataset"]["orders"], cfg["zipf"]["s"], cfg["zipf"]["perm_seed"])
    hot = hot_key_load(cfg, z)
    cap.to_csv(out / "capacity_plan.csv", index=False)
    hot.to_csv(out / "hot_key_load.csv", index=False)
    over = hot[hot["over_partition_limit"]]
    lines = ["# Design checks (arithmetic predictions, not measurements)", "",
             f"Zipf s = {cfg['zipf']['s']} over {z.n:,} orders: hottest 10% of keys get {z.top_share():.1%} of operations; "
             f"the single hottest order gets {z.p(0):.2%}, the hottest customer {hottest_shares(z, 10)['customer']:.2%}.", "",
             "## Provisioned capacity plan (C2)", "", md_table(cap), "",
             "## Hot partition-key load at the profile's peak rate", "",
             f"{len(over)} of {len(hot)} design x workload x item-size cases would pass the documented per-partition "
             f"limit ({PER_PARTITION_RCU} RCU/s, {PER_PARTITION_WCU} WCU/s):", "",
             md_table(over[["key_design", "workload", "item_kb", "hot_key_rcu_s", "hot_key_wcu_s"]])
             if len(over) else "none", ""]
    (out / "README.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
