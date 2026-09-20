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
| Live AWS campaigns | **IN PROGRESS** (Anji lite 4/4 done; Vikas/Chaitanya/Venkat as listed) |

## AWS-goal (8)

| Thesis | Sole AWS residual? | Live AWS | Alignment | **Status** |
|--------|:------------------:|:--------:|-----------|------------|
| Venkat | **yes** (multi-instance matmul + eval sync) | Round-1 saved (`ec2_round1_summary.json`); `da.matmul` timed out | <100% | **NOT COMPLETE** |
| Chaitanya | **soft** (confirmatory $n$ / Holm / bytecode) | Init+H3+H4+ROI-lite **DONE** (`data/processed/live/`; n=12; H3 on0/off0.2) | **~95%** | **NOT COMPLETE** |
| Vikas | **yes** (full campaign) | Campaign_r2 daemon seed=20260929 workers=4 | <100% | **NOT COMPLETE** |
| Anji | **partial** (confirmatory/deeper live still open) | Lite **4/4 done** (`results/live/key_cells/`; n=1; ≈$0.00144) | **~94%** | **NOT COMPLETE** |
| Varun | **yes** (full S3 FinOps) | Lite DONE (`live_lite_summary.json`; CE $3.6e-09; GET 187/524 ms; Wilcoxon p≈1e-7; destroyed) | **~90%** | **NOT COMPLETE** (`READY_FOR_AWS=yes`) |
| Yashaswini | **yes** (Leg3) | No | **~88%** | **NOT COMPLETE** (`READY_FOR_AWS=yes`) |
| Rasool | **yes** (live DDB) | No | **~78%** | **NOT COMPLETE** (READY_FOR_AWS=yes) |
| Nemi | no (baseline/UNSW + cloud FL) | No | **~68%** | **NOT COMPLETE** |

## Formal-CA2 rescore (4) — was “alignment-only / proxy”

Rescored 2026-09-20 against formal docx (not proxy `CA2_COMMITMENTS`). **No AWS deploy this pass.** Synthetic is a blocker only where formal requires real traces (Mehak GCT; Pooja GCT/Alibaba) — **not** where formal commits to synthetic (Uday devices; Vish corpus).

| Thesis | Formal file | Approx alignment | AWS required by formal? | Live AWS | **Status** |
|--------|-------------|-----------------:|:-----------------------:|:--------:|------------|
| Mehak | `MAHEK NAAZ.docx` | **~64%** | **no** (Colab/EC2 train optional) | **No** | **NOT COMPLETE** |
| Pooja | `Pooja_25120921_CA2.docx` | **~48%** | **yes** (EC2/S3/CloudWatch+K8s) | **No** | **NOT COMPLETE** (Gantt missing — note) |
| Uday | `UdayKiranReddyDodda_X25166484_proposal.docx` | **~18%** | **yes** (IoT Core+Lambda+DDB) | **No** | **NOT COMPLETE** (artefact≠MQTT CA2) |
| Vishvaksen | `VishvaksenMachana_25173421_proposal.docx` | **~28%** | **no** (do not apply) | **No** | **NOT COMPLETE** (artefact≠scanner CA2) |

Residuals: `mehak_alignment.md`, `pooja_alignment.md`, `uday_alignment.md`, `vishvaksen_alignment.md`; AWS-goal: `anji_AWS_RESIDUAL.md`, `varun_AWS_RESIDUAL.md`, `yashaswini_AWS_RESIDUAL.md`, `rasool_AWS_RESIDUAL.md`, `nemi_AWS_RESIDUAL.md`, `venkat_AWS_RESIDUAL.md`, `chaitanya_AWS_RESIDUAL.md`, `vikas_AWS_RESIDUAL.md`.

## Credits
~$131 ceiling. Prefer destroy-after-round. Avoid long-lived EC2.
