# scoped_E_guidance_1 — E_guidance_transfer (20/20)

**Generated:** `2026-09-23T07:56:39.607470+00:00`  
**Campaign:** `E_guidance_transfer` (localsim)  
**Matrix:** VT ∈ {30, 600} × batch ∈ {10, 50} × n=5 → **20/20**  
**Baseline framing:** Kyrychenko et al. (2025) steady-state guidance under fault (Obj 3 / H3).

## Cell means

| VT | batch | n | loss | dup | DLQ | recovery_s | thr | Kyrychenko-fav? |
|---:|------:|--:|-----:|----:|----:|-----------:|----:|:---------------:|
| 30 | 10 | 5 | 0.0000 | 0.1048 | 0.0000 | 36.00 | 20.053 | no |
| 30 | 50 | 5 | 0.0000 | 0.0699 | 0.0000 | 36.00 | 20.069 | no |
| 600 | 10 | 5 | 0.0000 | 0.0765 | 0.0000 | 600.00 | 5.004 | no |
| 600 | 50 | 5 | 0.0000 | 0.0651 | 0.0000 | 600.00 | 5.003 | yes |

## Reading

- Loss=0 all cells under this localsim consumer_kill protocol.
- Kyrychenko-favourable VT600 cells show **recovery ≈ 600 s** vs VT30 **≈ 36 s** — guidance that optimises steady-state throughput does **not** minimise recovery under fault (aligns with localsim H3_recovery fail-to-reject after Holm).
- This pack **does not** close full IV live matrix (batch/burst/multi-fault grid on AWS) — that limb is **amended / dated WONTFIX**.

