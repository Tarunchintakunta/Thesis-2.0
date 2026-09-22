# GENAI_HANDOFF.md — Pooja (PAKS)

Evidence-only. Unknown/incomplete marked explicitly. No invented metrics.
**Kasi excluded.** Artefact-only paths under `pooja-thesis/paks-framework/` (plus binding CA2 docs cited by path).
Do **not** use `results/live/archive/invalidated_pre_causal_hpa_*` as CA2 evidence.

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Pooja |
| Student ID | 25120921 |
| Programme | MSc Cloud Computing Research Project (formal CA2: `Pooja_25120921_CA2.docx`) |
| Artefact root | `pooja-thesis/paks-framework/` |
| Honest CA2 floor | **PARTIAL (~62)** — independent review 2026-09-22; prior STATUS/CA2 “100%” **REJECTED** |
| Eval completeness | **3 causal lite live AWS finals done** (`results/live/final_1\|2\|3/`) under causal HPA artefact; **not** full multi-intensity / multi-node / billing-linked campaign |
| AWS | Applied then destroyed — Free-Tier 1× `t3.micro` + k3s, `project=paks-k8s-live`, `destroy_confirmed=true` ×3 |
| Handoff date | 2026-09-22 |
| Authority | `../CA2_COMMITMENTS.md`, `../STATUS.md`, `_analysis_extract/reports/INDEPENDENT_REVIEW_POOJA.md`, `results/live/FINAL3_BASELINE.md`, on-disk `results/live/final_{1,2,3}/` |

## 1. Research problem, motivation, research question, and objectives

**Problem:** Reactive Kubernetes Horizontal Pod Autoscaler (HPA) scales after utilisation crosses thresholds; under dynamic cloud workloads this can lag demand and waste capacity.

**Motivation:** Predictive workload forecasting plus adaptive Scale decisions (PAKS) may improve management of utilisation, latency, and cost versus traditional HPA alone.

**RQ (formal CA2 / STATUS):** Effect of PAKS vs **traditional Kubernetes HPA** on prediction accuracy, utilisation, response time, scaling latency, and infrastructure cost (GCT + Alibaba; LSTM; AWS EC2 Kubernetes).

**Objectives (must evidence — from `CA2_COMMITMENTS.md`):**
1. Preprocess public cloud workload data (Google Cluster Trace / Alibaba Cluster Trace) and train a workload prediction model (LSTM / TensorFlow per resources table).
2. Build an adaptive scaling engine that acts on predictions via the Kubernetes API (not HPA-default alone).
3. Implement/evaluate on a Kubernetes cluster hosted on AWS (EC2 compute, S3 datasets, CloudWatch metrics; Prometheus/Grafana optional).
4. Compare PAKS vs reactive HPA across varied workload intensities (low/moderate/high/burst).

## 2. Identified literature gap and how this research addresses it

**Gap (CA2 framing):** Predictive autoscaling vs reactive HPA on real cluster-trace workloads and live Kubernetes — not synthetic-only proxy trade-offs.

**How addressed (evidence-bound):**
- TRACE LSTM on disclosed GCT 2011 job-window series + Alibaba v2018 64 MiB RANGE sample (`formal_prediction_metrics.csv`, `data/traces/PROVENANCE.md`).
- Live comparison of **traditional HPA controller observe** vs **PAKS Scale PATCH** on AWS k3s (`LIVE-CONTROLLER-HPA` vs `LIVE`).
- Related work NimbusGuard (DQN+LSTM) is **literature only**; binding baseline is Kubernetes HPA (`baseline_papers/BASELINE_PAPER.md`). Prior NimbusGuard-proxy synthetic path is **superseded** (`src/proxy/`, `results/PROXY_NIMBUSGUARD.md`).

This handoff does **not** restate the full CA2 literature review; successor should read `Pooja_25120921_CA2.docx` for citation depth.

## 3. CA2 proposal alignment and any extensions beyond the proposal

**Aligned (partial):**
- GCT/Alibaba-derived TRACE prediction + NumPy LSTM.
- Adaptive K8s Scale engine + real HPA baseline object/controller path.
- AWS EC2 + S3 + CloudWatch Free-Tier method with destroy-after.
- Metric harness: MAE/RMSE, util, response, throughput, scaling latency, cost, SLA (many util/SLA/cost fields tagged SIMULATED).

