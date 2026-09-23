# SecureFL-IDS Project Status

**Student:** Nemi Ishwarlal Vikani (24303046)  
**Programme:** MSc Cloud Computing  
**Institution:** National College of Ireland

**Project:** SecureFL-IDS — Privacy-Preserving Federated Intrusion Detection for Cloud-Native Environments

## Overall status: **COMPLETE** (CA2 floor; beyond-CA2 optional)

**ONE source of truth:** `CA2_PROPOSED_VS_ARTEFACT.md` (same-metrics vs Saklani).  
**Scripted audit:** `securefl-ids/scripts/audit_k8s_deferral_root_causes.py` → EXIT 0 / remediable_total=0.  
**N-Nemi (K8s deferred):** `DATED_WONTFIX_N_Nemi_2026-09-23.md`.

**Research alignment:** CA2 floor met — centralised comparator + real UNSW sample; **live cloud FL lite** final_1–3 destroy-after; **Docker FL ×3** closed packaging. Soft items (full 2.5M-flow, 50-round, **K8s/EKS**, improved-arm plateau) are **beyond-CA2** / dated WONTFIX — not blockers. **AWS residual: closed.**

**INITIAL_EVAL_PASS:** **yes** (live cloud FL lite treated as initial eval). Final-3 **DONE** (`results/live/final_1|2|3/`; baseline `FINAL3_BASELINE.md`). Docker final-3 **DONE** (`results/docker_fl/`).

```
COMPLETE=yes CA2_FLOOR=met SOLE_AWS_RESIDUAL=closed BEYOND_CA2=optional
K8S=dated_wontfix_2026-09-23 DOCKER_FL=done_3of3
INITIAL_EVAL_PASS=yes
FINAL3=done_3of3
LIVE_INITIAL_EVAL_1=yes
SOT_AUDIT=EXIT_0
```

Authoritative live lite: `securefl-ids/results/live/cloud_lite_summary.json`.  
Initial-eval gate: `securefl-ids/results/live/initial_eval_1/`.  
Final-3: `securefl-ids/results/live/final_{1,2,3}/`.

### Rubric quality notes (aim 70–100; Eval 25% + Artefact 27%)

From `securefl-ids/results/live/FINAL3_BASELINE.md` + centralised comparator.

- **Artefact:** SecureFL-IDS FL vs **centralised** IDS; live Free-Tier EC2+S3+CW FL lite; destroy-after; real UNSW training-partition sample locked locally.
- **Pos:** three destroy-after live finals completed; centralised comparator present; privacy-preserving FL method executed on cloud lite path.
- **Neg / mixed retained:** lite rounds are method-scale (not 50-round / 2.5M-flow confirmatory); improved-arm plateau retained; **K8s dated WONTFIX** (Docker FL ×3 closed packaging) — do not over-claim production FL / K8s performance.
- **vs Saklani et al. (2026) baseline framing:** same-metrics acc/F1/comm under Free-Tier + Docker×3 — **not** a clone of Saklani ~91.8% depth numbers.
- **Limitations:** Free-Tier depth; K8s deferred — `DATED_WONTFIX_N_Nemi_2026-09-23.md`.

---

## Component Status

### 1. Research & Literature Review
- [x] Literature review and baseline paper (Saklani et al. 2026)
- [x] Research gaps and RQ formulated
- [x] WhatsApp DOI `note={doi:...}` present on wired scholarly entries in `latex_report/refs.bib`

### 2. Artefact Implementation

#### Code Structure
- [x] `securefl-ids/` with baseline, improved, **centralised**, and common modules
- [x] Unit tests present (`tests/`, including `test_centralised.py`)
- [x] Experiment scripts and docs (`make centralised`, `make unsw-real`, `make live-cloud-fl`)
- [x] Terraform at `securefl-ids/terraform/` — **applied for lite round, then destroyed** (no student name/ID tags)

#### Synthetic PoC (FL + centralised comparator)
**Authoritative synthetic:** `results/comparison/results.json` (synthetic data, 30 rounds/epochs, sample_size=10000):

| Metric | Centralised | Baseline FL | Improved FL |
|--------|-------------|-------------|-------------|
| Accuracy | **0.7975** | **0.793** | **0.800** |
| F1-Score | ~0.015 | ~0.019 | **0.0** |
| Avg Comm (MB/round) | 0.0 (N/A) | 1.83 | 3.12 |

