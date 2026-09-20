# Nemi alignment residual (AWS-goal — sole live cloud FL)

**Updated:** 2026-09-20  
**Alignment after non-AWS evidence pass:** **~78/100** (was ~68%)

## Compact
`RQ6 Obj10 Method11 Impl11 Exp9 Metrics8 Evidence9 Claims7 Rubric7` → **~78/100**

## Closed this pass (evidence only — no invented metrics)
1. **Centralised IDS comparator** — `src/centralised/`, `scripts/run_centralised.py`, `results/centralised/`, merged into `results/comparison/results.json`  
   Synthetic (sample 10k / 30 epochs): acc **0.7975**, F1 **≈0.015**, comm **0.0** MB/round (N/A)
2. **Real UNSW-NB15 training-partition sample** — `scripts/download_data.py --real`, `scripts/run_unsw_real.py`, `results/unsw_real/`  
   Provenance `kind=real` (~175341×45). Stratified 25k / 39 numeric features / 30 rounds:  
   centralised **0.9452 / 0.9603**; baseline FL **0.8934 / 0.9262**; improved FL **0.6800 / 0.8095**
3. Packaging: Makefile `centralised` / `unsw-real`; non-IID empty-client fix; README download path

## Sole residual to 100%
1. **Live cloud-native FL evaluation** — `securefl-ids/terraform/` scaffold present, **not applied**

**AWS residual:** yes (cloud FL) — **sole**

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=yes READY_FOR_AWS=yes
```

Do **not** `terraform apply` / start live AWS FL while shared-account concurrency is hot (Vikas r5 RUNNING).  
**Prep this pass:** `Nemi/CLOUD_FL_PREP.md`; `terraform/preflight.sh` (`terraform validate` only). No live cells.
