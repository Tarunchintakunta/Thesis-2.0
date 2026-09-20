# Nemi Thesis Traceability Report (SecureFL-IDS only)

**Scope:** `Nemi/` only.  
**Alignment after claim hygiene (2026-09-20):** **~58/100** (was 44%)

## A. Identification
- Student: Nemi Ishwarlal Vikani (24303046)
- CA2: `Nemi/NemiIshwarlalVikani_24303046_CA2.txt`
- Artefact: `Nemi/securefl-ids/`
- Cloud platform: AWS intended for CA2 cloud-native FL; **Terraform at `securefl-ids/terraform/` exists but not applied**

## J. Alignment score (post claim hygiene): ~58/100
RQ5 Obj8 Method8 Impl10 Exp6 Metrics8 Evidence5 Claims5 Rubric3

## Claim hygiene done
- Abstract / intro / eval / conclusion / STATUS / README / RESULTS_NOTE / ARCHITECTURE / CONFIGURATION_MANUAL aligned to PoC `results/comparison/results.json` (accuracy ~0.793/0.800, F1 near 0; improved comm **higher**)
- Removed Docker / K8s / Helm / live AWS / production overclaims
- Noted Terraform scaffold present, **not applied**
- STATUS: **NOT COMPLETE / <100%**, not SUBMIT-READY

## Critical gaps remaining
- Centralised IDS baseline still missing
- Real UNSW-NB15 full run not executed
- DOI `note={doi:...}` format may still need bib pass
- **AWS residual: yes** (live cloud FL once gate allows)

```
GATE_READY=no AWS_CLASS=required SOLE_AWS_RESIDUAL=no
```
