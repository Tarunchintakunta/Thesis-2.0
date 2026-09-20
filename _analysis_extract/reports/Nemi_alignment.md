# Nemi Thesis Traceability Report (SecureFL-IDS only)

**Scope:** `Nemi/` only.  
**Alignment after non-AWS evidence pass (2026-09-20):** **~78/100** (was 44% → 58% → 64% → 68%)

## A. Identification
- Student: Nemi Ishwarlal Vikani (24303046)
- CA2: `Nemi/NemiIshwarlalVikani_24303046_CA2.txt`
- Artefact: `Nemi/securefl-ids/`
- Cloud platform: AWS intended for CA2 cloud-native FL; **Terraform at `securefl-ids/terraform/` exists but not applied**

## J. Alignment score (post non-AWS evidence): ~78/100
RQ6 Obj10 Method11 Impl11 Exp9 Metrics8 Evidence9 Claims7 Rubric7

## Evidence closed this pass
- Centralised IDS comparator on synthetic PoC path (`results/comparison/results.json` + `results/centralised/`)
- Real UNSW-NB15 **training-partition** stratified sample (`results/unsw_real/`; provenance `kind=real`)
- Makefile packaging (`centralised`, `unsw-real`); download script prefers real mirrors

## Metrics (do not invent beyond these JSON files)
- Synthetic comparison: centralised 0.7975 / baseline FL 0.793 / improved 0.800
- Real UNSW sample: centralised 0.9452 / baseline FL 0.8934 / improved FL 0.6800

## Critical gap remaining
- **AWS residual: yes — sole** (live cloud FL). Terraform not applied.

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=yes READY_FOR_AWS=yes
```
