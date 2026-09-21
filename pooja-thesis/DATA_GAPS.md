# Exact missing datasets — Pooja formal CA2 (PAKS)

**Binding CA2:** `Pooja_25120921_CA2.docx` (formal PAKS)  
**Required datasets:** Google Cluster Trace **and/or** Alibaba Cluster Trace, used to train a workload **LSTM** (TensorFlow named in the CA2 resources table).  
**AWS / K8s:** Formal method is a Kubernetes cluster on **AWS EC2 + S3 + CloudWatch**. **Not deployed this pass.**

## What is present

| Artefact | Path | Role |
|----------|------|------|
| Google Cluster Data **v1** (2010, ~7 h Borg cell, CC-BY) | download: `paks-framework/data/raw/google-cluster-data-1.csv.gz` (gitignored, 30 MiB) | Canonical public GCT family member; SHA1 `98c87f059aa1cc37f1e9523ac691ee0fd5629188` |
| Derived GCT v1 cluster / job series | `paks-framework/data/traces/gct2010_*.csv*` | LSTM + scaling (TRACE) |
| **GCT 2011** `task_usage` **part-00000-of-00500** | `data/gct/2011/task_usage/` (gitignored raw); SHA256 `841254d3…ed1c6e28` | One public shard (~87 MiB); **not** full 29-day cell |
| Derived GCT 2011 series | `data/traces/gct2011_part00000_*.csv*` | Job-window LSTM (TRACE); cluster bins short (17) |
| **Alibaba v2018** `machine_usage` **64 MiB HTTP RANGE** sample | `data/alibaba/v2018/machine_usage.tar.gz.partial64m` (gitignored); SHA256 `49396e44…192f378` | Public OSS range sample; **not** full 1.7 GiB dump |
| Alibaba `machine_meta.tar.gz` | same dir; SHA256 `b5b1b786…c8f6d55` | Meta only |
| Derived Alibaba cluster series | `data/traces/alibaba_v2018_machine_usage_sample_cluster_cpu.csv` | Cluster LSTM + scaling loop (TRACE sample) |
| Provenance / SHA index | `data/traces/PROVENANCE.md`, `SAMPLE_SHA256.txt` | License, URLs, aggregation rules |

Fetch scripts: `scripts/fetch_public_trace_slice.py` (v1), `scripts/fetch_extended_trace_samples.py` (2011 + Alibaba range).

## Still missing (fail-closed if requested without samples)

### Google Cluster Data 2011 — remaining parts / full cell

Canonical: https://github.com/google/cluster-data (`ClusterData2011_2.md`)  
Bucket: `gs://clusterdata-2011-2` / `https://storage.googleapis.com/clusterdata-2011-2/`

| Expected local path | Role |
|---------------------|------|
| `paks-framework/data/gct/2011/task_usage/part-*-of-*.csv.gz` | Full CPU/memory usage (only `part-00000` present) |
| `paks-framework/data/gct/2011/task_events/part-*-of-*.csv.gz` | Optional lifecycle context |

`--dataset gct2011` succeeds when derived series from part-00000 exist; **do not claim full 29-day coverage**.

### Google Borg traces 2019

Canonical: https://github.com/google/cluster-data (`ClusterData2019.md`)

| Expected local path | Role |
|---------------------|------|
| `paks-framework/data/gct/2019/<cell>/instance_usage/*` | Usage time series |
| `paks-framework/data/gct/2019/<cell>/instance_events/*` | Optional events |

`--dataset gct2019` fail-closed.

### Alibaba Cluster Trace — full dumps

Canonical: https://github.com/alibaba/clusterdata  

| Expected local path | Role |
|---------------------|------|
| Full `machine_usage.tar.gz` (~1.7 GiB) | Complete machine CPU/memory |
| `container_usage` / `batch_task` / etc. | Optional |

`--dataset alibaba` succeeds on the **RANGE sample** derived series; provenance must say `HTTP_RANGE_64MiB`.

## TensorFlow runtime

Formal CA2 resources name **TensorFlow** for the LSTM. This evaluation host may lack a TF wheel (seen on CPython 3.14). The artefact trains a **vanilla LSTM (NumPy, BPTT)**. `--backend tensorflow` raises `ImportError` (fail-closed) rather than silently substituting MLP.

MLP `MLPRegressor` remains only on the **proxy** path (`src/proxy/`).

## Synthetic / NimbusGuard simulator

`src/data/workload_simulator.py` is **PROXY**. It must not be used as a silent fallback when `--dataset gct*`, `--dataset alibaba`, or `--dataset gct` is requested.

## Loader contract

`paks-framework/src/data/trace_loader.py`:

- `--dataset gct2010` / default formal slice: load committed derived series (or re-aggregate from SHA1-verified raw gzip).
- `--dataset gct`: prefer 2011 derived sample if present, else 2019, else 2010.
- `--dataset gct2011` / `alibaba`: load derived series when ready; else raise with this checklist.
- `--dataset gct2019`: **raise** until files exist.
- `--dataset synthetic`: explicit proxy only; `meta["proxy"]=True`.

## Not a substitute for live K8s-on-AWS

Dry-run `apps/v1` Scale patches and simulated util/latency/cost **do not** close the formal AWS EC2+S3+CloudWatch Kubernetes experiment. Local kind/minikube were **unavailable** this pass (`results/K8S_LOCAL_PROBE.md`).
