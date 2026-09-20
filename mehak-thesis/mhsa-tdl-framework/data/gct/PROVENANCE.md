# GCT provenance — Mehak formal CA2

**Source bucket:** `gs://clusterdata-2011-2` (Google Cluster Data 2011 / ClusterData2011_2)  
**License:** CC-BY 4.0 (see google/cluster-data)  
**Downloaded:** 2026-09-20 via `gsutil cp`  
**Layout:** `data/gct/2011/{machine_events,task_events,task_usage}/`

## Files landed (minimum viable subset)

| Local path | Remote object | Role |
|------------|---------------|------|
| `2011/machine_events/part-00000-of-00001.csv.gz` | same | Machine capacity / failure events |
| `2011/task_events/part-00000-of-00500.csv.gz` | same | Task lifecycle / FAIL labels |
| `2011/task_events/part-00001-of-00500.csv.gz` | same | Extra events coverage |
| `2011/task_usage/part-00000-of-00500.csv.gz` | same | CPU/mem/disk telemetry features |

**Not downloaded:** remaining 498 `task_events` / `task_usage` parts (~41 GB full trace). Formal first-run uses this time-sliced subset; expand parts for stronger coverage.

## Join contract

`src/data/gct_loader.py` joins `task_usage` ↔ `task_events` on `(job_id, task_index)` with a fixed prediction horizon (default 5 usage steps ≈ 25 min of 5‑minute buckets). Labels: healthy / L1 stress / L2 stress-or-fail from future usage peaks and FAIL/EVICT/KILL/LOST events.

## Fetch notes (2026-09-20)

A sibling `gsutil -m cp` into this tree was stuck at a 0-byte `*.csv.gz_.gstmp`.
The same official objects were completed via HTTPS
`https://storage.googleapis.com/clusterdata-2011-2/...` (public CC-BY bucket;
byte sizes match GCS `Content-Length`). SHA-256 of the landed files is recorded
in `2011/DOWNLOAD_PROVENANCE.json`. Re-fetch: `scripts/download_gct_2011.py`.
