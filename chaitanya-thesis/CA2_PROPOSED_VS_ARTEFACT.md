# Chaitanya — ONE source of truth (thesis #2)

**Authority:** formal CA2 / master prompt + live `lambda-coldstart-isolation/`.  
**Baseline (binding):** Bluemke & Zdanowski (2025) — `baseline_papers/BASELINE_PAPER.md` (doi:10.24425/ijet.2025.153619).  
**Audit script (binding):** `lambda-coldstart-isolation/scripts/audit_h3_h4_root_causes.py` → `results/live/analysis/h3_h4_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated warming Holm win / H4 memory ADOPT.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted H3/H4 audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; N-H4 = dated WONTFIX |
| Strong (H1 runtime Init / H2 package Init)? | **Yes** — confirmatory_n30 r1–3 **reject** (Holm) |
| Strong (H3 warming Holm confirmatory)? | **No** — lite **fail to reject** (`p_holm=1.0`; underpowered; directional drop 0.20 only) |
| Strong (H4 memory as free ADOPT Init control)? | **No** — **practical null evidenced** (HOLD/avoid; Init flat ~73–85 ms); exploratory KW ≠ win |
| Audit remediable gaps? | **0** (`audit_h3_h4_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

H3/H4 were the silent-park risk (STATUS “ADOPT warming” vs Holm null; KW reject marketed as memory win). Gate is **`scripts/audit_h3_h4_root_causes.py`**: missing packs, fabricated H3 reject, H4 ADOPT marketing, missing Bluemke/SoT/WONTFIX → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_H4_PRACTICAL_NULL_H3_UNDERPOWERED`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | How do **runtime**, **package size**, **memory**, and **low-frequency warming** change AWS Lambda **cold-start Init Duration** and cost under free controls? |
| Factors | runtime ∈ {python, nodejs, java} × package ∈ {default, optimised}; memory ladder; EventBridge warmer on/off |
| Scale | confirmatory n≥30 / cell (power plan); lite n disclosed where used |
| Metrics | **Init Duration** (primary); Duration; cold fraction; list-price $/1k; ADOPT bands |
| Stats | Kruskal/MWU + Holm; Wilcoxon / Fisher for warming |
| Baseline | Bluemke & Zdanowski (2025) — configuration **Duration/cost** (Python-leaning); **not** Init-isolated multi-runtime |

---

## 2. SAME METRICS — live Init vs Bluemke Duration/cost gap

**Bluemke:** measures aggregate configuration **Duration** and **cost** (arm64 cheaper, etc.).  
**Ours:** keep Duration/cost framing and **add** CloudWatch REPORT **Init Duration** across three runtimes + free controls — **gap-fill**, not a numeric clone of their Python Duration tables.

### Confirmatory H1/H2 (primary) — `confirmatory_n30/round_{1,2,3}`

| Limb | Decision (Holm) | Snapshot (r3 medians Init ms) |
|------|-----------------|--------------------------------|
| H1 runtime (py/node/java optimised) | **reject** | ≈ 89.2 / 144.1 / 418.4 |
| H2_python / H2_nodejs / H2_java (default vs opt) | **reject** | e.g. python ≈3473 vs ≈88 |

Destroy-after each round (`destroy_confirmed=yes`).

### H3-lite warming — evidenced null (Holm)

| Arm | n | cold rate |
|-----|--:|----------:|
| on | 10 | **0.00** |
| off | 10 | **0.20** |

- Cold-fraction drop **0.20** (directional).  
- Wilcoxon signed-rank on 3 blocks: **`reject=false`**, `p_holm=1.0`.  
- **Do not** claim confirmatory H3 reject.

### H4-lite memory — practical null evidenced (N-H4)

| memory_mb | mean Init ms (python opt) |
|----------:|--------------------------:|
| 128 | 81.12 |
| 512 | 83.43 |
| 1024 | 73.22 |
| 1769 | 84.32 |
| 3008 | 85.18 |

- Span ≈ **12 ms** across ladder; ROI band **HOLD_lite**; decision matrix **avoid**.  
- Exploratory KW may show `reject=true` (p≈0.027) — **retained**, not marketed as free memory ADOPT.  
- **N-H4 hard-close:** practical null / no ADOPT win.

**Verdict:** Init isolation vs Bluemke is the contribution. H1/H2 supported. H3 Holm null + H4 practical null retained honestly.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: free controls → cold-start | Bluemke Duration/cost | Init + Duration/cost | Partial→gap-fill Init | **MET** |
| 2 | Multi-runtime package cells | Bluemke Python-leaning | py/node/java × def/opt | Yes (Init ms) | **MET** |
| 3 | H1/H2 confirmatory n≥30 | — | confirmatory_n30 ×3 | Yes | **MET** |
| 4 | H3 warming frequency | — | H3-lite; Holm fail-to-reject | Yes | **NULL evidenced** |
| 5 | H4 memory Init | Bluemke memory/Duration | H4-lite flat Init; HOLD/avoid | Yes | **Practical null (N-H4)** |
| 6 | Confirmatory H3/H4 n≥30 / 4 h | power plan | **absent** (deferred 2026-09-22) | — | **WONTFIX soft** |
| 7 | Bytecode arm | — | Unhandled; dropped | — | **Closed (ASSUMPTIONS)** |
| 8 | Destroy-after | ethics | destroy_confirmed on packs | — | **MET** |
| 9 | Marketing ALIGNMENT=100 perfect marks | — | forbidden | — | **Retained honest ~78** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-H4** | Memory as free Init ADOPT / “H4 win” | **DATED_WONTFIX 2026-09-23** — practical null evidenced; KW exploratory only; `DATED_WONTFIX_N_H4_2026-09-23.md` |
| H3 Holm | Warming confirmatory reject | **Evidenced null** — fail to reject; directional drop only |
| Confirmatory H3/H4 depth | n≥30 / 4 h | **WONTFIX beyond-floor** — ANALYSIS_PLAN 2026-09-22 |
| Marketing 100 | Forbidden | **Closed** — honest floor ~78 |

Reproduce:

```bash
cd chaitanya-thesis/lambda-coldstart-isolation
python3 scripts/audit_h3_h4_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `results/live/confirmatory_n30/round_{1,2,3}/` | **Primary H1/H2 cite** | n≈30; destroy_confirmed |
| `data/processed/live/` + `reports/paper/tables/live_lite/` | H3/H4 lite + Init cells | Holm family underpowered on H3 |
| `results/live/final_{1,2,3}/` | H1 stability smoke | lite n=5 |
| `results/live/analysis/h3_h4_audit_report.*` | Move gate | remediable_total=0 |
| `baseline_papers/Bluemke_Zdanowski_2025_Lambda_baseline.pdf` | Binding baseline | Duration/cost |

---

## 6. Thesis #2 gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-H4 hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs Bluemke | **Yes** |
| Configuration manual | **Yes** (`docs/CONFIGURATION_MANUAL.md`) |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (Init gap-fill vs Bluemke Duration/cost) | **Filled** — §2 |
| Alts / H3–H4 soft | **WONTFIX** dated — practical null + underpowered null retained |
| Config manual | Present |
| Claim↔evidence | H1/H2 reject; H3 fail-to-reject; H4 HOLD/avoid |
| Accidental silent park | Forbidden — N-H4 dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~78.** Confirmatory H1/H2 Demonstrated; H3/H4 soft limbs dated/honest. Do **not** market ALIGNMENT=100 / full H1–H4 confirmatory.  
Authority: `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md`.
