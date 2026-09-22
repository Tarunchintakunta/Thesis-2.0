# GENAI_HANDOFF.md — Uday (MQTT QoS IoT Core)

Evidence-only. Numbers and judgments below are bound to on-disk artefacts and `_analysis_extract/reports/INDEPENDENT_REVIEW_UDAY.md`. Do not invent formal-N results.

## 0. Document meta

| Field | Value |
|-------|-------|
| Student | Uday Kiran Reddy Dodda |
| Student ID | X25166484 |
| Programme | MSc Cloud Computing Research Project |
| Artefact root | `uday-thesis/mqtt-qos-iot-core/` |
| Formal proposal | `uday-thesis/UdayKiranReddyDodda_X25166484_proposal.docx` |
| Binding contract | `uday-thesis/CA2_COMMITMENTS.md` |
| Honest CA2 floor | **Closed under disclosed lite scope (~70)** — final_1–3 lite Demonstrated; formal N / Holm / d60≠d300 are beyond-floor (DESIGN_RATIONALE) |
| Eval completeness | **3× lite** destroy-after finals (`results/live/final_1\|2\|3/`); **not** formal 80-cell / ~600k-msg design |
| AWS | **Required and applied** (eu-west-1 IoT Core; destroy confirmed each final) |
| Handoff date | 2026-09-22 |
| Authority | `CA2_COMMITMENTS.md`, `INDEPENDENT_REVIEW_UDAY.md`, `results/live/FINAL3_BASELINE.md`, `final_* /LIVE_EVIDENCE.json` |

**§0 honesty (required):** Formal CA2 replications (5 reps), Holm–Bonferroni at formal N, and schedule that separates disconnect 60 s vs 300 s are **Not met**. Calling research-scope 100% after moving formal N to “beyond floor” is **rejected** by independent review.

## 1. Research problem, motivation, research question, and objectives

**Problem:** Publishers on AWS IoT Core may disconnect; MQTT QoS 0 vs 1 trade delivery completeness against latency/cost, but managed-broker disconnect behaviour needs measured evidence with per-message ground truth.

**RQ (formal CA2):** To what extent does publishing at MQTT QoS level 1 rather than level 0 reduce telemetry message loss in AWS IoT Core when the publishing device undergoes controlled disconnections of varying duration?

**Objectives (must evidence):**
1. Quantify message **loss** at QoS 0 vs 1 across controlled disconnection durations (none, 15 s, 1 m, 5 m).
2. Quantify **duplication** and end-to-end **latency** (mean / p95 / p99) as the price of reliability.
3. Measure **reconnection** behaviour and backlog survival.
4. Place each configuration on a **reliability–cost** surface (published unit prices × counted operations).

## 2. Identified literature gap and how this research addresses it

**Named baseline:** Shvaika et al. (2025), *A distributed architecture for MQTT messaging: the case of TBMQ* (Journal of Big Data) — self-hosted Kafka/Redis-backed broker under **steady high load**; varying QoS, intermittent connectivity, and varying client conditions named as **future work** (`uday-thesis/baseline_papers/BASELINE_PAPER.md`).

**Gap taken up:** No reviewed study jointly combines (a) a **managed** broker the tenant does not control, (b) **controlled publisher disconnect**, (c) more than one QoS service level, and (d) a **per-message device-side ID log** matched to delivered records.

**How addressed (lite depth):** Live AWS IoT Core factorial QoS × disconnect × rate with device-log ↔ DynamoDB match. Does **not** reproduce Shvaika TBMQ throughput figures (different RQ).

## 3. CA2 proposal alignment and any extensions beyond the proposal

| Item | Status |
|------|--------|
| RQ / objectives / AWS IoT Core method | Aligned (formal CA2) |
| Factors QoS ∈ {0,1} × disconnect ∈ {0,15,60,300} s × {steady,bursty} | Aligned in configs; **executed at lite N** |
| 5 devices × 1000 msgs; 5 replications; α=0.05 Holm–Bonferroni | **Not met** (lite: 5×50 msgs; n=1 rep/cell) |
| Device-side ID log ↔ DynamoDB | Demonstrated (live packs) |
| Free-tier + destroy | Demonstrated (lite ~6 000 IoT msgs upper ≈2.4% of 250 000) |
| Formal ~600 000 msgs / 80 cells | **Beyond floor / Free-Tier-blocked** single-month (`DESIGN_RATIONALE_BEYOND_CA2.md`) |
| Prior proxy federated RF (`_superseded_proxy/iot-reliability/`) | **Quarantined** — not this CA2 |

