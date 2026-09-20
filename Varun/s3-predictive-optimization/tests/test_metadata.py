"""Metadata collector: inventory CSV + lite-round reconstruct (no live AWS)."""
from src.metadata.collector import from_inventory_csv, from_lite_round, inventory_summary


def test_inventory_csv_parse():
    text = (
        "bucket,key,size,last_modified_date,storage_class\n"
        "b,a.bin,163840,2026-09-19T00:00:00+00:00,STANDARD\n"
        "b,c.bin,163840,2026-09-19T00:00:00+00:00,STANDARD_IA\n"
    )
    rows = from_inventory_csv(text)
    assert len(rows) == 2
    assert rows[0]["storage_class"] == "STANDARD"
    assert rows[1]["size_bytes"] == 163840
    s = inventory_summary(rows)
    assert s["n_objects"] == 2
    assert s["storage_class_counts"]["STANDARD_IA"] == 1


def test_lite_round_reconstructs_48_objects():
    summary = {
        "collected_at": "2026-09-20T12:05:10+00:00",
        "s3": {
            "prefix": "lite/p/",
            "objects_per_arm": 24,
            "object_bytes": 163840,
            "sample_objects": [
                {
                    "key_standard": "lite/p/std/obj-000.bin",
                    "key_ia": "lite/p/ia/obj-000.bin",
                    "size_bytes": 163840,
                }
            ],
        },
    }
    rows = from_lite_round(summary)
    assert len(rows) == 48
    classes = {r["storage_class"] for r in rows}
    assert classes == {"STANDARD", "STANDARD_IA"}
    assert inventory_summary(rows)["n_objects"] == 48
    keys = {r["key"] for r in rows}
    assert "lite/p/std/obj-000.bin" in keys
    assert "lite/p/ia/obj-023.bin" in keys
