# Anji — ONE source of truth (SQS reliability–recovery)

**Authority:** formal CA2 / `AnjaneyaReddyGurram_24288853_MASTER_PROMPT.md` + live `sqs-reliability-recovery/results/live/`.  
**Baseline (binding):** Kyrychenko et al. (2025) — `baseline_papers/` / DOI `10.37394/23202.2025.24.4` (steady-state SQS optima; **no** fault injection).  
**Audit script (binding):** `sqs-reliability-recovery/scripts/audit_scoped_e_root_causes.py` → `results/live/scoped_E_guidance_1/scoped_e_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated full-IV live matrix / live Holm H1–H3 wins.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted scoped_E audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; full IV live = dated WONTFIX |
| Strong (scoped guidance-transfer 20/20 under fault)? | **Yes** — `scoped_E_guidance_1` VT×batch×n=5 complete |
| Strong (full CA2 IV live matrix / live Holm H1–H3)? | **No** — amended out; localsim H1–H3 fail-to-reject |
| Audit remediable gaps? | **0** (`audit_scoped_e_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

Manual “E looks done / full IV later” was how the live matrix silently parked. Anji soft N is gated by **`scripts/audit_scoped_e_root_causes.py`**: scoped_E ≠20/20, wrong campaign/cells, fabricated full-IV complete, missing Kyrychenko framing → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_FULL_IV_LIVE_AMENDED`**.

---

## 1. CA2 proposed (fresh from master prompt)

| Item | Formal CA2 |
|------|------------|
| RQ | How does Amazon SQS configuration affect message **reliability and recovery** under injected consumer/downstream failures? |
| IVs | VT, maxReceiveCount/DLQ, batch, load, fault type, arm |
| DVs | loss, dup, DLQ capture, recovery_time, throughput/latency, cost |
| Stats | H1–H3 α=0.05 Holm–Bonferroni |
| Baseline | Kyrychenko et al. (2025) steady-state guidance — test whether it **persists under fault** |

---

## 2. SAME METRICS — scoped_E_guidance_1 vs Kyrychenko gap

**Pack:** `results/live/scoped_E_guidance_1/` — campaign `E_guidance_transfer`, backend **localsim**, **20/20**.  
**Matrix:** VT ∈ {30, 600} × batch ∈ {10, 50} × repeats=5.  
**Kyrychenko:** steady-state optima ~VT 600 / batch 50 — **no** fault. Ours keep throughput/recovery names and **add** fault + loss/dup/DLQ.

### Cell means (loss / recovery_s / thr)

| VT | batch | n | loss | recovery_s | thr msg/s | Kyrychenko-fav? |
|---:|------:|--:|-----:|-----------:|----------:|:---------------:|
| 30 | 10 | 5 | 0.0 | ≈36 | ≈20.05 | no |
| 30 | 50 | 5 | 0.0 | ≈36 | ≈20.07 | no |
| 600 | 10 | 5 | 0.0 | ≈600 | ≈5.00 | partial |
| 600 | 50 | 5 | 0.0 | ≈600 | ≈5.00 | **yes** |

**Reading:** Under `consumer_kill`, Kyrychenko-favourable long VT does **not** minimise recovery (≈600 s vs ≈36 s at VT30). Aligns with localsim H3_recovery **fail-to-reject after Holm** (p_adj≈0.084). Loss floor 0 on this protocol.

**Supporting live (lite only):** `final_1|2|3` smoke + `key_cells_n3` — not full IV.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact | Same-metrics? | Status |
|---|--------------|----------------------|----------|:-------------:|--------|
| 1 | RQ: SQS config → reliability/recovery under fault | Kyrychenko steady-state only | fault campaigns + live lite | Yes (gap-fill) | **MET (scoped)** |
| 2 | VT / MRC / DLQ → loss+dup | absent under fault in baseline | live key cells + localsim | Yes | **MET (lite)** |
| 3 | Recovery vs VT/MRC | — | scoped_E + live n=3 means | Yes | **MET (scoped/lite)** |
| 4 | Guidance persists under fault (Obj3) | Kyrychenko optima | scoped_E 20/20 | Yes | **MET (descriptive)** |
| 5 | Localsim H1–H3 Holm | confirmatory family | stats_H1_H2_H3.json **nulls** | Yes | **FALSIFIED / retained null** |
| 6 | Live smoke finals ×3 | — | final_1–3 | — | **MET** |
| 7 | Live confirmatory n=3 (4 cells) | — | key_cells_n3 | — | **MET** |
| 8 | Full IV live matrix | formal breadth | **absent** | — | **WONTFIX amended** |
| 9 | Live Holm H1–H3 | powered live | **not run** | — | **WONTFIX** |
| 10 | Adaptive VT / DIVE | optional | off in matrix | — | **Quarantined / not claimed** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Anji** | Full IV live matrix amended | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_N_Anji_2026-09-23.md`; scoped_E 20/20 landed; audit EXIT 0 |
| Live Holm H1–H3 | Confirmatory live family | **WONTFIX** — underpowered / not claimed |
| STATUS ALIGNMENT=100 | Overstated vs ~78 lite floor | **Closed** — honest floor in SoT / GENAI |
| Marketing full IV complete | Forbidden | **Closed** |

Reproduce:

```bash
cd anji-thesis/sqs-reliability-recovery
python3 scripts/audit_scoped_e_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| **`results/live/scoped_E_guidance_1/`** | **Cite for guidance-under-fault** | 20/20 localsim; summary.csv + manifests |
| `results/live/final_1` … `final_3` | Lite smoke | loss=0; MRC1 DLQ pos |
| `results/live/key_cells_n3/` | Live n=3 confirmatory (4 cells) | Supporting |
| `results/summary/stats_H1_H2_H3.json` | Localsim H1–H3 | All fail-to-reject after Holm |
| `scoped_e_audit_report.*` | Move gate | remediable_total=0 |

---

## 6. Thesis gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Anji hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs Kyrychenko | **Yes** |
| Configuration manual | **Yes** (`docs/CONFIGURATION_MANUAL.md` audit section) |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (thr/recovery retained; fault gap-fill) | **Filled** — §2 |
| Alts / synth | localsim confirmatory + scoped_E; live = lite only |
| Config manual | Present + audit reproduce |
| Claim↔evidence | scoped_E 20/20; full IV amended; H1–H3 nulls retained |
| Accidental silent park | Forbidden — N-Anji dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~78 under disclosed lite + scoped E.** Guidance-under-fault evidenced at 20/20; full IV live matrix and live Holm retained honestly. Do **not** market ALIGNMENT=100 / full IV complete.
