# Rasool — ONE source of truth (thesis #4)

**Authority:** formal CA2 `RasoolBashaDurbesula_24205478_proposal.docx` + master prompt + live `dynamodb-pk-capacity-eval/results/`.  
**Baseline (binding):** Pantelić et al. (2026) — `baseline_papers/BASELINE_PAPER.md` (self-hosted SQL/NoSQL; **no** RCU/throttle/cost meter).  
**Audit script (binding):** `dynamodb-pk-capacity-eval/scripts/audit_soft_limbs_root_causes.py` → `results/analysis/soft_limbs_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated full W1–W4 confirmatory ANOVA / K4 dominance.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted soft-limbs audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **YES** — §7–§11 + config; soft n=1 W1/W2 = dated WONTFIX |
| Strong (key-design → mean latency on W3/W4)? | **Yes** — pooled final-3 ANOVA key F≈59 (W3) / ≈17 (W4) |
| Strong (capacity / interaction on W3 mean latency)? | **No** — capacity p≈0.28; interaction p≈0.81 (**fail to reject**) |
| Strong (full W1–W4 confirmatory ANOVA / formal n=30)? | **No** — W1/W2 = n=1 exploratory only |
| Audit remediable gaps? | **0** (`audit_soft_limbs_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual chat

Manual “W1/W2 looks closed / looks fine” was how soft limbs silently parked. Rasool soft N is gated by **`scripts/audit_soft_limbs_root_causes.py`**: missing final/w1w2 packs, metric holes, destroy gaps, pooled ANOVA claim drift, fabricated ALIGNMENT=100 / K4 wins → EXIT 2. This pack: **EXIT 0**, disposition **`DATED_WONTFIX_SOFT_LIMBS_N1_EXPLORATORY_W1W2`**.

---

## 1. CA2 proposed (fresh from formal)

| Item | Formal CA2 |
|------|------------|
| RQ | How does DynamoDB table configuration (partition-key design × capacity mode) determine the **performance–cost** trade-off under serverless workloads? |
| Factors | K∈{K1,K2,K3} × C∈{on-demand, provisioned} × W∈{W1,W2,W3,W4} |
| Scale | n=30 / cell (power plan); Zipfian; Lambda-driven; destroy-after IaC |
| Metrics | latency mean/p95/p99; throughput; throttle; RCU/WCU; cost per 10k ops (list-price) |
| Stats | two-way ANOVA + interaction; ART if needed; Holm–Bonferroni; α=0.05 |
| Baseline | Pantelić et al. (2026) — retain latency/throughput framing; **add** metered DVs they cannot produce |

---

## 2. SAME METRICS — pooled final_1–3 (W3/W4) + w1w2_a vs Pantelić gap

**Pantelić:** self-hosted SQL vs NoSQL under read/write/mixed loads — **relative** latency/throughput ordering; **no** capacity units, throttles, or $/op. Ours keep latency/throughput and **add** throttle + list-price cost on live DynamoDB.

### Pooled confirmatory ANOVA — latency_mean_ms (n=3 fleets × 6 configs)

| Workload | Key F (p) | Capacity F (p) | Interaction F (p) |
|----------|-----------|----------------|-------------------|
| W3 | **59.00 (1e-06)** | 1.27 (0.28) | 0.21 (0.81) |
| W4 | **17.01 (0.0003)** | 0.25 (0.63) | 3.08 (0.083) |

**Source:** `results/pooled_final3_anova.json` (n_rows=36; source_packs final_1–3).

### Pooled cell means — latency_mean_ms / throughput_ops_s / throttle_rate (finals)

| Cell | mean lat ms | thr ops/s | throttle |
|------|------------:|----------:|---------:|
| K1-on_demand-W3 | 4.217 | 199.921 | **0.0** |
| K1-provisioned-W3 | 4.315 | 199.924 | **0.0** |
| K2-on_demand-W3 | 4.315 | 199.920 | **0.0** |
| K2-provisioned-W3 | 4.337 | 199.920 | **0.0** |
| K3-on_demand-W3 | **4.836** | 199.920 | **0.0** |
| K3-provisioned-W3 | **4.882** | 199.915 | **0.0** |
| K1-on_demand-W4 | 4.733 | 466.533 | **0.0** |
| K1-provisioned-W4 | 4.630 | 466.310 | **0.0** |
| K2-on_demand-W4 | 4.837 | 466.532 | **0.0** |
| K2-provisioned-W4 | 4.702 | 466.532 | **0.0** |
| K3-on_demand-W4 | **5.118** | 466.508 | **0.0** |
| K3-provisioned-W4 | **5.498** | 465.624 | **0.0** |

**Reading:** Key design shifts mean latency (K3 often higher); capacity main effect **not** supported on W3 mean latency; throttle floor 0 under measured load. Pantelić has **no** throttle/cost scalars to clone — contrast is **gap-fill**, not numeric SQL/NoSQL clone.

### W1/W2 exploratory key-cells (`results/w1w2_a/`, n=1)

