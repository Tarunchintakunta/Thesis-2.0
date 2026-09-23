# DATED_WONTFIX — N-Vikas / P4 TransactWrite (2026-09-23)

**Thesis:** Vikas (`lambda-idempotency-eval`)  
**Item:** P4 / `TransactWriteItems` multi-item transactional idempotency  
**Disposition:** **WONTFIX under disclosed CA2 scope** (quarantined; not remediable floor debt)

## Why amended out

- Binding `config/experiment.yaml` registers **paths: [P1, P2, P3] only**.
- `docs/ASSUMPTIONS.md` **A12**: single-item writes only; no `TransactWriteItems` (master prompt §6; future work).
- Live campaign cells/deliveries contain **zero** P4 rows (scripted audit).
- Draft `vikas_final_report.md` P4 narrative is **NON-AUTHORITATIVE** (banner on file).

## What remains in floor

Live campaign E1–E3 on P1/P2/P3 (N=1000×3×3 = 24000 deliveries), Streams GT, destroy-after. Honest floor **~88**.

## Reproduce

```bash
cd vikas-thesis/lambda-idempotency-eval
python3 scripts/audit_campaign_root_causes.py
# expect EXIT 0; disposition DATED_WONTFIX_P4_QUARANTINED; remediable_total=0
```
