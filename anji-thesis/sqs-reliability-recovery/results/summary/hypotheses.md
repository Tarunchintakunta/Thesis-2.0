# Confirmatory tests

_Numbers come from the local simulator (DRY_RUN=1), not from AWS._

| hypothesis | campaign | dv | test | stat | p | p (Holm) | effect | size | decision |
|---|---|---|---|---|---|---|---|---|---|
| H1 | A_vt_consumer_kill | loss_rate | none (no variance) | 0 | 1 | 1 | n/a | 0 | fail to reject H0 |
| H2 | B_mrc_unhandled_error | recovery_time_s | Kruskal-Wallis | 4.98 | 0.1733 | 0.5199 | epsilon_squared | 0.128 | fail to reject H0 |
| H3_loss | E_guidance_transfer | loss_rate | none (no variance) | 0 | 1 | 1 | rank_biserial | 0 | fail to reject H0 |
| H3_recovery | E_guidance_transfer | recovery_time_s | Mann-Whitney U | 250 | 0.0007919 | 0.003168 | rank_biserial | 0.667 | reject H0 |

## Exploratory

| hypothesis | campaign | dv | test | stat | p | p (Holm) | effect | size | decision |
|---|---|---|---|---|---|---|---|---|---|
| X_B_mrc_unhandled_error_dlq_capture_rate_by_max_receive_count | B_mrc_unhandled_error | dlq_capture_rate | Kruskal-Wallis | 37.69 | 3.282e-08 | nan | epsilon_squared | 0.966 | - |
| X_C_mrc_datastore_reject_dlq_capture_rate_by_max_receive_count | C_mrc_datastore_reject | dlq_capture_rate | Kruskal-Wallis | 32.7 | 3.722e-07 | nan | epsilon_squared | 0.839 | - |
| X_C_mrc_datastore_reject_recovery_time_s_by_max_receive_count | C_mrc_datastore_reject | recovery_time_s | Kruskal-Wallis | 4.431 | 0.2185 | nan | epsilon_squared | 0.114 | - |
| X_D_vt_datastore_timeout_recovery_time_s_by_visibility_timeout | D_vt_datastore_timeout | recovery_time_s | Kruskal-Wallis | 48.32 | 8.08e-10 | nan | epsilon_squared | 0.986 | - |
| X_A_vt_consumer_kill_recovery_time_s_by_visibility_timeout | A_vt_consumer_kill | recovery_time_s | Kruskal-Wallis | 48.5 | 7.439e-10 | nan | epsilon_squared | 0.99 | - |
| X_A_vt_consumer_kill_duplicate_rate_by_visibility_timeout | A_vt_consumer_kill | duplicate_rate | Kruskal-Wallis | 24.3 | 6.942e-05 | nan | epsilon_squared | 0.496 | - |
| X_baseline_vt_batch_throughput_msg_s_by_batch_size | baseline_vt_batch | throughput_msg_s | Kruskal-Wallis | 186.6 | 3.343e-40 | nan | epsilon_squared | 0.938 | - |
| X_baseline_vt_batch_throughput_msg_s_by_visibility_timeout | baseline_vt_batch | throughput_msg_s | Kruskal-Wallis | 0.85 | 0.9316 | nan | epsilon_squared | 0.00427 | - |
