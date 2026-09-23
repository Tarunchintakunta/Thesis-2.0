# Pooja — ONE source of truth (thesis PAKS)

**Authority:** formal CA2 `Pooja_25120921_CA2.docx` + live `paks-framework/results/`.  
**Baseline (binding):** Kubernetes **HPA** (reactive) — `baseline_papers/BASELINE_PAPER.md` (NimbusGuard = literature/proxy only).  
**Audit script (binding):** `paks-framework/scripts/audit_cost_explorer_root_causes.py` → `results/live/analysis/cost_explorer_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No Cost Explorer bill claimed measured; no fabricated PAKS superiority / LSTM win over persistence.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted Cost Explorer audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; Cost Explorer = dated WONTFIX |
| Strong (live HPA vs PAKS scale latency on k3s)? | **Yes (method)** — final_1–3 destroy-after; ordering **not** monotone |
| Strong (LSTM beats persistence on TRACE)? | **No** — LSTM MAE **worse** than persistence (retained) |
| Strong (Cost Explorer / billing-linked cost)? | **No** — LIST_PRICE `$0.04`/pod-hour SIMULATED only |
| Audit remediable gaps? | **0** (`audit_cost_explorer_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

LIST_PRICE vs Cost Explorer, LSTM&lt;persistence, and HPA baseline must be pack-proven. Script EXIT 0 → disposition **`DATED_WONTFIX_COST_EXPLORER`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | Effect of PAKS on prediction accuracy, util, response time, scaling latency, and infrastructure **cost** vs traditional **HPA** |
| Stack | Kubernetes, Docker, Python, TensorFlow, AWS EC2/S3/CloudWatch |
| Traces | Google Cluster Trace + Alibaba Cluster Trace |
| Metrics | MAE/RMSE; util; response; scaling latency; **cost**; SLA |
| Baseline | Traditional Kubernetes HPA |

---

## 2. SAME METRICS — artefact vs HPA / prediction gap

**HPA baseline:** reactive autoscaling/v2 CPU formula — **no** TRACE LSTM MAE table and **no** Free-Tier k3s destroy-after latency pack in the HPA product docs.  
**Ours:** retain **scaling latency** (LIVE) + **MAE/RMSE vs persistence** (TRACE) + **cost** as **LIST_PRICE** `$0.04`/pod-hour (`USD_PER_POD_HOUR` in `src/eval/metrics.py`); Cost Explorer bill validation = dated WONTFIX.

### Live k3s final_1–3 — scaling latency mean (s)

Source: `results/live/final3_latency_summary.json` (steps=16; destroy_confirmed each).

| Round | HPA mean | PAKS mean | HPA p50 | PAKS p50 |
|-------|---------:|----------:|--------:|---------:|
| final_1 | 0.334 | 0.279 | 0.141 | 0.142 |
| final_2 | 0.296 | 0.319 | 0.141 | 0.137 |
| final_3 | 0.395 | 0.312 | 0.143 | 0.145 |

**Reading:** PAKS faster on f1/f3, HPA on f2 — **not** confirmatory superiority.

### TRACE prediction — LSTM vs persistence (MAE)

Source: `results/formal_prediction_metrics.csv`.

| Series | LSTM MAE | Persistence MAE | Verdict |
|--------|---------:|----------------:|---------|
| GCT 2011 held-out jobs | **0.102** | **0.048** | LSTM **worse** |
| Alibaba RANGE cluster CPU% | **3.435** | **2.803** | LSTM **worse** |

### Cost (LIST_PRICE / SIMULATED)

| Field | Value |
|-------|-------|
| `evidence.cost` | **SIMULATED** |
| Assumed unit | **`$0.04` / pod-hour** (`USD_PER_POD_HOUR`) |
| Cost Explorer / GetCostAndUsage | **Not called** — dated WONTFIX |

Example live cell cost_usd (capacity model) ≈ 0.00267 both arms at lite replica cap — **not** a billing receipt.

**Verdict:** Same metric families as CA2 (latency, MAE/RMSE, cost scalar); cost is list-price model, not Cost Explorer. LSTM&lt;persistence retained.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: PAKS vs HPA | HPA reactive | live k3s HPA observe vs PAKS Scale | Yes (latency) | **MET (method)** |
| 2 | Scaling latency | HPA lag framing | final3_latency_summary | Yes | **MET** |
| 3 | MAE/RMSE prediction | Kumar-class LSTM lit | formal_prediction_metrics | Yes | **MET (neg)** |
| 4 | Infrastructure cost | CA2 cost DV | LIST_PRICE $/pod-hour | Partial (model) | **MET (list-price)** |
| 5 | Cost Explorer bill validation | optional strength | **absent** | — | **WONTFIX soft** |
| 6 | LSTM beats persistence | stronger limb | LSTM MAE higher | Yes | **FALSIFIED / retained** |
| 7 | Monotone PAKS&lt;HPA latency | confirmatory | not monotone | Yes | **Not claimed** |
| 8 | Full multi-GB dumps / multi-node | CA2 families | disclosed samples | Partial | **Beyond-floor** |
| 9 | NimbusGuard as binding baseline | proxy only | superseded | — | **Closed** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Pooja** | Cost Explorer / billing-linked cost soft | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_N_Pooja_2026-09-23.md`; audit EXIT 0; disposition `DATED_WONTFIX_COST_EXPLORER` |
| LSTM &lt; persistence | Prediction negative | **Evidenced retain** — §2 |
| HPA vs PAKS ordering | Mixed finals | **Evidenced mixed** — §2 |
| Marketing 100 / CE measured | Forbidden | Keep ~62 floor + LIST_PRICE visible |

Reproduce:

```bash
cd pooja-thesis/paks-framework
python3 scripts/audit_cost_explorer_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

Dated note: `pooja-thesis/DATED_WONTFIX_N_Pooja_2026-09-23.md`

---

## 5. Evidence packs

| Pack | Role |
|------|------|
| `results/live/final_1`…`final_3` | Live HPA vs PAKS ×3 + destroy |
| `results/live/final3_latency_summary.json` | Same-metrics latency |
| `results/live/FINAL3_BASELINE.md` | Binding live baseline |
| `results/formal_prediction_metrics.csv` | TRACE MAE/RMSE vs persistence |
| `src/eval/metrics.py` | `USD_PER_POD_HOUR = 0.04` LIST_PRICE |
| `results/live/analysis/cost_explorer_audit_report.*` | Move gate |

---

## 6. Thesis gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Pooja Cost Explorer hard-closed | **Yes** |
| ONE-file SoT + same-metrics vs HPA | **Yes** |
| Configuration manual | **Yes** (`docs/CONFIGURATION_MANUAL.md`) |
| Report/viva | Fold later |
| **MOVE ALLOWED** | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (latency + MAE + list-price cost) | **Filled** — §2 |
| HPA baseline | **Filled** — BASELINE_PAPER |
| Cost Explorer | **WONTFIX** — §4 |
| LSTM&lt;persistence | **Retained negative** |
| Config manual | Present + audit reproduce |
| Accidental silent park | Forbidden — N-Pooja dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~62.** Causal lite HPA vs PAKS method closed; prediction negative retained; cost = LIST_PRICE not Cost Explorer. Do **not** market confirmatory PAKS dominance or billing-validated cost.
