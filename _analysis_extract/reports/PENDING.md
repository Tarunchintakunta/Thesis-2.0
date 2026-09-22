# Pending work (artefact-first; no report writing)

**Language:** use **baseline** and **proposed** only — never “arm(s)”.  
**Credits:** ~$100+ Free Tier / promo — use **aggressively and usefully** for full-scale AWS where the thesis is AWS-class.  
**Regression rule:** any artefact code/config/IaC change ⇒ **full regression** (tests + one smoke) then **full-scale evaluation again** (AWS or local per thesis), destroy-after. Do not half-rerun.

Strategy: `/RUBRIC_70_TO_100_STRATEGY.md` · Gap sheet: `_analysis_extract/reports/ARTEFACT_GAP_HUNT.md`

---

## Now (blocking)

| # | Item | Where | Action |
|--:|------|-------|--------|
| 1 | **Uday final-3** | `mqtt-qos-iot-core` AWS | **IN FLIGHT** final_3 campaign; then `write_final3_baseline.sh` (**baseline**=QoS0, **proposed**=QoS1) |
| 2 | **Chaitanya confirmatory n≥30** | Lambda AWS | After Uday: `run_confirmatory_n30.sh` — package_size + runtime_compare reps=30; destroy-after; budget raised for credits |

## Next (aggressive full-scale / useful spend)

Only after Uday finals closed. Prefer **deeper AWS** where soft residuals were “beyond-CA2 lite” and credits allow — still destroy-after each round.

| Thesis | Mode | Useful full-scale next (artefact) | Notes |
|--------|------|-----------------------------------|-------|
| Uday | AWS | After ×3 lite: optional **deeper disconnect schedule** or more msgs/cell if Free-Tier headroom | Keep baseline=QoS0, proposed=QoS1 |
| Chaitanya | AWS | Confirmatory Init **n≥30** package_size + runtime_compare (was soft) | baseline=default package; proposed=optimised |
| Rasool | AWS | Optional W1/W2 cells or n>1 on W3/W4 | baseline=on-demand; proposed=provisioned (or K1 vs K3 as designed) |
| Anji | AWS | Optional live n>1 on same 4 cells | baseline=MRC5/VT90 as control; proposed=MRC1/VT30 as designed |
| Nemi | AWS | Deeper FL rounds / more rows if budget | baseline=centralised; proposed=FL |
| Pooja | AWS | Multi-step or longer live scale loop | baseline=HPA; proposed=PAKS |
| Venkat | AWS | Multi-order matmul sweep (n beyond 250) | baseline=1×t3.small; proposed=2×t3.micro |
| Yashaswini | AWS | Already Leg3 ×3; deepen only if artefact change | baseline=tracing off/pass; proposed=policy/full |
| Vikas | AWS | Campaign already full-scale; re-run **only if artefact changes** | baseline=P1; proposed=P2/P3 |
| Mehak | **Local** | Full GCT epochs/seeds if artefact changes | baseline=RF/Aldomi; proposed=MHSA |
| Vishvaksen | **Local** | Rescan N=240 if scanners/labels change | baseline=label-oracle; proposed=Checkov/tfsec/OPA |
| Varun | Local/AWS as designed | Re-run e1–e3 only if artefact changes | baseline=Lifecycle; proposed=RIC |

## Done (artefact packs)

Anji, Chaitanya, Yashaswini, Rasool, Varun, Vikas, Nemi, Venkat, Mehak, Pooja, Vishvaksen finals/campaign packs on disk.  
Rubric evidence matrices + gap hunt written (pointers only).

## Explicitly deferred

- Report / LaTeX / Discussion prose  
- GENAI_HANDOFF (until operator asks)  
- Kasi (excluded)

## If you change artefact code

```text
1. pytest / make test (or thesis equivalent)
2. smoke (dry or tiny live)
3. FULL-SCALE eval again (AWS destroy-after OR local full pack)
4. Update results/final_* + FINAL3_BASELINE numbers from disk
5. Do not claim old packs after a breaking artefact change
```

**Updated:** 2026-09-22T05:40Z