**Do not cite** `results/pilot/pilot_results.json` as the CA2 PoC.  
**Do not cite** literature-style 91–94% accuracy as *synthetic PoC* results.

#### Real UNSW-NB15 (training-partition stratified sample)
**Authoritative real:** `results/unsw_real/results.json` (official training-set CSV mirror, 25k stratified sample, 39 numeric features, 30 rounds/epochs, 5 clients):

| Metric | Centralised | Baseline FL | Improved FL |
|--------|-------------|-------------|-------------|
| Accuracy | **0.9452** | **0.8934** | **0.6800** |
| F1-Score | **0.9603** | **0.9262** | **0.8095** |
| Avg Comm (MB/round) | 0.0 (N/A) | 3.08 | 3.12 |

Provenance: `results/unsw_real/DATA_PROVENANCE.json` (`kind=real`, ~175341 rows / 45 cols).  
This is the **official training partition sample**, not the full 2.5M-flow corpus. Improved FL plateaued at 0.68 accuracy on this run — reported honestly.

### 3. Live cloud FL lite (2026-09-20, measured only)

Protocol: `scripts/run_live_cloud_fl.sh` — 1× `t3.micro` (eu-west-1), S3 parameter bus, CloudWatch namespace `SecureFL-IDS`, 2 in-process clients, 3 rounds, 2500-row real-lite sample. **No Lambda** (Vikas `idem-eval-fn` was live: 1171 invocations / 10 min, ConcurrentExecutions max=10). Destroy-after-round.

| Metric | Baseline FL | Improved FL |
|--------|-------------|-------------|
| Accuracy | **0.5000** | **0.5480** |
| F1-Score | **0.0000** | **0.2260** |
| Avg Comm (MB/round) | 1.230 | 1.246 |
| S3 global round-trip | yes | yes |

Instance `i-012ae234495584077` **terminated**. Bucket `securefl-ids-artifacts-0fb66e133bb11fcdd263c314e4` **gone**. Terraform **9 resources destroyed**. These lite numbers do **not** supersede the 30-round local tables above.

### 4. Documentation
- [x] README, CONFIGURATION_MANUAL, ARCHITECTURE, RESULTS_NOTE
- [x] LaTeX report draft present (methodology/eval aligned to evidence)
- [x] Terraform README + live runner

### 5. Deployment honesty
| Claim | Reality |
|-------|---------|
| Local multi-process simulation | **Yes** — default PoC / real-sample mode |
| Real UNSW training-partition sample | **Yes** — `results/unsw_real/` |
| Live AWS EC2 + S3 + CloudWatch FL | **Yes (lite)** — measured then destroyed |
| Docker / docker-compose | **Yes** — `docker-compose.yml` + docker_fl final_1–3 (Not K8s) |
| Kubernetes / Helm | **Not present / not tested** — **DATED_WONTFIX 2026-09-23** |
| Lambda | **Not used** |

---

## Known Limitations (honest)

1. Synthetic PoC F1 near zero (majority-class collapse on 20-feature sample)
2. Improved FL uses **more** communication MB/round than baseline on local campaigns
3. Improved FL **did not beat** baseline FL on the 30-round real-UNSW sample (0.680 vs 0.893 accuracy)
4. Live cloud FL is **lite** (3 rounds / 2 clients / 2500 rows); 3-round accuracies ~0.50–0.55 are expected under DP noise
5. Kubernetes / EKS not executed (dated WONTFIX 2026-09-23); Docker FL ×3 is present

---

## Remaining blockers to 100%

**None at CA2 floor.** Optional beyond-CA2: full 2.5M-flow corpus, 50-round campaigns, multi-instance WAN FL, **K8s/EKS** (dated deferred), improved-arm tuning.

---

## Build / run

```bash
cd Nemi/securefl-ids
make centralised   # synthetic PoC + merge into comparison/
make unsw-real     # real training-partition sample (central + FL)
make test
# Live lite (Free Tier EC2; destroys after round):
# make live-cloud-fl
```

**Last Updated:** 2026-09-23  
**Status:** COMPLETE at CA2 floor (live lite + Docker×3 + destroy). K8s dated WONTFIX. SoT audit EXIT 0.
