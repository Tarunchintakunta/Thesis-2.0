# Verdet comparison — McNemar and Holm–Bonferroni

**Evidence only.** Numbers below are taken from this pass’s measured
outputs (`results/mcnemar_pairs.csv`, `results/holm_bonferroni.csv`,
`results/metrics_per_category.csv`). No invented p-values.

## Gap relative to Verdet et al. (2025)

Verdet et al. study Terraform security-policy *adoption* and report
accuracy mainly on disputed Checkov/tfsec cases. This artefact instead
scores **labelled** secure/insecure AWS modules (N=240; 144 insecure)
with per-category precision / recall / F1 / FN for:

- scripted checklist (not a human rater),
- Checkov 3.3.19,
- tfsec v1.28.14,
- static union (Checkov ∨ tfsec),
- OPA 1.4.2 category gate.

RQ “% identified” (recall on labelled insecure): checklist 81.2%,
Checkov 56.2%, tfsec 61.8%, union 70.8%, OPA 60.4%.

## McNemar (exact two-sided) on insecure modules (n=144)

Discordant detections between pre-registered stage pairs
(`results/mcnemar_pairs.csv`):

| Pair (A vs B) | b (A+ B−) | c (A− B+) | p (two-sided) |
|---------------|----------:|----------:|--------------:|
| Checkov vs tfsec | 13 | 21 | 0.229 |
| Static union vs OPA | 35 | 20 | 0.058 |
| Checklist vs static union | 34 | 19 | 0.053 |
| Checklist vs OPA | 30 | 0 | 1.86×10⁻⁹ |

Interpretation (evidence-bound): Checkov and tfsec do **not** differ
significantly on this labelled set (p=0.229). Checklist vs OPA is
highly discordant (30 modules caught by checklist only; 0 the reverse).

## Holm–Bonferroni (α = 0.05, m = 4)

Applied to the four pre-registered McNemar tests
(`results/holm_bonferroni.csv`):

| Rank | Pair | Raw p | Holm threshold α/(m−j+1) | Adjusted p | Reject @ 0.05? |
|-----:|------|------:|-------------------------:|-----------:|:--------------:|
| 1 | Checklist vs OPA | 1.86×10⁻⁹ | 0.0125 | 7.45×10⁻⁹ | **Yes** |
| 2 | Checklist vs static union | 0.053 | 0.0167 | 0.160 | No |
| 3 | Static union vs OPA | 0.058 | 0.025 | 0.160 | No |
| 4 | Checkov vs tfsec | 0.229 | 0.050 | 0.229 | No |

After correction, **only** checklist vs OPA remains significant. The
nominal near-0.05 contrasts (checklist vs union; union vs OPA) do **not**
survive Holm–Bonferroni on this corpus.

## Claims discipline

- These tests compare **detection disagreement on labelled insecure
  modules**, not Verdet’s adoption metrics.
  human agreement.

Checklist stage is the **label-oracle** deterministic pass scored against `labels.csv`.
