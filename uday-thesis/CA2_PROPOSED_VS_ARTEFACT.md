# Uday — ONE source of truth (MQTT QoS IoT Core)

**Authority:** formal CA2 `UdayKiranReddyDodda_X25166484_proposal.docx` + `CA2_COMMITMENTS.md` + live `mqtt-qos-iot-core/results/live/`.  
**Baseline (binding):** Shvaika et al. (2025) TBMQ — `baseline_papers/BASELINE_PAPER.md` (self-hosted steady load; disconnect/multi-QoS = future work).  
**Audit script (binding):** `mqtt-qos-iot-core/scripts/audit_holm_root_causes.py` → `results/live/confirmatory_1/holm_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated schedule-separation Holm success / formal-N complete.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted Holm audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; Holm d300>d60 = dated WONTFIX |
| Strong (QoS1 loss ≪ QoS0 under disconnect, lite)? | **Yes** — pooled mean loss QoS0 **0.415** vs QoS1 **0.0** |
| Strong (Holm d300>d60 loss separation)? | **No** — d60≡d300 loss **0.68** under lite schedule |
| Audit remediable gaps? | **0** (`audit_holm_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

Manual “d60/d300 looks fine” was how the schedule ceiling silently parked. Uday soft N is gated by **`scripts/audit_holm_root_causes.py`**: missing finals/confirmatory_1, QoS1 nonzero loss, fabricated schedule-separation Holm success, missing Shvaika framing → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_HOLM_D300_GT_D60`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | To what extent does MQTT **QoS 1** vs **QoS 0** reduce telemetry **loss** on **AWS IoT Core** under controlled publisher disconnects? |
| Factors | QoS ∈ {0,1} × disconnect ∈ {0,15,60,300}s × rate ∈ {steady,bursty} |
| Scale | Formal: 5 devices × 1000 msgs × 5 reps; **lite executed:** 5×50 × n=1/cell |
| Metrics | loss; duplicate-id; E2E latency mean/p95/p99; reconnect/backlog; usd_est |
| Stats | α=0.05 Holm–Bonferroni at formal N |
| Baseline | Shvaika et al. (2025) — gap paper (managed + disconnect omitted) |

---

## 2. SAME METRICS — confirmatory_1 (final_1+final_2 pool) vs Shvaika gap

**Pack:** `results/live/confirmatory_1/` (derived from destroy-after `final_1` + `final_2`).  
**Shvaika:** self-hosted TBMQ steady high load — **no** managed-broker disconnect factorial. Contrast is **gap-fill** (IoT Core + disconnect + per-message log), not TBMQ throughput clone.

### Pooled mean loss (all disconnect × rate)

| Role | Mean loss |
|------|----------:|
| baseline QoS0 | **0.415** |
| proposed QoS1 | **0.000** |

### QoS0 loss by disconnect (pooled)

| disconnect_s | mean loss |
|-------------:|----------:|
| 0 | 0.00 |
| 15 | 0.30 |
| 60 | **0.68** |
| 300 | **0.68** (≡ d60) |

### Soft N — Holm d300 > d60

**FAIL.** Lite ~49 s publish schedule → both 60 s and 300 s cuts cover remaining messages → identical QoS0 loss. Two-proportion / Holm cannot support d300>d60. **Dated WONTFIX** — not marketed as pass.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: QoS1 vs QoS0 loss under disconnect | Shvaika omits disconnect | live IoT Core factorial | Yes (loss) | **MET (lite)** |
| 2 | Factors QoS × d ∈ {0,15,60,300} × rate | future work in Shvaika | 16-cell lite finals | Yes | **MET (lite)** |
| 3 | Device-log ↔ DynamoDB match | — | LIVE_EVIDENCE + manifests | — | **MET** |
| 4 | Latency / dup / backlog / cost | steady-load framing | cell metrics + usd_est | Partial | **MET (lite)** |
| 5 | Destroy-after + Free Tier | — | destroy_confirmed finals | — | **MET** |
| 6 | Holm at formal N | powered design | confirmatory_1 lite pool only | Partial | **WONTFIX beyond-floor** |
| 7 | d300 > d60 loss separation | construct validity | d60≡d300=0.68 | Yes (fail) | **WONTFIX soft N** |
| 8 | Formal 80-cell / ~600k msgs | — | **absent** | — | **WONTFIX beyond-floor** |
| 9 | final_3 pack | optional third lite | **absent** on disk | — | **WONTFIX** (confirmatory_1 uses 1+2) |
| 10 | Shvaika numeric clone | TBMQ thr | not claimed | No | **Retained limit** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Uday** | Holm d300>d60 fail | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_N_Uday_2026-09-23.md`; confirmatory_1 limb FAIL; audit EXIT 0 |
| Formal N / 80-cell | Power upgrade | **WONTFIX beyond-floor** — Free-Tier / DESIGN_RATIONALE |
| Marketing formal complete | Forbidden | **Closed** — honest floor ~70 under disclosed lite |
| Shvaika prose fold | Soft packaging | Report later |

Reproduce:

```bash
cd uday-thesis/mqtt-qos-iot-core
python3 scripts/audit_holm_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `results/live/final_1` … `final_2` | Lite 16-cell destroy-after | QoS1 loss 0; d60≡d300 |
| **`results/live/confirmatory_1/`** | **Cite for Holm / same-metrics** | pools 1+2; limb FAIL documented |
| `results/live/initial_eval_1/` | Gate / early lite | Supporting |
| `results/live/confirmatory_1/holm_audit_report.*` | Move gate | remediable_total=0 |

---

## 6. Thesis gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Uday hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs Shvaika | **Yes** |
| Configuration manual | **Yes** (`mqtt-qos-iot-core/docs/CONFIGURATION_MANUAL.md`) |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (loss retained; managed+disconnect gap-fill) | **Filled** — §2 |
| Alts / synth | mock = harness only; live finals = evidence |
| Config manual | Present + audit reproduce |
| Claim↔evidence | QoS1 loss win (lite); Holm d300>d60 FAIL retained |
| Accidental silent park | Forbidden — N-Uday dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~70 under disclosed lite.** Directional QoS1 loss elimination evidenced; Holm schedule-separation limb and formal N retained honestly. Do **not** market ALIGNMENT=100 / formal complete / d300≠d60 after Holm.