**Beyond / incomplete vs proposal:**
- TensorFlow LSTM named in CA2 resources table → **NumPy BPTT only**; `--backend tensorflow` fail-closed (`DATA_GAPS.md`).
- Memory prediction → **claimed-only** (`mem_util_mean: null` in live packs).
- Multi-intensity low/moderate/high/burst suite → **not demonstrated** (lite n=12 steps, max_replicas=4, single-node).
- Billing-linked cost → **SIMULATED** `$0.04`/pod-hour assumption.
- Full GCT 2011 cell / full Alibaba 1.7 GiB dumps → samples only (`DESIGN_RATIONALE_BEYOND_CA2.md`).

**Prior floor error (withdrawn):** Scripted HPA Scale PATCH + metrics-server disabled + `pause` image + ceiling theatre — packs archived as **INVALIDATED** (`results/live/archive/invalidated_pre_causal_hpa_*`).

## 4. Research methodology and experimental design

1. **Offline TRACE prediction:** Train vanilla LSTM (NumPy, lookback=12, hidden=16) on GCT 2011 held-out job windows and Alibaba cluster CPU bins; compare to persistence MAE/RMSE (`scripts/train_lstm_and_evaluate.py`, `formal_prediction_metrics.csv`).
2. **Dry-run K8s path (retained):** Adaptive engine emits Scale / HPA-schema bodies with `dryRun=All` (`formal_k8s_dry_run.json`) — not the authoritative live latency source.
3. **Live AWS causal lite campaign (authoritative for HPA vs PAKS):**  
   - 1× `t3.micro` AL2023 + single-node **k3s** (not EKS).  
   - metrics-server enabled; busybox CPU burn Deployment; real `HorizontalPodAutoscaler`.  
   - Baseline arm: `run_controller_hpa_k8s` **OBSERVE** controller (`evidence=LIVE-CONTROLLER-HPA`) — no Scale PATCH on HPA arm.  
   - Proposed arm: PAKS adaptive Scale PATCH (`evidence=LIVE`).  
   - Protocol: steps=12; lookback=3; max_replicas_live=4; seeds 41/42/43; destroy-after.  
   - Orchestrator: `scripts/run_live_aws_k8s.py` (SSM) + `scripts/live_scale_on_node.py`; wrapper `scripts/run_final_k3s.sh` / `run_all_finals.sh`.

## 5. Artefact purpose and artefact-only project structure

**Purpose:** Implement PAKS (predictive LSTM + adaptive Kubernetes scaling) and evaluate against traditional HPA on disclosed traces and Free-Tier AWS k3s.

```
paks-framework/
  src/
    data/           # trace_loader (fail-closed); PROXY workload_simulator
    models/         # numpy LSTM predictor; TF fail-closed
    k8s/            # adaptive_engine, live_client, dry_run_client
    eval/           # metrics.py (TRACE vs SIMULATED tags)
    proxy/          # NimbusGuard-framed synthetic path — NOT binding CA2
    lambda_handler/ # unused SAM proxy packaging
  scripts/          # train_lstm_and_evaluate, run_live_aws_k8s, fetch traces, finals
  data/traces/      # derived GCT/Alibaba series + PROVENANCE.md
  data/gct|alibaba/ # raw samples (often gitignored) + SHA indexes
  terraform/        # Free-Tier EC2+S3+CW+SSM stack (project=paks-k8s-live)
  results/          # TRACE CSVs, dry-run JSON, live/final_{1,2,3}, archive/
  tests/            # unit/engine tests
  Makefile, requirements.txt, template.yaml, README.md, RUBRIC_EVIDENCE_MATRIX.md
```

Parent binding docs (outside artefact root but required contract): `pooja-thesis/CA2_COMMITMENTS.md`, `STATUS.md`, `DATA_GAPS.md`, `DESIGN_RATIONALE_BEYOND_CA2.md`.

## 6. AWS architecture, services, configurations, and experimental setup

**Applied (then destroyed).** Not N/A.

| Item | Committed evidence |
|------|-------------------|
| Region | `eu-west-1` (per final packs `aws.region`) |
| Compute | 1× `t3.micro` EC2 AL2023; role `k3s-single`; cluster `k3s-single-node` |
| Project tag | `paks-k8s-live` (do not touch Venkat stacks) |
| Storage | Ephemeral S3 buckets per run (e.g. final_3: `paks-k8s-live-922384915031-e6dd7cf7`) |
| Observability | CloudWatch namespace `PAKS/LiveK8s`; log group `/paks-k8s-live/paks-k8s-live`; `live_cloudwatch=true` |
| Control | SSM instance profile (no public kube-apiserver); kubectl on node |
| IaC | `terraform/` — apply → live scale → destroy |
| Final instances | final_1 `i-0f14a9dc4b6a97ea9`; final_2 `i-01947d765d456a7a0`; final_3 `i-07837058709d02909` |
| Destroy | Each `aws_destroy_verify.json`: `destroy_confirmed=true`; leftovers empty |