## 4. Research methodology and experimental design

- **Design:** Factorial experiment on simulated MQTT publishers against live AWS IoT Core.
- **Factors:** `qos` ∈ {0,1}; `disconnect_s` ∈ {0,15,60,300}; `rate_mode` ∈ {steady, bursty}.
- **Matching:** Device-side message ID log before publish; IoT rule → Lambda → DynamoDB; match delivered IDs for loss / duplicate / latency.
- **Lite scale (executed finals):** 5 devices × 50 msgs × 16 cells × 1 replication; `interval_s=1.0` (`configs/experiment.yaml` `lite`).
- **Formal scale (configured, not run live):** 5×1000 msgs × 5 reps = 80 runs; ≈600 000 IoT msgs (`formal` block) — blocked.
- **Region / destroy:** eu-west-1; terraform apply → measure → destroy-after each final pack.
- **Synthetic telemetry:** Explicitly allowed by formal CA2.

## 5. Artefact purpose and artefact-only project structure

**Purpose:** Implement and evaluate MQTT QoS 0 vs 1 loss under controlled disconnect on AWS IoT Core for formal CA2.

```
mqtt-qos-iot-core/
  configs/           # experiment.yaml (dry_run/lite/smoke/formal), analysis_plan, pricing
  src/simulator/     # synthetic devices, disconnect windows, mock + live publishers
  src/matching/      # device-log ↔ delivered match (loss/dup/latency)
  src/analysis/      # cost surface, Holm helpers, plots
  src/lambda_ingest/ # IoT rule Lambda (stdlib + boto3)
  src/common/        # shared helpers
  terraform/         # IoT Core + rule + Lambda + DynamoDB (enable_apply default false)
  scripts/           # run_live, destroy_stack, free-tier guards, finals helpers
  results/mock/      # harness only — NOT AWS evidence
  results/live/      # AWS evidence: initial_eval_1, final_1|2|3, archives
  tests/             # unit/harness tests
  template.yaml      # Lambda packaging
  Makefile           # test, dry-run, plan-ft, ready, live, destroy
```

**Out of artefact tree (parent):** `uday-thesis/CA2_COMMITMENTS.md`, `DESIGN_RATIONALE_BEYOND_CA2.md`, `baseline_papers/BASELINE_PAPER.md`. Quarantine: `uday-thesis/_superseded_proxy/`.

## 6. AWS architecture, services, configurations, and experimental setup

**Required.** Live path:

| Piece | Role |
|-------|------|
| AWS IoT Core (MQTT) | Managed broker; QoS 0/1 publishes |
| IoT topic rule | Routes telemetry to ingest |
| Lambda (`src/lambda_ingest/`) | Writes delivered message IDs |
| DynamoDB | Ground-truth delivery store for matching |
| Terraform modules `iot_core`, `ingest` | Provision/destroy; project tags |
| Simulated devices | Publish with controlled disconnect windows |

**Setup (lite finals):** `device_count=5`; 16 cells; Free-Tier-safe envelope; stack **destroyed** after each round (`destroy_confirmed.txt` = yes). Formal apply remains blocked by `scripts/run_live.py` / free-tier guard until multi-month staging or accepted overage.

## 7. Evaluation metrics and why they were selected

| Metric | Role | Why |
|--------|------|-----|
| Loss rate | Primary DV | Direct RQ — delivery completeness under disconnect |
| Duplicate-id rate | Secondary | Cost of QoS1 reliability (obj 2) |
| E2E latency mean / p95 / p99 | Secondary | Latency price of reliability (obj 2) |
| Reconnect time; backlog queued/survived | Secondary | Reconnection / backlog (obj 3) |
| `usd_est` (unit prices × ops) | Secondary | Reliability–cost surface (obj 4) |

## 8. Baseline definition and baseline comparison

| Role | Definition |
|------|------------|
| **Experimental baseline (treatment contrast)** | QoS **0** (at-most-once) |
| **Proposed** | QoS **1** (at-least-once) |
| **Literature baseline** | Shvaika et al. (2025) self-hosted steady-load characterisation — gap paper, not a numeric clone |

**Comparison rule:** Same factorial cells on live IoT Core; judge QoS1 vs QoS0 on loss first, then latency/backlog/cost. Do not claim Shvaika throughput parity.

Bound means (`FINAL3_BASELINE.md` / `final3_qos_summary.json`): QoS0 mean loss **0.415** vs QoS1 **0.0** across all three finals.

## 9. Complete evaluation process and number of runs

