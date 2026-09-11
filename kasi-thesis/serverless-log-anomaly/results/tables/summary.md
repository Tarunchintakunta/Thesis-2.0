# Detector summary (phase B evaluation, phase C elasticity)

_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._

| label | precision | recall | f1 | f1_ci_low | f1_ci_high | far_B_normal | far_C_elasticity | far_C_burst | far_C_no_burst | injections_detected | median_delay_s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 source-free (primary) | 0.958 | 0.863 | 0.908 | 0.892 | 0.924 | 0.019 | 0.091 | 0.368 | 0.048 | 0.988 | 0.000 |
| D1a OC-SVM | 0.958 | 0.863 | 0.908 | 0.892 | 0.924 | 0.019 | 0.091 | 0.368 | 0.048 | 0.988 | 0.000 |
| D1b Isolation Forest | 0.711 | 0.048 | 0.090 | 0.070 | 0.112 | 0.010 | 0.102 | 0.715 | 0.007 | 0.129 | 60.000 |
| D2 transfer (ELFA-Log style) | 0.826 | 0.847 | 0.836 | 0.785 | 0.887 | 0.089 | 0.247 | 0.000 | 0.285 | 0.983 | 0.000 |
| D3 threshold alarms | 1.000 | 0.880 | 0.936 | 0.923 | 0.947 | 0.000 | 0.000 | 0.000 | 0.000 | 0.999 | 0.000 |
