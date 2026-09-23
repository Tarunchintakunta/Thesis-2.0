# Varun r4+r5 independence remediable audit (scripted)

Generated: `2026-09-23T07:49:30.525659+00:00`
Live root: `/Users/valletivarish/Documents/Thesis-2.0/Varun/s3-predictive-optimization/results/live`

## Move gate

- **remediable_total:** 0
- **move_blocker:** False
- **disposition:** `DATED_WONTFIX_ALLOC_ACC`
- **alloc_acc_weak_vs_lifecycle:** True
- **destroy_ok:** True

## SHA inventory

```json
{
  "1": "dbc3c0f1d944b644a052e641d53195d6f9a1a505",
  "2": "dbc3c0f1d944b644a052e641d53195d6f9a1a505",
  "3": "dbc3c0f1d944b644a052e641d53195d6f9a1a505",
  "4": "7babd39cee64656b34bc876a34b645e2b460c3a5",
  "5": "53bec5e526389e479ef524c67be2a7dafe65cfd5"
}
```

## Remediable bag

```json
{}
```

## Findings

- `archival_r1_r3_identical_ok` remediable=False eval=-
- `indep_sha_ok` remediable=False eval=4
- `indep_sha_ok` remediable=False eval=5
- `r4_r5_distinct_sha` remediable=False eval=-
- `rebuilt_from_run_log_false` remediable=False eval=4
- `meets_ca2_ok` remediable=False eval=4
- `wilcoxon_consistent` remediable=False eval=4
- `wilcoxon_consistent` remediable=False eval=4
- `wilcoxon_consistent` remediable=False eval=4
- `rebuilt_from_run_log_false` remediable=False eval=5
- `meets_ca2_ok` remediable=False eval=5
- `wilcoxon_consistent` remediable=False eval=5
- `wilcoxon_consistent` remediable=False eval=5
- `wilcoxon_consistent` remediable=False eval=5
- `destroy_confirmed` remediable=False eval=-
- `alloc_acc_weaker_than_lifecycle` remediable=False eval=-
- `dated_wontfix_alloc_acc_present` remediable=False eval=-
- `dryrun_improved_alloc_acc` remediable=False eval=-

```bash
cd Varun/s3-predictive-optimization
python3 scripts/audit_independence_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