| Pack | Path | Scale | Cells | Destroy |
|------|------|-------|------:|---------|
| smoke | `results/live/archive/smoke-2026-09-21/` | 2×8 msgs; 4 cells | 4 | destroyed |
| initial_eval_1 / root lite | `results/live/initial_eval_1/`, `results/live/LIVE_EVIDENCE.json` | lite 5×50 | 16 | destroyed (2026-09-21) |
| final_1 | `results/live/final_1/` | lite 16-cell; 32 manifests | 16 | `destroy_confirmed=yes` (2026-09-22T04:29:17Z) |
| final_2 | `results/live/final_2/` | same | 16 | yes (2026-09-22T05:44:06Z) |
| final_3 | `results/live/final_3/` | same | 16 | yes (2026-09-22T06:58:53Z) |
| formal 80-cell | — | 5×1000×5 | — | **Not run** |

**Lite vs full:** All finals are **lite** (n=1 rep/cell; 50 msgs/device). Formal powered design is **absent**. Mock under `results/mock/` is harness only.

## 10. Final results and key findings (committed evidence only)

### Mean loss (all disconnect × rate cells) — `FINAL3_BASELINE.md`

| Round | baseline QoS0 mean loss | proposed QoS1 mean loss |
|-------|------------------------:|------------------------:|
| final_1 | 0.415 | 0.0 |
| final_2 | 0.415 | 0.0 |
| final_3 | 0.415 | 0.0 |

### QoS0 loss by disconnect (mean across rounds × rate_mode)

| disconnect_s | mean loss |
|-------------:|----------:|
| 0 | 0.0 |
| 15 | 0.3 |
| 60 | **0.68** |
| 300 | **0.68** (≡ d60 under lite schedule) |

### QoS1 (all finals, both rate modes)

- Loss **0.0** at every disconnect.
- Under disconnect cells: backlog queued = survived (e.g. 75 at d15; 170 at d60/d300).
- Latency cost: mean latency under disconnect ≈ **3.2–14.5 s** (ms figures in `LIVE_EVIDENCE.json` cells); connected d0 remains sub-second mean.

### Pack integrity

- 32 manifests per final pack; `destroy_confirmed=yes` each.
- Duplicate-id rate **0.0** in reported lite cells.

## 11. How results satisfy or address each research objective

1. **Loss QoS0 vs QoS1 across disconnects:** **Partial / Demonstrated at lite.** Directional: QoS0 loss rises with disconnect (0 → 0.3 → 0.68); QoS1 loss 0.0. Formal durations fully powered and d60≠d300 **Not met**.
2. **Duplication + latency:** **Demonstrated at lite.** Dup 0.0; QoS1 pays large latency under disconnect (obj “price of reliability”).
3. **Reconnection / backlog:** **Demonstrated at lite.** QoS1 backlog survives disconnect cuts; reconnect times recorded in cell metrics.
4. **Reliability–cost surface:** **Demonstrated at lite depth** via `usd_est` per cell; not a full formal cost campaign.

## 12. How results answer the research question

At **lite** Free-Tier depth on live AWS IoT Core, publishing at QoS 1 rather than QoS 0 **eliminated measured loss** under controlled publisher disconnect (mean loss 0.415 → 0.0 across cells), at the cost of multi-second mean latency and backlog flush after reconnect.

This is a **directional** answer only. It does **not** close the formal RQ under the proposal’s 5-replication / ~600k-msg / Holm design, and **cannot** claim distinct effects of 60 s vs 300 s disconnect (identical QoS0 loss 0.68 under lite wall-clock).

## 13. How findings relate to the literature gap and previous research

Supplies the managed-broker + disconnect + multi-QoS + per-message log cell that Shvaika et al. (2025) leave as future work / omit. Contrast is methodological (managed + disconnect), **not** a numeric reproduction of TBMQ throughput. Prior federated-RF proxy is superseded and must not be cited as this CA2.

## 14. Statistical analysis and significance

- Formal plan: α=0.05 Holm–Bonferroni across factorial contrasts at **5 replications**.
- **Delivered:** n=1 per cell per final; three lite packs with identical mean loss pattern (0.415 vs 0.0).
- **Independent review:** confirmatory stats across final_1–3 cells still recommended; report power honestly — **underpowered vs formal plan**.
- Treat finals as **repeatability of the lite pipeline**, not a substitute for formal N. No claim of Holm-controlled significance at proposal power.

## 15. Important observations, trends, positive/negative findings, and anomalies

