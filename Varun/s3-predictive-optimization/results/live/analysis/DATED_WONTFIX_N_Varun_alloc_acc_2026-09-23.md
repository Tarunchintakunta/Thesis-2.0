# DATED_WONTFIX — N-Varun allocation-accuracy limb (2026-09-23)

**Item:** RQ limb “improve storage-class allocation accuracy vs AWS Lifecycle / Intelligent-Tiering”  
**Artefacts:** `results/live/allocation_accuracy_r4_r5_offline.json` + dry-run `results/data/improved_results.json`  
**Script:** `scripts/audit_independence_root_causes.py` → disposition `DATED_WONTFIX_ALLOC_ACC` when `remediable_total=0`

## Evidence (not remediable in-code)

| Pack / arm | Proposed Acc | Lifecycle Acc | Δ (prop−LC) |
|------------|-------------:|--------------:|------------:|
| Offline r4 (seed 4242) | **0.369** | **0.854** | **−0.485** |
| Offline r5 (seed 5252) | **0.345** | **0.853** | **−0.508** |
| Dry-run improved ML | **0.178** | (heuristic oracle) | weak |

Protocol: offline seed regeneration vs pattern oracle (`hot→STANDARD`, `warm→STANDARD_IA`, `cold→GLACIER_*`). Not HeadObject-derived production labels.

## Why WONTFIX (not silent soft)

| Check | Result |
|-------|--------|
| Cost Wilcoxon limb (r4+r5) | **Supported** — both `meets_ca2_two_of_three=true` (3/3) |
| Alloc-acc vs Lifecycle | **Negative** — evidenced; inventing labels or flipping metrics would fabricate a win |
| Live HeadObject alloc metric | Would need a **new** instrumented AWS pack — beyond disclosed confirmatory floor |
| Marketing “allocation improved” | **Forbidden** |

## Retain honesty

- Confirmatory claim = modeled cost cut vs Lifecycle **and** Intelligent-Tiering under `ca2_three_workload_wilcoxon`.
- Allocation-accuracy RQ limb is **falsified / weak** on available artefacts — dated here so MOVE is not blocked by a remediable silence.
