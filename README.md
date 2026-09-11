# Thesis 2.0

MSc Cloud Computing (NCI) research project artefacts. One folder per project,
each folder has the original proposal (`.docx`), the master prompt with the
rules for that project, and the actual artefact code in its own sub folder.

| Folder | Project | Artefact folder | Status |
|--------|---------|-----------------|--------|
| `anji-thesis/` | Reliability and recovery of Amazon SQS under injected failures | `sqs-reliability-recovery/` | artefact done (simulated results), live AWS runs + report pending |
| `kasi-thesis/` | Source-free log anomaly detection for AWS serverless apps | `serverless-log-anomaly/` | artefact done (emulated logs), live run + report pending |
| `chaitanya-thesis/` | Isolating cold-start latency reduction in AWS Lambda (runtime, package size, warming) | `lambda-coldstart-isolation/` | artefact done (mock pipeline + local init-proxy benchmark), live AWS runs + report pending |
| `rassool-thesis/` | Partition-key design x capacity mode in Amazon DynamoDB under Lambda workloads | `dynamodb-pk-capacity-eval/` | artefact done (Terraform + workloads + analysis, tested on moto), live AWS campaign + report pending |
| `vikas-thesis/` | see master prompt | - | todo |
| `yashaswini-thesis/` | see master prompt | - | todo |

Other stuff at the top level:

- `master_rubric.md` - notes from the module slides (marking scheme, report structure, ethics)
- `_extracted/` - plain text versions of the proposals so they are easy to grep

## How the folders are laid out

Every artefact folder follows roughly the same shape so it is easy to jump between them:

```text
<artefact>/
├── README.md          # what it is + one command quick start
├── src/               # the actual code
├── configs/           # experiment configs (yaml)
├── scripts/           # helper shell/python scripts
├── analysis/          # stats + plots
├── results/           # manifests, summaries, figures (raw dumps are gitignored)
├── docs/              # configuration manual etc.
├── weekly/            # weekly report template
└── tests/             # unit + integration tests
```

Each project runs in a local **dry-run / simulation mode** by default so nothing
costs money. Live cloud mode is there but needs your own account and has to be
switched on explicitly.

## CI

GitHub Actions runs the tests for every project on each push
(`.github/workflows/ci.yml`).
