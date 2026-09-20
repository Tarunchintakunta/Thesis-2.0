# Exact missing datasets — Mehak formal CA2

**Binding CA2:** `MAHEK NAAZ.docx`  
**Required dataset:** Google Cluster Trace (GCT) — CPU, memory, disk I/O, network, scheduling/machine events  
**Status in this repo:** **ABSENT** — no GCT files under `mehak-thesis/` or elsewhere in Thesis-2.0 (verified 2026-09-20).

Formal CA2 does **not** pin a GCT generation. Both public families are acceptable sources; **neither is present**.

## Missing artefacts (must land under `mehak-thesis/mhsa-tdl-framework/data/gct/`)

### Option A — Google Cluster Data 2011 (Borg cell, ~29 days)
Canonical: https://github.com/google/cluster-data (2011 schema)

| Path (expected local) | Upstream role | Formal use |
|-----------------------|---------------|------------|
| `data/gct/2011/machine_events/part-00000-of-00001.csv.gz` | Machine add/remove/update | Machine capacity / failure events |
| `data/gct/2011/machine_attributes/part-00000-of-00001.csv.gz` | Machine attributes | Optional context |
| `data/gct/2011/job_events/part-?????-of-?????.csv.gz` | Job submit/schedule/finish/fail/kill | Job-level failure labels |
| `data/gct/2011/task_events/part-?????-of-?????.csv.gz` | Task schedule/evict/fail/finish | **Primary failure / health labels** (event type) |
| `data/gct/2011/task_usage/part-?????-of-?????.csv.gz` | Per-task CPU, memory, disk, network samples | **Telemetry features** for MHSA windows |

Minimum viable subset for a first formal run: **≥1** `task_events` part **and** **≥1** `task_usage` part covering the same time range (plus `machine_events` if machine-level health is labelled).

### Option B — Borg cluster traces 2019 (eight cells)
Canonical: https://github.com/google/cluster-data (2019 / “Borg: the Next Generation”)

| Path (expected local) | Upstream role | Formal use |
|-----------------------|---------------|------------|
| `data/gct/2019/<cell>/instance_usage/*.json.gz` (or parquet export) | Instance resource usage | Telemetry features |
| `data/gct/2019/<cell>/instance_events/*.json.gz` | Instance lifecycle / fail | Failure labels |
| `data/gct/2019/<cell>/machine_events/*.json.gz` | Machine events | Capacity / health |

Full 2019 cells are multi‑GB; a **single cell, time-sliced export** is enough for alignment if labels + telemetry join cleanly.

## Labels required by formal CA2 (not inventable)

Formal evaluation is **healthy vs unhealthy / failure** classification with Acc, Prec, Rec, F1, ROC-AUC, latency.

| Label field | Source | Notes |
|-------------|--------|-------|
| Task/job failure (or eviction→fail) within horizon *H* | `task_events` / `instance_events` event type | Binary or multiclass health; horizon must be fixed and documented |
| Optional severity | fail vs kill vs finish | Only if formally justified |

**Synthetic `TelemetrySimulator` labels are not a substitute** for these GCT-derived labels under formal CA2.

## Baselines blocked without GCT

Formal baselines (Aldomi-style hybrid; RF / KNN / SVM / GRU monitors) must be scored on the **same GCT-derived splits**. Artefact classical baselines on synthetic telemetry (see `results/`) are **scaffold only** — not formal CA2 evidence.

## Loader contract

`mhsa-tdl-framework/src/data/gct_loader.py` looks for `MHSA_GCT_ROOT` or `data/gct/{2011,2019}/`. If missing, it raises with this file’s checklist — **no silent synthetic fallback** when `--dataset gct` is requested.

## What exists today (artefact-as-built)

| Artefact | Path | Formal CA2 role |
|----------|------|-----------------|
| Synthetic telemetry | `src/data/telemetry_simulator.py` | Proxy / development only |
| 5-seed results (incl. formal metric suite on synthetic) | `results/results_*.csv` | **Not** GCT evidence |
| Optional SAM/Lambda | `template.yaml` | **Not** required by formal CA2 |
