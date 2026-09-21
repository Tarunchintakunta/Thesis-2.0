# Venkat — AWS residual gate note

**Date:** 2026-09-21  
**Artefact:** `venkat-bora-thesis/distributed-matrix-scaling/`

## Non-AWS alignment (evidence)
- Eval/STATUS match `results/data/summary_statistics.json` (local Dask suite).
- Local Dask ≠ EC2 multi-instance (documented).
- No crossover through 2000×2000 in committed local JSON.
- Terraform at `terraform/` — defaults `t3.small` / `t3.micro` / `count=2` (matched 2 vCPU); `python3.11` user_data; intra-SG TCP for workers.

## Live EC2 round-1 (evidence)
- Artefact: `results/live/ec2_round1_summary.json` (`eu-west-1`; fleet destroyed).
- Topology: **1× t3.small** vs **2× t3.micro**.
- Multi-instance: futures smoke OK; **`da.matmul` timed_out** at n=500.

## Live EC2 round-2 (evidence) — residual closed
- Artefact: `results/live/ec2_round2_summary.json` (`eu-west-1`; fleet destroyed).
- Binding timings (from that JSON only):
  - Scale-up numpy n=250: **0.001562 s**
  - On-node Dask LocalCluster mean n=250: **0.5497 s**
  - Multi-instance `da.matmul` n=250: **0.2546 s**, status **ok**, **2** workers, futures `[0,1,4,9]`, scheduler `tcp://172.31.15.96:8786`
- Destroy verified: instances **terminated**; SG/IAM gone; terraform state empty.

## Sole hard residual
**closed** — multi-instance `da.matmul` completed; STATUS/alignment/scoreboard folded.

## Soft residuals (beyond CA2 floor)
- LaTeX evaluation chapter prose sync
- Optional multi-order live crossover sweep
- Live RSS/CPU; inferential artefacts

## READY_FOR_AWS_ALIGNMENT_PATH
**closed** (campaign executed; destroy confirmed)

## Discipline
Prefer least-privilege IAM; Free-Tier–safe types; destroy after rounds; no hallucinated timings.
