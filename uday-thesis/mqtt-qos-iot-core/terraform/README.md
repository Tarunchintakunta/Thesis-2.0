# Terraform — MQTT QoS IoT Core campaign stack (lite / smoke)

**Default:** `enable_apply=false` (scaffold / plan only).

Apply only after `STATUS.md` says `READY_FOR_AWS: YES` and free-tier guard passes for `lite` or `smoke`.

## Layout

| Path | What |
|------|------|
| `modules/iot_core` | N things, thing type, per-device certs, connect/publish policy |
| `modules/ingest` | DynamoDB delivered table, ingest Lambda, IoT topic rule `devices/+/telemetry` |

Names use `mqtt-qos-<stage>-…` only. No student name or student ID.

## Tags (always)

`Project=mqtt-qos-iot-core`, `Thesis=uday-mqtt-qos`, `Environment=research`, `ManagedBy=terraform`, `Campaign=lite`.

## Apply / destroy (lite|smoke only)

```bash
# from artefact root, after READY_FOR_AWS
python scripts/assert_free_tier_guard.py --mode smoke
python scripts/check_ready_for_aws.py

cd terraform
terraform init
terraform plan -var='enable_apply=true' -var='device_count=2' -out tfplan
terraform apply tfplan
# … scripts/run_live.py --scale smoke …
../scripts/destroy_stack.sh
```

Certificates land under `../.certs/` (gitignored). Destroy removes AWS resources and local certs.

Region default: `eu-west-1`.