**Workload artefact (causal):** metrics-server + busybox CPU burn + HPA object; demand scaled for headroom (`workload_scaled_for_headroom=true`).

## 7. Evaluation metrics and why they were selected

| Metric | Why (CA2) | Evidence tag in packs |
|--------|-----------|------------------------|
| Prediction MAE, RMSE | Forecast quality vs persistence | **TRACE** (`formal_prediction_metrics.csv`) |
| Resource utilisation (CPU/mem) | Efficiency under scale | Live packs: CPU util model fields present; **mem null**; independent review: util fill still open |
| Response time, throughput | Service quality under load | Live: `evidence_response_throughput=SIMULATED` |
| Scaling latency | Reactivity of policy path | Live: `evidence_latency=LIVE` |
| Infrastructure cost | Economic outcome | Live: `evidence_cost=SIMULATED` (`usd_per_pod_hour_assumed=0.04`) |
| SLA compliance / availability | Reliability | Live fields present but partly capacity-model / SIMULATED path |

Live loop evidence: HPA `evidence_loop=LIVE` / `LIVE-CONTROLLER-HPA`; PAKS `LIVE`. Prediction series on live: `TRACE-or-synthetic-fallback` (see pack `evidence.lstm_series`).

## 8. Baseline definition and baseline comparison

| Role | Definition |
|------|------------|
| Binding baseline | Traditional Kubernetes **HorizontalPodAutoscaler** (`baseline=traditional-HorizontalPodAutoscaler`) |
| Proposed | **paks-adaptive** predictive Scale via K8s API |
| Literature (not contract) | NimbusGuard DQN+LSTM — proxy only |

**Comparison rule (causal artefact):** HPA arm **observes** controller desired/current replicas; PAKS arm **PATCHes** Scale. Divergence of `mean_replicas` / `scaling_events` is the primary live contrast. Prior identical-ceiling packs are **invalid**.

## 9. Complete evaluation process and number of runs

### Authoritative causal live packs (use these)

| Pack | Path | Seed | Scale | Destroy |
|------|------|-----:|-------|---------|
| final_1 | `results/live/final_1/` | 41 | lite: 12 steps, max_replicas=4, 1×t3.micro k3s | `destroy_confirmed=true` |
| final_2 | `results/live/final_2/` | 42 | same | `destroy_confirmed=true` |
| final_3 | `results/live/final_3/` | 43 | same | `destroy_confirmed=true` |

Each pack contains: `formal_k8s_live_aws.json`, `aws_live_run_summary.json`, `aws_destroy_verify.json`, `PROVENANCE.txt`. Summary: `results/live/FINAL3_BASELINE.md`.

**Honesty:** These are **lite Free-Tier smoke stability** finals, **not** three full-scale multi-intensity AWS campaigns. Wall times (elapsed): final_1 ≈223 s; final_2 ≈172 s; final_3 ≈188 s.

### Invalidated (do not cite for CA2 claims)

`results/live/archive/invalidated_pre_causal_hpa_20260922T070121Z/` — pre-causal scripted HPA / pause / metrics-server-off packs.

### Supporting offline / dry-run (not live latency authority)

- `results/formal_prediction_metrics.csv` — TRACE MAE/RMSE  
- `results/formal_scaling_metrics.csv` — SIMULATED scaling metrics (`live_k8s=false`)  
- `results/formal_k8s_dry_run.json` — dryRun=All  
- Proxy CSVs `results/results_*.csv` — **not** formal evidence  

## 10. Final results and key findings (committed evidence only)

### A. TRACE prediction (`formal_prediction_metrics.csv`)

| Dataset | Split | LSTM MAE (test) | LSTM RMSE | Persistence MAE | Persistence RMSE | Verdict |
|---------|-------|----------------:|----------:|----------------:|-----------------:|---------|
| gct2011 | held-out jobs | **0.1025** | 1.3494 | **0.0477** | 0.6553 | LSTM **worse** than persistence |
| alibaba | last 30% cluster bins | **3.4349** | 4.3020 | **2.8026** | 3.9552 | LSTM **worse** than persistence |

Backend: `numpy-lstm`; evidence=`TRACE`. Memory/TF: **not demonstrated**.

