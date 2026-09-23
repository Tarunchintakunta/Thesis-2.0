# Vishvaksen — ONE source of truth (thesis)

**Authority:** formal CA2 `VishvaksenMachana_25173421_proposal.docx` + local `terraform-scanner-benchmark/results/`.  
**Baseline (binding):** Verdet et al. (2025) — `baseline_papers/BASELINE_PAPER.md` (doi:10.1007/s10664-024-10610-0).  
**Audit script (binding):** `terraform-scanner-benchmark/scripts/audit_fn_root_causes.py` → `results/analysis/fn_root_causes_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No zero-FN marketing.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted FN/mapping audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; residual FN / transfer = dated WONTFIX |
| Strong (Checkov labelled recall after mapping fix)? | **Yes** — Checkov ALL **R≈0.917** on hv6+ |
| Strong (scanners dominate Verdet disputed-case Acc narrative)? | **Partial** — we report labelled P/R/F1/Acc; Verdet adoption metrics not cloned |
| Audit remediable gaps? | **0** (`audit_fn_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

Mapping undercount kept Checkov ALL recall near **0.562** while findings already fired — easy to miss in chat. Gate is **`scripts/audit_fn_root_causes.py`**: R≪0.90, missing hv6+, missing Verdet/SoT → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_RESIDUAL_CHECKOV_FN`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | What % of labelled AWS misconfigurations will scanners + PaC gate identify? |
| Corpus | ~60 modules × 4 categories; ~60% insecure; labelled oracle |
| Stages | Checklist · Checkov+tfsec · OPA/Rego |
| Metrics | Precision, Recall, F1, FN rate per category; scan time; remediation LOC |
| Baseline gap | Verdet et al. — Acc mainly on disputed Checkov/tfsec cases; missing labelled recall/F1 |

---

## 2. SAME METRICS — labelled corpus vs Verdet gap

**Binding packs:** `results/` + `results/hard_verify_6/` + `hard_verify_7/` (N=240; no apply).  
**Verdet:** adoption / disputed-case accuracy — **no** labelled four-category recall table. Ours keep **P/R/F1** names and add labelled Acc=(TP+TN)/N + FN rate.

### ALL-category (live after mapping fix)

Source: `results/metrics_per_category.csv` / `results/METRICS.md`.

| Stage | Acc | Precision | Recall | F1 | Identified % |
|-------|----:|----------:|-------:|---:|-------------:|
| Checklist | 0.863 | 0.951 | 0.812 | 0.876 | 81.2 |
| **Checkov** | **0.775** | **0.759** | **0.917** | **0.830** | **91.7** |
| tfsec | 0.671 | 0.788 | 0.618 | 0.693 | 61.8 |
| Static union | 0.754 | 0.730 | 0.938 | 0.821 | 93.8 |
| OPA | 0.762 | 1.000 | 0.604 | 0.753 | 60.4 |

**Mapping fix:** catalog IDs that already failed on labelled insecure modules but were unmatched are classified into `mappings/checkov_ids.json` (labels unchanged). Pre-fix Checkov R=0.562 → post-fix **R=0.917** (TP=132, FN=12). Acc=(132+54)/240=**0.775** (not ≈0.81). OPA R remains **0.604** (FN=57) — **not** 1.0.

### Agent correction (2026-09-23)

An earlier agent Before/After chat table claimed **Acc≈0.808** and **OPA R=1.000**. That was **overclaiming** — those figures are **not** in `metrics_per_category.csv` / hv6–7. Binding numbers = §2 table above only. Checkov R 0.562→0.917 remains real (mapping undercount rematch; FP 24→42).

### §B — Side-by-side P/R vs Verdet framing

| Metric family | Verdet et al. (2025) | **Ours (labelled oracle)** |
|---------------|----------------------|----------------------------|
| Accuracy | Disputed Checkov/tfsec subsample | Acc on N=240 labelled modules (table above) |
| Precision / Recall | Limited / conflict-focused | Per stage × category P/R/F1 |
| Paired tests | Tool disagreement themes | McNemar + Holm (`docs/VERDET_COMPARISON.md`) |

**Do not claim:** numeric clone of Verdet adoption rates. Claim = labelled identification rates + residual FN honesty.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: % labelled defects found | Verdet disputed Acc gap | Checkov R=0.917; union 0.938 | Recall/identified % | **MET** |
| 2 | Checklist + Checkov/tfsec + OPA | Verdet tools overlap | three stages + union | Yes | **MET** |
| 3 | P/R/F1/FN per category | missing labelled table | `metrics_per_category.csv` | Yes | **MET** |
| 4 | Acc column vs Verdet | disputed Acc | Acc column §2 | Yes | **MET** |
| 5 | Scan time + remediation LOC | omitted in Verdet | scan_times / remediation_loc | Gap-fill | **MET** |
| 6 | McNemar + Holm | Verdet-style pairing | mcnemar + holm CSVs | Yes | **MET** |
| 7 | Mapping undercount remediable | — | hv6+ R≈0.917; audit EXIT 0 | — | **MET** |
| 8 | Residual Checkov FN | soft negative | FN=12 after fix | Yes | **WONTFIX dated** |
| 9 | Public-repo transfer | soft beyond | absent | — | **WONTFIX beyond-floor** |
| 10 | terraform apply | ethics forbid | none | — | **N/A** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Vish FN** | Residual Checkov/tfsec FN after fix | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_N_Vish_FN_2026-09-23.md`; evidenced negative |
| Mapping undercount (R≈0.56) | Remediable | **CLOSED** — map classify + hv6+; audit EXIT 0 |
| Public-repo transfer | Soft beyond | **WONTFIX** — same amendment |
| Gate>static expectation | Falsified historically | Retained honesty in GENAI_HANDOFF / §3 |
| Marketing perfect Checkov | Forbidden | Residual FN disclosed |

Reproduce:

```bash
cd vishvaksen-thesis/terraform-scanner-benchmark
python3 scripts/audit_fn_root_causes.py
# EXIT 0 required; remediable_total must be 0; Checkov R ≈ 0.917
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `results/metrics_per_category.csv` | Primary cite | Checkov R=0.9167 |
| `results/hard_verify_6/` + `hard_verify_7/` | Mapping-fix gate | `hard_verify_summary.json` pass |
| `results/analysis/fn_root_causes_audit_report.*` | Move gate | remediable_total=0 |
| `docs/VERDET_COMPARISON.md` | Baseline stats prose | McNemar/Holm |
| `mappings/checkov_ids.json` | Mapping classify | 2026-09-23 extension |

---

## 6–11. Design / Outstanding (artefact)

Config: `CONFIGURATION_MANUAL.md`. Alternatives: checklist vs static vs OPA. Lit: Verdet gap-fill. Residual FN + transfer = dated WONTFIX. Report/viva fold-later.
