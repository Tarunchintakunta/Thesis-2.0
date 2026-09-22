# Nemi final-3 baseline (live cloud FL lite)

**Date:** 2026-09-21  
**Packs:** `results/live/final_1|2|3/`  
**Protocol:** 1× t3.micro + S3 + CW; 2 in-process clients × 3 rounds × 2500-row real-lite; destroy-after each.

## Destroy
All three rounds: terraform destroy complete + verified absent.

## Verdict
- **Positive:** three independent live FL lite rounds; no Lambda; destroy confirmed.
- **Soft:** lite depth (not 50-round / full 2.5M-flow) — beyond-CA2.

**CA2 floor:** still **100%**.
