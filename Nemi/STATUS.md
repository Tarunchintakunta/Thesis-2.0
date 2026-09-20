# SecureFL-IDS Project Status

**Student:** Nemi Ishwarlal Vikani (24303046)  
**Programme:** MSc Cloud Computing  
**Institution:** National College of Ireland

**Project:** SecureFL-IDS — Privacy-Preserving Federated Intrusion Detection for Cloud-Native Environments

## Overall Status: NOT COMPLETE (CA2 alignment < 100%)

**Research alignment (non-AWS evidence pass):** ~78% — centralised IDS comparator + real UNSW-NB15 training-partition sample campaign committed; synthetic PoC FL metrics still locked; DOI notes unchanged.  
**Not SUBMIT-READY for CA2.** Sole remaining residual for 100%: **live cloud-native FL** (Terraform present, not applied). Do **not** apply while shared-account concurrency is hot.

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=yes READY_FOR_AWS=yes
```

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
- [x] Experiment scripts and docs (`make centralised`, `make unsw-real`)
- [x] Terraform scaffold at `securefl-ids/terraform/` (**exists; not applied** — no live AWS; no student name/ID tags)

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

### 3. Experiments & Evaluation
- [x] Local synthetic PoC (`results/comparison/results.json`) including centralised arm
- [x] Centralised IDS comparator implemented (`src/centralised/`, `results/centralised/`)
- [x] Real UNSW training-partition sample campaign (`results/unsw_real/`)
- [x] Honest limitations in `RESULTS_NOTE.md`
- [ ] Full 2.5M-flow corpus / 50-round campaign (optional depth; not blocking sole-AWS)
- [ ] No live AWS / ECS / Kubernetes evaluation

### 4. Documentation
- [x] README, CONFIGURATION_MANUAL, ARCHITECTURE, RESULTS_NOTE
- [x] LaTeX report draft present (methodology/eval aligned to evidence)
- [x] Terraform README notes apply gate (not applied)

### 5. Deployment honesty
| Claim | Reality |
|-------|---------|
| Local multi-process simulation | **Yes** — default executed mode |
| Real UNSW training-partition sample | **Yes** — `results/unsw_real/` |
| Docker / docker-compose | **No committed compose/Helm charts** — future work only |
| Kubernetes / Helm | **Not present / not tested** |
| AWS ECS / live cloud | **Not deployed** |
| Terraform (`securefl-ids/terraform/`) | **Present; `terraform apply` not run** |

---

## Known Limitations (honest)

1. Synthetic PoC F1 near zero (majority-class collapse on 20-feature sample)
2. Improved FL uses **more** communication MB/round than baseline on both campaigns here
3. Improved FL **did not beat** baseline FL on the real-UNSW sample (0.680 vs 0.893 accuracy)
4. No Docker/K8s/AWS production evidence
5. Terraform not applied (await live cloud FL after concurrency clears)

---

## Remaining blockers to 100%

**Sole AWS residual:**
1. Live cloud-native FL evaluation — Terraform ready, not applied (do not start while Vikas+Rasool consume shared account)

**Optional depth (not sole blockers):**
- Full 2.5M-flow UNSW corpus / longer 50-round campaigns
- Improved-arm tuning so CNN-LSTM does not plateau on real data

---

## Build / run (local only)

```bash
cd Nemi/securefl-ids
make centralised   # synthetic PoC + merge into comparison/
make unsw-real     # real training-partition sample (central + FL)
make test
# Do NOT terraform apply until budget approval + shared-account concurrency clears
```

**Last Updated:** 2026-09-20  
**Status:** Non-AWS gaps closed with evidence (~78%); cloud-FL **prep only** (`CLOUD_FL_PREP.md`, `terraform validate` OK). **No apply** (Vikas r5 RUNNING). SOLE_AWS_RESIDUAL=yes; CA2 **not** 100%
