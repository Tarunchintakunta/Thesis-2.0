# Project Status — Artefact and Evaluation

**Student:** Vikas Reddy Amanagantti (X25178849)  
**Project:** An Empirical Evaluation of Application-Level Idempotency Strategies for Retry Correctness on AWS Lambda and Amazon DynamoDB  
**Last updated:** 2026-09-19

---

## Summary

This project implements a **controlled retry experiment** to measure duplicate-mutation rates, latency, and consumed capacity across three application-level write paths (P1 plain put, P2 conditional put, P3 idempotency-key pattern) on AWS Lambda + Amazon DynamoDB.

**Current status:** Artefact complete and functionally tested on **moto** (local DynamoDB mock). Live AWS campaign **NOT yet run**.

---

## What has been completed

### ✓ Artefact implementation

- **Three write paths** (P1, P2, P3) implemented in `src/lambda_fn/paths.py` and `src/lambda_fn/handler.py`
- **Injected timeout mechanism** to force after-commit duplicate scenarios
- **Driver** (`src/driver/`) that schedules known retry counts (1, 2, 5 deliveries), invokes Lambda (or local backend), records ground truth
- **Stream processing** (`src/driver/streams.py`) for duplicate-mutation detection from DynamoDB Streams
- **Analysis pipeline** (`analysis/`) implementing pilot-sizing rule (Wen et al. 2025), statistical tests (z-tests, chi-square, Mann-Whitney U), 95% CIs with Holm–Bonferroni correction, expectation evaluation
- **Infrastructure as Code** (`infra/`) — Terraform configurations for DynamoDB table, Lambda function, IAM roles, CloudWatch log groups, alarms, and budget constraints
- **Configuration** (`config/`) — pinned versions (Python 3.12, boto3 1.35.36, Terraform 1.15.7, AWS provider 6.64.0), experiment design parameters, and price estimates
- **Tests** — 63 pytest tests covering all modules; **all tests pass** ✓

### ✓ Functional validation on moto

The `make functional` target runs the complete experiment pipeline (pilot, campaign N=30, sensitivity) using **moto** — a Python library that mocks DynamoDB locally. This validation confirms:

- **Plumbing correctness:** P1 produces 100% duplicate mutations at multiplicity 2 and 5; P2 and P3 produce 0% (as expected)
- **Stream agreement:** 0 mismatches between stream-observed mutations and function self-reports; 0 missing deliveries out of 720 invocations
- **Analysis outputs:** All tables, figures, and statistical tests execute without errors
- **Pre-registered expectations:** E1 (P1 majority duplicates) and E3 (P3 higher capacity than P2) supported; E2 (>90% reduction) supported at multiplicity 5, inconclusive at multiplicity 2 due to small N=30

**Outputs from moto functional check:**

- Summary markdown: `results/moto/summary.md`
- CSV tables: `results/moto/*.csv` (cells, tests, expectations, pilot sizing, etc.)
- Figures: `figures/moto/*.png` (duplicate rate, latency, capacity, correctness-cost surface)

### ✓ Documentation

- **Configuration Manual:** `docs/CONFIGURATION_MANUAL.md` — step-by-step instructions for environment setup, deployment, running campaigns, and teardown
- **Analysis Plan:** `docs/ANALYSIS_PLAN.md` — statistical methods, hypothesis tests, pilot-sizing rule
- **Ethics:** `docs/ETHICS.md` — declaration of synthetic data, own-account resources, bounded spend, no human participants
- **Assumptions:** `docs/ASSUMPTIONS.md` — threat-to-validity analysis, scope limitations

---

## What has NOT been done: live AWS campaign

### ❌ Live pilot and campaign

The artefact is **ready to deploy** but has **not** been run on live AWS. The reasons:

1. **No AWS credentials** are configured in this repository (by design — credentials must be provided by the researcher at deployment time)
2. **Cost consciousness** — even though the estimated spend is only ~USD 0.17 (see `results/moto/pilot_report.md` and budget estimate), this is the researcher's own account
3. **Research integrity** — the moto results are explicitly labelled as **NOT AWS data**; they serve only to validate the implementation, not to answer the research question

