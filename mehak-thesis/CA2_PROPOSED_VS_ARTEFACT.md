# Mehak — ONE source of truth (thesis)

**Authority:** formal CA2 `MAHEK NAAZ.docx` + local `mhsa-tdl-framework/results/gct/`.  
**Baseline (binding):** Aldomi et al. (2026) — `baseline_papers/BASELINE_PAPER.md` (doi:10.1016/j.sasc.2026.200442). Thapliyal = related architecture only.  
**Audit script (binding):** `mhsa-tdl-framework/scripts/audit_mhsa_negative_root_causes.py` → `results/gct/analysis/mhsa_negative_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated MHSA wins.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted MHSA-negative audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; net-bytes = dated WONTFIX |
| Strong (MHSA Acc/P/R/F1/AUC beats Aldomi/RF)? | **No** — MHSA Acc **below** Aldomi GRU-RF and RF on final-3 + hv1–5 |
| Strong (GCT metric suite vs hybrid/classical)? | **Yes** — Acc/P/R/F1/AUC + latency on disclosed 2011 subset |
| Audit remediable gaps? | **0** (`audit_mhsa_negative_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

“MHSA looks close / maybe wins on Fail-F1” was how soft negatives get marketed. Gate is **`scripts/audit_mhsa_negative_root_causes.py`**: missing hv packs, `mhsa_beats_*=true`, Thapliyal-as-baseline, missing net-bytes WONTFIX / SoT → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_NET_BYTES_SCHEMA`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | Performance of **MHSA-TDL** predicting cluster health / failures from cloud telemetry vs **hybrid DL** and **traditional** monitors |
| Dataset | Google Cluster Trace |
| Metrics | Accuracy, Precision, Recall, F1, ROC-AUC, prediction latency |
| Baselines | Aldomi-style hybrid + RF/KNN/SVM (GRU-style monitors) |
| Proposed | Multi-head self-attention over multi-metric windows (CPU, mem, disk, network, scheduling) |

---

## 2. SAME METRICS — GCT final / hard-verify vs Aldomi + RF

**Binding packs:** `results/gct/final_1|2|3/` + `hard_verify_1..5/` (seeds 42–46, epochs=15, N=12000).  
**Aldomi paper:** SelectKBest+GRU+RF/KNN on GCT — we keep **same metric names**; not a 2019 Borg hyperparameter clone.  
**Channel honesty:** `net` = sampled CPU (`net_channel_is_network_bytes=false`).

### Mean ± std (seeds 42–46) — Acc / P / R / Macro-F1 / ROC-AUC

Source: `results/gct/final_1/results_summary.csv` (final_2/final_3 identical at reported precision; hv1–5 `mhsa_beats_*=false`).

| Model | Acc | Precision | Recall | Macro-F1 | ROC-AUC | Fail-F1 |
|-------|----:|----------:|-------:|---------:|--------:|--------:|
| **RF (classical)** | **0.9439±0.0022** | 0.8805±0.0086 | 0.6087±0.0111 | 0.6701±0.0129 | **0.8123±0.0516** | 0.5154±0.0312 |
| **Aldomi GRU-RF** | **0.9425±0.0006** | 0.8332±0.0090 | **0.6197±0.0058** | **0.6764±0.0054** | 0.7531±0.1275 | **0.5244±0.0095** |
| Aldomi GRU-KNN | 0.9403±0.0012 | 0.8282±0.0146 | 0.6073±0.0090 | 0.6623±0.0091 | 0.7243±0.0715 | 0.4958±0.0216 |
| MHSA-Fused (proposed) | 0.9223±0.0016 | 0.6841±0.0083 | 0.5809±0.0057 | 0.6130±0.0063 | 0.6172±0.1054 | 0.4116±0.0161 |
| MHSA-PerHead | 0.9211±0.0022 | 0.6776±0.0106 | 0.5843±0.0048 | 0.6146±0.0063 | 0.5708±0.1099 | 0.4087±0.0184 |

**Reading:** On this disclosed 2011 subset, **MHSA Acc < Aldomi GRU-RF Acc < RF Acc**. Fail-F1 also leads on Aldomi/RF. Last-seed CM MHSA-Fused FN≫TP (`confusion_mhsa_fused_last_seed.csv`).

**Verdict:** Comparative RQ answered as an **evidenced negative** — do **not** claim MHSA superiority.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: MHSA vs hybrid/traditional on GCT | Aldomi GRU+SelectKBest family | GCT 2011 subset finals + hv | Acc/P/R/F1/AUC | **MET (negative)** |
| 2 | Acc, Prec, Rec, F1, ROC-AUC, latency | Aldomi / classical DVs | `results_summary.csv` | Yes | **MET** |
| 3 | Aldomi hybrid baseline | Aldomi26 doi above | SelectKBest+GRU-RF/KNN | Family | **MET** |
| 4 | Classical monitors | RF/KNN/SVM | same splits | Yes | **MET** |
| 5 | Multi-metric incl. network | CA2 list | `net`=sampled CPU | Named + honest | **WONTFIX schema** |
| 6 | Hard-verify ×5 negative | — | hv1–5 `mhsa_beats_*=false` | Acc | **MET** |
| 7 | Full 2011 dump / 2019 cells | Aldomi 2019 gen | absent | — | **WONTFIX beyond-floor** |
| 8 | AWS deploy | optional compute | not required | — | **N/A** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Mehak** | MHSA Acc/Fail-F1 below Aldomi/RF | **Evidenced negative** — §2 table; hv1–5; audit EXIT 0 |
| **M2 net-bytes** | True network-byte channel on 2011 | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_M2_M3_2026-09-23.md` + `CHANNEL_HONESTY.md` |
| **M3 dump/2019** | Full parts / Borg cells | **DATED_WONTFIX** — same amendment |
| Thapliyal as CA2 baseline | Forbidden | **Closed** — `BASELINE_PAPER.md` = Aldomi |
| Marketing MHSA win / ALIGNMENT=100 as superiority | Forbidden | Honest negative retained |

Reproduce:

```bash
cd mehak-thesis/mhsa-tdl-framework
python3 scripts/audit_mhsa_negative_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `results/gct/final_1..3/` | Primary cite | Stable Acc means |
| `results/gct/hard_verify_1..5/` | Negative gate | `hard_verify_summary.json` |
| `results/gct/analysis/mhsa_negative_audit_report.*` | Move gate | remediable_total=0 |
| `results/gct/FINAL3_BASELINE.md` | Baseline compare prose | RF/Aldomi lead |
| `data/gct/CHANNEL_HONESTY.md` | Schema limit | net≠bytes |

---

## 6. Design / Outstanding (artefact) — fold report later

Config: `CONFIGURATION_MANUAL.md`. Alternatives: MHSA-Fused vs PerHead vs Aldomi vs RF in DESIGN + SoT §2. Lit critique: Aldomi family vs attention fusion — MHSA does not win here. Synthesis: retain negative Acc/Fail-F1 in conclusions.

---

## 7–11. Rubric Outstanding cells (artefact-closed)

| Cell | Artefact path |
|------|----------------|
| Config reproducibility | `CONFIGURATION_MANUAL.md` |
| Alternatives considered | SoT §2 + `DESIGN_RATIONALE_BEYOND_CA2.md` |
| Critical lit vs Aldomi | `baseline_papers/BASELINE_PAPER.md` + GENAI_HANDOFF |
| Eval honesty (negative) | §2 table + hv summaries |
| Limitations (net/schema) | WONTFIX M2/M3 + CHANNEL_HONESTY |
