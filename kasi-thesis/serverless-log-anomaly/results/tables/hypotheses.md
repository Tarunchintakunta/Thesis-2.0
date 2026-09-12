# Hypothesis tests (Holm-Bonferroni, alpha 0.05)

_Logs from the local Lambda runtime emulator (simulated serverless workload), not live AWS._

| test | null hypothesis | test used | statistic | p | p (Holm) | effect | size | reject H0 |
|---|---|---|---|---|---|---|---|---|
| H1 | F1(source-free) = F1(transfer) | Wilcoxon signed-rank | 685.500 | 0.1321 | 0.1321 | rank_biserial | 0.225 | False |
| H2_d1_primary | F1 does not differ across fault categories for D1 source-free (primary) | Friedman | 128.568 | 0.0000 | 0.0000 | kendalls_w | 0.714 | True |
| H2_d2_transfer | F1 does not differ across fault categories for D2 transfer (ELFA-Log style) | Friedman | 38.966 | 0.0000 | 0.0000 | kendalls_w | 0.216 | True |
| H2_d3_thresholds | F1 does not differ across fault categories for D3 threshold alarms | Friedman | 84.598 | 0.0000 | 0.0000 | kendalls_w | 0.470 | True |
| H2_d4_novel | F1 does not differ across fault categories for D4 Context-Aware OC-SVM (novel) | Friedman | 15.365 | 0.0015 | 0.0031 | kendalls_w | 0.085 | True |
| H3 | elasticity false-alarm rate does not differ between approaches | Friedman | 61.365 | 0.0000 | 0.0000 | kendalls_w | 0.568 | True |

**Decision rule** (source-free is a viable substitute if within 10 F1 points of transfer AND better than the threshold alarms):

* F1 source-free = 0.908, transfer = 0.836, thresholds = 0.936
* gap (transfer - source-free) = -0.072
* within 10 points: True; beats alarms: False
* **viable substitute: False**
