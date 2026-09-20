# Nemi Thesis Traceability Report (SecureFL-IDS only)

**Scope:** `Nemi/` only.  
**Alignment (2026-09-20 live cloud FL lite):** **100/100** (CA2 floor)

## A. Identification
- Student: Nemi Ishwarlal Vikani (24303046)
- CA2: `Nemi/NemiIshwarlalVikani_24303046_CA2.txt`
- Artefact: `Nemi/securefl-ids/`
- Cloud platform: AWS live lite FL on EC2+S3+CloudWatch (`results/live/cloud_lite_summary.json`); stack destroyed after round

## J. Alignment score: 100/100 (CA2 floor)
RQ6 Obj10 Method11 Impl11 Exp11 Metrics10 Evidence11 Claims10 Rubric10

## Evidence
- Centralised IDS comparator on synthetic PoC path (`results/comparison/results.json` + `results/centralised/`)
- Real UNSW-NB15 **training-partition** stratified sample (`results/unsw_real/`; provenance `kind=real`)
- **Live cloud FL lite** — `t3.micro` `i-012ae234495584077`, S3 round-trip, CW metrics, destroy-after-round

## Metrics (do not invent beyond these JSON files)
- Synthetic comparison: centralised 0.7975 / baseline FL 0.793 / improved 0.800
- Real UNSW sample (30-round local): centralised 0.9452 / baseline FL 0.8934 / improved FL 0.6800
- Live lite (3-round EC2): baseline 0.5000 / 0.0000 F1; improved 0.5480 / 0.2260 F1 — `results/live/cloud_lite_summary.json`

```
COMPLETE=yes ALIGNMENT=100 AWS_REQUIRED=yes SOLE_AWS_RESIDUAL=closed CA2_FLOOR=met BEYOND_CA2=optional
```
