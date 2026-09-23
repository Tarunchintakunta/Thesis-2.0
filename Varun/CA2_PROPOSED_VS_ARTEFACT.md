# Varun — ONE source of truth (S3 predictive cost optimisation)

**Authority:** formal CA2 `VarunGampa_RIC_CA2.txt` + live `s3-predictive-optimization/results/live/`.  
**Baseline (binding):** Shen et al. (2025) TierBase — `baseline_papers/BASELINE_PAPER.md` (doi:10.1109/ICDE65448.2025.00049).  
**Audit script (binding):** `s3-predictive-optimization/scripts/audit_independence_root_causes.py` → `results/live/analysis/independence_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated alloc-acc wins / marketing 100.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted independence audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; alloc-acc = dated WONTFIX |
| Strong (cost cut vs Lifecycle **and** IT, ≥2/3 workloads)? | **Yes** — independent r4+r5 both `meets_ca2_two_of_three=true` (3/3) |
| Strong (allocation accuracy improves vs natives)? | **No** — offline r4/r5 proposed Acc ≪ Lifecycle; dry-run improved Acc=0.178 |
| Audit remediable gaps? | **0** (`audit_independence_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

Manual “r4/r5 look independent” was how archival r1–r3 almost counted as three evals with identical SHA. Independence is gated by **`scripts/audit_independence_root_causes.py`**: SHA collapse, `rebuilt_from_run_log`, `meets_ca2` inconsistency, Wilcoxon recompute mismatch, missing destroy → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_ALLOC_ACC`**.

---

## 1. CA2 proposed (fresh from formal extract)

| Item | Formal CA2 |
|------|------------|
| RQ | Integrated predictive storage-class framework — reduce S3 **cost** and improve **allocation accuracy** vs Lifecycle + Intelligent-Tiering in **live AWS** |
| Modules | Metadata + rule/ML recommender + time-series forecast + savings estimator + reporting |
| Workloads | static/archival, mixed-access, high-churn |
| Metrics | Allocation accuracy; forecast MAPE/RMSE vs **naive persistence**; realised USD/% vs Lifecycle & IT; operational overhead |
| Stats | Paired Wilcoxon α=0.05; success = sig cost cut vs **both** natives on **≥2 of 3** workloads + forecast beats naive |
| Baseline lit | Shen et al. TierBase (workload-driven cost-optimised placement) |

---

## 2. SAME METRICS — confirmatory live + dry-run vs natives / naive / TierBase gap

**Binding confirmatory packs:** `evaluation_r4` + `evaluation_r5` (destroy-after; distinct `raw_costs` SHA).  
**Archival only:** `evaluation_r1|r2|r3` — identical SHA `dbc3c0f1…`, `rebuilt_from_run_log=true` — **do not** cite as independent.  
**Shen/TierBase:** KV-store tiering paper — gap-fill is **S3 class + live Wilcoxon vs AWS natives**, not numeric clone of TierBase internal metrics.

### Live cost Wilcoxon (primary DV) — r4 / r5

| Workload | r4 ΔLC / p / both? | r5 ΔLC / p / both? |
|----------|--------------------|--------------------|
| static_archival | ≈0.00249 / 0.00195 / **Yes** | ≈0.00267 / 0.00195 / **Yes** |
| mixed_access | ≈0.00238 / 0.00195 / **Yes** | ≈0.00234 / 0.00195 / **Yes** |
| high_churn | ≈0.00013 / 0.0488 / **Yes** | ≈0.00025 / 0.0098 / **Yes** |
| `meets_ca2_two_of_three` | **true** (3/3) | **true** (3/3) |

Modeled monthly $ via SavingsEstimator — **not** CE-settled per-object bills (disclosed).

### Forecast vs naive (dry-run; Beck et al. gate)

| Arm | MAPE | Naive MAPE | Beats naive |
|-----|-----:|-----------:|:-----------:|
| Pilot | 0.016 | 0.44 | **Yes** |
| Baseline rules | 0.006 | 0.44 | **Yes** |
| Improved ML | 0.231 | 0.44 | **Yes** |

### Allocation accuracy (RQ limb — negative retained)

| Source | Proposed Acc | Lifecycle Acc | Verdict |
|--------|-------------:|--------------:|---------|
| Offline r4 | 0.369 | 0.854 | **Worse than LC** |
| Offline r5 | 0.345 | 0.853 | **Worse than LC** |
| Dry-run improved | 0.178 | heuristic oracle | **Weak** |

**Verdict:** Cost limb **supported** on independent live packs. Alloc-acc limb **falsified / weak** — dated WONTFIX, not marketed.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: cost + alloc-acc vs LC & IT live | TierBase placement theme | r4+r5 Wilcoxon cost; offline alloc | Cost yes; alloc named | **MET (cost) / FALSIFIED (alloc)** |
| 2 | Three workloads | CA2 §3.3 | static / mixed / high_churn | Yes | **MET** |
| 3 | Wilcoxon ≥2/3 vs both natives | CA2 success gate | `meets_ca2_two_of_three=true` ×2 indep | Yes | **MET** |
| 4 | Forecast beats naive | Beck et al. 2025 | dry-run `beats_naive=true` ×3 | MAPE | **MET** |
| 5 | Allocation accuracy improve | vs LC/IT / labelled set | offline oracle + dry-run | Acc | **WONTFIX dated** |
| 6 | Independent confirmatory evals | — | r4 SHA `7babd39c…` ≠ r5 `53bec5e5…` | — | **MET** (audit) |
| 7 | Archival r1–r3 as ×3 indep | — | identical SHA + rebuild | — | **Rejected / history** |
| 8 | Destroy-after | ethics | empty TF state + `destroy_confirmed.txt` | — | **MET** |
| 9 | CE-settled production bills | CA2 billing lag note | probe only | Partial | **WONTFIX non-claim** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Varun-alloc** | Alloc-acc vs Lifecycle | **DATED_WONTFIX 2026-09-23** — `results/live/analysis/DATED_WONTFIX_N_Varun_alloc_acc_2026-09-23.md`; script disposition |
| Archival r1–r3 independence | Identical SHA | **Closed** — history only (`FINAL3_NOTE.md`) |
| high_churn on archival e1–e3 | Null vs LC | Superseded by r4/r5 (sig retained); archival null still disclosed in `BASELINE_COMPARE.md` |
| Marketing 100 / alloc solved | Forbidden | Honest floor ~88 |
| CE-settled campaign $ | Not demonstrated | Disclosed non-claim |

Reproduce:

```bash
cd Varun/s3-predictive-optimization
python3 scripts/audit_independence_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `results/data/*_results.json` | Dry-run MAPE / alloc | `beats_naive=true` |
| `results/live/live_lite_*` | Live smoke | 48 objects; destroy complete |
| `evaluation_r1`–`r3` | Archival | Identical raw SHA; not confirmatory |
| **`evaluation_r4`** | **Cite** | Seed 4242; SHA `7babd39c…`; `rebuilt_from_run_log=false` |
| **`evaluation_r5`** | **Cite** | Seed 5252; SHA `53bec5e5…`; `rebuilt_from_run_log=false` |
| `allocation_accuracy_r4_r5_offline.json` | Alloc limb | Negative vs Lifecycle |
| `analysis/independence_audit_report.*` | Scripted gate | EXIT 0 |

---

## 6. Thesis gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Varun-alloc hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs natives / naive | **Yes** |
| Configuration manual audit section | **Yes** |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (cost vs LC/IT; MAPE vs naive) | **Filled** — §2; TierBase = placement gap-fill |
| Alts / synth | Dry-run = method; live r4/r5 = evidence |
| Config manual | `s3-predictive-optimization/docs/CONFIGURATION_MANUAL.md` § audit |
| Claim↔evidence | Cost reject; alloc WONTFIX retained honestly |
| Accidental silent park | Forbidden — N-Varun-alloc dated in §4 |

---

## 8. Honest CA2 floor

**~88.** Independent r4+r5 cost gate landed; forecast beats naive on dry-run; **allocation-accuracy limb not supported**. Do **not** market 100.
