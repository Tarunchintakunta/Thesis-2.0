# Analysis plan (pre-registered)

Kondragunta Lakshmi Chaitanya - 25171216

Written 11 September 2026, **before any live data**. The numbers the code uses
are in `configs/analysis_plan.yaml`. The pilot section at the end is filled in
by `scripts/pilot_power.py`; anything else that changes after the live campaign
starts goes into "Amendments" with a date and a reason.

## 1. What is analysed

| Name | Rows used |
|---|---|
| cold sample | `role == measure`, `intended_cold`, **Init Duration present**, no error |
| warm sample | `role in (measure, follow_up)` with no Init Duration, no error (Phase A: `role == measure` only) |
| warmer ping | REPORT lines from `warm-target` with no client record - only for cost |

Dropped from every analysis: function errors / non-200 status, warm-up calls,
warmer pings, and intended-cold calls that came back warm. The last group is
**counted and published** (`discarded_intended_colds.csv`), never analysed as cold.

`DATA_MODE=mock` rows are synthetic. They test the pipeline and are never results.

## 2. Hypotheses and tests

alpha = 0.05. For every comparison the Shapiro-Wilk test (alpha 0.05, per group)
picks the family: all groups normal -> parametric, otherwise rank-based.

| ID | Question | Data | Test (normal / not normal) | Effect size |
|---|---|---|---|---|
| H1 | Does mean Init Duration differ between Python, Node.js and Java? | `runtime_compare`, optimised packages, 1024 MB, cold samples | one-way ANOVA / Kruskal-Wallis | eta^2 / epsilon^2 |
| H2_python, H2_nodejs, H2_java | Does pruning the package change Init Duration? (one test per runtime) | `package_size`, 1024 MB, cold samples | Welch t / Mann-Whitney U | Cohen's d / rank-biserial r |
| H3 | Does a 5-minute EventBridge warmer change the cold-start **frequency**? | `warming`, per 20-minute block: cold fraction of each arm (both arms get the same arrivals, so blocks pair them) | paired t / Wilcoxon signed-rank | d_z / matched-pairs rank-biserial |
| H4_python, H4_nodejs, H4_java (exploratory) | Does memory change Init Duration inside each runtime? | `memory`, optimised, cold samples, 5 memory levels | ANOVA / Kruskal-Wallis | eta^2 / epsilon^2 |

Also reported for H3: Fisher's exact test on the pooled cold/warm counts with
Wilson 95% intervals for each arm's cold fraction.

Post-hoc for H1 (only if H1 is rejected): pairwise Mann-Whitney U between the
three runtimes, Holm inside those three, descriptive.

Combined free controls (descriptive, Holm inside its own three tests): per
runtime, default package at 128 MB vs optimised package at 1024 MB, cold samples.

## 3. Multiple comparisons

Holm-Bonferroni over the **confirmatory family**: H1, H2_python, H2_nodejs,
H2_java, H3 (five p-values). H4 and "combined" are corrected inside their own
family and are labelled exploratory in every table.

## 4. What is reported for every cell

n, mean, SD, p50, p95, p99 of Init Duration (cold) and Duration (cold and
warm), client round-trip p50/p95/p99, cold-start fraction, error rate, cost per
1,000 invocations. Median differences get a bootstrap 95% interval (2,000 resamples).

## 5. Practical significance (fixed now, before data)

* An Init Duration saving smaller than **50 ms** at the median is not worth a code change.
* A warming effect smaller than a **0.10** absolute drop in cold-start fraction is not worth the extra resource.
* A change is "free" if it adds at most **$0.001 per 1,000 invocations**.

## 6. Decision matrix

For every control: typical Init delta (ms, median), cold-frequency delta,
delta cost per 1,000 invocations, and a band:

* **adopt** - significant after Holm, saving >= 50 ms (or cold-fraction drop >= 0.10) and delta cost <= +$0.001 / 1k
* **situational** - significant and big enough, but costs more than that, or helps only some runtimes / patterns
* **avoid** - not significant, or the saving is below the practical threshold

Cost per 1,000 invocations uses a traffic mix: a share `f` of invocations is
cold, where `f` is the cold fraction measured on the warm-control arm of the
warming phase (sparse traffic, no warmer). For a control that changes a cold
invocation's cost by `dc` and a warm one's by `dw`:

    delta cost / 1k = 1000 x (f x dc + (1 - f) x dw)

Warming: delta cost / 1k = cost of the pings per 1,000 real invocations minus the
billed init time it saves; "ms saved" for warming is the expected saving per
invocation, `(f_off - f_on) x median Init Duration (off arm)`.

Rows and contrasts: switch runtime (slowest -> fastest median Init at 1024 MB),
prune package (per runtime), raise memory (128 -> 1024 MB per runtime,
exploratory), low-frequency warming, combined free controls (per runtime),
provisioned concurrency (future work, no numbers).

## 7. Sample size

Plan before the pilot: 50 cold samples per cell for H1/H2, 40 for H4 and
combined, 40 blocks for Phase A. `scripts/pilot_power.py` checks these against
the pilot spread (two-sided alpha 0.05/5 for the confirmatory family, power 0.80,
smallest effect 50 ms, inflated by 1/0.864 for the rank test) and never lowers
a cell below 30.

<!-- pilot-power:start -->
_Not run yet. `python scripts/pilot_power.py --in data/pilot/<mode>/ --out docs/ANALYSIS_PLAN.md` fills this in._
<!-- pilot-power:end -->

## 8. Amendments

### 2026-09-22 — confirmatory H3/H4 deferred beyond confirmatory floor

**Delivered:** confirmatory n≥30 packs for **H1/H2** (`results/live/confirmatory_n30/round_{1,2,3}/`).  
**Deferred:** confirmatory-depth **H3** (warming frequency) and **H4** (memory sweep) at n≥30. H3-lite / H4-lite evidence remains as directional (see `DESIGN_RATIONALE_BEYOND_CA2.md`); do not claim confirmatory H3/H4 Holm families filled.  
**Reason:** sole AWS slot + destroy-after; H1/H2 already close the primary Init Duration RQ limbs under confirmatory n. Re-open H3/H4 confirmatory only when slot free.