### B. Causal live HPA vs PAKS (`FINAL3_BASELINE.md` / final packs)

| Round | seed | HPA mean_replicas | HPA scaling_events | HPA lat_s (mean) | PAKS mean_replicas | PAKS scaling_events | PAKS lat_s (mean) | destroy |
|-------|-----:|------------------:|-------------------:|-----------------:|-------------------:|--------------------:|------------------:|:-------:|
| final_1 | 41 | 1.0 | 0 | 12.699 | 2.333 | 2 | 0.936 | True |
| final_2 | 42 | 1.0 | 0 | 9.172 | 1.75 | 1 | 0.534 | True |
| final_3 | 43 | 1.0 | 0 | 9.063 | 1.833 | 5 | 1.621 | True |

**Findings (pos + neg):**
- **Positive:** ×3 destroy-after under real HPA controller path; policies **diverge** (HPA mean_replicas=1.0 se=0; PAKS ~1.75–2.33 se=1–5).
- **Negative / retained:** HPA did **not** raise measured mean replicas on these lite windows (`scaling_events=0`) — undershoot / settle / metrics conditions; documented as limitation, not a PAKS superiority claim.
- **Negative:** cost SIMULATED; LSTM < persistence TRACE unchanged; `mem_util_mean=null`.
- Example SIMULATED cost (final_3): HPA `cost_usd≈0.000667`; PAKS `≈0.001222` at `$0.04`/pod-hour.

## 11. How results satisfy or address each research objective

1. **Preprocess traces + train LSTM:** **Partial.** Demonstrated TRACE NumPy LSTM on GCT 2011 shard + Alibaba RANGE sample with MAE/RMSE. **Open:** TensorFlow runtime; memory prediction; full dumps.
2. **Adaptive scaling engine via K8s API:** **Demonstrated (lite).** PAKS live Scale PATCH with scaling_events 1–5 and mean_replicas >1 across finals.
3. **Kubernetes on AWS EC2+S3+CloudWatch:** **Demonstrated (lite Free-Tier).** Apply + live metrics path + destroy ×3. Not multi-node / EKS.
4. **Compare vs HPA across intensities:** **Partial.** Causal HPA vs PAKS contrast exists on one lite intensity window ×3 seeds. **Not** low/moderate/high/burst suite. HPA undershoot retained as **negative** finding.

## 12. How results answer the research question

On disclosed TRACE samples, **NumPy LSTM does not beat persistence** (GCT MAE 0.102 vs 0.048; Alibaba 3.435 vs 2.803). On Free-Tier causal lite AWS k3s, **PAKS and traditional HPA diverge** in replica behaviour and live scaling latency, but traditional HPA **mean_replicas stayed 1.0** with **zero scaling_events** on these windows — so the RQ is **not** answered as confirmatory PAKS superiority. Honest answer: **partial causal method demonstration + negative prediction result + HPA undershoot limitation**; CA2 floor **~62**, not 100%.

## 13. How findings relate to the literature gap and previous research

Addresses the CA2 gap (predictive scaler vs reactive HPA on traces + live K8s) at **method** level under Free-Tier constraints. Does **not** confirm literature-style claims that predictive LSTM autoscaling improves accuracy or utilisation here. NimbusGuard remains related work only; proxy synthetic numbers must not be mixed into formal claims (`PROXY_NIMBUSGUARD.md`).

## 14. Statistical analysis and significance

**None / exploratory only.**  
- Live: n=12 steps × 3 seeds; no Holm / paired significance suite on HPA vs PAKS.  
- TRACE: single reported held-out / last-30% splits in CSV — not multi-seed confirmatory stats.  
Independent review: “Multi-intensity + stats | Partial | n=12 steps ×3 seeds; no Holm suite.”

## 15. Important observations, trends, positive/negative findings, and anomalies

- Causal artefact change **invalidated** prior finals where both policies ceilinged identically.
- After re-eval, PAKS scaling_events and mean_replicas move; HPA mean_replicas do not — **divergence without HPA reaction**.
- OBSERVE samples can show controller conditions such as `FailedGetResourceMetric` / desired≠current while pack-level `mean_replicas` remains 1.0 and `scaling_events=0` — treat pack aggregates + FINAL3_BASELINE as authoritative summary.
- Live response/throughput/SLA/cost numbers exist in JSON but are tagged **SIMULATED** — do not present as measured CloudWatch billing or real RPS.
- README/`final_report.md` may lag STATUS (stale “NOT COMPLETE” / “~92%” / “100%”); **STATUS + independent review (~62) win**.

