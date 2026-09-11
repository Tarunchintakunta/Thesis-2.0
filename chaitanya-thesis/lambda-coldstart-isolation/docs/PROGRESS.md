# Progress

Kondragunta Lakshmi Chaitanya - 25171216

Checklist from the master prompt (section 10). "Artefact" means the code is
done and tested; "live" means it still needs the AWS campaign in the student's
own account.

- [x] Scaffold repo
- [x] Three runtimes x two package variants (same digest in all six, checked in CI)
- [x] IaC for arm64 (SAM template, cfn-lint clean) - **not deployed yet (needs the student's account)**
- [ ] Pilot + analysis plan freeze - plan written, pilot tooling tested on mock; **live pilot to do**
- [ ] Phase A baseline-style duration/cost - pipeline and figure tested on mock; **live run to do**
- [ ] Phase B Init Duration isolation tracks - **live run to do**
- [ ] Warming frequency experiment - **live run to do**
- [x] Stats + decision matrix code (runs end to end on mock)
- [ ] Report sections (student)
- [x] Configuration manual + outputs summary
- [ ] Weekly reports (student; blank template in `reports/weekly/`)
- [ ] Viva scripts (student; checklist in `reports/viva/`)
- [x] `references.bib` >= 20 verified (26 entries, 22 from 2022-2026, `scripts/check_bib.py` passes online)
- [ ] Final self-audit - gate status below

## Quality gates

| # | Gate | Status |
|---|---|---|
| 1 | Baseline | Phase A code, table and `baseline_style_duration_cost.png` exist for mock; live Phase A pending. Baseline DOI 10.24425/ijet.2025.153619 is in the plan and bib. |
| 2 | Isolation | pass - `tests/test_report_parser.py` |
| 3 | Runtime | pass locally and in CI for all six packages (`scripts/check_digests.py --require python,nodejs,java`); deploy pending |
| 4 | Variance | interleaved randomised blocks + p50/p95/p99 in every table; pilot-derived n needs the live pilot |
| 5 | Warming | pass - EventBridge `rate(5 minutes)`, no provisioned concurrency (`tests/test_infra.py`) |
| 6 | Stats | pass - pre-registered plan, Holm, effect sizes, warm-discard counts published |
| 7 | Cost | pass - decision matrix has Init saved, delta $ / 1k and band |
| 8 | Citation | pass - online check of all 26 entries |
| 9 | Ethics / budget | mechanism in place (own account printed at deploy, daily cap, spend log); spend log appears with the first live call |
| 10 | Report | student |
| 11 | Honesty | pass - mock is watermarked and refused when mixed with live; proxy always called a proxy |
| 12 | Identity | name and ID on every document in this folder |
