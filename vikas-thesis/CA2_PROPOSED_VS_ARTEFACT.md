# Vikas — ONE source of truth (thesis #6)

**Authority:** formal CA2 / `VikasReddyAmanagantti_X25178849_MASTER_PROMPT.md` + live `lambda-idempotency-eval/`.  
**Baseline (binding):** Qi et al. (2025) Halfmoon / asymmetric logging — `baseline_papers/BASELINE_PAPER.md` (doi:10.1145/3725985).  
**Audit script (binding):** `lambda-idempotency-eval/scripts/audit_campaign_root_causes.py` → `results/live/campaign_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No P4 marketed as CA2 evidence; no fabricated E1–E3.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted campaign audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; P4 = dated WONTFIX |
| Strong (E1–E3 on live P1/P2/P3)? | **Yes** — all **supported** on campaign |
| Strong (P4 TransactWrite / exactly-once on managed AWS)? | **No** — quarantined (A12); draft report NON-AUTHORITATIVE |
| Audit remediable gaps? | **0** (`audit_campaign_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

N-scale (24000), E1–E3 decisions, and P4 quarantine must be proven by pack inventory + cell invariants, not STATUS prose. Script EXIT 0 → disposition **`DATED_WONTFIX_P4_QUARANTINED`**.

---

## 1. CA2 proposed (fresh from master prompt)

| Item | Formal CA2 |
|------|------------|
| RQ | By how much do **conditional write (P2)** and **idempotency-key (P3)** reduce **duplicate state mutation** vs **plain put (P1)** under **injected** after-commit timeouts — and what do they cost in **latency** and **consumed capacity**? |
| Paths | P1 plain put · P2 ConditionExpression · P3 idempotency-key (Powertools-style) |
| Scale | Provisional N=1000/cell; multiplicities {1,2,5}; Streams GT |
| Metrics | duplicate-mutation rate (primary); latency mean/p95; WCU/capacity; CCF |
| Expectations | E1 majority dups on P1; E2 P2/P3 reduce >90% vs P1; E3 P3 costs more capacity than P2 |
| Baseline | Qi/Halfmoon **criterion** (no duplicate mutation after retry) on **custom** runtime — not reimplemented |

---

## 2. SAME METRICS — live campaign vs Qi/Halfmoon criterion

**Pack:** `data/runs/live/campaign/` + `results/live/` · N=1000 × {P1,P2,P3} × {1,2,5} = **9000 requests / 24000 deliveries** · destroy_confirmed  
**Qi/Halfmoon:** custom-runtime exactly-once via asymmetric logging — **no** stock-Lambda P1/P2/P3 dup×capacity table. Contrast is **same correctness criterion** (dup mutation after retry) + application-level cost, **not** a numeric clone of Halfmoon logging overhead.

### Duplicate rate (primary DV; injected retries)

| Path | mult=2 dup_rate | mult=5 dup_rate |
|------|----------------:|----------------:|
| P1 (plain) | **1.0** | **1.0** |
| P2 (conditional) | **0.0** | **0.0** |
| P3 (idempotency key) | **0.0** | **0.0** |

### Capacity (secondary; mean WCU / request)

| Path | mult=1 | mult=2 | mult=5 |
|------|-------:|-------:|-------:|
| P1 | 1 | 2 | 5 |
| P2 | 1 | 2 | 5 |
| P3 | 3 | 4 | 7 |
| **P3 − P2** | **+2** | **+2** | **+2** |

### Pre-registered expectations (campaign)

| Expectation | Decision |
|-------------|----------|
| E1 (P1 majority dups @ mult 2,5) | **supported** |
| E2 (P2/P3 relative reduction >0.90 vs P1) | **supported** (×4 rows) |
| E3 (P3 capacity > P2; Holm) | **supported** (×3 multiplicities) |

**Sensitivity (retained):** P3 `p3_between` crash → dup_rate=1.0 @ mult 2/5 — atomicity gap under mid-path timeout; **not** a P4 win claim.

**Verdict:** On stock Lambda+DynamoDB, P2/P3 eliminate measured duplicate mutations under after-commit injection; P3 costs +2 WCU vs P2. Halfmoon’s omitted managed-platform cost table is the gap filled — do **not** claim Halfmoon formal runtime guarantees.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: P2/P3 vs P1 dup under injected retry | Qi criterion = no dup after retry | campaign factorial | Yes (dup rate) | **MET** |
| 2 | Paths P1/P2/P3 on stock Lambda+DDB | Halfmoon = custom runtime | P1–P3 only in yaml | Yes | **MET** |
| 3 | Latency + capacity with CIs | cost omitted in runtime lit | cells + capacity/latency tests | Yes | **MET** |
| 4 | E1/E2/E3 pre-registered | falsifiable thresholds | `expectations.csv` all supported | Yes | **MET** |
| 5 | Streams / known retry GT | — | deliveries + ground_truth | — | **MET** |
| 6 | N≈1000/cell full factorial | provisional N | 1000×3×3 = 24k deliveries | Yes | **MET** |
| 7 | Destroy-after | ethics / AUP | tfstate resources=[] + destroy_confirmed | — | **MET** |
| 8 | P4 TransactWrite exactly-once | beyond A12 | **absent** from live | — | **WONTFIX quarantined** |
| 9 | Separate lite final_1–3 | optional beyond-floor | campaign is primary pack | — | **WONTFIX beyond-floor** |
| 10 | Moto latency/capacity as AWS | — | moto functional only | No | **Retained limit** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Vikas / P4** | TransactWrite / draft report wins | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_N_Vikas_P4_2026-09-23.md`; A12; audit EXIT 0; no P4 in campaign |
| Marketing 100 | Forbidden | **Closed** — honest floor ~88; RUBRIC stamp purged |
| Moto as AWS latency | Forbidden | **Closed** — STATUS negatives retained |
| Separate final_1–3 | Soft beyond | **WONTFIX beyond-floor** — campaign is binding pack (`FINAL3_NOTE.md`) |

Reproduce:

```bash
cd vikas-thesis/lambda-idempotency-eval
python3 scripts/audit_campaign_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `data/runs/live/campaign/` | **Primary cite** | 24000 deliveries; run_info; Streams |
| `results/live/` | Analysis | summary.md; expectations; cells; figures |
| `results/live/campaign_audit_report.*` | Move gate | remediable_total=0 |
| `data/runs/live/sensitivity/` | E2 crash-between | P3 p3_between; 1400 deliveries |
| `data/runs/live/pilot/` | Sizing only | chose N=1000 |
| `results/moto/` | Harness | **not** AWS evidence |

---

## 6. Thesis #6 gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Vikas P4 hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs Qi criterion | **Yes** |
| Configuration manual | **Yes** (`docs/CONFIGURATION_MANUAL.md`) |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (dup after retry vs Qi criterion) | **Filled** — §2; Halfmoon has no stock P1/P2/P3 table to clone |
| Alts / P4 | **WONTFIX** dated — A12 quarantine |
| Config manual | Present |
| Claim↔evidence | E1–E3 supported; P1 dups retained as control |
| Accidental silent park | Forbidden — N-Vikas dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~88.** Live E1–E3 campaign Demonstrated under P1–P3 scope; P4 quarantined; campaign ≠ perfect-marks. Do **not** market ALIGNMENT=100.  
Authority: `_analysis_extract/reports/CA2_ALIGNMENT_SCOREBOARD.md`.
