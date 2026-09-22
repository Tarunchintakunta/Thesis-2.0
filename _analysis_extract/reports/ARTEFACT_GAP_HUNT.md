# Artefact gap hunt (no report)

**Rule:** Fix gaps by **design/config/scripts/runs**, not prose.  
**Wording:** **baseline** and **proposed** only (never “arm/arms”).  
**Driver:** `/RUBRIC_70_TO_100_STRATEGY.md` §16.  
**Pending queue:** `_analysis_extract/reports/PENDING.md`

Legend: OK = on-disk evidence · GAP = needs artefact work · SOFT = beyond-CA2 optional · IN FLIGHT = running

| Thesis | Baseline + proposed in matrix | Final-3 / repeats | Destroy-after | Neg cell kept | Stats runnable | Full-scale runner | Priority |
|--------|:-----------------------------:|:-----------------:|:-------------:|:-------------:|:--------------:|:-----------------:|----------|
| Anji | OK | OK | OK | OK | OK | campaign scripts | SOFT live n>1 |
| Chaitanya | OK (default vs optimised) | OK H1 finals | OK | OK | OK | live pack | SOFT n≥30 Init |
| Yashaswini | OK (off vs policy/full) | OK | OK | OK | OK | run_final_lite_leg3 | SOFT |
| Rasool | OK (K/mode contrasts) | OK | OK | OK | OK | run_final_keycell | SOFT W1/W2 |
| Varun | OK (Lifecycle vs RIC) | OK e1–e3 | OK | OK | OK | packs | SOFT |
| Vikas | OK (P1 vs P2/P3) | OK campaign | OK | OK | OK | campaign | re-run only if code changes |
| Nemi | OK (centralised vs FL) | OK | OK | OK | OK | live-cloud-fl | SOFT deeper FL |
| Venkat | OK (1×small vs 2×micro) | OK | OK | OK | OK | run_ec2_final_* | SOFT multi-order |
| Mehak | OK (RF/Aldomi vs MHSA) | OK | N/A local | OK | OK | train_and_evaluate | SOFT full dump |
| Pooja | OK (HPA vs PAKS) | OK | OK | OK | OK | run_final_k3s | SOFT multi-node |
| Uday | OK (QoS0 baseline vs QoS1 proposed) | **IN FLIGHT** f2→f3 | OK f1 | OK | OK | run_final_lite | **Finish final-3** |
| Vishvaksen | OK (oracle vs scanners) | OK | N/A | OK | OK | local scan | SOFT Verdet |

## Regression (binding)

Artefact change ⇒ tests + smoke + **full-scale eval again** (AWS or local) + destroy-after. Use credits usefully; do not leave stacks up.

**Updated:** 2026-09-22
