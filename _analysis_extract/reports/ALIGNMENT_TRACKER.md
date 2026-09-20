# Alignment iteration tracker (AWS blocked until 100%)

**Rule:** No AWS deploy until Research Alignment to CA2 = **100%** per thesis (or sole remaining gaps are the live-AWS experiments CA2 requires).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md` — all **NOT COMPLETE**.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **~78% centralised+real UNSW** | Soft: full 2.5M / improved plateau | **Yes — sole (cloud FL)** |
| Varun | 58% | **~93% metadata + FinOps notes** | Soft: live Inventory job; fuller FinOps campaign | **Yes — sole (fuller FinOps)** |
| Anji | 58–72% | **~96% live SQS lite + fidelity** | Soft: confirmatory n>1 | **No — hard lite closed** |
| Yashaswini | 62% | **~97% lite Leg3 + learned-LB subset** | Soft: CausalRCA 90 / PDF | **No — hard Leg3 closed (lite)** |
| Venkat | 63% | **DOI + READY_FOR_AWS** | Soft: scheduler wired | **Yes — sole (matmul)** |
| Rasool | 62% | **~94% live DDB 12/12 + exploratory stats** | Soft: W1/W2 / confirmatory n | **No — hard K×W3/W4 closed** |
| Chaitanya | 67% | **~97% live Init+H3+H4 + lite Holm** | Soft: confirmatory n≥30 | **No — hard Init closed (lite)** |
| Vikas | 68% | **~74% campaign in progress** | Soft: DOI | **Yes — sole (full campaign)** — **r5 RUNNING** |
| Mehak | 80% | **~64% vs formal** | GCT files + Aldomi-on-GCT | **No** |
| Pooja | 77% | **~48% vs formal** | Traces+LSTM+K8s; AWS not sole | **Yes** (not sole) |
| Uday | 83% | **~18% vs formal MQTT** | Artefact≠CA2 | **Yes** (not sole) |
| Vishvaksen | 78% | **~28% vs formal scanner** | Artefact≠CA2 | **No** |

## Iteration log
1–13. Prior hygiene / exploration / formal rescore (see git history).  
14. **2026-09-20 — Anji live SQS lite** 4/4 + destroy (~94–98%).  
15. **2026-09-20 — Varun live S3 lite** + Wilcoxon (~90%).  
16. **2026-09-20 — Chaitanya live Init+H4+H3-lite** (~94–95%).  
17. **2026-09-20 — Rasool live DDB 12/12** K×cap×W3/W4 + destroy (~88–92%).  
18. **2026-09-20 — Mehak non-AWS raise** (~54→~64); GCT still absent.  
19. **2026-09-20 — Nemi non-AWS raise** (~68→~78); sole=cloud FL; no apply.  
20. **2026-09-20 — Yashaswini Leg3 lite prep** (validate/plan; apply deferred under concurrency=10).  
21. **2026-09-20 — Reconverge** agent cursor/* branches onto `feature/aws-ca2-alignment`; Vikas r5 workers=4 continues.  
22. **2026-09-20 — Yashaswini Leg3 lite live** apply→3 conditions→`results/live/overhead.json`→destroy (~96%; sole AWS residual closed; reduction=0.803).
24. **2026-09-20 — High-% soft residuals (no new AWS apply):** Yash learned-LB subset $n{=}8$ (~96→~97); Anji live↔sim relative-rank fidelity (~94→~96); Chaitanya lite Holm + bytecode drop (~95→~97); Rasool exploratory n=1 stats (~92→~94); Varun metadata collector + FinOps notes (~90→~93). **None COMPLETE.**
