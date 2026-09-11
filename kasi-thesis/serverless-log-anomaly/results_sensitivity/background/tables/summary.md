# Detector summary (phase B evaluation, phase C elasticity)

_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._

| label | precision | recall | f1 | f1_ci_low | f1_ci_high | far_B_normal | far_C_elasticity | far_C_burst | far_C_no_burst | injections_detected | median_delay_s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D1 source-free (primary) | 0.971 | 0.949 | 0.960 | 0.953 | 0.966 | 0.014 | 0.074 | 0.403 | 0.024 | 1.000 | 0.000 |
| D1a OC-SVM | 0.971 | 0.949 | 0.960 | 0.953 | 0.966 | 0.014 | 0.074 | 0.403 | 0.024 | 1.000 | 0.000 |
| D1b Isolation Forest | 0.933 | 0.243 | 0.386 | 0.360 | 0.411 | 0.009 | 0.093 | 0.667 | 0.004 | 0.442 | 60.000 |
| D2 transfer (ELFA-Log style) | 0.762 | 0.587 | 0.663 | 0.599 | 0.727 | 0.092 | 0.028 | 0.208 | 0.000 | 0.696 | 0.000 |
| D3 threshold alarms | 0.996 | 0.841 | 0.912 | 0.894 | 0.928 | 0.002 | 0.007 | 0.056 | 0.000 | 0.990 | 0.000 |
