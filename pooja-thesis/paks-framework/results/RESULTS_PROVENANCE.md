# Results provenance — Pooja PAKS

**Status:** NOT COMPLETE. No live Kubernetes. No AWS EC2/S3/CloudWatch deploy.

## Formal (this driver)
- Dataset meta: `{'dataset': 'gct2011', 'family': 'gct', 'proxy': False, 'evidence': 'TRACE', 'generation': 'GCT 2011 task_usage part-00000-of-00500 (single shard sample)', 'residual': 'Full 500-part 29-day dump and GCT 2019 still absent; Alibaba is a separate --dataset.', 'note': 'One public GCS shard (~87 MiB), SHA256-verified; not the full 29-day cell.', 'cluster_csv': 'gct2011_part00000_cluster_cpu.csv', 'jobs_csv': 'gct2011_part00000_job_cpu_series.csv.gz', 'files': ['/Users/valletivarish/Documents/Thesis-2.0/pooja-thesis/paks-framework/data/gct/2011/task_usage/part-00000-of-00500.csv.gz'], 'n_steps': 17, 'bin_seconds': 300, 'dropped_zero_tail': False, 'scale_dataset': 'alibaba', 'scale_family': 'alibaba', 'scale_proxy': False, 'scale_evidence': 'TRACE', 'scale_generation': 'Alibaba cluster-trace-v2018 machine_usage RANGE sample (first 64 MiB of tar.gz)', 'scale_residual': 'Full 1.7 GiB machine_usage.tar.gz not downloaded; GCT 2019 still absent.', 'scale_note': 'Public OSS range sample, SHA256-verified; resampled to 300s mean CPU. Scaling loop uses Alibaba RANGE sample (CPU%×10 demand units) because primary GCT cluster bins were too few.', 'scale_cluster_csv': 'alibaba_v2018_machine_usage_sample_cluster_cpu.csv', 'scale_files': ['/Users/valletivarish/Documents/Thesis-2.0/pooja-thesis/paks-framework/data/alibaba/v2018/machine_usage.tar.gz.partial64m', '/Users/valletivarish/Documents/Thesis-2.0/pooja-thesis/paks-framework/data/alibaba/v2018/machine_usage.tar.gz.partial64m.sha256'], 'scale_sample_kind': 'HTTP_RANGE_64MiB', 'scale_n_steps': 300, 'scale_bin_seconds': 300, 'scale_dropped_zero_tail': False, 'scale_scaled_from_pct': True, 'scale_demand_scale': 10.0, 'pred_dataset': 'gct2011'}`
- Prediction CSV: `formal_prediction_metrics.csv`
  - Job-split LSTM MAE/RMSE is **TRACE** when GCT 2010/2011 job series are used.
  - Alibaba cluster LSTM (if present) is **TRACE** on a **64 MiB HTTP RANGE**
    sample of `machine_usage.tar.gz` (not the full 1.7 GiB dump).
  - GCT 2011 evidence here is **one** public `task_usage` shard
    (`part-00000-of-00500`), SHA256-verified — not the full 29-day cell.
- Scaling CSV: `formal_scaling_metrics.csv` — util / response / throughput / cost / SLA /
  scaling latency are **SIMULATED** (capacity mapping, M/M/1-style queue proxy,
  assumed $0.04/pod-hour). `live_k8s=false`, `live_cloudwatch=false`.
- K8s: dry-run `PATCH .../scale?dryRun=All` recorded in `formal_k8s_dry_run.json`.
- Local kind/minikube: see `results/K8S_LOCAL_PROBE.md` (Docker daemon / kind absent
  on this host → live apply still unmet).

## Proxy (do not mix)
- `results_summary.csv` / `results_per_seed.csv` = NimbusGuard-framed MLP on synthetic sine/spikes.
- See `PROXY_NIMBUSGUARD.md` and `src/proxy/README.md`.

