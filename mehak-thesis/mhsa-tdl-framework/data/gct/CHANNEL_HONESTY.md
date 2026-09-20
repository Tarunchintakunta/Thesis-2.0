# Channel honesty — Google Cluster Data 2011

Formal CA2 names CPU, memory, disk I/O, **network**, and scheduling telemetry.

## Network channel

ClusterData2011_2 `task_usage` (20 CSV fields) has **no network-byte / bandwidth column**.
Canonical schema: https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md

The MHSA 4th channel (`net`) is therefore **sampled CPU usage** (field 20 / index 19).
It is a utilization proxy so the tensor stays 4-wide; it is **not** packet or byte
throughput. `LAST_LOAD_META["net_channel_is_network_bytes"] = false`.

The 2019 Borg traces *do* expose assigned network; those cells are **not** in this
repo. Do not back-fill a fake 2011 network series.

## Scheduling channel

History-window counts of `task_events` types SCHEDULE (1) and UPDATE_PENDING /
UPDATE_RUNNING (7, 8) are appended as Aldomi expanded features only.
Future FAIL/EVICT/KILL/LOST events are **labels**, never features.

## MHSA vs Aldomi feature sets

| Path | Features |
|------|----------|
| MHSA-TDL | 4: cpu, mem, disk, net=sampled CPU |
| Aldomi SelectKBest+GRU | 11 usage columns + 2 history scheduling counts; SelectKBest k≤14 |
