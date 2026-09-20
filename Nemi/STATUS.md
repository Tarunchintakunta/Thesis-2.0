# SecureFL-IDS Project Status

**Student:** Nemi Ishwarlal Vikani (24303046)  
**Programme:** MSc Cloud Computing  
**Institution:** National College of Ireland

**Project:** SecureFL-IDS — Privacy-Preserving Federated Intrusion Detection for Cloud-Native Environments

## Overall Status: NOT COMPLETE (CA2 alignment < 100%)

**Research alignment (claim hygiene pass):** ~64% — PoC metrics honest; Docker/K8s/AWS/production overclaims removed; DOI `note={doi:…}` added; README baseline-paper figures demoted.  
**Not SUBMIT-READY for CA2.** Live AWS / full UNSW-NB15 / centralised baseline remain blockers.

---

## Component Status

### 1. Research & Literature Review
- [x] Literature review and baseline paper (Saklani et al. 2026)
- [x] Research gaps and RQ formulated
- [ ] WhatsApp DOI `note={doi:...}` format not fully verified across `refs.bib`

### 2. Artefact Implementation

#### Code Structure
- [x] `securefl-ids/` with baseline, improved, and common modules
- [x] Unit tests present (`tests/`)
- [x] Experiment scripts and docs
- [x] Terraform scaffold at `securefl-ids/terraform/` (**exists; not applied** — no live AWS)

#### Baseline / Improved (PoC only)
Committed PoC in `results/comparison/results.json` (synthetic data, 30 rounds, 5 clients):

| Metric | Baseline | Improved |
|--------|----------|----------|
| Accuracy | **0.793** (~79.3%) | **0.800** (~80.0%) |
| F1-Score | ~0.019 (~1.9%) | **0.0** |
| Avg Comm (MB/round) | 1.83 | 3.12 |

**Do not cite** literature-style 91–94% accuracy, ~90% F1, or −45% communication as *achieved* results — those are baseline-paper / expected-with-full-data figures only, not this PoC.

### 3. Experiments & Evaluation
- [x] Local PoC experiment committed (`results/comparison/results.json`)
- [x] Honest limitations in `RESULTS_NOTE.md`
- [ ] Full UNSW-NB15 (49 features / large sample) not run
- [ ] Centralised IDS baseline not implemented
- [ ] No live AWS / ECS / Kubernetes evaluation

### 4. Documentation
- [x] README, CONFIGURATION_MANUAL, ARCHITECTURE, RESULTS_NOTE
- [x] LaTeX report draft present
- [x] Terraform README notes apply gate (not applied)

### 5. Deployment honesty
| Claim | Reality |
|-------|---------|
| Local multi-process simulation | **Yes** — default and only executed mode |
| Docker / docker-compose | **No committed compose/Helm charts** — future work only |
| Kubernetes / Helm | **Not present / not tested** |
| AWS ECS / live cloud | **Not deployed** |
| Terraform (`securefl-ids/terraform/`) | **Present; `terraform apply` not run** |

---

## Known Limitations (honest)

1. PoC F1 near zero (majority-class collapse on synthetic 20-feature sample)
2. Improved variant uses **more** communication MB/round than baseline in the committed PoC (larger CNN-LSTM), not a −45% win
3. No Docker/K8s/AWS production evidence
4. No centralised IDS comparator
5. Terraform not applied (alignment-first gate)

---

## Remaining blockers to 100% (non-AWS first, then AWS residual)

1. Keep report/STATUS/README metrics locked to `results.json` (no 91–94% as “achieved”)
2. Centralised IDS baseline (CA2 comparator gap)
3. Real UNSW-NB15 (or documented equivalent) experiment
4. DOI `note={doi:...}` hygiene if required by cohort rule
5. **AWS residual (yes):** live cloud-native FL evaluation once alignment-first gate allows — Terraform ready, not applied

---

## Build / run (local only)

```bash
cd Nemi/securefl-ids
make pilot      # local PoC
make test
# Do NOT terraform apply until alignment gate + budget approval
```

**Last Updated:** 2026-09-20  
**Status:** Claim hygiene raised; CA2 alignment **not** 100%
