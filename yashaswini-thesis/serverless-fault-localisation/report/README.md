# Report checklist (NCI research-paper format, max 20 pages)

The report is the student's own writing; this file only maps the master
prompt's required sections (5B) to what the artefact produces. Result tables
stay marked as placeholders until the live campaign has run; simulated or
functional-check numbers never appear as results.

| section | must contain | artefact source |
|---|---|---|
| Abstract | background, objectives, method, results, findings | results/*/summary.md |
| Introduction (1-2 pp) | problem, importance, RQ, objectives and success tests, contribution, limitations, outline | master prompt 1, docs/ANALYSIS_PLAN.md |
| Literature survey (3-4 pp) | critical review: RCA, thresholds, TraceRCA-style methods, CloudWatch / X-Ray overhead; strengths / weaknesses; niche - rewrite, do not paste the proposal | bib/references.bib only |
| Outputs summary (max 2 pp) | each artefact output, its type and users | README.md layout table |
| Research methodology | IVs / DVs, three-leg protocol, injection, calibration freeze, stats plan, validity threats | docs/ANALYSIS_PLAN.md, docs/FAULT_TAXONOMY.md, docs/ASSUMPTIONS.md |
| Design and implementation | architecture, ranking formula, tools - no long code listings | template.yaml, detector/ranker.py docstring |
| Evaluation | P / R / F1 / delay / top-k / overhead tables and figures, hypothesis tests, Xing ceiling and RCAEval baselines, implications, negative results | results/rcaeval, results/live, figures/ |
| Conclusions and discussion | answer the RQ, confidence and validity, future work | |
| References | Harvard, verified sources only | bib/references.bib |

## Rules to check before submitting (master prompt 7)

- [ ] no same-rig victory claimed over Xing et al. (2025) - ceiling only
- [ ] every overhead comparison carries the asymmetry (learned arm = lower bound)
- [ ] thresholds were never retuned on evaluation data
- [ ] refuted expectations reported honestly
- [ ] every figure / table numbered and referenced
- [ ] the detection-F1 decision in docs/ANALYSIS_PLAN.md ("Open decision") is settled and stated
- [ ] title page ends with name and student ID

Yashaswini Penumarthi (24262404)
