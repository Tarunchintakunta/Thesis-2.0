# Per fault category

_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._

| detector | category | f1 | recall | injections_detected | median_delay_s |
|---|---|---|---|---|---|
| d1_primary | permission_denied | 0.894 | 0.899 | 1.000 | 0.000 |
| d1_primary | config_error | 0.928 | 0.965 | 1.000 | 0.000 |
| d1_primary | dependency_timeout | 0.926 | 0.961 | 1.000 | 0.000 |
| d1_primary | resource_exhaustion | 0.932 | 0.972 | 1.000 | 0.000 |
| d1_ocsvm | permission_denied | 0.894 | 0.899 | 1.000 | 0.000 |
| d1_ocsvm | config_error | 0.928 | 0.965 | 1.000 | 0.000 |
| d1_ocsvm | dependency_timeout | 0.926 | 0.961 | 1.000 | 0.000 |
| d1_ocsvm | resource_exhaustion | 0.932 | 0.972 | 1.000 | 0.000 |
| d1_iforest | permission_denied | 0.015 | 0.008 | 0.028 | 60.000 |
| d1_iforest | config_error | 0.016 | 0.008 | 0.033 | 90.000 |
| d1_iforest | dependency_timeout | 0.494 | 0.351 | 0.750 | 60.000 |
| d1_iforest | resource_exhaustion | 0.724 | 0.607 | 0.956 | 60.000 |
| d2_transfer | permission_denied | 0.301 | 0.305 | 0.356 | 0.000 |
| d2_transfer | config_error | 0.344 | 0.363 | 0.456 | 0.000 |
| d2_transfer | dependency_timeout | 0.687 | 0.908 | 0.994 | 0.000 |
| d2_transfer | resource_exhaustion | 0.618 | 0.775 | 0.978 | 0.000 |
| d3_thresholds | permission_denied | 0.870 | 0.780 | 0.989 | 0.000 |
| d3_thresholds | config_error | 0.952 | 0.920 | 1.000 | 0.000 |
| d3_thresholds | dependency_timeout | 0.945 | 0.906 | 0.994 | 0.000 |
| d3_thresholds | resource_exhaustion | 0.857 | 0.759 | 0.978 | 0.000 |
