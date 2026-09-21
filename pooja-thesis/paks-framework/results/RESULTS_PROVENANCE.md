# Results provenance — Pooja PAKS

**Status:** Formal AWS + live K8s method **closed** this pass (Free-Tier k3s,
destroy-after). Full GCT/Alibaba dumps still absent. **NOT** submission-ready 100%.

## Formal — live AWS k3s (2026-09-21)

- Stack: 1× `t3.micro` AL2023 + **k3s** (not EKS), S3 bucket, CloudWatch log group
  + custom metrics namespace `PAKS/LiveK8s`, tags `project=paks-k8s-live`.
- Orchestrator: `scripts/run_live_aws_k8s.py` (SSM); on-node: `scripts/live_scale_on_node.py`.
- Evidence JSON: `formal_k8s_live_aws.json` — `live_apply=true`, `aws_deployed=true`.
- Scaling latency: **LIVE** (kubectl scale → readyReplicas).
- Util / response / throughput / cost / SLA: still capacity-model **SIMULATED**
  (live replica count capped at 3 on t3.micro).
- Destroy: `aws_destroy_verify.json` — Pooja leftovers empty. Terraform state only
  contained `paks-k8s-live` resources.

## Formal — offline TRACE / dry-run (prior)

- Dataset meta: GCT 2011 part-00000 + Alibaba 64 MiB RANGE (see `data/traces/PROVENANCE.md`).
- Prediction CSV: `formal_prediction_metrics.csv`
  - Job-split LSTM MAE/RMSE is **TRACE** when GCT 2010/2011 job series are used.
  - Alibaba cluster LSTM is **TRACE** on a **64 MiB HTTP RANGE** sample (not full 1.7 GiB).
  - GCT 2011 evidence is **one** public `task_usage` shard — not the full 29-day cell.
- Scaling CSV: `formal_scaling_metrics.csv` — util / response / throughput / cost / SLA /
  scaling latency **SIMULATED**; `live_k8s=false` in that CSV (superseded for latency by live JSON).
- K8s dry-run: `formal_k8s_dry_run.json` (`dryRun=All`).
- Local kind/minikube: `K8S_LOCAL_PROBE.md` (Docker daemon / kind absent on laptop).

## Proxy (do not mix)

- `results_summary.csv` / `results_per_seed.csv` = NimbusGuard-framed MLP on synthetic sine/spikes.
- See `PROXY_NIMBUSGUARD.md` and `src/proxy/README.md`.
