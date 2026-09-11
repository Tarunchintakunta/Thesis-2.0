# Outputs summary

Kondragunta Lakshmi Chaitanya - 25171216

Factual list of what the project produces and who could use it. Status column
is honest about what exists today.

| Output | Type | Where | Status | Who could use it |
|---|---|---|---|---|
| Multi-runtime Lambda estate (Python 3.12 / Node.js 20 / Java 21, default and optimised packages, warming pair) | IaC + code | `infra/template.yaml`, `functions/` | built; packages build and give the same digest in CI | practitioners who want to repeat the measurement in their own account |
| Deterministic packaging + package manifest | script | `scripts/package_all.sh`, `src/coldstart/packaging.py` | done | anyone comparing package sizes |
| Invokers with interleaved randomised blocks, budget guard | scripts | `scripts/invoke_*.py`, `scripts/budget_guard.py` | done, tested against the mock | researchers running cold-start experiments |
| REPORT-line parser and request-id join | library | `src/coldstart/report_parser.py`, `src/coldstart/metrics.py` | done, unit-tested | anyone mining Lambda logs for Init Duration |
| Cost model per 1,000 invocations | library | `src/coldstart/cost_model.py`, `configs/pricing.yaml` | done; prices must be re-checked before live runs | FinOps / practitioners |
| Pre-registered analysis + decision matrix | scripts + plan | `docs/ANALYSIS_PLAN.md`, `scripts/analyse.py` | done; runs on mock data | practitioners choosing cold-start controls |
| Processed dataset (live) | CSV | `data/processed/live/` | **not collected yet** (needs the student's AWS campaign) | researchers |
| Processed dataset (mock) | CSV | `data/processed/mock/` | synthetic, pipeline test only | - |
| Local init-proxy dataset | CSV | `data/proxy/github/` | measured on a GitHub Actions runner (proxy, not Lambda) | developers comparing runtime/package load cost |
| Figures | PNG | `figures/mock/`, `figures/proxy/`, later `figures/live/` | mock + proxy exist | report, viva |
| Configuration manual | document | `reports/configuration_manual.md` | done | examiners, anyone re-running |

Potential follow-ups: the same harness can take provisioned concurrency,
SnapStart or container-image packaging as extra arms, other regions, or other
providers' functions (with a new backend).