## 16. Limitations, validity, reproducibility, and generalisability

| Dimension | Evidence-bound limit |
|-----------|----------------------|
| Validity | Single-node t3.micro; lite burn may undershoot HPA 50% util target |
| Construct | Cost/util/SLA partly SIMULATED; mem null |
| Prediction | LSTM loses to persistence on both TRACE sets |
| Scope | No multi-intensity, no multi-node, no TF, no billing export |
| Reproducibility | Scripts + terraform + PROVENANCE/SHA; AWS destroy-after required; Free-Tier slot contention possible |
| Generalisability | Not claimed beyond Free-Tier smoke + disclosed samples |

## 17. Final conclusions and research contribution

**Contribution:** A fail-closed PAKS artefact with TRACE prediction on public GCT/Alibaba **samples**, and a **causal** Free-Tier AWS k3s evaluation path that observes a real HorizontalPodAutoscaler controller versus predictive Scale — with three destroy-confirmed lite finals.

**Conclusion:** Research-scope CA2 is **PARTIAL (~62)**. Differentiating live packs and causal baseline are demonstrated; HPA undershoot, LSTM&lt;persistence, SIMULATED cost, and open TF/memory/multi-intensity limbs prevent a 100% floor or a confirmatory PAKS-win claim.

## 18. What changed or improved during the evaluation process

1. Withdrew “CA2 100%” after independent audit of confounded HPA baseline.  
2. Enabled metrics-server; replaced `pause` with busybox burn; real HPA object; observe-only HPA arm.  
3. Raised default max_replicas to 4; scaled demand into headroom so policies can diverge.  
4. Archived pre-causal packs; re-ran final_1–3; wrote `FINAL3_BASELINE.md`.  
5. Floor updated to **partial (~62)** with undershoot retained as negative.

## 19. Remaining issues or recommended future work

1. Increase burn / lower HPA target / longer settle so traditional HPA **current** replicas move — or keep undershoot as explicit limitation.  
2. Fill util/SLA metric honesty (reduce null/SIMULATED ambiguity).  
3. Multi-intensity campaign; optional statistical tests.  
4. TensorFlow LSTM and/or memory forecasting if CA2 resources table remains binding.  
5. Billing-linked cost vs `$0.04` assumption.  
6. Do **not** restore “100%” without examiner-facing scope amendment.  
7. Soft packaging: Gantt chart figure missing in formal CA2 docx (`CA2_COMMITMENTS.md`).

## 20. Important files, scripts, configurations, datasets, and artefacts to reproduce/continue

| Kind | Path |
|------|------|
| Binding contract | `pooja-thesis/CA2_COMMITMENTS.md`, `Pooja_25120921_CA2.docx` |
| Status / audit | `pooja-thesis/STATUS.md`, `_analysis_extract/reports/INDEPENDENT_REVIEW_POOJA.md` |
| Design honesty | `pooja-thesis/DESIGN_RATIONALE_BEYOND_CA2.md`, `DATA_GAPS.md` |
| TRACE train/eval | `scripts/train_lstm_and_evaluate.py`, `src/models/lstm_predictor.py`, `src/data/trace_loader.py` |
| Live AWS | `scripts/run_live_aws_k8s.py`, `scripts/live_scale_on_node.py`, `scripts/run_final_k3s.sh`, `scripts/run_all_finals.sh` |
| K8s engine | `src/k8s/adaptive_engine.py`, `src/k8s/live_client.py`, `src/k8s/dry_run_client.py` |
| Metrics | `src/eval/metrics.py` |
| Terraform | `terraform/` (`README.md`, `main.tf`, …) |
| Datasets | `data/traces/PROVENANCE.md`, `SAMPLE_SHA256.txt`, derived GCT/Alibaba CSVs; fetch scripts under `scripts/fetch_*.py` |
| Authoritative live results | `results/live/FINAL3_BASELINE.md`, `results/live/final_{1,2,3}/*` |
| TRACE numbers | `results/formal_prediction_metrics.csv` |
| Invalid archive | `results/live/archive/invalidated_pre_causal_hpa_*` (**do not cite**) |
| Proxy quarantine | `src/proxy/`, `results/PROXY_NIMBUSGUARD.md`, `results/results_*.csv` |

Reproduce live (destructive AWS): from `paks-framework/`, follow `terraform/README.md` then `scripts/run_final_k3s.sh` / `run_all_finals.sh`; always destroy and verify `aws_destroy_verify.json`.
