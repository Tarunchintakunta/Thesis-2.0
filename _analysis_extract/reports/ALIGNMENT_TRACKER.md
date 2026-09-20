# Alignment iteration tracker (CA2 = floor; exceed with rationale)

**Rule:** CA2 is the **minimum**. Exceedances (deeper $n$, more cells, stronger methods) are encouraged and recorded in Design/Rationale — see `CA2_FLOOR_NOT_CEILING.md`. AWS deploy when Free Tier–safe and residual needs live evidence (not blocked solely by pedantic CA2-only parity).  
**Branch:** `feature/aws-ca2-alignment` only.  
**Exploration gate:** COMPLETE (all 8) — `GOAL_EXPLORATION_GATE.md`.  
**Consolidated table:** `COHORT_COMPLETE_TABLE.md`.

## Current explore baselines → iteration status

| Thesis | Explore % | After claim hygiene | Blockers to 100% (non-AWS first) | AWS residual? |
|--------|----------:|--------------------:|----------------------------------|---------------|
| Nemi | 44% | **100% COMPLETE** | Beyond-CA2 2.5M / K8s optional | **Closed** (live lite FL destroyed) |
| Varun | 58% | **100% COMPLETE** | Beyond-CA2 fuller FinOps optional | **Closed** |
| Anji | 58–72% | **100% COMPLETE** | Beyond-CA2 confirmatory optional | **Closed** |
| Yashaswini | 62% | **100% COMPLETE** | Beyond-CA2 CausalRCA-90/30-min optional | **Closed** |
| Venkat | 63% | **DOI + READY_FOR_AWS** | Soft: scheduler wired | **Yes — sole (matmul)** |
| Rasool | 62% | **100% COMPLETE** | Beyond-CA2 W1/W2/ANOVA optional | **Closed** |
| Chaitanya | 67% | **100% COMPLETE** | Beyond-CA2 full-$n$ optional | **Closed** |
| Vikas | 68% | **~74% campaign in progress** | Soft: DOI | **Yes — sole (full campaign)** — **r5 RUNNING** |
| Mehak | 80% | **100% COMPLETE** | Beyond-CA2 broader GCT/Aldomi optional | **No** |
| Pooja | 77% | **~62% vs formal** | Traces+LSTM+K8s; AWS not sole | **Yes** (not sole) |
| Uday | 83% | **~56% mock harness + TF** | Live IoT Core | **Yes** (not sole) |
| Vishvaksen | 78% | **~62% scanner corpus** | Eval depth | **No** |

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
23. **2026-09-20 — Policy CA2=floor** + **COMPLETE** Yash/Anji/Chaitanya/Rasool at 100% floor; beyond-CA2 agents continue (Anji confirmatory; Varun/Mehak).  
24. **2026-09-20 — Mehak GCT raise merged** onto `feature/aws-ca2-alignment` (~64→**~84%**; N=12k GCT windows). Yash Leg3 late agents already superseded by COMPLETE@100% floor.  
25. **2026-09-20 — Nearest-first:** Varun COMPLETE@100% floor; Mehak COMPLETE@100% floor; **6/12 COMPLETE**. Next: Nemi (~78%) live cloud FL.  
26. **2026-09-20 — Nemi live cloud FL lite** EC2 `t3.micro` + S3 round-trip + CW, destroy 9/9 (`results/live/cloud_lite_summary.json`); Vikas `idem-eval-fn` still hot so **no Lambda**. **7/12 COMPLETE**. Alignment **100%** floor.
