# Nemi Thesis Traceability Report (SecureFL-IDS only)

**Scope:** `Nemi/` only.  
**Alignment after claim hygiene (2026-09-20):** **~68/100** (was 44% → 58% → 64%)

## A. Identification
- Student: Nemi Ishwarlal Vikani (24303046)
- CA2: `Nemi/NemiIshwarlalVikani_24303046_CA2.txt`
- Artefact: `Nemi/securefl-ids/`
- Cloud platform: AWS intended for CA2 cloud-native FL; **Terraform at `securefl-ids/terraform/` exists but not applied**

## J. Alignment score (post claim hygiene): ~68/100
RQ6 Obj9 Method10 Impl10 Exp6 Metrics8 Evidence7 Claims7 Rubric5

## Claim hygiene done
- Abstract / intro / eval / conclusion / STATUS / README / RESULTS_NOTE / ARCHITECTURE aligned to PoC `results/comparison/results.json` (accuracy ~0.793/0.800, F1 near 0; improved comm **higher**)
- Methodology: synthetic PoC / 30 rounds; full UNSW and 50-round configs demoted; pilot smoke quarantined
- Removed Docker / K8s / Helm / live AWS / production overclaims; README 91–94% demoted to literature-only
- Noted Terraform scaffold present, **not applied**; bib `note={doi:…}`
- STATUS: **NOT COMPLETE / <100%**, not SUBMIT-READY

## Critical gaps remaining
- Centralised IDS baseline still missing (**non-AWS**)
- Real UNSW-NB15 full run not executed (**non-AWS**)
- **AWS residual: yes** (live cloud FL) — **not sole**

```
GATE_READY=no AWS_CLASS=required SOLE_AWS_RESIDUAL=no READY_FOR_AWS=no
```
