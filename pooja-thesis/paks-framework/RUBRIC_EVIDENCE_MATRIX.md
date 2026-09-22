# Rubric evidence matrix — Pooja (PAKS k8s)

**Driver:** `/RUBRIC_70_TO_100_STRATEGY.md`  
**Artefact:** `pooja-thesis/paks-framework/`  
**CA2:** 100% | **INITIAL_EVAL_PASS:** yes | **Final-3:** done (`results/live/final_{1,2,3}/`)  

| Rubric requirement | Where evidence exists | Concrete evidence | Gap to 80+/90+ |
|--------------------|----------------------|-------------------|----------------|
| Objectives fully achieved | STATUS; live JSON | Live HPA vs PAKS scale latency | Obj→latency map in Conclusion |
| Critical literature review | CA2 / report | Predictive vs reactive autoscaling | Critique matrix |
| Alternatives considered | DESIGN_RATIONALE | HPA vs PAKS; TF vs NumPy LSTM | Decision table |
| Methodology justified | run_live_aws_k8s.py | Free-Tier 1×t3.micro+k3s; destroy-after | Why steps=16 |
| Rigorous implementation | terraform; final_1–3 | destroy_confirmed ×3 | — |
| Rigorous evaluation | FINAL3_BASELINE | p50≈0.14s both; mean order not monotone | Stability stats across seeds |
| Synthesis of data | TRACE MAE + live latency | LSTM < persistence MAE (**neg**) | Connect prediction miss → scale behaviour |
| Relevant theory | STATUS | Reactive HPA baseline | Lit compare paragraph |
| Insightful conclusions | FINAL3 verdict | No confirmatory PAKS win at lite n | Why single-node masks policy gap |
| Academic implications | DESIGN_RATIONALE | Method closed under Free-Tier | Contribution bullet |
| Practitioner implications | STATUS | Do not over-claim PAKS superiority | Manual takeaway |
| Validity | destroy verify; tags | project=paks-k8s-live only | Single node |
| Generalisability | DESIGN_RATIONALE | Multi-node beyond-CA2 | Soft |
| Limitations | STATUS; FINAL3 | n=16; cost SIMULATED | Keep |
| Reproducibility | scripts/run_final_k3s.sh | apply→SSM→scale→destroy | — |
| Viva evidence | STATUS Rubric | Defend LSTM<persistence | — |

**Scoreboard:** raised→yes path · **Updated:** 2026-09-22
