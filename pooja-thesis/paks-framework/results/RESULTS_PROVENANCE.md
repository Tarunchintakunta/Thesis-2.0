# Results provenance — Pooja PAKS

**Status:** NOT COMPLETE. No live Kubernetes. No AWS EC2/S3/CloudWatch deploy.

## Formal (this driver)
- Dataset meta: `{'dataset': 'gct2010', 'family': 'gct', 'proxy': False, 'evidence': 'TRACE', 'generation': 'Google Cluster Data v1 (2010, ~7h)', 'residual': 'GCT 2011/2019 and Alibaba still absent (DATA_GAPS.md)', 'note': 'Public CC-BY 7-hour GCT sample; not the 29-day 2011 or 2019 traces.', 'cluster_csv': 'gct2010_cluster_cpu.csv', 'jobs_csv': 'gct2010_job_cpu_series.csv.gz', 'n_steps': 75, 'bin_seconds': 300, 'dropped_zero_tail': True}`
- Prediction CSV: `formal_prediction_metrics.csv`
  - Job-split LSTM MAE/RMSE is **TRACE** (GCT v1, held-out jobs).
  - Honesty: last-value **persistence MAE is lower** than LSTM on job windows
    (many jobs are near-constant). Cluster-aggregate LSTM vs persistence is the
    scaling-relevant series but **n_test is small** (~19 bins). Neither result
    is GCT 2011/2019 or Alibaba.
- Scaling CSV: `formal_scaling_metrics.csv` — util / response / throughput / cost / SLA /
  scaling latency are **SIMULATED** (capacity mapping, M/M/1-style queue proxy,
  assumed $0.04/pod-hour). `live_k8s=false`, `live_cloudwatch=false`.
- K8s: dry-run `PATCH .../scale?dryRun=All` recorded in `formal_k8s_dry_run.json`.

## Proxy (do not mix)
- `results_summary.csv` / `results_per_seed.csv` = NimbusGuard-framed MLP on synthetic sine/spikes.
- See `PROXY_NIMBUSGUARD.md` and `src/proxy/README.md`.

