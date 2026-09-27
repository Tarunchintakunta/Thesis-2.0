# Dataset note

- **Type:** synthetic webhook JSON payloads.
- **PII:** none.
- **Generator:** `src/sim/runner.py` → `make_event(i)`.
- **Fields:** `event_id`, `source`, `type`, `amount_cents`, `currency`, `poison`, `synthetic`.
- **Fault injection:** transient/permanent split of configured fault rate (default 85/15); duplicate ingestions at `duplicate_rate` (default 0.10).
- **Rates used in pilot:** 0, 0.10, 0.25, 0.50 (CA2).
- **Storage:** event bodies exist only in-memory during a run; aggregate metrics JSON under `results/local_sim/`.
