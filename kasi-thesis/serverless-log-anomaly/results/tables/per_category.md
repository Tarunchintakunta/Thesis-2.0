# Per fault category

_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._

| detector | category | f1 | recall | injections_detected | median_delay_s |
|---|---|---|---|---|---|
| d1_primary | permission_denied | 0.726 | 0.654 | 0.950 | 0.000 |
| d1_primary | config_error | 0.860 | 0.869 | 1.000 | 0.000 |
| d1_primary | dependency_timeout | 0.911 | 0.963 | 1.000 | 0.000 |
| d1_primary | resource_exhaustion | 0.916 | 0.972 | 1.000 | 0.000 |
| d1_ocsvm | permission_denied | 0.726 | 0.654 | 0.950 | 0.000 |
| d1_ocsvm | config_error | 0.860 | 0.869 | 1.000 | 0.000 |
| d1_ocsvm | dependency_timeout | 0.911 | 0.963 | 1.000 | 0.000 |
| d1_ocsvm | resource_exhaustion | 0.916 | 0.972 | 1.000 | 0.000 |
| d1_iforest | permission_denied | 0.003 | 0.001 | 0.006 | 0.000 |
| d1_iforest | config_error | 0.013 | 0.007 | 0.028 | 180.000 |
| d1_iforest | dependency_timeout | 0.097 | 0.055 | 0.161 | 60.000 |
| d1_iforest | resource_exhaustion | 0.214 | 0.129 | 0.322 | 60.000 |
| d2_transfer | permission_denied | 0.702 | 0.920 | 1.000 | 0.000 |
| d2_transfer | config_error | 0.600 | 0.739 | 0.933 | 0.000 |
| d2_transfer | dependency_timeout | 0.706 | 0.935 | 1.000 | 0.000 |
| d2_transfer | resource_exhaustion | 0.631 | 0.791 | 1.000 | 0.000 |
| d3_thresholds | permission_denied | 0.946 | 0.897 | 1.000 | 0.000 |
| d3_thresholds | config_error | 0.980 | 0.961 | 1.000 | 0.000 |
| d3_thresholds | dependency_timeout | 0.953 | 0.910 | 1.000 | 0.000 |
| d3_thresholds | resource_exhaustion | 0.858 | 0.751 | 0.994 | 0.000 |
| d4_novel | permission_denied | 0.895 | 0.900 | 1.000 | 0.000 |
| d4_novel | config_error | 0.927 | 0.964 | 1.000 | 0.000 |
| d4_novel | dependency_timeout | 0.926 | 0.959 | 1.000 | 0.000 |
| d4_novel | resource_exhaustion | 0.921 | 0.950 | 1.000 | 0.000 |
