# GENAI_HANDOFF.md — Nemi (SecureFL-IDS)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Nemi Ishwarlal Vikani |
| Artefact root | `Nemi/securefl-ids/` |
| Honest CA2 floor | **PARTIAL (~55–65)** after Docker close — K8s still Not met if CA2 requires it |
| Eval completeness | Live cloud lite final_1–3 (prior) + **Docker multi-container final_1–3** (2026-09-22) |
| AWS | Lite EC2 path historically; Docker regression is local Compose |
| Handoff date | 2026-09-22 |

## 1. Research problem, motivation, research question, and objectives

Secure federated learning for intrusion detection vs centralised baseline, with cloud-native packaging (Docker; K8s claimed in some CA2 text).

## 2. Identified literature gap and how this research addresses it

FL+DP IDS vs centralised monitors on UNSW-NB15; cloud packaging evidence beyond in-process clients.

## 3. CA2 proposal alignment and any extensions beyond the proposal

- Demonstrated: centralised vs FL (synthetic + UNSW), live cloud lite, ablations, **Docker Compose multi-container FedAvg**.
- **Not met:** Kubernetes (explicit residual).

## 4. Research methodology and experimental design

Baseline FL vs improved SecureFL; centralised comparator; Docker: 2 client containers + orchestrator FedAvg via shared volume.

## 5. Artefact purpose and artefact-only project structure

```
securefl-ids/
  Dockerfile docker-compose.yml
  src/{baseline,improved,centralised,common}/
  scripts/run_docker_fl_worker.py scripts/run_docker_fl_continue.sh
  results/docker_fl/final_{1,2,3}/ results/live/ results/unsw_real/
```

## 6. AWS architecture, services, configurations, and experimental setup

Prior lite: EC2/S3/CW. Docker path: local Compose (not AWS-managed K8s).

## 7. Evaluation metrics and why they were selected

Accuracy, F1, elapsed_s; containers list for cloud-native packaging evidence.

## 8. Baseline definition and baseline comparison

Centralised vs FL (baseline/improved). Docker packaging vs prior in-process clients.

## 9. Complete evaluation process and number of runs

| Pack | Path |
|------|------|
| Docker final_1–3 | `results/docker_fl/final_{1,2,3}/docker_fl_summary.json` |
| Baseline note | `results/docker_fl/DOCKER_FINAL3_BASELINE.md` |
| Prior live finals | `results/live/final_{1,2,3}/` |

## 10. Final results and key findings (committed evidence)

Docker multi-container (UNSW sample_rows=2500, 2 clients, 3 FL rounds):

| Round | accuracy | F1 | elapsed_s |
|------:|---------:|---:|----------:|
| 1 | 0.9060 | 0.9357 | 2.549 |
| 2 | 0.9080 | 0.9372 | 2.572 |
| 3 | 0.8980 | 0.9295 | 2.581 |

## 11–12. Objectives / RQ

Docker cloud-native packaging **Demonstrated** and repeated ×3. K8s objective still open. Prior UNSW/live findings retained (improved can lose — keep negative honesty from independent review).

## 13–17. Literature / stats / observations / limitations / conclusions

Descriptive Acc/F1 across 3 Docker rounds (stable ~0.90 Acc / ~0.93 F1). Limitation: not K8s; synthetic/sampled UNSW; FedAvg via volume not production mesh. Contribution: executable multi-container FL packaging with regression evidence.

## 18–19. Changes / remaining

Docker artefact added 2026-09-22; K8s still residual if required by CA2 text.

## 20. Important files

`Dockerfile`, `docker-compose.yml`, `scripts/run_docker_fl_worker.py`, `results/docker_fl/DOCKER_FINAL3_BASELINE.md`
