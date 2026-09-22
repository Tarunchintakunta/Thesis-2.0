# Independent review — Nemi (securefl-ids)

**Date:** 2026-09-22  
**STATUS claim overturned:** `CA2 floor 100%` — **not accepted**.  
**Honest CA2 floor:** **partial (~55)**

## RQ (CA2)
> What is the effect of combining Federated Learning and Differential Privacy on the accuracy, privacy preservation and overall performance of cloud-native intrusion detection systems compared with traditional systems and existing federated learning-based approaches?

CA2 method text commits TensorFlow Federated, Docker, Kubernetes, AWS.

## Artefact reality
Python FL + DP (`src/improved/securefl_ids.py`, `epsilon` base=1.0) + centralised comparator + Terraform EC2/S3/CW lite. **No Docker/compose/Helm/K8s** in tree. Clients run **in-process on one EC2**.

## Evidence (disk)

| Claim | Verdict | Path / numbers |
|-------|---------|----------------|
| Centralised vs FL (synthetic) | **Demonstrated (weak F1)** | `results/comparison/results.json`: centralised acc=0.7975 F1≈0.015; baseline FL acc=0.793 F1≈0.019; improved acc=0.800 F1=**0.0** |
| Real UNSW sample | **Demonstrated** | `results/unsw_real/results.json` + `DATA_PROVENANCE.json` (175341×45 training partition, 25k stratified): centralised **0.9452 / 0.9603**; baseline FL **0.8934 / 0.9262**; improved FL **0.6800 / 0.8095** (improved **loses**) |
| Live cloud FL | **Demonstrated (toy)** | `results/live/cloud_lite_summary.json`: elapsed=**6.08s**, 2 clients, 3 rounds, 2500 rows; baseline acc=0.50 F1=0.0; improved acc=0.548 F1=0.226. final_1–3 same protocol ~6.2s each |
| Cloud-native (Docker/K8s) | **Not met** | `RESULTS_NOTE.md`: Docker/K8s not executed |
| Literature-style 91–94% as PoC | **Claimed / false if cited** | STATUS correctly warns; do not cite |

## Floor
**Partial / soft not-met on cloud-native scope.** FL+DP code and centralised comparator exist; real-UNSW shows improved arm regression; “cloud-native” live path is a 6-second single-box S3 round-trip, not orchestration.

## Highest-value next steps
1. Multi-instance clients (or containers) so “cloud-native FL” is not in-process theatre.  
2. Fix/diagnose improved-arm plateau (0.68 vs 0.89) before claiming DP benefit.  
3. Honest scope note: drop Docker/K8s from CA2 delivery claims or implement one compose path.
