# Nemi Docker FL final-3 baseline (multi-container)

**Date:** 2026-09-22
**Artefact:** docker-compose.yml + scripts/run_docker_fl_worker.py
**Note:** Not Kubernetes; separate containers + FedAvg via shared volume.

| Round | accuracy | F1 | elapsed_s | clients |
|------:|---------:|---:|----------:|--------:|
| 1 | 0.9060 | 0.9357 | 2.549 | 2 |
| 2 | 0.9080 | 0.9372 | 2.572 | 2 |
| 3 | 0.8980 | 0.9295 | 2.581 | 2 |

## Verdict
- Rounds present: 3/3
- Accuracy range: 0.8980–0.9080
- F1 range: 0.9295–0.9372
- Positive: Docker multi-client path executed ×3.
- Residual: Kubernetes still Not met if CA2 requires K8s.

