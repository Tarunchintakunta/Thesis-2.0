# MQTT QoS reliability in AWS IoT Core

Formal CA2 artefact for Uday (binding: `../CA2_COMMITMENTS.md`, source
`../UdayKiranReddyDodda_X25166484_proposal.docx`).

**Research question.** To what extent does publishing at MQTT QoS 1 rather than
QoS 0 reduce telemetry message loss in **AWS IoT Core** when the publishing
device undergoes controlled disconnections of 0 / 15 s / 1 min / 5 min?

This tree is Terraform-first: IoT Core things + topic rule → Lambda → DynamoDB
matching against a **device-side ID log**. Synthetic devices are what the
formal CA2 specifies.

## Honesty (read this first)

| What you can run now | What it is |
|----------------------|------------|
| `make dry-run` | Local **mock** broker + in-memory DynamoDB matcher. Proves the harness. |
| `make terraform-validate` | IaC syntax check. **Does not apply.** |
| `make live` | Exits 2 — live AWS is **blocked this pass**. |

**Mock numbers are not AWS IoT Core evidence.** The federated-RF tree under
`../_superseded_proxy/iot-reliability/` is a **different thesis** and is not
evidence for this CA2.

## Factorial (formal)

- QoS ∈ {0, 1} × disconnect ∈ {0, 15 s, 60 s, 300 s} × rate ∈ {steady, bursty}
- 5 devices × 1000 messages × 5 replications (16 cells)
- α = 0.05, Holm–Bonferroni over the campaign family
- Baseline: Shvaika et al. (2025) — managed vs self-hosted, under disconnection

Dry-run scale (harness proof): 5 × 40 × 2 reps, virtual clock (no 5 s sleeps).

## Layout

```
terraform/           IoT Core + ingest path (ready, not applied)
src/simulator/       device processes, disconnect window, mock broker
src/matching/        device-log ↔ delivered-record match
src/lambda_ingest/   live Lambda (put delivered item; keeps duplicates)
src/analysis/        loss / dup / latency / cost / Holm–Bonferroni
scripts/dry_run.py   local mock campaign
configs/             experiment, analysis plan, published unit prices
```

Resource names use the slug `mqtt-qos` only — no student name or ID.

## Usage

```bash
pip install -r requirements.txt
make test
make dry-run
make analyse
make terraform-validate
make cost
make guard
```

## Free tier

The **formal** live campaign (400k publishes + QoS 1 PUBACKs) exceeds the
typical 250k monthly IoT message free-tier envelope. `scripts/assert_free_tier_guard.py`
blocks that plan. A later **lite** live fold (16 cells × 5 devices × 50 msgs × 1
rep) fits; it is **not** executed here.

## Status

See `STATUS.md`. Alignment is **not** 100%. **NOT COMPLETE.**
