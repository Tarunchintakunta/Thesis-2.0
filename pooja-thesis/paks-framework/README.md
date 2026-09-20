# PAKS — Predictive Adaptive Kubernetes Scaling (formal CA2)

Binding research contract: `../CA2_COMMITMENTS.md` (formal `Pooja_25120921_CA2.docx`).

**Research question:** Can predictive workload forecasting plus adaptive Kubernetes
scaling (PAKS) improve cloud resource management under dynamic workloads versus
traditional **reactive Kubernetes HPA**?

This artefact is **NOT COMPLETE**. No live AWS EC2/S3/CloudWatch Kubernetes
cluster is deployed in this pass.

## What is formal vs proxy

| Path | Role |
|------|------|
| `scripts/train_lstm_and_evaluate.py` | **Formal driver** — LSTM on GCT-derived series + dry-run K8s Scale vs HPA |
| `src/models/lstm_predictor.py` | Vanilla LSTM (NumPy BPTT). `--backend tensorflow` **fail-closed** (no TF on CPython 3.14) |
| `src/data/trace_loader.py` | GCT/Alibaba loader; **no synthetic fallback** for `gct*` / `alibaba` |
| `data/traces/` | Public **Google Cluster Data v1 (2010, CC-BY)** derived series + `PROVENANCE.md` |
| `src/k8s/` | Adaptive engine emitting `autoscaling/v2` HPA schema + `apps/v1` Scale PATCH (`dryRun=All`) |
| `src/eval/metrics.py` | MAE/RMSE, util, response, throughput, scaling latency, cost, SLA — tagged SIMULATED vs TRACE |
| `src/proxy/` + `scripts/train_and_evaluate.py` | **PROXY** NimbusGuard-framed MLP on synthetic sine/spikes. Not binding CA2. |
| `src/lambda_handler/` + `template.yaml` | **PROXY / unused** Kinesis+Lambda SAM. Formal AWS method is K8s on EC2, not this. |

NimbusGuard (Wanigasooriya & Ekanayake, 2026) is **related literature**, not the
binding CA2 baseline. The binding baseline is **Kubernetes HPA**.

## Dataset

A 7-hour Google Cluster Data v1 sample was fetched and SHA1-verified
(`98c87f059aa1cc37f1e9523ac691ee0fd5629188`). Cluster CPU (76 × 5 min bins) and
per-job series are committed under `data/traces/`. **GCT 2011, Borg 2019, and
Alibaba remain absent** — `--dataset gct2011|gct2019|alibaba` raises
`FileNotFoundError` (`../DATA_GAPS.md`).

Re-fetch / re-aggregate:

```bash
python scripts/fetch_public_trace_slice.py
```

## Usage

```bash
pip install -r requirements.txt
# formal (GCT v1 slice + LSTM + K8s dry-run vs HPA)
python scripts/train_lstm_and_evaluate.py --dataset gct2010
# fail-closed examples
python scripts/train_lstm_and_evaluate.py --dataset alibaba   # exits 2
python scripts/train_lstm_and_evaluate.py --backend tensorflow  # exits 3 without TF
# proxy (not formal evidence)
python scripts/train_and_evaluate.py
pytest tests/ -v
```

## Evidence honesty

| Metric | This pass |
|--------|-----------|
| LSTM MAE / RMSE on GCT v1 job windows | **TRACE** (public GCT sample, not 2011/2019, not Alibaba) |
| CPU util, response, throughput, cost, SLA, scaling latency | **SIMULATED** (capacity mapping / queue proxy / assumed $/pod-hour) |
| K8s Scale / HPA objects | **Dry-run JSON** — no kubelet, no kind/minikube apply |
| CloudWatch / EC2 / S3 | **Not collected** |

Proxy CSVs (`results/results_*.csv`) answer a stability trade-off on synthetic
load only. See `results/RESULTS_PROVENANCE.md`.
