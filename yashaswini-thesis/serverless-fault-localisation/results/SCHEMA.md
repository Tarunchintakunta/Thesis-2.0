# Data and result files

## Live run folder (`data/runs/live/`, gitignored until the campaign is done)

| file | written by | content |
|---|---|---|
| `windows.json` | scripts/campaign.py | time range of every phase (calibration, steady / peak control + campaign, overhead-*) |
| `schedule_<load>.jsonl` | scripts/campaign.py | the injections, written before the first one: id, load, fault, target, start, end, parameters |
| `applied_<load>.jsonl` | injector/injector.py | the same with the real `applied_at` / `cleared_at` |
| `requests_<phase>.csv` | workloads/loadgen.py | t_sent, kind, status, latency_ms, trace_id, error |
| `series.parquet` | scripts/collect_telemetry.py | per-minute `<service>/ErrorRate`, `ThrottleRate`, `Duration` |
| `spans.jsonl.gz` | scripts/collect_telemetry.py | flat spans: trace_id, span_id, parent_id, service, start, end, fault, throttle |
| `overhead_<condition>.json` | scripts/collect_overhead.py | requests, log bytes, traces recorded, bytes per 1000 requests, latency, policy |

## Results

| folder | from | content |
|---|---|---|
| `results/rcaeval/raw/<method>/<case>.json` | baseline_runner/ | ranking (services), time, error per case and method |
| `results/rcaeval/` | eval/leg2.py | ranks.csv, localisation*.csv, comparisons.csv, detection.json, top3_expectation.json, summary.md |
| `results/live/` | eval/rig.py, scripts/collect_overhead.py | per_injection.csv, false_positives.csv, rig_summary.csv, control_false_positives.csv, thresholds.json, trace_calibration.json, overhead.json, summary.md |
| `results/sim/` | eval/rig.py --source sim | the same files from simulated telemetry - a functional check, NOT AWS data |

Figures go to `figures/<source>/`.

Yashaswini Penumarthi (24262404)
