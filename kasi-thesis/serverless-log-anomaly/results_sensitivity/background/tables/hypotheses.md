# Hypothesis tests (Holm-Bonferroni, alpha 0.05)

_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._

| test | null hypothesis | test used | statistic | p | p (Holm) | effect | size | reject H0 |
|---|---|---|---|---|---|---|---|---|
| H1 | F1(source-free) = F1(transfer) | Wilcoxon signed-rank | 13.000 | 0.0000 | 0.0000 | rank_biserial | 0.986 | True |
| H2_d1_primary | F1 does not differ across fault categories for D1 source-free (primary) | Friedman | 20.039 | 0.0002 | 0.0002 | kendalls_w | 0.111 | True |
| H2_d2_transfer | F1 does not differ across fault categories for D2 transfer (ELFA-Log style) | Friedman | 52.338 | 0.0000 | 0.0000 | kendalls_w | 0.291 | True |
| H2_d3_thresholds | F1 does not differ across fault categories for D3 threshold alarms | Friedman | 73.305 | 0.0000 | 0.0000 | kendalls_w | 0.407 | True |
| H3 | elasticity false-alarm rate does not differ between approaches | Friedman | 43.725 | 0.0000 | 0.0000 | kendalls_w | 0.607 | True |

**Decision rule** (source-free is a viable substitute if within 10 F1 points of transfer AND better than the threshold alarms):

* F1 source-free = 0.960, transfer = 0.663, thresholds = 0.912
* gap (transfer - source-free) = -0.297
* within 10 points: True; beats alarms: True
* **viable substitute: True**
