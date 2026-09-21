# Exact missing datasets — Mehak formal CA2

**Binding CA2:** `MAHEK NAAZ.docx`  
**Required dataset:** Google Cluster Trace (GCT) — CPU, memory, disk I/O, network, scheduling/machine events  
**CA2 floor status (2026-09-21):** **MET** on disclosed 2011 subset. Full dump / 2019 / true net-bytes are **scoped-out optional** (`DESIGN_RATIONALE_BEYOND_CA2.md`), not open floor blockers.

**In-tree evidence:** `mhsa-tdl-framework/data/gct/2011/` — 4 `task_events` parts + 2 `task_usage` parts + `machine_events`. 2011 **network-byte** channel does not exist (`CHANNEL_HONESTY.md`).

Formal CA2 does **not** pin a GCT generation. 2011 expanded subset is present and scored; 2019 cells remain absent by design choice.

## Landed (formal floor)

| Artefact | Path | Formal CA2 role |
|----------|------|-----------------|
| GCT 2011 expanded subset | `mhsa-tdl-framework/data/gct/2011/` | **Landed** — 2 usage + 4 event parts + machine_events |
| GCT 5-seed metrics | `mhsa-tdl-framework/results/gct/` | Formal-path evidence (`dataset=gct`) |
| Channel honesty | `data/gct/CHANNEL_HONESTY.md` | Documents net≠bytes; no invention |
| Scope rationale | `DESIGN_RATIONALE_BEYOND_CA2.md` | Maps commitments → delivered; scopes optional dumps |

## Optional beyond-CA2 (not required for 100% floor)

### Option A extras — remaining Google Cluster Data 2011 (~41 GB full)
Canonical: https://github.com/google/cluster-data (2011 schema)

| Path (if ever fetched) | Role | Floor impact |
|------------------------|------|--------------|
| Remaining `task_events` / `task_usage` parts | Broader coverage | Soft power / validity only |
| `job_events/*`, `machine_attributes/*` | Extra context | Not required for binary fail-horizon labels used here |

Minimum viable for a first formal run was **≥1** events + **≥1** usage part; this repo exceeds that (4+2).

### Option B — Borg cluster traces 2019 (eight cells)
Canonical: https://github.com/google/cluster-data (2019)

| Path (if ever fetched) | Role | Floor impact |
|------------------------|------|--------------|
| One cell `instance_usage` + `instance_events` | Aldomi paper generation; optional true network field | Beyond CA2; not pinned by formal docx |

## Labels required by formal CA2 (not inventable)

| Label field | Source | Notes |
|-------------|--------|-------|
| Task/job failure (or eviction→fail) within horizon *H* | `task_events` event type | Delivered via FAIL/EVICT/KILL/LOST in future window |
| Optional severity | fail vs kill vs finish | Not claimed |

**Synthetic `TelemetrySimulator` labels are not a substitute** for GCT-derived labels under formal CA2. Synthetic CSVs under `results/` remain artefact-as-built only.

## Baselines on this GCT subset

RF / KNN / SVM and Aldomi **SelectKBest + GRU + RF/KNN** are scored on the same GCT windows (`results/gct/`). That is **not** a hyperparameter-identical clone of Aldomi et al. (2026) (their paper uses 2019 Borg cells).

## Loader contract

`mhsa-tdl-framework/src/data/gct_loader.py` looks for `MHSA_GCT_ROOT` or `data/gct/{2011,2019}/`. If missing, it raises with this checklist — **no silent synthetic fallback** when `--dataset gct` is requested.

## Network channel (impossible invent)

ClusterData 2011 has **no** network-byte column. MHSA 4th channel = sampled CPU; `net_channel_is_network_bytes=false`. Do not back-fill fake bandwidth. True bytes require 2019 (scoped out above).
