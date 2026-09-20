# results/

> **Everything under `mock/` is a local simulator** (`backend: mock` in every
> manifest). These are **not** measurements of AWS IoT Core. They show that the
> device-side ID log, DynamoDB-shaped matcher, metrics, Holm–Bonferroni script,
> and cost estimator run end to end. Numeric loss/dup/latency depend on
> `configs/experiment.yaml` → `mock:` parameters, **not** on the managed broker.
>
> Live AWS runs, if authorised later, go in `live/` with `backend: live` and
> must be reported separately.

## Layout

| Path | What |
|------|------|
| `mock/manifests/` | Per-run spec + measurement_kind |
| `mock/device_log/` | Ground-truth IDs written **before** publish |
| `mock/delivered/` | Mock DynamoDB items (`msg_id` + `delivery_id`) |
| `mock/runs.csv` `cells.csv` | Loss / dup / latency / reconnect / USD estimate |
| `mock/summary/stats.json` | Pre-registered tests on **mock** data |
| `mock/figures/` | Loss, duplication, reliability–cost plots (labelled mock) |
| `live/` | Absent this pass (AWS not applied) |

## What the mock is allowed to show

Protocol-shaped properties of **this** client model, used as a harness check:

- QoS 0 drops intended messages for the disconnect window (they are logged, not delivered). Loss rises with duration (dry-run cells: 0% at 0 s up to ~67.5% at 300 s).
- QoS 1 queues that window in a local outbox and flushes after reconnect, so loss is ~0 in the mock.
- Duplicates appear for QoS 1 when the last pre-cut PUBLISH is retried (`duplicate_id_rate` ~0.8–2% in the dry-run).
- Matcher loss = IDs in the device log missing downstream; duplicate = ID with count > 1.

Holm–Bonferroni decisions in `summary/stats.json` are **executed on mock rows**. Rejecting H0 there does **not** answer the AWS IoT Core question.

It is **not** allowed to show what IoT Core session retention, queue depth, or
throttling do. That is the live experiment.

## Baseline

Shvaika et al. (2025) characterise a self-hosted broker at steady load and name
QoS variation + intermittent connectivity as future work. This CA2 inverts that
arrangement. No live contrast exists until IoT Core is measured.
