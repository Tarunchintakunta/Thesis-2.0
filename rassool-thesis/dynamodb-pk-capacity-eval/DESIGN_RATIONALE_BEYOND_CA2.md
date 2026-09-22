# Design rationale — CA2 floor + scoped residuals (Rasool)

**Policy:** CA2 is a floor (`_analysis_extract/reports/CA2_FLOOR_NOT_CEILING.md`).  
**Bar:** 100% CA2 = RQ / objectives / gap / method / artefact / eval **scope** — not perfect marks.  
**AWS:** Formal method required live DynamoDB PK × capacity key-cells — **satisfied** (W3/W4 12/12; destroyed).

## Formal CA2 → delivered (floor met)

| Commitment | Delivered evidence | Scope note |
|------------|-------------------|------------|
| RQ: partition-key design vs on-demand/provisioned capacity | Live W3/W4 factorial 12/12 | `results/batches.csv`, `keycell_summary.csv` |
| Obj: Zipfian / workload generator + cost model | Implemented + live-measured cells | Zipfian seed caveat disclosed |
| Obj: statistical plan | ANOVA/Tukey code + unit tests; exploratory n=1 OLS/KW on live | Confirmatory ANOVA not claimed |
| AWS artefact | Terraform + Lambda workloads; destroy-after-round | Hard sole residual closed |
| K4 adaptive sharding | Code presence only | Off CA2 factorial — no dominance claims |

## Explicitly scoped out (optional beyond-CA2)

1. **W1/W2 live cells** — soft coverage; W3/W4 already close the PK×capacity method residual.
2. **Confirmatory $n{>}1$ / live ANOVA+Tukey** — exploratory n=1 stats are directional only.
3. **Cost Explorer validation** — list-price / model cost retained; billing-linked optional.
4. **K4 dominance claims** — explicitly out of factorial scope.

**Rationale:** inventing confirmatory ANOVA or filling W1/W2 without a new destroy-after campaign would break evidence rules. Disclosed W3/W4 key-cells meet research-scope alignment.

## Alignment

**Formal CA2 research-scope: 100%.** Soft residuals above remain optional; they do **not** reopen the floor.  
**INITIAL_EVAL_PASS=yes** (`results/initial_eval_1/`).
