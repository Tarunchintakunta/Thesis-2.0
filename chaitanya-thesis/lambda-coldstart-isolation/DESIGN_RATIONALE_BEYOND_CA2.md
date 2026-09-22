# Design rationale — CA2 floor + scoped residuals (Chaitanya)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Bar:** 100% CA2 = RQ / objectives / gap / method / artefact / eval **scope** — not perfect marks.  
**AWS:** Formal method required live Lambda Init Duration — **satisfied** at lite depth (H1/H2/H3/H4).

## Formal CA2 → delivered (floor met)

| Commitment | Delivered evidence | Scope note |
|------------|-------------------|------------|
| RQ: cold-start isolation / package / memory / warming controls | Live REPORT Init Duration + H3/H4 lite | Lite $n$ disclosed; directional ROI/ADOPT |
| Obj: multi-runtime package cells | Python / Node / Java default vs optimised Init | Bytecode dropped (Unhandled) |
| Obj: memory sweep | H4 python optimised 128–3008 MB | Lite point estimates |
| Obj: warming | H3-lite EventBridge on vs off | Sparse 30m; not 4 h confirmatory |
| Metrics: Init ms, cost, ADOPT bands | `data/processed/live/` | Holm family underpowered on lite $n$ |

## Explicitly scoped out (optional beyond-CA2)

1. **Confirmatory $n{\ge}30$ per cell** — power-plan depth; lite already closes method + Init residual.
2. **Full-length H3 (4 h / gap 360)** — soft validity upgrade beyond H3-lite.
3. **python-bytecode arm** — formally dropped after live Unhandled (ASSUMPTIONS).
4. **Holm-confirmatory ADOPT** — lite Holm ran underpowered; point-estimate ADOPT-lite retained as directional.

**Rationale:** inventing confirmatory power or keeping a broken bytecode cell would break evidence rules. Disclosed lite depth meets research-scope alignment.

## Alignment

**Formal CA2 research-scope: 100%.** Soft residuals above remain optional; they do **not** reopen the floor.  
**INITIAL_EVAL_PASS=yes** (`data/processed/live/initial_eval_1/`).
