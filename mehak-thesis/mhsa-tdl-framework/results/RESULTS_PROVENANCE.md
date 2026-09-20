# Results provenance

## Synthetic (artefact-as-built, not formal CA2)

- Files: `results_per_seed.csv`, `results_summary.csv` from `--dataset synthetic`.
- These rows are **not** Google Cluster Trace evidence.

## Google Cluster Trace (formal CA2)

- Files: `gct/results_per_seed.csv`, `gct/results_summary.csv`, `gct/RESULTS_PROVENANCE.md` from `--dataset gct`.
- Load meta: `{"family": "2011", "root": "/Users/valletivarish/Documents/Thesis-2.0/mehak-thesis/mhsa-tdl-framework/data/gct", "seq_length": 10, "horizon": 5, "n_windows": 12000, "fail_forced_windows": 489, "n_fail_event_keys": 14819, "n_usage_series": 20412, "transient_rate": 0.21466666666666667, "task_events_parts": ["part-00000-of-00500.csv.gz", "part-00001-of-00500.csv.gz"], "task_usage_parts": ["part-00000-of-00500.csv.gz"], "metrics": ["cpu", "mem", "disk", "net"], "channel_notes": {"cpu": "mean CPU usage rate", "mem": "canonical memory usage", "disk": "mean disk I/O time \u00d750 clipped", "net": "sampled CPU (no network-byte field in 2011 schema)"}, "seed": 42}`
- Dataset flag in those CSVs: **gct**.