### ✓ Live campaign runbook available

**See `RUNBOOK.md` for complete step-by-step instructions.**

**One-command path (requires AWS credentials):**

```bash
# Set credentials first (fails closed without them)
export AWS_PROFILE=your-profile

# Complete campaign
make deploy              # Terraform apply: table + Lambda + IAM
make pilot && make pilot-size
make campaign WORKERS=16
make sensitivity WORKERS=16
make cloudwatch         # Wait ~10 min after campaign
make analyse
make destroy
```

**Credential safety:** All live targets (`deploy`, `pilot`, `campaign`, `sensitivity`, `cloudwatch`, `destroy`) check for AWS credentials via `make check-aws-creds` and **fail immediately** with a clear error message if credentials are not found. No live target will proceed without valid credentials.

**Safety guards:**

- **Credential check:** Makefile fails closed without `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`
- **Invocation limit:** Maximum 60,000 invocations (hard-coded in `src/driver/run.py`)
- **Budget alarm:** Terraform creates CloudWatch alarm at USD 1.00
- **Seed guard:** Deterministic request IDs allow exact replication
- **Path separation:** `results/live/` and `figures/live/` are distinct from `results/moto/` and `figures/moto/`

**Expected outcomes on live AWS:**

- **Duplicate mutation rates** will match or exceed moto results for P1; P2 and P3 should remain near-zero
- **Latency** will reflect real cold-start overheads (~100–500 ms INIT, then ~1–5 ms per DynamoDB write) — moto reports unrealistic sub-2 ms means
- **Consumed capacity** will match AWS billing units (moto always reports 0.5, which is not accurate) — expect 1.0 WCU for unconditional writes, 1.0 for successful conditionals, 1.0 for failed conditionals (still billed), 2–3 for P3 (read + write(s))

---

## Moto vs live AWS: what is trustworthy

### Summary Table

| Aspect | Moto functional check | Live AWS campaign |
|--------|----------------------|-------------------|
| **Three write paths implemented correctly** | ✓ YES — logic validated | ✓ YES (same code) |
| **Injected retries produce duplicates for P1** | ✓ YES — 100% at N=30 | ✓ EXPECTED — will measure at N~1000 |
| **Conditionals / idempotency keys prevent duplicates** | ✓ YES — 0% for P2, P3 | ✓ EXPECTED — will confirm with CIs |
| **Stream vs self-report agreement** | ✓ YES — 0 mismatches | ✓ EXPECTED (DynamoDB Streams is the same) |
| **Latency measurements** | ❌ NO — moto has no latency model; reports ~1 ms | ✓ YES — only live AWS gives real latency |
| **Consumed capacity measurements** | ❌ NO — moto reports fixed 0.5 units | ✓ YES — only live AWS bills correctly |
| **Cold start vs warm latency** | ❌ NO — moto doesn't simulate Lambda lifecycle | ✓ YES — real INIT times on AWS |
| **Statistical power (N)** | ⚠ PARTIAL — N=30 too small for narrow CIs | ✓ YES — pilot-determined N~1000 |
| **Expectation E2 at multiplicity 2** | ⚠ INCONCLUSIVE (wide CI) | ✓ WILL TEST with larger N |

### Critical Distinction

**Moto results (`results/moto/`, `figures/moto/`):**
- ❌ **NOT an AWS measurement**
- ❌ **NOT suitable for research conclusions**
- ✓ **Proves implementation works** (functional validation only)
- ✓ **Tests pass** (logic is correct)

**Live AWS results (`results/live/`, `figures/live/`):**
- ✓ **Real AWS measurements** (DynamoDB on-demand, Lambda arm64)
- ✓ **Suitable for research conclusions**
- ✓ **Answers the research question** (quantitative duplicate rate, latency, capacity)
- 🚧 **Not yet run** (requires AWS credentials and ~USD 0.17 spend)

### Interpretation

