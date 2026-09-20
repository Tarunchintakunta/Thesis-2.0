# Results provenance

## Synthetic (artefact-as-built, not formal CA2)

- Files: `results_per_seed.csv`, `results_summary.csv` from `--dataset synthetic`.
- These rows are **not** Google Cluster Trace evidence.

## Google Cluster Trace (formal CA2)

- Files: `gct/results_per_seed.csv`, `gct/results_summary.csv`, `gct/RESULTS_PROVENANCE.md` from `--dataset gct`.
- Load meta: `{"family": "2011", "root": "/Users/valletivarish/Documents/Thesis-2.0/mehak-thesis/mhsa-tdl-framework/data/gct", "seq_length": 10, "horizon": 5, "n_windows": 12000, "fail_forced_windows": 981, "n_fail_event_keys": 40225, "n_usage_series": 33206, "transient_rate": 0.08633333333333333, "task_events_parts": ["part-00000-of-00500.csv.gz", "part-00001-of-00500.csv.gz", "part-00002-of-00500.csv.gz", "part-00003-of-00500.csv.gz"], "task_usage_parts": ["part-00000-of-00500.csv.gz", "part-00001-of-00500.csv.gz"], "metrics": ["cpu", "mem", "disk", "net"], "expanded_features": ["mean_cpu", "canonical_mem", "assigned_mem", "unmapped_cache", "total_cache", "max_mem", "mean_disk_io", "mean_local_disk", "max_cpu", "max_disk_io", "sampled_cpu", "sched_count_hist", "update_count_hist"], "n_expanded_features": 13, "channel_notes": {"cpu": "mean CPU usage rate", "mem": "canonical memory usage", "disk": "mean disk I/O time \u00d750 clipped", "net": "sampled CPU (ClusterData 2011 has no network-byte field; not a fabricated bandwidth series)"}, "scheduling_features": "history-only SCHEDULE/UPDATE counts; no future FAIL leak", "net_channel_is_network_bytes": false, "fail_series_first": true, "seed": 42}`
- Dataset flag in those CSVs: **gct**.
