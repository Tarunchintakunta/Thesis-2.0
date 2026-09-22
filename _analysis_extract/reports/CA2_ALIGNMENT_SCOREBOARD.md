# CA2 alignment scoreboard (12 thesis projects — Kasi excluded)

**Updated:** 2026-09-22 (six-thesis deep audit closed — prior 100% labels **not trusted**)  
**Bar:** **100% CA2** = complete match to approved RQ/objectives/gap/method/artefact/eval scope — **not** perfect marks.  
**Authority for honesty:** [`INDEPENDENT_CRITICAL_AUDIT.md`](INDEPENDENT_CRITICAL_AUDIT.md) + per-thesis `INDEPENDENT_REVIEW_*.md`.  
**Rubric strategy:** [`/RUBRIC_70_TO_100_STRATEGY.md`](../../RUBRIC_70_TO_100_STRATEGY.md) — but **do not raise Rubric70 on a false CA2 floor**.

| # | Thesis | CA2_% (honest) | Rubric70 | Block full-eval? | Independent verdict / next |
|--:|--------|---------------:|----------|:----------------:|----------------------------|
| 1 | Anji | **~72 partial** | unverified | soft | Live 4-cell smoke Demonstrated; H1–H3 localsim all null; live n>1 Not met — `INDEPENDENT_REVIEW_ANJI.md` |
| 2 | Chaitanya | **~70 partial** | unverified | soft | Lite H1/H2 Demonstrated; confirmatory n≥30 / H3 / hygiene Not met — `INDEPENDENT_REVIEW_CHAITANYA.md` |
| 3 | Yashaswini | **~68 partial** | unverified | soft | Leg2 Demonstrated; Leg3 ≥50% cut **fails** on final_1–3 (0.383–0.472) — `INDEPENDENT_REVIEW_YASHASWINI.md` |
| 4 | Rasool | **~74 partial** | unverified | soft | W3/W4 live Demonstrated; W1/W2 reframe; pool finals first — `INDEPENDENT_REVIEW_RASOOL.md` |
| 5 | Varun | **~70 partial** | unverified | soft | Live Wilcoxon structure Demonstrated; e1≡e2≡e3 rebuilt clone — `INDEPENDENT_REVIEW_VARUN.md` |
| 6 | Vikas | **~85 partial** | unverified | soft | Live E1–E3 **Demonstrated**; LaTeX/P4 integrity **Not met** — see `INDEPENDENT_REVIEW_VIKAS.md` |
| 7 | Nemi | **~55 partial** | unverified | soft | UNSW+central Demonstrated; improved loses; Docker/K8s Not met; live ~6s toy — `INDEPENDENT_REVIEW_NEMI.md` |
| 8 | Venkat | **~70 partial** | unverified | soft | Matched-vCPU n=250 **Demonstrated**; RQ memory/CPU/size **Not met** — `INDEPENDENT_REVIEW_VENKAT.md` |
| 9 | Mehak | **~88 met** | unverified | no | GCT negative MHSA result Demonstrated; keep FN honesty — `INDEPENDENT_REVIEW_MEHAK.md` |
| 10 | Pooja | **~45 not met** | **no** | **yes** | Causal HPA artefact fix **in tree** (metrics-server + burn + controller observe); prior finals INVALIDATED; AWS re-eval after Uday — `INDEPENDENT_REVIEW_POOJA.md` |
| 11 | Uday | **~65 partial** | partial | no | Lite QoS1 loss=0 Demonstrated; formal N/Holm/d60≠d300 **Not met**. final_3 in flight — `INDEPENDENT_REVIEW_UDAY.md` |
| 12 | Vishvaksen | **~90 met** | unverified | no | N=240 labelled-oracle Demonstrated; Checkov recall 0.562 — `INDEPENDENT_REVIEW_VISHVAKSEN.md` |

## Overturned prior claims (do not restore without new evidence)

- “All 12 at CA2 100%” — **false** (only Mehak ~88 and Vishvaksen ~90 clear a met floor among the six re-audited here; none are perfect-marks 100).
- Anji / Yashaswini / Nemi / Varun STATUS `ALIGNMENT=100` — **overturned** (smoke ≠ confirmatory; Yash ≥50% overhead rule fails finals; Nemi cloud-native gap; Varun e1≡e2≡e3).
- Yashaswini STATUS locking reduction **0.803** — **stale**; finals are 0.383 / 0.422 / 0.472.
- Pooja / Uday `DESIGN_RATIONALE_BEYOND_CA2.md` “COMPLETE / 100%” — treated as **scope reframe**, not examiner-grade floor closure.
- Vikas scoreboard jump ~74→100 on campaign fill — measurement ≠ full research-package readiness.

## Fix order (research-valid)

1. **Uday** — finish final_3 + baseline; then decide genuine deepen (schedule/N) vs honest partial.
2. **Pooja** — AWS re-eval under new causal HPA artefact (code already changed; destroy-after).
3. **Yashaswini** — policy retune until ≥3 live rounds clear 0.50 reduction, or rewrite decision rule.
4. **Varun** — fresh independent trial sampling (new raw_costs hashes).
5. **Nemi** — multi-instance/container clients + improved-arm diagnosis.
6. **Anji** — live n≥3 key cells; stop citing null H1–H3 as effects.
7. **Venkat / Vikas** — as prior reviews.
8. Rubric70 raises only after honest floors.

**Kasi:** never. **GENAI_HANDOFF:** still deferred until per-thesis finals + honest floor.
