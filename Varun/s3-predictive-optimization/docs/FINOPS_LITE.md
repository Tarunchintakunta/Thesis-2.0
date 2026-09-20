# FinOps notes (lite round + what is still not evidenced)

**Updated:** 2026-09-20  
**Live AWS apply:** not repeated (stack already destroyed after lite).

## What exists on disk

| Surface | Evidence | Not this |
|---------|----------|----------|
| Boto3 metadata collector | `src/metadata/collector.py` (`from_list_objects`, Inventory CSV parser) | A live Inventory *job* was never enabled |
| Destroyed-bucket reconstruct | `results/live/lite_metadata.json` — 48 objects (24 STANDARD + 24 STANDARD_IA × 160 KiB) from committed lite JSON | Not `ListObjectsV2` after destroy |
| Wilcoxon | Lite probe n=24 in `live_lite_summary.json`; helper `analysis/statistics.py` | Multi-workload CA2 success protocol (≥2/3 workloads) **not run live** |
| Cost Explorer | Account-window Unblended S3 **$3.6e-09** (2026-09-13→20) | **Not** settled campaign savings (CE lag; lite ≠ billing trial) |
| CloudWatch | API ok; `BucketSizeBytes` datapoints empty (new-bucket lag) | Inventory reports / storage-lens |
| Pricing | Live Pricing API ping ok (`price_list_count=0` in lite summary); savings arithmetic uses `configs/pricing.json` | Do not label savings as Pricing-API quotes |

## Why this does not close the AWS residual

CA2 asks for evaluation in a live AWS environment with Inventory/metadata, multi-workload Wilcoxon vs native Lifecycle/Intelligent-Tiering, and CE-settled costs. The collector module and reconstructed lite table close the **missing-file / missing-notes** gap. They do **not** replace a fuller FinOps campaign. `SOLE_AWS_RESIDUAL=yes`.

Do not start a new apply unless that campaign is authorised as Free-Tier-safe and destroy-after.
