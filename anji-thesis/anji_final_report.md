> **NOT AUTHORITATIVE FOR CA2 ALIGNMENT (2026-09-20)**  
> Quarantined overclaim draft. Prefer LaTeX (`latex_report/text/*.tex`) + committed `sqs-reliability-recovery/results/summary/stats_H1_H2_H3.json` / `hypotheses.md`.  
> **DIVE / adaptive_vt was not evaluated** (`adaptive_vt: false` in manifests). Do not cite DIVE performance numbers from this file.

---

# Reliability and Recovery of Amazon SQS Messaging under Injected Consumer and Downstream Failures

## Abstract
Amazon SQS is widely used for event-driven decoupling. Prior work (Kyrychenko et al., 2025) optimises SQS for steady-state throughput; this thesis extends that baseline with controlled failure injection in a **local simulator** (`backend: localsim`). Measured DVs are loss, duplicates, DLQ capture, recovery time, throughput, and latency. **Adaptive visibility (DIVE) code exists but was disabled in all committed runs.** No live AWS spend; cost figures elsewhere are estimator projections only.

## 1. Introduction
**RQ:** How does Amazon SQS configuration affect message reliability and recovery under injected consumer and downstream failures?

**Objectives (as pursued in the artefact):**
1. Quantify VT / MRC / batch effects on loss, duplicates, and DLQ under injected faults.
2. Measure recovery time to steady state.
3. Test whether steady-state-optimal configs remain favourable under fault (H3 guidance transfer).
4. Provide statistically corrected guidance; **monetary cost was not an experimental DV**.

## 2. Literature Survey
CA2-related anchors: Kyrychenko et al. (2025) steady-state SQS baseline; Al-Said Ahmad et al. (2024) chaos/fault-injection precedent; Bosilia et al. (2025) async vs sync resilience framing. See `latex_report/refs.bib` and `latex_report/text/relatedwork.tex`.

## 3–4. Method / Design
Two-arm SAM design (sync vs SQS→Lambda) with in-process fault injection; experiments executed via localsim. Optional `adaptive_vt` path in `queue_consumer/handler.py` was **off** for the matrix.

## 5. Evaluation (authoritative numbers)
Source: `results/summary/stats_H1_H2_H3.json` / `hypotheses.md`.

| Test | Decision | Key numbers |
|------|----------|-------------|
| H1 (VT→loss, campaign A) | fail to reject; not estimable | loss = 0.0 all VT; p_adj = 1 |
| H2 (MRC→recovery, campaign B) | fail to reject | H=2.43, p=0.489, p_adj=1.0, ε²=0.128 (n=5/cell after packaging-dedup) |
| H3_loss | fail to reject; not estimable | loss = 0 |
| H3_recovery | **fail to reject** after Holm | U=62.5, p=0.021, p_adj=0.084, r=0.667; opt mean 600 s vs rest mean 224 s (n_opt=5); twin-inflated reject drafts withdrawn |

Exploratory: DLQ capture vs MRC strong under unhandled_error (MRC1≈0.294 vs ≈0 at MRC≥5); recovery tracks VT 1:1 under consumer_kill.

## 6. Conclusions
Static VT is a recovery knob under the tested faults; steady-state-favourable long VT lengthens mean recovery (descriptive; H3_recovery fails to reject after Holm). Do **not** claim DIVE beat static configs—that comparison was not run. Live AWS validation remains required for CA2 cloud evidence.

## 7. References
See `latex_report/refs.bib` (includes Kyrychenko2025, AlSaidAhmad2024Chaos, Bosilia2025AsyncResilience with `note={doi:…}`).

Anjaneya Reddy Gurram
