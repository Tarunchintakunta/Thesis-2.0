# Initial evaluation pass (live cloud FL lite)

**Date:** 2026-09-21 (gate recorded; live round 2026-09-20)  
**Evidence:** `../cloud_lite_summary.json` (copied pointer artefacts in this folder)  
**Protocol:** Free-Tier `t3.micro` + S3 artefact bus + CloudWatch; 2 in-process clients × 3 rounds × 2500-row real-lite UNSW sample; stack **destroyed** after round.  
**INITIAL_EVAL_PASS:** **yes**

## Verdict
CA2 re-check after this live method round: still **100%** research-scope floor (`DESIGN_RATIONALE_BEYOND_CA2.md`). Centralised comparator + real-lite sample + live cloud FL lite close the floor. Soft items (full 2.5M-flow, 50-round, Docker/K8s charts) remain beyond-CA2.

## Artefacts
- `cloud_lite_summary.json` (symlink/copy of authoritative live summary)
- Live provenance under `../` (`ssm_params_*.json`, `s3_listing_*.txt`, destroy inventory)

Final-3 confirmatory full-scale live rounds are **not** started here.
