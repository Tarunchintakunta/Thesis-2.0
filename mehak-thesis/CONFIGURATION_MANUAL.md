# Configuration manual — Mehak MHSA-TDL (local GCT)

**Artefact:** `mehak-thesis/mhsa-tdl-framework/`  
**Compute:** local / Colab-class CPU; **no AWS deploy required** for CA2.

## Environment
```bash
cd mehak-thesis/mhsa-tdl-framework
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Data
- Official ClusterData 2011 parts under `data/gct/2011/` (4 `task_events` + 2 `task_usage` in scored subset).
- Channel honesty: `data/gct/CHANNEL_HONESTY.md` (`net` = sampled CPU, not bytes).

## Train / evaluate (formal metric suite)
```bash
python3 scripts/train_and_evaluate.py \
  --dataset gct --epochs 15 --max-windows 12000 \
  --seeds 42,43,44,45,46 \
  --out-dir results/gct/final_1
```

Hard-verify packs (negative MHSA Acc check):
```bash
for i in 1 2 3 4 5; do
  python3 scripts/train_and_evaluate.py --dataset gct --epochs 15 \
    --max-windows 12000 --seeds 42,43,44,45,46 \
    --out-dir results/gct/hard_verify_$i
  python3 scripts/write_hard_verify_summary.py results/gct/hard_verify_$i
done
```

## Remediable audit (move gate)
```bash
python3 scripts/audit_mhsa_negative_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

## Pins / honesty
- Baseline: Aldomi et al. (2026) SelectKBest+GRU-RF/KNN family — `baseline_papers/BASELINE_PAPER.md`
- Soft: full dump / 2019 / true net-bytes = `DATED_WONTFIX_M2_M3_2026-09-23.md`
