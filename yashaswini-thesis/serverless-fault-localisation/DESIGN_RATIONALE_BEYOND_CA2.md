# Design rationale — CA2 floor + scoped residuals (Yashaswini)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Bar:** 100% CA2 = RQ / objectives / gap / method / artefact / eval **scope** — not perfect marks.  
**AWS:** Formal method required live Leg 3 overhead on serverless microservices — **satisfied** (lite protocol; destroyed).

## Formal CA2 → delivered (floor met)

| Commitment | Delivered evidence | Scope note |
|------------|-------------------|------------|
| RQ: lightweight fault detection/localisation | Leg 2 RCAEval raw + recomputed tables | CausalRCA quarantined $n{=}4$ |
| Obj: multi-method localisation | Rules/BARO/CIRCA/TraceRCA/hybrid $n{=}90$ | Evidence-locked AC@3/F1 |
| Obj: live overhead / cost of tracing | Lite Leg 3 `overhead.json` (full/policy/off) | 5 min × 3 @ 1 rps |
| Obj: learned lower bound | $n{=}8$ RE2-OB parquet subset | Compressed LB, not full catalogue |
| AWS artefact | Terraform `faultlab` apply→measure→destroy | eu-west-1 |

## Explicitly scoped out (optional beyond-CA2)

1. **CausalRCA full 90-case peer** — quarantined fixed-order $n{=}4$; not required once other methods lock Leg 2.
2. **30-minute Leg 3 cells** — soft confirmatory depth beyond lite window.
3. **Full 90-case parquet catalogue for learned-LB** — subset $n{=}8$ already fills the LB cell.
4. **Clean PDF rebuild** — packaging soft (pdflatex errors / length); claims hygiene already rewritten in MD.

**Rationale:** inventing CausalRCA peer status or confirmatory 30-min cells would break evidence rules. Disclosed lite + quarantined CausalRCA meets research-scope alignment.

## Alignment

**Formal CA2 research-scope: 100%.** Soft residuals above remain optional; they do **not** reopen the floor.  
**INITIAL_EVAL_PASS=yes** (`results/live/initial_eval_1/`).
