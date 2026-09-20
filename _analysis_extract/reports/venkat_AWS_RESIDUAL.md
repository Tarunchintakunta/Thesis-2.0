# Venkat — AWS residual gate note

**Date:** 2026-09-20  
**Branch:** `feature/aws-ca2-alignment`  
**Artefact:** `venkat-bora-thesis/distributed-matrix-scaling/`

## Non-AWS alignment (evidence)
- Eval/STATUS match `results/data/summary_statistics.json` (local Dask suite).
- Local Dask ≠ completed multi-instance EC2 matmul (documented).
- No crossover through 2000×2000 in committed local JSON.
- DOI `note={doi:…}` on bibliography DOI entries.
- Terraform at `terraform/` — defaults `t3.small` / `t3.micro` / `count=2` (matched 2 vCPU).

## Live EC2 round-1 (evidence)
- Artefact: `results/live/ec2_round1_summary.json` (`eu-west-1`; fleet destroyed after round).
- Topology: **1× t3.small** scale-up vs **2× t3.micro** scale-out (matched aggregate 2 vCPU).
- Scale-up numpy n=500: **0.006709 s**.
- On-node Dask LocalCluster per micro n=500: mean **0.5252 s**.
- Multi-instance: 2 workers registered; futures smoke OK; **`da.matmul` timed out** — no completed multi-instance matmul timing.

## Sole hard residual
Multi-instance `da.matmul` completion (round-1 timed out) **and** evaluation LaTeX full sync to live cells. Not “no EC2 at all.”

## READY_FOR_AWS_ALIGNMENT_PATH
**yes** (round-1 path exercised; residual is completion/sync, not bootstrap)

## Discipline
Prefer least-privilege IAM; ~$131 credit ceiling; destroy after rounds; no hallucinated EC2 / multi-instance matmul timings.
