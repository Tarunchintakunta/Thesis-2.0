# Analysis plan (written before any measurement)

Rasool Basha Durbesula - 24205478

Written 11 September 2026. The code that carries it out is `analysis/stats.py`
and `analysis/analyse.py`; the numbers it uses are in `config/experiment.yaml`
(`analysis:` block). Changes after the pilot go under "Amendments" with a date.

## Unit of analysis

One **measured batch** (all its Lambdas merged) is one observation. 30 batches
per configuration x workload (6 x 4 cells, 720 batches), one per randomised block.

Excluded from the primary analysis (but counted and published): batches with a
cold Lambda start (`cold_contaminated`), cells stopped by the abort rule. Rows
with `data_source` other than `live` are never analysed as results.

## Dependent variables

Primary: mean latency (H_key), throttle rate = throttled / attempted (H_cap),
cost per 10,000 successful operations (H_joint, with mean latency).
Secondary (reported for every cell, not tested in the family): p50/p95/p99
latency, throughput, consumed RCU and WCU per 10k operations, the
consumed-equivalent provisioned cost.

## Hypotheses (two-sided) and tests - per workload W1..W4

| ID | H0 | Test statistic |
|---|---|---|
| H_key_Wx | mean latency is equal across K1-K3 | key-design term of the two-way model on `latency_mean_ms` |
| H_cap_Wx | throttle rate is equal for on-demand and provisioned | capacity-mode term of the two-way model on `throttle_rate` |
| H_joint_Wx | the latency-optimal and the cost-optimal configuration coincide | bootstrap over batches (2,000 resamples): p = share of resamples in which the configuration with the lowest mean latency is also the one with the lowest mean cost per 10k |

The two-way model is `y ~ key_design * capacity_mode` (interaction included - it
is the term of interest, not a nuisance).

* Normality is checked **first**: Shapiro-Wilk on the model residuals (alpha 0.05).
* Normal -> two-way ANOVA (type II sums of squares), partial eta^2 for every term.
* Not normal -> Aligned Rank Transform: for each term the response is aligned
  (residual + that term's estimated effect), ranked, and the same factorial model
  is fitted; only that term's F-test is read. epsilon^2 for every term.
* A significant interaction is followed by Tukey HSD across the three key designs
  inside each capacity mode (simple effects).
* A DV with no variance at all (e.g. no throttles anywhere) is reported as "not
  testable", p = 1.

## Multiple comparisons

Holm-Bonferroni across the 12 primary tests (3 hypotheses x 4 workloads), alpha 0.05.

## Practical significance (fixed now)

* Latency: the gap between the best and worst key design is at least **10%** of
  the reference configuration's mean latency (K1 on-demand, the "default" choice).
* Cost: the gap between configurations is at least **5%** of the reference's cost per 10k ops.
* A significant but smaller effect is reported as "statistically but not practically significant".

## Trade-off surface

Per workload, each configuration is a point (mean latency, throttle rate, cost
per 10k). Points that no other configuration beats on all three at once form
the Pareto front (`pareto.csv`, `tradeoff_surface.png`).

## Sensitivity (not in the family)

Item size 1 / 8 / 32 KB on the best and worst configuration of the main campaign
("best" = on the Pareto front with the lowest cost per 10k averaged over the four
workloads, "worst" = highest), 10 batches each, descriptive only.

## Pilot (1 block at 25% of the rate)

The pilot does not fix n (n = 30 is fixed in advance). It checks:

1. the settling interval: mean latency of the first vs the last third of each
   batch - if more than 10% of batches drift by more than 10%, settling is
   lengthened (amendment);
2. that the variance is in line with the power assumption (f = 0.25, 80%):
   `analysis/pilot_check.py` reports the power of the two-way terms for the
   pilot's spread;
3. that `hot_rank_share` is about 0.90 in every batch (the skew really happens).

## Amendments

### 2026-09-22 — W1/W2 live cells deferred (scope amendment)

**Date:** 2026-09-22  
**Change:** Live factorial measurement for workloads **W1** (read-heavy) and **W2** (write-heavy) is **deferred** and treated as **beyond confirmatory CA2 floor** for this submission cycle.

**Reason:** Confirmatory evidence for the RQ’s key×capacity method residual is already on disk for **W3/W4** (`results/final_{1,2,3}/`, `results/pooled_final3_anova.json`, live key-cell campaign). A further 12-cell W1/W2 destroy-after fleet would re-occupy the sole cohort AWS slot without changing the demonstrated W3/W4 ANOVA finding. Cohort policy: one AWS slot (eu-west-1), destroy-after; remaining slot priority is independence re-runs for other theses.

**What remains claimed:** W3/W4 live cells + pooled confirmatory ANOVA (key main effect supported; capacity/interaction ns on W3 mean latency as reported).  

**What is not claimed:** Full W1–W4 CA2 100%; W1/W2 cell tables filled; Holm over all 12 primary tests with W1/W2 present.

**Re-open condition:** Run W1/W2 only when AWS slot is FREE and no higher-priority independence residual is queued; then amend this plan again with the run date and destroy confirmation.

### 2026-09-22 — confirmatory n>1 already partially filled

Pooled ANOVA across `final_1|2|3` (n_rows=36) supersedes the earlier “n=1 saturates interaction” soft note for W3/W4 latency. Per-pack exploratory n=1 OLS/KW remain non-confirmatory and must not be cited as the family tests.
