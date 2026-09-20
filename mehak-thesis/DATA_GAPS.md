# Exact missing datasets — Mehak formal CA2

**Binding CA2:** `MAHEK NAAZ.docx`  
**Required dataset:** Google Cluster Trace (GCT) — CPU, memory, disk I/O, network, scheduling/machine events  
**Status in this repo (2026-09-20):** **PARTIAL+** — 2011 subset under `mhsa-tdl-framework/data/gct/2011/`: 4 `task_events` parts + 2 `task_usage` parts + `machine_events`. Full 41 GB trace not downloaded. 2011 **network-byte** channel does not exist (`CHANNEL_HONESTY.md`).

Formal CA2 does **not** pin a GCT generation. 2011 MV subset is present; 2019 cells remain absent.

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

## Baselines on this GCT subset

RF / KNN / SVM and an Aldomi **SelectKBest + GRU extractor + RF/KNN** hybrid are scored on the
same GCT windows (`results/gct/`). That is **not** a hyperparameter-identical clone of
Aldomi et al. (2026) (their paper uses 2019 Borg cells; we use 2011 expanded usage columns).
Synthetic `results/results_*.csv` remain artefact-as-built only.

## Loader contract

`mhsa-tdl-framework/src/data/gct_loader.py` looks for `MHSA_GCT_ROOT` or `data/gct/{2011,2019}/`. If missing, it raises with this file’s checklist — **no silent synthetic fallback** when `--dataset gct` is requested.

## What exists today

| Artefact | Path | Formal CA2 role |
|----------|------|-----------------|
| GCT 2011 subset | `mhsa-tdl-framework/data/gct/2011/` | **Landed** — 2 usage parts + 4 event parts + machine_events |
| GCT 5-seed metrics | `mhsa-tdl-framework/results/gct/` | Formal-path evidence on this subset (`dataset=gct`) |
| Synthetic telemetry | `src/data/telemetry_simulator.py` | Proxy / development only |
| Synthetic 5-seed CSVs | `results/results_*.csv` | **Not** GCT evidence |
| Optional SAM/Lambda | `template.yaml` | **Not** required by formal CA2 |

## Still missing

- Remaining 2011 `task_events` / `task_usage` parts (~41 GB full trace)
- `job_events`, `machine_attributes`
- 2011 **network-byte** channel (schema has none; 4th MHSA channel = sampled CPU — do not invent)
- Entire 2019 Borg eight-cell family (Aldomi paper's generation)
- Line-by-line Aldomi 2019 preprocessing / k=14 search on that schema
