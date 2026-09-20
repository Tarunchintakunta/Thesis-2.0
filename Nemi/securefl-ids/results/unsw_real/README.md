# Real UNSW-NB15 training-partition sample results

**Do not invent metrics beyond `results.json`.**

| File | Role |
|------|------|
| `DATA_PROVENANCE.json` | `kind=real` download provenance (~175341×45) |
| `config.json` | sample_size=25000, 30 rounds/epochs, 5 clients |
| `results.json` | centralised / baseline_fl / improved_fl metrics |
| `history_*.pkl` | per-arm training histories |

This campaign uses a stratified sample of the **official training-set CSV**, not the full 2.5M-flow corpus.