- **Moto results are NOT a measurement.** They prove the code works — paths execute, injections produce the expected duplicate/no-duplicate pattern, tests run, figures generate.
- **Research conclusions require live AWS data.** The research question asks "**by how much** do P2 and P3 reduce duplicates, and what do they cost in latency and capacity?" — those numbers must come from real AWS.
- **Path separation enforced:** Makefile writes moto output to `results/moto/` and `figures/moto/`; live output goes to `results/live/` and `figures/live/`. These paths are never conflated.

---

## How to recognize moto vs live results

### Directory Structure (Enforced Separation)

```
lambda-idempotency-eval/
├── results/
│   ├── moto/          ← Functional validation (NOT AWS data)
│   │   ├── summary.md
│   │   ├── cells.csv
│   │   └── ...
│   └── live/          ← Real AWS measurements (ONLY source for conclusions)
│       ├── .gitkeep   (directory exists but empty until campaign runs)
│       └── ...
└── figures/
    ├── moto/          ← Figures from functional check
    │   ├── dup_rate.png
    │   └── ...
    └── live/          ← Figures from live AWS
        ├── .gitkeep   (directory exists but empty until campaign runs)
        └── ...
```

### Source Labels in Output Files

All outputs carry a **source label** in the first line or metadata:

- **Moto:** `results/moto/summary.md` begins with "Source: **moto functional check - NOT an AWS measurement (capacity and latency are not AWS numbers)**"
- **Live:** `results/live/summary.md` will state "Source: **AWS Lambda eu-west-1 + DynamoDB on-demand**" with date and run metadata

### Makefile Target Separation

| Target | Output Path | AWS Data? | Requires Credentials? |
|--------|-------------|-----------|----------------------|
| `make functional` | `results/moto/`, `figures/moto/` | ❌ NO | ❌ NO |
| `make pilot` | `data/runs/live/pilot/` | ✅ YES | ✅ YES |
| `make pilot-size` | `results/live/` | ✅ YES | ❌ NO (reads pilot data) |
| `make campaign` | `data/runs/live/campaign/` | ✅ YES | ✅ YES |
| `make sensitivity` | `data/runs/live/sensitivity/` | ✅ YES | ✅ YES |
| `make cloudwatch` | `data/runs/live/campaign/cloudwatch.json` | ✅ YES | ✅ YES |
| `make analyse` | `results/live/`, `figures/live/` | Depends on input | ❌ NO (reads campaign data) |

**Never conflate the two.** Any research paper, report, or presentation must clearly state whether results are from the moto functional check (implementation validation) or the live AWS campaign (the actual measurement that answers the research question).

**Credential enforcement:** See `RUNBOOK.md` for complete documentation of credential requirements and fail-closed behavior.

---

## Next steps to complete the project

1. **Deploy to live AWS** (researcher must provide credentials and accept ~USD 0.17 spend)
2. **Run pilot** (50 requests × 3 paths)
3. **Determine N** from pilot variance (provisional: N = 1000)
4. **Run full campaign** (9000 requests, 24000 invocations)
5. **Run sensitivity test** (P3 crash between writes)
6. **Collect CloudWatch metrics** (~10 minutes after campaign)
7. **Re-run analysis** on `data/runs/live/` → `results/live/` and `figures/live/`
8. **Integrate live results into report** — update evaluation section with real numbers, discuss against baseline (Qi et al. 2025 Halfmoon)
9. **Peer review and submission**

---

## References for this status document

- Wen, J., Chen, Z., Sarro, F. and Wang, S. (2025) Unveiling overlooked performance variance in serverless computing. *Empirical Software Engineering*, 30(2). doi:[10.1007/s10664-025-10615-3](https://doi.org/10.1007/s10664-025-10615-3). *(Pilot-sizing rule justification.)*
- Qi, S., Feng, H., Liu, X. and Jin, X. (2025) Efficient fault tolerance for stateful serverless computing with asymmetric logging. *ACM Transactions on Computer Systems*, 43(1–2). doi:[10.1145/3725985](https://doi.org/10.1145/3725985). *(Baseline idea: no duplicate mutation after retry via custom runtime.)*

---

Vikas Reddy Amanagantti
