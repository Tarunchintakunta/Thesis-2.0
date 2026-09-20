# Configuration Manual — Venkat Bora (25164414)

**Artefact:** `venkat-bora-thesis/distributed-matrix-scaling/`  
**Scope:** Local reproduction only. **AWS EC2 is not configured or executed** in this deliverable.

## 1. Purpose

This manual documents how to install, configure, run, and verify the local matrix-scaling benchmark harness. It does **not** provide live cloud credentials, Terraform/CloudFormation stacks, or measured EC2 results.

## 2. Prerequisites

- Python 3.12+
- `pip` / `venv`
- macOS or Linux (developed on Ubuntu-class / Darwin environments)
- Optional: `make`

## 3. Install (local)

```bash
cd venkat-bora-thesis/distributed-matrix-scaling
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# or: make install
```

## 4. Environment controls

For fair threading comparisons, pin BLAS/OpenMP internal threads (as in methodology):

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

## 5. Run tests

```bash
make test
# or: pytest tests/ -v --timeout=60
```

Expected: **20** `test_*` functions (11 + 9) under `tests/`.

## 6. Run benchmarks (local Dask)

```bash
make quick-test    # subset
make benchmark     # full local suite (long)
```

Distributed mode uses Dask **`LocalCluster` on one machine**. This is **not** multi-instance AWS EC2 and does **not** satisfy CA2 matched-vCPU cloud execution.

### CLI note

`src/main.py` does **not** currently expose `--scheduler-address`. Older docs that claim remote-scheduler CLI wiring are incorrect for this tree. Remote multi-node runs require code changes plus provisioned hosts; neither is delivered here.

## 7. Outputs

| Path | Contents |
|------|----------|
| `results/data/benchmark_results.json` / `.csv` | Per-iteration raw metrics |
| `results/data/summary_statistics.json` | Mean/std per config; **`n_iterations: 3`** |
| `results/figures/*.png` | Evaluation plots |

Authoritative numbers for the report are those in `summary_statistics.json`.

## 8. Visualizations

```bash
make visualize
# or: python src/visualize_results.py
```

## 9. What is intentionally absent

- AWS credentials / account setup
- EC2 instance launch / destroy IaC
- CloudWatch dashboards / spend reports
- Implemented Shapiro / t-test / Holm pipelines (methodology describes them; code does not ship them)
- Fabricated multi-node timings

## 10. CA2 residual

To close the cloud half of the CA2 research question, a future campaign must:

1. Provision matched aggregate vCPU EC2 topologies
2. Run multi-threaded on one instance vs distributed across instances with the same total cores
3. Replace LocalCluster evidence with that campaign’s metrics

Until then, treat all published numbers as **local proxy evidence only**.
