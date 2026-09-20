# Consolidated COMPLETE / NOT COMPLETE

**Updated:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**COMPLETE** only at Research Alignment to CA2 = **exactly 100%**.

## Gates
| Gate | Status |
|------|--------|
| Exploration (8) | **COMPLETE** |
| Terraform (8, no personal IDs) | **READY** — see `TERRAFORM_POLICY.md` / `GENUINE_AWS_GOAL_LIST.md` |
| Alignment-first | Open — AWS allowed only where sole residual = live CA2 AWS |
| Live AWS campaigns | **IN PROGRESS** (Vikas + Chaitanya); Venkat EC2 not yet applied |

## AWS-goal (8)

| Thesis | Sole AWS residual? | Live AWS | Alignment | **Status** |
|--------|:------------------:|:--------:|-----------|------------|
| Venkat | **yes** (EC2) | Terraform ready; CLI `--scheduler-address` wired; EC2 not applied | <100% | **NOT COMPLETE** |
| Chaitanya | **yes** (Init Duration) | **Py+Node Init + H4-lite DONE**; Java/H3/ROI pending | <100% | **NOT COMPLETE** |
| Vikas | **yes** (full campaign) | Campaign daemon workers=4 (~1.5/s; ETA hours) | <100% | **NOT COMPLETE** |
| Anji | **yes — sole hard (live SQS)** | No | **~90%** | **NOT COMPLETE** (READY_FOR_AWS=yes) |
| Varun | no (beats_naive + live S3) | No | **~70%** | **NOT COMPLETE** |
| Yashaswini | no (CausalRCA n=4 + Leg3) | No | **~75%** | **NOT COMPLETE** |
| Rasool | no (fill cells + live DDB) | No | **~74%** | **NOT COMPLETE** |
| Nemi | no (baseline/UNSW + cloud FL) | No | **~64%** | **NOT COMPLETE** |

## Alignment-only (4)

| Thesis | Approx alignment | Live AWS | **Status** |
|--------|-----------------:|:--------:|------------|
| Mehak | ~88% | **No** (do not deploy) | **NOT COMPLETE** |
| Pooja | ~85% | **No** | **NOT COMPLETE** |
| Uday | ~90% | **No** | **NOT COMPLETE** |
| Vishvaksen | ~86% | **No** | **NOT COMPLETE** |

Residuals: `mehak_alignment.md`, `pooja_alignment.md`, `uday_alignment.md`, `vishvaksen_alignment.md`; AWS-goal five: `anji_AWS_RESIDUAL.md`, `varun_AWS_RESIDUAL.md`, `yashaswini_AWS_RESIDUAL.md`, `rasool_AWS_RESIDUAL.md`, `nemi_AWS_RESIDUAL.md`.

## Credits
~$131 ceiling. Prefer destroy-after-round. Avoid long-lived EC2.
