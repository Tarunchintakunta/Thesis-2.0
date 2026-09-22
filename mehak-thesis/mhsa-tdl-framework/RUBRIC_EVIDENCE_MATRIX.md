# Rubric evidence matrix — Mehak (MHSA-TDL / GCT)

**Driver:** `/RUBRIC_70_TO_100_STRATEGY.md`  
**Artefact:** `mehak-thesis/mhsa-tdl-framework/`  
**CA2:** 100% | **INITIAL_EVAL_PASS:** yes | **Final-3:** done (`results/gct/final_{1,2,3}/`)  

| Rubric requirement | Where evidence exists | Concrete evidence | Gap to 80+/90+ |
|--------------------|----------------------|-------------------|----------------|
| Objectives fully achieved | STATUS; FINAL3_BASELINE | Acc/F1/ROC on GCT; RF/Aldomi/MHSA compared | Explicit Obj→metric table in Conclusion |
| Critical literature review | report / CA2 doc | Hybrid monitors vs attention | Critique matrix vs Aldomi |
| Alternatives considered | DESIGN_RATIONALE; STATUS | MHSA vs classical vs Aldomi GRU-RF | Decision table in Method |
| Methodology justified | train_and_evaluate; STATUS | Fail-series-first windows; 5 seeds | Why epochs=15 disclosed |
| Rigorous implementation | results/gct; provenance SHA | Official 2011 subset; net=CPU honesty | — |
| Rigorous evaluation | FINAL3_BASELINE; CM | RF 0.944 > MHSA 0.922; FN≫TP | Effect-size / McNemar if added soft |
| Synthesis of data | results_summary.csv | Fail-F1 vs Acc trade-off | Cross-metric synthesis paragraph |
| Relevant theory | STATUS | MHSA does **not** win — vs expected lift | Lit agree/disagree |
| Insightful conclusions | FINAL3_BASELINE neg | Attention fusion insufficient on this subset | Mechanism: class imbalance / channel limits |
| Academic implications | DESIGN_RATIONALE | Negative result is a contribution | State in Conclusion |
| Practitioner implications | STATUS | Prefer RF/Aldomi for this trace slice | Config/ops note |
| Validity | STATUS | net≠bytes disclosed | External: 2011 subset only |
| Generalisability | DESIGN_RATIONALE | Full dump beyond-CA2 | Soft |
| Limitations | STATUS; FINAL3 | FN high; subset depth | Keep |
| Reproducibility | scripts; seeds 42–46 | `--dataset gct --epochs 15` | README one-liner |
| Viva evidence | STATUS Rubric | Defend negative MHSA result | — |

**Scoreboard:** raised→yes path · **Updated:** 2026-09-22