- **Positive:** Three independent destroy-after lite finals; QoS1 loss 0.0 all disconnect cells; QoS0 loss monotone with disconnect duration until schedule ceiling.
- **Negative / retain:** QoS1 reliability costs latency (~3–14 s mean under disconnect) and backlog; n=1/cell; Free-Tier scope shrink.
- **Anomaly / confound:** QoS0 **d60 ≡ d300** loss **0.68** — lite publish schedule (~49 s) means both cuts cover remaining messages; cannot separate long disconnects.
- **Honesty:** Internal “100% research-scope floor” language is **rejected** as full formal delivery (`INDEPENDENT_REVIEW_UDAY.md`).

## 16. Limitations, validity, reproducibility, and generalisability

- Lite N (50 msgs/device; 1 rep) ≠ formal (1000 msgs; 5 reps).
- Schedule confound (d60≡d300) limits construct validity for long disconnect factor.
- Synthetic devices / lab disconnect model — not physical radios or multi-region.
- Cost estimates from published unit prices × counted ops — not invoice-level.
- Destroy-after aids cost hygiene but stack is not left running for external audit without re-apply.
- Generalisability limited to AWS IoT Core MQTT path as configured; QoS 2 deferred.

## 17. Final conclusions and research contribution

**Contribution (honest):** A reproducible Free-Tier-safe live factorial on AWS IoT Core showing **directional** evidence that QoS 1 reduces telemetry loss under controlled publisher disconnect relative to QoS 0, with measured latency/backlog cost, plus explicit documentation of schedule and power limits.

**Not a contribution claim:** Formal confirmatory delivery of the proposal’s powered statistical design, or separation of 1 m vs 5 m disconnect effects under lite scheduling.

## 18. What changed or improved during the evaluation process

- Quarantined federated-RF proxy; locked formal MQTT QoS IoT Core CA2.
- Smoke → full lite 16-cell (2026-09-21) → three destroy-after finals (2026-09-22).
- Bound loss tables and FINAL3 baseline; retained d60≡d300 and formal-N gaps in STATUS / independent review.
- Formal volume explicitly staged as beyond-floor / Free-Tier-blocked rather than silently claimed complete.

## 19. Remaining issues or recommended future work

1. **Formal N Not met:** If credits allow, run multi-month or accepted-overage formal (5×1000×16×5) for power.
2. **d60≡d300 Not met:** Lengthen wall-clock / message schedule so 60 s and 300 s disconnects are separable.
3. Confirmatory descriptive/stats across final_1–3 cells with **honest power** disclosure (even if underpowered).
4. Fold Shvaika contrast prose into the examiner final report using bound lite tables (soft packaging).
5. Do **not** raise CA2_% to 100 until formal design is run **or** proposal scope is formally amended with examiner-facing honesty (not `DESIGN_RATIONALE` alone).

## 20. Important files, scripts, configurations, datasets, and artefacts to reproduce/continue

| Path | Role |
|------|------|
| `../CA2_COMMITMENTS.md` | Binding formal contract |
| `../DESIGN_RATIONALE_BEYOND_CA2.md` | Floor vs beyond-floor formal depth |
| `../baseline_papers/BASELINE_PAPER.md` | Shvaika gap mapping |
| `../../_analysis_extract/reports/INDEPENDENT_REVIEW_UDAY.md` | Honest floor closed under lite scope ~70 |
| `configs/experiment.yaml` | dry_run / lite / smoke / formal scales |
| `configs/pricing.yaml` | Unit prices for `usd_est` |
| `configs/analysis_plan.yaml` | Analysis plan |
| `terraform/` | IoT Core + ingest IaC |
| `scripts/run_live.py` | Live runner (formal blocked) |
| `scripts/destroy_stack.sh` | Mandatory destroy |
| `scripts/check_ready_for_aws.py` / `plan_free_tier.py` | Gates |
| `scripts/run_final_lite.sh` / `run_all_finals.sh` | Final pack runners |
| `scripts/write_final3_baseline.sh` | Baseline table generator |
| `results/live/final_{1,2,3}/LIVE_EVIDENCE.json` | Per-round cell metrics |
| `results/live/final_{1,2,3}/manifests/` | 32 manifests each |
| `results/live/final_{1,2,3}/destroy_confirmed.txt` | Destroy evidence |
| `results/live/FINAL3_BASELINE.md` | Cross-round QoS0 vs QoS1 means |
| `results/live/final3_qos_summary.json` | Machine-readable means |
| `results/mock/` | Local harness only — do not cite as IoT Core |

**Reproduce lite (high level):** `make test` → `make ready` → terraform apply with lite vars → `make live` / final scripts → `make destroy`. Do not claim formal completion without formal-scale evidence on disk.
