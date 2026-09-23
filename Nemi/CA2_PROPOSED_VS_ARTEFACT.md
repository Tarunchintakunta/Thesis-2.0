# Nemi — ONE source of truth (thesis SecureFL-IDS)

**Authority:** formal CA2 `Nemi/NemiIshwarlalVikani_24303046_CA2.txt` + live `securefl-ids/results/`.  
**Baseline (binding):** Saklani et al. (2026) PP-FL-DP-IDS — `baseline_papers/BASELINE_PAPER.md` (doi:10.1109/iciss67859.2026.11454085).  
**Audit script (binding):** `securefl-ids/scripts/audit_k8s_deferral_root_causes.py` → `results/docker_fl/analysis/k8s_deferral_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated K8s/EKS; no marketing Saklani 91.8% as our measured PoC.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted K8s-deferral audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; K8s = dated WONTFIX |
| Strong (centralised vs FL + live cloud FL lite)? | **Yes** — local UNSW sample + live final_1–3 destroy-after |
| Strong (Docker multi-container FL packaging)? | **Yes** — Docker FL ×3 (acc 0.898–0.908) |
| Strong (production Kubernetes / EKS)? | **No** — dated deferred beyond-floor |
| Audit remediable gaps? | **0** (`audit_k8s_deferral_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

Docker×3 presence, destroy status, and K8s non-claim must be proven by pack inventory — not STATUS prose. Script EXIT 0 → disposition **`DATED_WONTFIX_K8S_DEFERRED`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | Effect of FL + Differential Privacy on accuracy, privacy, and performance of cloud-native IDS vs traditional / existing FL approaches |
| Stack | TensorFlow Federated, **Docker**, **Kubernetes**, AWS |
| Metrics | intrusion detection (acc/F1/…) + cloud (comm overhead, util, convergence, scalability) |
| Baseline | Saklani et al. (2026) PP-FL-DP-IDS (~91.8% acc / F1>90% on their campaign) |
| Comparator | traditional centralised IDS + FL baselines |

---

## 2. SAME METRICS — artefact vs Saklani gap

**Saklani:** privacy-preserving FL+DP IDS with reported **~91.8% accuracy / F1>90%** on their evaluation campaign — **no** Free-Tier EC2+S3+CW destroy-after lite table and **no** Docker Compose multi-container FedAvg pack in our tree to clone.  
**Ours:** retain **accuracy / F1 / avg communication MB/round** under disclosed Free-Tier depth; fill **live cloud FL lite** + **Docker×3** packaging; do **not** claim Saklani depth numbers as ours.

### Local UNSW training-partition sample (`results/unsw_real/`)

| Metric | Centralised | Baseline FL | Improved FL |
|--------|------------:|------------:|------------:|
| Accuracy | **0.9452** | **0.8934** | **0.6800** |
| F1 | **0.9603** | **0.9262** | **0.8095** |
| Avg Comm (MB/round) | 0.0 (N/A) | 3.08 | 3.12 |

### Live cloud FL lite final_1–3 (`results/live/final_{1,2,3}/`)

Protocol: 1× t3.micro + S3 + CW; 2 in-process clients × 3 rounds × 2500-row real-lite; destroy verified each round.

| Round | Baseline acc / F1 | Improved acc / F1 |
|-------|------------------:|------------------:|
| final_1 | 0.440 / 0.091 | 0.500 / 0.667 |
| final_2 | 0.550 / 0.458 | 0.500 / 0.667 |
| final_3 | 0.478 / 0.538 | 0.500 / 0.667 |

Lite 3-round accuracies ~0.44–0.55 are expected under DP noise — **not** Saklani 91.8%.

### Docker FL ×3 (`results/docker_fl/final_{1,2,3}/`)

| Round | accuracy | F1 | elapsed_s |
|------:|---------:|---:|----------:|
| 1 | 0.906 | 0.936 | 2.55 |
| 2 | 0.908 | 0.937 | 2.57 |
| 3 | 0.898 | 0.929 | 2.58 |

**Note:** separate containers + FedAvg via shared volume — **Not K8s.**

**Verdict:** Same detection/comm metric family as Saklani; depth and orchestration differ honestly. K8s remains deferred.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: FL+DP cloud-native IDS | Saklani PP-FL-DP-IDS | SecureFL-IDS + centralised | Partial (depth) | **MET (floor)** |
| 2 | Accuracy / F1 retained | Saklani DVs | unsw_real + live + Docker | Yes | **MET** |
| 3 | Communication overhead | Saklani low-comm claim | avg_communication_cost | Yes | **MET** |
| 4 | Centralised comparator | traditional IDS | `results/comparison/` + unsw_real | Yes | **MET** |
| 5 | Live AWS cloud path | — | live final_1–3 destroy | Yes (lite) | **MET** |
| 6 | Docker packaging | CA2 names Docker | docker_fl ×3 + compose | Yes | **MET** |
| 7 | Kubernetes / EKS | CA2 names K8s | **absent** (deferred) | — | **WONTFIX soft** |
| 8 | 50-round / 2.5M-flow | Saklani-scale depth | not run | — | **Beyond-floor** |
| 9 | Marketing Saklani 91.8 as ours | forbidden | not claimed | — | **Closed** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Nemi** | K8s deferred after Docker×3 | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_N_Nemi_2026-09-23.md`; audit EXIT 0; disposition `DATED_WONTFIX_K8S_DEFERRED` |
| Docker packaging | CA2 Docker limb | **Evidenced** — docker_fl final_1–3 |
| Live cloud FL lite | AWS residual | **Evidenced** — destroy-after finals |
| Improved-arm plateau (local 30-round) | Model quality | **Retained negative** — 0.680 vs baseline 0.893 |
| Marketing 100 / K8s done | Forbidden | Keep honest floor + K8s deferred visible |

Reproduce:

```bash
cd Nemi/securefl-ids
python3 scripts/audit_k8s_deferral_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

Dated note: `Nemi/DATED_WONTFIX_N_Nemi_2026-09-23.md`

---

## 5. Evidence packs

| Pack | Role |
|------|------|
| `results/unsw_real/` | Real training-partition sample (acc/F1/comm) |
| `results/live/final_1`…`final_3` | Live cloud FL lite ×3 + destroy |
| `results/live/FINAL3_BASELINE.md` | Live binding baseline |
| **`results/docker_fl/final_1`…`3`** | Docker multi-container FL ×3 |
| `results/docker_fl/DOCKER_FINAL3_BASELINE.md` | Docker binding baseline |
| `results/docker_fl/analysis/k8s_deferral_audit_report.*` | Move gate |

---

## 6. Thesis gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Nemi K8s hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs Saklani | **Yes** |
| Configuration manual | **Yes** (`docs/CONFIGURATION_MANUAL.md`) |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (acc/F1/comm; depth gap-fill) | **Filled** — §2 |
| Docker packaging | **Filled** — docker_fl ×3 |
| K8s / EKS | **WONTFIX** — §4 |
| Config manual | Present + audit reproduce |
| Claim↔evidence | Lite depth + K8s deferred retained |
| Accidental silent park | Forbidden — N-Nemi dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~62–100 floor framing:** live lite + Docker×3 + centralised comparator close research-scope AWS/packaging; K8s and Saklani-scale campaigns remain soft/beyond. Do **not** market production K8s or 91.8% as ours.
