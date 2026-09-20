# Full cohort alignment tracker (13 theses; kasi excluded from work)

**Total theses in repo:** 13  
**Active alignment iteration:** **all 12** (kasi excluded) — including theses **not** on the AWS goal list  
**Same bar for everyone:** Research Alignment to CA2 = **exactly 100%** before COMPLETE  
**Kasi:** excluded from all tasks  
**Branch:** `feature/aws-ca2-alignment` only — do not push to `main`  
**AWS deploy:** only after that thesis hits 100%, and only if its CA2 requires AWS

## Scores (latest)

| # | Thesis | Latest % | CA2 file | Need 100%? |
|---|--------|---------:|----------|------------|
| 1 | Anji | **~90%** | proposal.docx | Yes (sole hard) |
| 2 | Varun | **~88%** | RIC_CA2.txt | Yes |
| 3 | Yashaswini | **~88%** | proposal.docx | Yes |
| 4 | Rasool | **~92%** | proposal.docx | Yes |
| 5 | Chaitanya | 67% | proposal.docx | Yes |
| 6 | Vikas | 68% | proposal.docx | Yes |
| 7 | Venkat | 63% | venkat_ca2.txt | Yes |
| 8 | Nemi | **~64%** | CA2.txt | Yes |
| 9 | Mehak | **~88%** | **NOT FOUND** → `CA2_COMMITMENTS.md` | Yes |
| 10 | Pooja | **~85%** | **NOT FOUND** → `CA2_COMMITMENTS.md` | Yes |
| 11 | Uday | **~90%** | **NOT FOUND** → `CA2_COMMITMENTS.md` | Yes |
| 12 | Vishvaksen | **~86%** | **NOT FOUND** → `CA2_COMMITMENTS.md` | Yes |
| 13 | Kasi | — | — | **EXCLUDED** |

**None at 100% yet.**


## Iteration log (alignment fixes, AWS still blocked)

- 2026-09-20: Anji `evaluation.tex` H1–H3 rewritten to match `stats_H1_H2_H3.json`
- 2026-09-20c: Anji abstract/conclusion/results README + DIVE VIVA/DEMO + CA2 Al-Said/Bosilia bib + Obj4 cost estimator-only; STATUS ~72% <100% (live SQS residual)
- 2026-09-20: Yashaswini RCAEval Top-k table corrected from raw JSON (rules AC@3=0.611)
- 2026-09-20: Venkat speedup/time narrative corrected from `summary_statistics.json`
- 2026-09-20: Varun STATUS completion demoted; minimal `refs.bib` with `note={doi:}`
- Genuine AWS goal list unchanged (8 CA2-verified); Mehak/Pooja/Uday/Vishvaksen not on AWS list
- **None at 100% yet**

- 2026-09-20b: Rasool intro/eval — no production/Cost-Explorer overclaim
- 2026-09-20b: Nemi README — PoC metrics; Docker/Helm/Opacus demoted
- 2026-09-20b: Chaitanya abstract — ADOPT band proxy-only
- 2026-09-20b: Vikas eval — acknowledge live pilot path + empty campaign
- 2026-09-20b: Added `CA2_COMMITMENTS.md` for Mehak/Pooja/Uday/Vishvaksen (binding until real CA2 exists)
- 2026-09-20c: Mehak/Pooja/Uday/Vishvaksen claim hygiene — STATUS &lt;100%, eval↔CSV, bib `note={doi:}`, residual notes; still NOT COMPLETE; no AWS
- 2026-09-20d: Anji/Varun/Yashaswini/Rasool/Nemi claim hygiene raise — eval↔JSON, STATUS demote, DOI notes, residual notes; still NOT COMPLETE; no AWS
- 2026-09-20e: Anji packaging-dedup + phase run-count reconcile → ~90%; READY_FOR_AWS=yes (sole=live SQS); no AWS
- 2026-09-20e: Varun temporal-holdout forecast fix; Yashaswini CausalRCA quarantine; both READY_FOR_AWS=yes; still NOT COMPLETE; no AWS apply
- 2026-09-20f: Rasool live DynamoDB key-cell round **12/12** (K1–K3 × capacity × W3/W4); STATUS/eval/cell_summary folded; stack destroyed; `SOLE_AWS_RESIDUAL=no`; alignment ~92%; soft W1/W2 + ANOVA remain
