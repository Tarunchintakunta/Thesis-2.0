# GCT provenance — Mehak formal CA2

**Source bucket:** `gs://clusterdata-2011-2` (Google Cluster Data 2011 / ClusterData2011_2)  
**License:** CC-BY 4.0 (see google/cluster-data)  
**Downloaded:** 2026-09-20 via HTTPS `storage.googleapis.com/clusterdata-2011-2`  
**Layout:** `data/gct/2011/{machine_events,task_events,task_usage}/`

## Files landed

| Local path | Role |
|------------|------|
| `2011/machine_events/part-00000-of-00001.csv.gz` | Machine capacity / failure events |
| `2011/task_events/part-00000` … `part-00003-of-00500.csv.gz` | Task lifecycle / FAIL labels (4 parts) |
| `2011/task_usage/part-00000` and `part-00001-of-00500.csv.gz` | CPU/mem/disk telemetry (2 parts) |

SHA-256: `2011/DOWNLOAD_PROVENANCE.json`. Network bytes: **absent** in 2011 schema (`CHANNEL_HONESTY.md`).

**Not downloaded:** remaining 496 `task_events` / 498 `task_usage` parts (~41 GB full trace); 2019 Borg cells.

## Join contract

`src/data/gct_loader.py` joins `task_usage` ↔ `task_events` on `(job_id, task_index)` with a fixed prediction horizon (default 5 usage steps ≈ 25 min of 5‑minute buckets). Labels: healthy / L1 stress / L2 stress-or-fail from future usage peaks and FAIL/EVICT/KILL/LOST events.

## Fetch notes (2026-09-20)

A sibling `gsutil -m cp` into this tree was stuck at a 0-byte `*.csv.gz_.gstmp`.
The same official objects were completed via HTTPS
`https://storage.googleapis.com/clusterdata-2011-2/...` (public CC-BY bucket;
byte sizes match GCS `Content-Length`). SHA-256 of the landed files is recorded
in `2011/DOWNLOAD_PROVENANCE.json`. Re-fetch: `scripts/download_gct_2011.py`.
