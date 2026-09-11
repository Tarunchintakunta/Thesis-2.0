# data/

| folder | what | measured? |
|---|---|---|
| `raw/<mode>/` | one folder per phase: `invocations.jsonl`, `run_info.json`, logs (git-ignored, recreated by the invokers) | - |
| `processed/live/` | the real dataset from the student's AWS campaign | **not collected yet** |
| `processed/mock/` | same pipeline on `DATA_MODE=mock` | **no - SYNTHETIC**, pipeline test only |
| `pilot/<mode>/` | pilot metrics + `pilot_power.md` / `power.json` | mock pilot is synthetic |
| `proxy/github/` | local process-start benchmark on a GitHub Actions runner (all three runtimes) | yes, but it is a proxy, not Lambda |
| `proxy/dev_macbook/` | the same benchmark on the development laptop (Python and Node.js only, no JDK there) | yes, proxy, supplementary |
| `spend_log.csv` | cost of every live call (written by the budget guard) | appears with the first live run |

Column meanings: `docs/DATASET.md`. Mock data comes from placeholder numbers in
`configs/mock_model.yaml` and must never be reported as a result.
