# Rubric quality bar (bound into goal)

**Sources (authoritative — use throughout this goal):**
1. `/Users/valletivarish/Downloads/WhatsApp Image 2026-09-17 at 7.23.54 PM.jpeg` — **MSc Cloud Computing – Research Project – Marking Rubric**
2. `/Users/valletivarish/Downloads/master_rubric.md` — module overview / handbook guidance (if present)
3. **`/RUBRIC_70_TO_100_STRATEGY.md` (repo root)** — operating strategy: protect 70+ descriptors; push Artefact+Eval beyond; evidence matrix + audit

**Standing exclusion:** `kasi-thesis` — never, unless user re-includes.

## What 100% CA2 means (separate from marks)

Complete alignment with approved **RQ, objectives, literature gap, methodology, artefact purpose, evaluation scope**.  
**Not** a perfect score in every rubric cell.

## What “70%+ quality check” means (from the JPEG rubric)

| Component | Weight | 70%+ characteristics to target |
|-----------|-------:|--------------------------------|
| Project Specification | 5% | Objectives clearly specified, **creative and appropriate**; fully **achieved or surpassed** |
| Literature Review | 8% | **Critical** application/critique of theory; **breadth and depth** |
| Artefact / Product Development | 27% | Alternatives **fully considered**; chosen method **fully justified**; application **rigorously** carried out |
| Evaluation & Analysis | 25% | **Rigorous and creative** analysis; **synthesize** data with relevant theory; **insightful** conclusions that **appreciate limitations and implications** |
| Report Presentation / Structure / Referencing | 8% | Excellent presentation/structure; rigorous referencing; correct grammar/spelling |
| Configuration Manual | 5% | Excellent description/structure to **reproduce environments** |
| Viva | 10% | Excellent, well-directed; impeccable Q&A (student-facing; not automated here) |

Lower bands (for gap diagnosis only): 60–69 = good/rigorous but less creative/insightful; 50–59 = adequate; below = weak/inadequate.

## Handbook / master_rubric.md checks (NCI guidance)

- Results critically analysed **against original RQ**; compare with **previous research** in the lit review.
- Use **statistical tools** for significance where applicable.
- **Include negative results** (do not hide non-improvement vs baseline).
- Discussion: confidence/validity/scope/generalisability; implications; future work.
- Config manual separate from 20-page report; must support reproduction.

## How this gates AWS work

1. Fix CA2 scope alignment to **100%** first (RQ/objectives/gap/method/artefact/eval — **not** perfect marks).  
2. Rubric quality (JPEG + handbook): aim **70–100** traits — not scrape-70. Include **negative results**; analyse vs RQ/baseline/previous research; appreciate limitations. Artefact (27%) + Eval (25%) dominate marks.  
3. **Evaluation cycle (binding):**  
   **100% CA2 → 1 evaluation → CA2 re-check → if needed fix → 1 evaluation → re-check → once still 100% → 3 full-scale final evaluations.**  
4. Baseline compare on the final 3 (pos+neg, stats, consistency). Then RQ/objectives/limitations/conclusions.  
5. `GENAI_HANDOFF.md` **only after** that thesis’s requirements + 3 finals are done (full e2e template).  

**Sources kept open for every edit/eval:**  
- `/Users/valletivarish/Downloads/WhatsApp Image 2026-09-17 at 7.23.54 PM.jpeg`  
- `/Users/valletivarish/Downloads/master_rubric.md`

## Per-thesis Rubric notes (evidence fold; aim **70–100**, not scrape-70)

Mark weights from JPEG: Spec 5% · Lit 8% · **Artefact 27%** · **Eval 25%** · Report 8% · Config 5% · Viva 10%.  
Raise path = fold final-3 **pos+neg** into STATUS/eval/conclusions vs RQ + baseline paper + limitations.

| Thesis | Rubric70 | Evidence used (no invented metrics) | Next |
|--------|----------|-------------------------------------|------|
| Anji | **yes** | final-3 + initial_eval_1; loss=0; MRC=1 DLQ pos; **neg:** VT→recovery non-monotone; vs Kyrychenko | soft; handoff deferred |
| Varun | **yes** | e1–e3 + BASELINE_COMPARE in STATUS/LaTeX; high_churn little/no vs Lifecycle | soft; handoff deferred |
| Yashaswini | **yes** | Leg3 lite final-3; CausalRCA quarantined; overhead pos+neg | soft PDF; handoff deferred |
| Chaitanya | **raised** | final-3 H1 stable; Init/H3/H4 lite; **neg:** lite n; H3 underpowered; vs Bluemke Init isolation | report prose polish |
| Mehak | **raised** | GCT final-3; RF/Aldomi lead; **neg:** MHSA does not win; FN≫TP | report prose polish |
| Venkat | **raised** | matched Free-Tier final-3; matmul ok; **neg:** n=250 single-shot; n=500 timed_out historically | report prose polish |
| Pooja | **raised** | k3s final-3; **neg:** HPA/PAKS not monotone; LSTM < persistence MAE | report prose polish |
| Nemi | **raised** | cloud FL lite final-3; **neg:** not 50-round/2.5M; vs Saklani depth | report prose polish |
| Rasool | **raised** | W3/W4 final-3 ×3; **neg:** n=1 exploratory only; W1/W2 soft | report prose polish |
| Vishvaksen | **raised** | labelled-oracle final-3; **neg:** scanner recall gaps; no apply | soft Verdet optional |
| Vikas | **raised** | full campaign N=1000×3×3; E1–E3 supported; **neg:** P1 dups; moto≠AWS | soft LaTeX optional |
| Uday | **partial** | lite 16-cell; final-3 in flight; **neg:** d60≡d300; QoS1 latency cost | finish final-3 + fold |
