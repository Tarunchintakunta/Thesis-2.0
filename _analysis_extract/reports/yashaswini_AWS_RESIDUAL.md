# Yashaswini alignment residual (AWS-goal → sole-AWS ready)

**Updated:** 2026-09-20 (lite Leg 3 prep; apply deferred — concurrency)  
**Alignment after CausalRCA quarantine + claim hygiene:** **~88/100** (was ~75%)  
**Live Leg 3:** **not closed** — prep ready; no measured `results/live/` yet

## Compact
`RQ9 Obj12 Method12 Impl13 Exp11 Metrics10 Evidence9 Claims7 Rubric5` → **~88/100**

## Hygiene / non-AWS work done
- `evaluation.tex` Leg 2 tables locked to `results/rcaeval/*` (AC@3=0.611, F1=0.469)
- CausalRCA **quarantined** as non-peer: $n{=}4$ + `fixed_order.json` share$=1.0$ (not an AWS blocker)
- `yashaswini_final_report.md` rewritten; invented competitiveness / live overhead withdrawn
- Intro Leg 2/3 wording corrected; latex `refs.bib` synced from verified artefact bib (DOI notes)
- STATUS <100%; overhead estimator-only

## Lite Leg 3 prep (this round) — READY, not applied

| Check | Result |
|-------|--------|
| Free-Tier lite plan | **yes** — `configs/experiment_lite_overhead.yaml`: 5 min × 3 conditions @ 1 rps (~900 req, ≈$0.009 list-price ignore FT) |
| Services | Lambda + API GW + DDB + CW + X-Ray (CA2) |
| Tags | `project` / `managed_by` / `purpose` / `data` only (no student name/ID) |
| Stack names | Terraform `name_prefix=faultlab` (no collision with `idem-eval-*`, `coldstart-study-*`, `sflad-*`, `ddbpk-*`) |
| Packages | `scripts/package_terraform.sh` → `build/*.zip` |
| Terraform | `terraform validate` **OK**; `plan` **27 to add** in `eu-west-1` |
| Runbook | `docs/LITE_LEG3_OVERHEAD.md`; `--config` on `campaign.py` / `collect_overhead.py` |
| Destroy after | yes (documented) |

## Exact blocker — STOP (no invent metrics)

**Account Lambda concurrency saturated by concurrent student campaigns.**

| Fact | Value (eu-west-1, 2026-09-20) |
|------|-------------------------------|
| Account `ConcurrentExecutions` limit | **10** |
| Observed account ConcurrentExecutions (recent) | **8–10** peak (often 8–9) |
| Active pressure | `idem-eval-fn` ≈4; `ddbpk-driver` ≈4; `coldstart-study-warm-*` present |
| Headroom for faultlab | **unsafe** — lite @1 rps still fans out orders-api→inventory/payments (sync) |

Per gate: *if concurrent Lambda pressure looks dangerous, prepare everything and wait — report readiness instead of apply.*

**Did not** `terraform apply`. **Did not** invent overhead numbers. **Did not** upgrade AWS account.

## Sole hard residual to 100%
1. Live Leg 3 AWS overhead campaign (`results/live/` still absent) — run lite (or full) when concurrency headroom exists, then destroy

**Soft / disclosed (not blockers to AWS):** optional CausalRCA 90-case completion; optional PDF rebuild.

**AWS residual:** yes (Leg 3) — **sole** — prep complete, execution deferred

```
GATE_READY=yes AWS_CLASS=required SOLE_AWS_RESIDUAL=yes READY_FOR_AWS=yes
LITE_PREP=yes LITE_APPLIED=no LIVE_OVERHEAD_EVIDENCE=no
BLOCKER=account_lambda_concurrency_limit_10_shared_campaigns
NEXT=wait_for_headroom_then_make_tf-package_apply_lite_destroy
```
