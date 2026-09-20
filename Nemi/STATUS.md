# SecureFL-IDS Project Status

**Student:** Nemi Ishwarlal Vikani (24303046)  
**Programme:** MSc Cloud Computing  
**Institution:** National College of Ireland

**Project:** SecureFL-IDS — Privacy-Preserving Federated Intrusion Detection for Cloud-Native Environments

## Overall Status: NOT COMPLETE (CA2 alignment < 100%)

**Research alignment (claim hygiene pass):** ~68% — PoC metrics locked to `results/comparison/results.json`; methodology demoted (synthetic PoC, not full UNSW / 50 rounds); Docker/K8s/AWS overclaims removed; DOI `note={doi:…}` verified on wired `refs.bib`.  
**Not SUBMIT-READY for CA2.** Non-AWS blockers remain (centralised IDS + full UNSW-NB15) before sole-AWS residual.

---

## Component Status

### 1. Research & Literature Review
- [x] Literature review and baseline paper (Saklani et al. 2026)
- [x] Research gaps and RQ formulated
- [x] WhatsApp DOI `note={doi:...}` present on wired scholarly entries in `latex_report/refs.bib`

### 2. Artefact Implementation

#### Code Structure
- [x] `securefl-ids/` with baseline, improved, and common modules
- [x] Unit tests present (`tests/`)
- [x] Experiment scripts and docs
- [x] Terraform scaffold at `securefl-ids/terraform/` (**exists; not applied** — no live AWS; no student name/ID tags)

#### Baseline / Improved (PoC only)
**Authoritative:** `results/comparison/results.json` (synthetic data, 30 rounds, 5 clients):

| Metric | Baseline | Improved |
|--------|----------|----------|
| Accuracy | **0.793** (~79.3%) | **0.800** (~80.0%) |
| F1-Score | ~0.019 (~1.9%) | **0.0** |
| Avg Comm (MB/round) | 1.83 | 3.12 |

**Do not cite** `results/pilot/pilot_results.json` (10-round smoke; baseline acc 0.4) as the CA2 PoC.  
**Do not cite** literature-style 91–94% accuracy, ~90% F1, or −45% communication as *achieved* results.

### 3. Experiments & Evaluation
- [x] Local PoC experiment committed (`results/comparison/results.json`)
- [x] Honest limitations in `RESULTS_NOTE.md`
- [ ] Full UNSW-NB15 (49 features / large sample) not run
- [ ] Centralised IDS baseline not implemented
- [ ] No live AWS / ECS / Kubernetes evaluation

### 4. Documentation
- [x] README, CONFIGURATION_MANUAL, ARCHITECTURE, RESULTS_NOTE
- [x] LaTeX report draft present (methodology aligned to PoC)
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
2. Improved variant uses **more** communication MB/round than baseline in the committed PoC
3. No Docker/K8s/AWS production evidence
4. No centralised IDS comparator
5. Terraform not applied (alignment-first gate)

---

## Remaining blockers to 100%

**Non-AWS (still open — blocks sole-AWS residual):**
1. Centralised IDS baseline (CA2 comparator gap) — no artefact path
2. Real UNSW-NB15 (or documented equivalent) experiment — not in `results/`

**AWS residual (yes, not sole):**
3. Live cloud-native FL evaluation — Terraform ready, not applied

Claim hygiene (metrics lock, DOI, overclaim demotion) is closed.

---

## Build / run (local only)

```bash
cd Nemi/securefl-ids
make pilot      # local PoC
make test
# Do NOT terraform apply until alignment gate + budget approval
```

**Last Updated:** 2026-09-20  
**Status:** Claim hygiene raised (~68%); CA2 alignment **not** 100%; SOLE_AWS_RESIDUAL=no
