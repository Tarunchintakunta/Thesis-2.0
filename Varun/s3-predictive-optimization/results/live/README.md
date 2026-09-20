# Live AWS results (Varun)

## Live lite (2026-09-20) — authoritative

| File | Role |
|------|------|
| `live_lite_summary.json` | Measured summary: S3 PUT/GET, CE, CW, modeled storage $, Wilcoxon, destroy status |
| `lite_metadata.json` | Reconstructed 48-object table from lite JSON (not post-destroy ListObjects; Inventory job never enabled) |

**Scope disclosure:** 24 objects × STANDARD vs STANDARD_IA @ 160 KiB in `eu-west-1`. Not Inventory-backed, not multi-workload, not CE-settled savings. Wilcoxon significance is for this probe only.

**Destroy:** terraform destroy complete (8 resources); bucket verified absent.
