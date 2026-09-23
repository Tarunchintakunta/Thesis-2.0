# Configuration manual — Vishvaksen Terraform scanner benchmark

**Artefact:** `vishvaksen-thesis/terraform-scanner-benchmark/`  
**Ethics:** labelled corpus evaluation only — **no `terraform apply`**.

## Environment
```bash
cd vishvaksen-thesis/terraform-scanner-benchmark
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# pins: Checkov 3.3.19, OPA 1.4.2 (see results/tool_versions.json)
```

## Full local pipeline
```bash
python3 scripts/run_all.py
# or stepwise: generate_corpus → run_checklist → run_checkov → run_tfsec → run_opa → evaluate
```

## Mapping fix re-score (no re-label)
If Checkov fired findings but category maps missed catalog IDs (FN undercount):
1. Extend `mappings/checkov_ids.json` with fired IDs for the module’s category only.
2. Re-score from `results/raw/checkov_batch.json` (do not invent labels).
3. `python3 scripts/evaluate.py`
4. Snapshot `results/hard_verify_6/` (+ `hard_verify_7`).

## Remediable audit (move gate)
```bash
python3 scripts/audit_fn_root_causes.py
# EXIT 0 required; remediable_total must be 0; Checkov ALL R ≈ 0.917
```

## Baseline
Verdet et al. (2025) — `baseline_papers/BASELINE_PAPER.md` + `docs/VERDET_COMPARISON.md`.
