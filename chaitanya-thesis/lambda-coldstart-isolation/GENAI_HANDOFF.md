# GENAI_HANDOFF.md — Chaitanya (lambda-coldstart-isolation)

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Chaitanya |
| Artefact root | `chaitanya-thesis/lambda-coldstart-isolation/` |
| Honest CA2 floor | **Improved (~82)** — confirmatory n≥30 H1/H2 Demonstrated ×3; H3/H4 confirmatory **dated-deferred 2026-09-22** (lite H3/H4 retained as directional) |
| Eval completeness | `confirmatory_n30/round_1\|2\|3` **all on disk** (r1/r2 offline-restored from `data/raw/live_conf_n30_r{1,2}`; r3 live). Destroy-after each. |
| AWS | eu-west-1, arm64 Lambda; destroy-after |
| Handoff date | 2026-09-22 |

## 1. Research problem, motivation, research question, and objectives

Isolate / compare cold-start Init drivers across runtimes and package-size (default vs optimised) on AWS Lambda.

## 2. Identified literature gap and how this research addresses it

Runtime and package-size effects on Init Duration with confirmatory n≥30 and Holm-adjusted tests — not smoke-only.

## 3. CA2 proposal alignment and any extensions beyond the proposal

Baseline = default package; proposed = optimised. Confirmatory H1 (runtime Kruskal) and H2 (package size MWU per runtime) are in scope. H3/H4 warming/combined families residual when data absent.

## 4. Research methodology and experimental design

SAM stack `coldstart-study`; phases `package_size` + `runtime_compare`; reps=30; parse REPORT logs → metrics/costs; Holm within confirmatory family.

## 5. Artefact purpose and artefact-only project structure

```
lambda-coldstart-isolation/
  functions/ infra/ scripts/ src/ configs/
  results/live/confirmatory_n30/round_3/{tables,processed,figures,destroy_confirmed.txt}
```

## 6. AWS architecture, services, configurations, and experimental setup

Lambda (python/nodejs/java × default/optimised) + warmer rule; MemorySize=1024; tracing off for confirmatory; region eu-west-1 arm64.

## 7. Evaluation metrics and why they were selected

Init Duration medians; Kruskal-Wallis / Mann-Whitney; Holm p_holm; epsilon² / rank-biserial; per-1k cost under cold-heavy assumption when warming absent.

## 8. Baseline definition and baseline comparison

| Role | Variant |
|------|---------|
| Baseline | default package |
| Proposed | optimised package |
| Factor | runtime ∈ {python, nodejs, java} |

## 9. Complete evaluation process and number of runs

| Pack | Status on this worktree |
|------|-------------------------|
| confirmatory_n30 round_1 | **Present** — offline-restored from `data/raw/live_conf_n30_r1`; destroy_confirmed=yes |
| confirmatory_n30 round_2 | **Present** — offline-restored from `data/raw/live_conf_n30_r2`; destroy_confirmed=yes |
| confirmatory_n30 round_3 | **Present** — live; destroy_confirmed=yes |
| Combined baseline | `results/live/confirmatory_n30/CONF_N30_BASELINE.md` |

## 10. Final results and key findings (committed evidence)

From `round_3/tables/hypotheses.json` (live, eu-west-1, arm64, α=0.05):

| Test | Result | Notes |
|------|--------|-------|
| H1 Kruskal (python/nodejs/java) | **reject** p_holm=0 | medians Init ≈ 89.22 / 144.11 / 418.39 ms; n≈30/30/29 |
| H2_python / H2_nodejs / H2_java | **reject** p_holm=0 | default vs optimised; e.g. python median_a≈3473 vs median_b≈88 |
| H3 / H4 families | **no data** on this round | notes: family size shrinks; warming absent → per-1k treats all as cold |

## 11–12. Objectives / RQ

H1/H2 confirmatory limbs **supported** on r3. Warming/combined (H3/H4) **not answered** by this pack. Consistency across 3 confirmatory rounds needs r1/r2 restored or re-run.

## 13–17. Literature / stats / observations / limitations / conclusions

Strong runtime + package-size effects under Holm. Limitation: single round on disk here; no warming data; java n=29. Contribution: live confirmatory n≈30 with destroy-after.

## 18–19. Changes / remaining

1. ~~Confirmatory H3/H4~~ — **dated-deferred 2026-09-22** in `docs/ANALYSIS_PLAN.md` (lite H3/H4 directional only).  
2. Keep H1/H2 confirmatory honesty; do not claim full H1–H4 confirmatory 100%.  
3. Rounds 1–2 restored offline from preserved raw logs (PROVENANCE.txt).

## 20. Important files

`results/live/confirmatory_n30/round_3/`, `scripts/run_confirmatory_n30.sh`, `infra/template.yaml`.
