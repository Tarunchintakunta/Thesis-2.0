# Dataset note

- Synthetic tenant IDs and document rows only.
- No personal data / no real customer tenancy.
- Generator: `sim.runner.run_pilot`.
- Cross-tenant probes: 10,000 attempts in pilot (JWT tenant mismatch + RLS).
- Quota dimensions: api, storage, compute.
