# Varun baseline compare (rebuilt from full-eval logs)

Evaluations: [1, 2, 3]

| Workload | Δ LC mean | Δ IT mean | Sig LC all? | Vs both all? | Little/no vs LC? |
|----------|----------:|----------:|:-----------:|:------------:|:----------------:|
| static_archival | 0.005119 | 0.000794 | True | True | False |
| mixed_access | 0.003180 | 0.004843 | True | True | False |
| high_churn | 0.000065 | 0.015775 | False | False | True |

Negative/null high_churn vs Lifecycle reported honestly.
Artefact rebuilt after results dir wipe; trial costs from run logs.
