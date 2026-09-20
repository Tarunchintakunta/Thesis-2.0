# Terraform — MQTT QoS IoT Core campaign stack

**Do not apply in this pass.** Modules are ready for a later free-tier-guarded live round.

## Layout

| Path | What |
|------|------|
| `modules/iot_core` | 5 things, thing type, per-device certs, connect/publish policy |
| `modules/ingest` | DynamoDB delivered table (msg_id, delivery_id), ingest Lambda, IoT topic rule `devices/+/telemetry` |

Names use `mqtt-qos-<stage>-…` only. No student name or student ID.

## Later apply / destroy (not this pass)

```bash
# only after free-tier guard and an explicit live-AWS decision
terraform init
terraform plan -out tfplan
# terraform apply tfplan
# … campaign …
# terraform destroy
```

Certificates created on apply land in state; destroy after the round.

Region default: `eu-west-1`. Device count default: 5 (formal CA2 constant).
