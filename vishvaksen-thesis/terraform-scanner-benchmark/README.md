# Terraform scanner / policy-as-code benchmark

Formal CA2 artefact for the labelled AWS Terraform misconfiguration study
(Checkov + tfsec + OPA/Rego). Binding contract:
`../CA2_COMMITMENTS.md`.

**Do not terraform apply.** Modules are evaluation-only (ethics in the formal
proposal). War comment-ablation code lives under `../_superseded_proxy/` and
is not evidence for this CA2.

## Research question

What percentage of the labelled AWS misconfigurations will be identified by
Terraform security scanners and an enforced policy-as-code gate?

## Scale

Formal N = **240** modules (60 per category × 4; 60% defective). See
`docs/SCALE.md`. Labels are generated with the modules in `corpus/labels.csv`.

## Categories (Buhler / Verdet prevalence)

1. `public_storage` — public ACL/policy, `publicly_accessible`, public AMI/IP
2. `overpermissive_access` — world CIDRs, IAM `*`, AdministratorAccess
3. `encryption_at_rest` — missing/disabled SSE
4. `weak_logging` — missing CloudTrail / flow logs / access logs

## Stages

| Stage | What this tree runs | Honesty |
|-------|---------------------|---------|
| Manual checklist | Scripted application of `docs/MANUAL_CHECKLIST.md`; human protocol + blank sheet ready | Metrics = **scripted**; human pass **not run** |
| Static scanning | Checkov and tfsec at **shipped defaults**, plus union | Tool versions pinned in `results/tool_versions.json` |
| OPA/Rego gate | Category-scoped packages under `policies/rego/` | Policies follow category definitions, not per-module IDs |

## Reproduce

```bash
python3 scripts/generate_corpus.py
python3 -m pytest tests/ -q
python3 scripts/run_all.py
```

`run_all.py` generates the corpus, runs checklist + Checkov + tfsec + OPA,
then writes `results/metrics_per_category.csv`. Individual Checkov/tfsec
accuracy uses a **batch** scan of `corpus/`; per-module seconds are a
stratified sample (Checkov/tfsec startup is otherwise dominated by process
launch).

Required tools (already used on this host when present): `checkov`, `tfsec`,
`opa`, Python 3 with `python-hcl2`. Terraform is **not** required for scoring
and must not be applied.

## Layout

```
corpus/                 labelled modules + labels.csv
policies/rego/          category OPA policies
mappings/               a priori Checkov/tfsec check-id maps
scripts/                generate + runners + evaluate
results/                metrics tables (after run_all)
docs/                   method, ethics, second-review protocol
```

## Status

**NOT COMPLETE (~82%)** — see `STATUS.md`. Independent human checklist and
independent second-human subsample remain open. Verdet McNemar/Holm prose is
in `docs/VERDET_COMPARISON.md`. Do not treat this tree as SUBMIT-READY.
