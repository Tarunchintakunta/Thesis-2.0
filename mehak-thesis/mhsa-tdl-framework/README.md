# MHSA-TDL: Cluster health prediction artefact (Mehak)

MSc Cloud Computing thesis codebase for **formal CA2** (`MAHEK NAAZ.docx`): MHSA-TDL for cloud cluster health / failure prediction on **Google Cluster Trace**, metrics Acc/Prec/Rec/F1/ROC-AUC/latency, vs hybrid + traditional monitors.

## Alignment honesty
| Formal CA2 | This repo today |
|------------|-----------------|
| Google Cluster Trace | **Missing** — see `../DATA_GAPS.md`; `src/data/gct_loader.py` fails closed |
| Acc/Prec/Rec/F1/ROC-AUC/latency | **Wired** in `scripts/train_and_evaluate.py` |
| Aldomi / RF·KNN·SVM·GRU | RF/KNN/SVM **scaffold** on synthetic; full Aldomi+GCT **blocked** |
| Thapliyal underprediction proxy | **Superseded** — related architecture only |

Synthetic 5-seed CSVs under `results/` are **artefact-as-built**, not formal GCT evidence (`results/RESULTS_PROVENANCE.md`).

## Layout
- `src/data/telemetry_simulator.py` — synthetic generator (dev only)
- `src/data/gct_loader.py` — GCT presence gate (no invented windows)
- `src/models/mhsa_model.py` — MHSA-PerHead / MHSA-Fused
- `src/models/baseline.py` — reactive threshold monitor
- `src/models/classical_baselines.py` — RF / KNN / SVM scaffold
- `scripts/train_and_evaluate.py` — 5-seed eval; `--dataset synthetic|gct`
- `template.yaml` / Lambda — **optional; not required by formal CA2**

## Usage
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/train_and_evaluate.py              # synthetic harness
.venv/bin/python scripts/train_and_evaluate.py --dataset gct # requires DATA_GAPS files
```

## AWS
Formal resources list Colab **or** EC2 GPU as training compute alternatives. **Do not deploy** Lambda/SAM for alignment.
