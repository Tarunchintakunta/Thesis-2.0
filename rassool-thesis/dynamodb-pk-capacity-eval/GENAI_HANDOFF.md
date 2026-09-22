# GENAI_HANDOFF.md — Rasool (dynamodb-pk-capacity-eval)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Rasool |
| Artefact root | `rassool-thesis/dynamodb-pk-capacity-eval/` |
| Honest CA2 floor | **PARTIAL (~82)** — W3/W4 live + pooled ANOVA Demonstrated; W1/W2 **dated-deferred** (not claimed filled) |
| Eval completeness | Live keycells + `final_1\|2\|3` for W3/W4; destroy-after; pooled confirmatory ANOVA on disk |
| AWS | DynamoDB live fleets (historically eu-west-1); slot free after destroy |
| Handoff date | 2026-09-22 |

## 1. Research problem, motivation, research question, and objectives

Effect of partition-key design and capacity mode on DynamoDB latency/throttle/cost under defined workloads.

## 2. Identified literature gap and how this research addresses it

Live factorial evidence (key × capacity) vs moto-only claims — with confirmatory pooled ANOVA across finals.

## 3. CA2 proposal alignment and any extensions beyond the proposal

Proposal / experiment.yaml register W1–W4. **Delivered:** W3/W4 live + pooled ANOVA. **W1/W2:** dated scope amendment in `docs/ANALYSIS_PLAN.md` (2026-09-22) — deferred beyond confirmatory floor; do not claim filled.

## 4. Research methodology and experimental design

Key-cell live fleets; three finals; pooled two-way ANOVA with interaction on latency (and related metrics) across configs.

## 5. Artefact purpose and artefact-only project structure

```
dynamodb-pk-capacity-eval/
  src/ scripts/ terraform/ results/
  results/final_{1,2,3}/ results/pooled_final3_anova.json results/FINAL3_BASELINE.md
```

## 6. AWS architecture, services, configurations, and experimental setup

Live DynamoDB capacity/key configurations for W3/W4; destroy-after rounds.

## 7. Evaluation metrics and why they were selected

Latency mean/p99; throttle; cost; two-way ANOVA F/p/partial η² for key, capacity, interaction.

## 8. Baseline definition and baseline comparison

Factorial cells across key designs × capacity modes (baseline vs proposed keys within W3/W4). Do not assume proposed keys win — report F/p honestly.

## 9. Complete evaluation process and number of runs

| Pack | Path |
|------|------|
| final_1–3 | `results/final_{1,2,3}/` |
| Pooled ANOVA | `results/pooled_final3_anova.json` (source_packs final_1–3; n_rows=36) |
| Keycell live | `results/keycell_summary.json` (+ logs) |

## 10. Final results and key findings (committed evidence)

From `pooled_final3_anova.json` (W3 factorial_latency_mean_ms):

| Term | df | F | p | partial_η² |
|------|---:|--:|--:|----------:|
| key | 2 | **59.000** | **1e-06** | 0.908 |
| capacity | 1 | 1.269 | 0.282 | 0.096 |
| interaction | 2 | 0.209 | 0.814 | 0.034 |

Independent review also cites W4 Key F≈17 p≈3e-4. Live 12/12 keycells historically; destroy-after.

## 11–12. Objectives / RQ

W3/W4 key-factor effects **supported** (strong key F; capacity/interaction ns on W3 mean latency). W1/W2 **unanswered by measurement** — explicitly deferred 2026-09-22 in ANALYSIS_PLAN (not hidden).

## 13–17. Literature / stats / observations / limitations / conclusions

Confirmatory pooled ANOVA is the statistical contribution. Limitation: W1/W2 absent; per-pack n=1 exploratory only. Keep moto-only claims corrected.

## 18–19. Changes / remaining

1. ~~Dated ANALYSIS_PLAN deferral~~ — done 2026-09-22.  
2. Do not claim full W1–W4 CA2 100%. Optional: reopen W1/W2 only when slot free and no higher-priority residual.

## 20. Important files

`docs/ANALYSIS_PLAN.md` (W1/W2 amendment), `results/pooled_final3_anova.json`, `results/final_{1,2,3}/`, `FINAL3_BASELINE.md`, experiment YAML registering W1–W4.
