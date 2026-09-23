# Venkat — ONE source of truth (thesis)

**Authority:** formal CA2 RQ (matched-vCPU scale-up vs scale-out; growing orders; time/memory/CPU) + live `distributed-matrix-scaling/results/live/`.  
**Baseline (binding):** Sabir & Alebrahim (2025) — `baseline_papers/BASELINE_PAPER.md` DOI:10.3390/math13020298.  
**Audit script (binding):** `distributed-matrix-scaling/scripts/audit_size_ladder_root_causes.py` → `results/live/size_ladder_ladder1/analysis/size_ladder_audit_report.{json,md}`  
**Move rule:** report/viva fold-later OK; do **not** leave while audit `move_blocker=true`. No fabricated crossover / marketing 100.  
**Date:** 2026-09-23.

---

## 0. Examiner self-verdict (after scripted size-ladder audit)

| Question | Answer |
|----------|--------|
| Outstanding (artefact/eval remediable)? | **NO** — audit remediable=0; config + SoT present |
| Strong (matched-vCPU live matmul)? | **Yes** — finals ×3 + RSS ×3 + size ladder 100/250/500 |
| Strong (distribution beats scale-up)? | **No** — **anti-crossover retained** (honest negative) |
| Audit remediable gaps? | **0** (`audit_size_ladder_root_causes.py` EXIT 0) |
| Report / viva? | Fold later |

### Why scripts, not manual

Soft N “full live 200–2000” and anti-crossover honesty must be proven by pack inventory + ratio checks, not chat. Script EXIT 0 → disposition **`DATED_WONTFIX_FULL_LIVE_LADDER_AMENDED`**.

---

## 1. CA2 proposed (fresh)

| Item | Formal CA2 / artefact RQ |
|------|--------------------------|
| RQ | How do **scale-up** vs **scale-out** matrix multiply compare on cloud for completion time, peak memory, and CPU efficiency as matrix order grows? |
| Topology | Matched aggregate cores: **1× t3.small** vs **2× t3.micro** (2 vCPU) |
| Metrics | elapsed_s, peak_rss_mb, avg_cpu_percent |
| Growing-order limb | Increasing n at fixed cores; crossover or no-crossover |
| Ops | Destroy-after; Free-Tier–safe |

---

## 2. SAME METRICS — live vs Sabir baseline

Sabir & Alebrahim (2025) report **multi-threaded / shared-memory** matrix–LU style **completion time** (and related efficiency) — not matched-vCPU multi-instance Dask on EC2. Ours keep **time** as the shared name and add live **peak RSS** + **avg CPU** + growing-order limb on EC2.

| Metric name | Sabir-style / lit | **Ours (live)** | Same name? | Honest note |
|-------------|-------------------|-----------------|:----------:|-------------|
| Completion / wall time | Threaded LU/matmul time | `elapsed_s` scale-up + multi | Yes | Primary shared DV |
| Peak memory | Often absent / not EC2 | `peak_rss_mb` (rss + ladder) | Gap-fill | Multi ~72–81 MB |
| CPU utilisation | Platform/thread efficiency | `avg_cpu_percent` | Partial | Multi ~39–46% |
| Scale-out distributed | Not Sabir’s EC2 limb | 2× t3.micro `da.matmul` | Extended | Contribution |
| Growing orders | Size sweeps in MT lit | live 100/250/500 + local 200–2000 | Yes (subset live) | Full live WONTFIX |

**Do not claim:** “we beat Sabir’s threaded times on EC2.” Different topology. Claim = matched-vCPU scale-up vs scale-out with RSS/CPU + anti-crossover honesty.

### Live confirmatory numbers (cite these)

**Time finals — `final_1–3` (n=250 multi `da.matmul`)**

| Round | status | elapsed_s |
|------:|:------:|----------:|
| 1 | ok | 0.2480 |
| 2 | ok | 0.2517 |
| 3 | ok | 0.2484 |

**RSS/CPU — `rss_size_final_1–3` (n=250)**

| Round | scale-up elapsed_s | multi elapsed_s | multi peak_rss_mb | multi avg_cpu% |
|------:|-------------------:|----------------:|------------------:|---------------:|
| 1 | 0.002467 | 0.2532 | 72.49 | 44.4 |
| 2 | 0.001914 | 0.2736 | 72.47 | 46.1 |
| 3 | 0.002016 | 0.2661 | 72.84 | 38.6 |

**Size ladder — `size_ladder_ladder1`**