| Stratum | KW p (exploratory) | median lat ms K1/K2/K3 |
|---------|-------------------:|------------------------|
| W1-on_demand | ≈0 | 3.813 / 3.860 / 5.077 |
| W1-provisioned | ≈0 | 3.929 / 3.931 / 4.817 |
| W2-on_demand | 1.68e-93 | 5.709 / 5.487 / 5.323 |
| W2-provisioned | ≈0 | 5.341 / 5.466 / 5.473 |

Throttle=0; thr≈200 ops/s. **Not** confirmatory ANOVA.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | RQ: PK × capacity → perf–cost | Pantelić engine ordering, no meter | live DynamoDB factorial | Partial (add throttle/cost) | **MET** |
| 2 | Latency + throughput retained | Pantelić DVs | batches.csv finals + w1w2_a | Yes | **MET** |
| 3 | Throttle + RCU/WCU + $/10k | **absent** in Pantelić | live + list-price model | Gap-fill | **MET** |
| 4 | W3/W4 × K1–K3 × 2 modes | — | final_1–3 (12×3) | Yes | **MET** |
| 5 | W1/W2 cells | Pantelić read/write framing | w1w2_a 12/12 n=1 | Yes (exploratory) | **MET (soft depth)** |
| 6 | Two-way ANOVA + interaction | — | pooled_final3_anova.json | Yes (W3/W4) | **MET** |
| 7 | Capacity / interaction sig on W3 mean lat | stronger limb | p≈0.28 / 0.81 | Yes | **FALSIFIED / retained null** |
| 8 | Full W1–W4 confirmatory ANOVA + Holm×12 | formal family | **absent** (audit) | — | **WONTFIX soft** |
| 9 | Formal n=30 / cell | power plan | n=3 fleets W3/W4; n=1 W1/W2 | Partial | **WONTFIX beyond-floor** |
| 10 | IaC provision + destroy | — | destroy_confirmed on packs | — | **MET** |
| 11 | K4 adaptive sharding dominance | off-factorial | code only | — | **Quarantined** |
| 12 | Cost Explorer bill validation | — | list-price only | — | **WONTFIX / not claimed** |

---

## 4. Soft / N — hard-closed in this file

| ID | Item | Close |
|----|------|-------|
| **N-Rasool** | W1/W2 n=1 exploratory; no full W1–W4 confirmatory ANOVA | **DATED_WONTFIX 2026-09-23** — packs on disk; audit EXIT 0; disposition `DATED_WONTFIX_SOFT_LIMBS_N1_EXPLORATORY_W1W2`; confirmatory authority = W3/W4 pooled |
| Key → latency (W3/W4) | Main method residual | **Evidenced reject** (pooled ANOVA) |
| Capacity / interaction (W3 mean lat) | Stronger limb | **Evidenced null** — retain |
| Marketing 100 / full ANOVA 100 | Forbidden | **Closed** — honest floor ~88 |
| K4 dominance | Off factorial | **Quarantined** |

Reproduce:

```bash
cd rassool-thesis/dynamodb-pk-capacity-eval
python3 scripts/audit_soft_limbs_root_causes.py
# EXIT 0 required; remediable_total must be 0
```

Dated note: `dynamodb-pk-capacity-eval/DATED_WONTFIX_N_Rasool_2026-09-23.md`

---

## 5. Evidence packs

| Pack | Role | Notes |
|------|------|-------|
| `results/final_1` … `final_3` | Confirmatory W3/W4 ×3 | 12 cells each; destroy_confirmed |
| **`results/pooled_final3_anova.json`** | **Cite for factor claims** | n_rows=36 |
| **`results/w1w2_a/`** | W1/W2 key-cells | n=1 exploratory KW; destroy_confirmed |
| `results/keycell_summary.*` | Historic first live round | Superseded for ANOVA by pooled finals |
| `results/analysis/soft_limbs_audit_report.*` | Move gate | remediable_total=0 |

---

## 6. Thesis #4 gate

| Gate | Done |
|------|:----:|
| Scripted remediable audit EXIT 0 | **Yes** |
| remediable_total = 0 | **Yes** |
| N-Rasool hard-closed (dated WONTFIX) | **Yes** |
| ONE-file SoT + same-metrics vs Pantelić | **Yes** |
| Configuration manual | **Yes** (`configuration_manual/` + `docs/CONFIGURATION_MANUAL.md`) |
| Report/viva | Fold later |
| **MOVE ALLOWED** (artefact remediable = 0) | **Yes** |

---

## 7–11. Outstanding remediable pack (summary)

| Cell | Status |
|------|--------|
| Lit same-metrics (latency/thr retained; meter gap-fill) | **Filled** — §2 |
| Alts / synth | moto = harness only; live finals + w1w2_a = evidence |
| Config manual | Present + audit reproduce |
| Claim↔evidence | Key reject; capacity/interaction null; W1/W2 exploratory retained |
| Accidental silent park | Forbidden — N-Rasool dated in §4 + tracker |

---

## 8. Honest CA2 floor

**~88.** W3/W4 pooled ANOVA + w1w2_a key-cells landed; soft depth on W1/W2 and formal n=30 retained honestly. Do **not** market 100 / full W1–W4 confirmatory ANOVA.