| n | scale-up elapsed_s | multi status | multi elapsed_s | multi peak_rss_mb | multi avg_cpu% |
|--:|-------------------:|:------------:|----------------:|------------------:|---------------:|
| 100 | 0.000213 | ok | 0.2442 | 71.79 | 43.8 |
| 250 | 0.002101 | ok | 0.2549 | 72.58 | 42.0 |
| 500 | 0.007588 | ok | 0.2855 | 80.84 | 46.1 |

**Reading:** scale-up ≪ multi at every live order (**anti-crossover retained**). Distribution does **not** pay sooner in this Free-Tier range.

---

## 3. Master table — CA2 · lit · artefact · status

| # | CA2 proposed | Literature / baseline | Artefact live | Same-metrics? | Status |
|---|--------------|----------------------|---------------|:-------------:|--------|
| 1 | Matched-vCPU scale-up vs scale-out | Sabir threaded shared-mem | 1×small vs 2×micro | time named | **MET** |
| 2 | Completion time | Sabir time | `elapsed_s` finals/RSS/ladder | Yes | **MET** |
| 3 | Peak memory + CPU | Often thin in baseline | `peak_rss_mb` / `avg_cpu_percent` | Gap-fill | **MET** |
| 4 | Growing orders / crossover | Size sweeps | ladder 100/250/500 | Yes (FT subset) | **MET (anti-crossover)** |
| 5 | Full live 200–2000 EC2 | — | **absent** (amended) | — | **WONTFIX 2026-09-23** |
| 6 | Destroy-after | Ethics | destroy_confirmed packs | — | **MET** |
| 7 | Holm across orders | Optional polish | not shipped | — | **soft beyond CA2** |

---

## 4. Soft / N — hard-closed

| ID | Item | Close |
|----|------|-------|
| **N-Venkat** | Full live 200–2000 EC2 ladder | **DATED_WONTFIX 2026-09-23** — `DATED_WONTFIX_FULL_LIVE_LADDER_2026-09-23.md` + DESIGN; audit EXIT 0 |
| Anti-crossover | Distribution slower | **Evidenced negative** — §2; campaign `anti_crossover_retained=true` |
| Marketing 100 / crossover win | Forbidden | Keep ~85 floor + anti-crossover visible |
| Scale-up RSS≈0 on ultrashort run | Sampler | Documented in `RSS_FINAL3_BASELINE.md` — multi RSS primary |

```bash
cd venkat-bora-thesis/distributed-matrix-scaling
python3 scripts/audit_size_ladder_root_causes.py
# EXIT 0; remediable_total=0
```

---

## 5. Evidence packs

| Pack | Role |
|------|------|
| `final_1`…`final_3` | Time smoke ×3 |
| `rss_size_final_1`…`3` | RSS/CPU ×3 |
| **`size_ladder_ladder1/`** | Growing-order Free-Tier limb + **audit report** |
| `FINAL3_BASELINE.md` / `RSS_FINAL3_BASELINE.md` / `SIZE_LADDER_BASELINE.md` | Binding baselines |
| Local `results/data/summary_statistics.json` | Full 200–2000 offline |

---

## 6. Thesis gate

| Gate | Done |
|------|:----:|
| Scripted audit EXIT 0 | **Yes** |
| N-Venkat full live ladder hard-closed | **Yes** |
| ONE-file SoT + same-metrics | **Yes** |
| Config manual | **Yes** (`CONFIGURATION_MANUAL.md`) |
| **MOVE ALLOWED** | **Yes** |

---

## 7–11. Outstanding remediable pack

| Cell | Status |
|------|--------|
| Spec / RQ | **Closed** — §1 |
| Lit / Sabir same-metrics | **Closed** — §2 |
| Artefact (matched vCPU + destroy) | **Closed** — packs |
| Eval (time/RSS/CPU + anti-crossover) | **Closed** — §2–§3 |
| Config | **Closed** — live+local |
| Report / viva | Fold later — **does not block MOVE** |

---

## 8. Objective → evidence

| Objective | Evidence | Achieved? |
|-----------|----------|:---------:|
| Scale-up vs scale-out time | finals + ladder elapsed_s | **YES** |
| Peak memory / CPU on live | rss_size_final ×3 + ladder | **YES** |
| Growing-order limb | size_ladder 100/250/500 | **YES (FT)** |
| Crossover detection | anti-crossover retained | **YES (honest)** |
| Full live 200–2000 | amended | **WONTFIX** |

---

## 9. Literature critique (one line)

Sabir strengthens threaded LU/time methodology but does not close matched Free-Tier multi-instance EC2 with RSS/CPU + growing-order honesty — this thesis fills that limb and retains the negative (no crossover).
