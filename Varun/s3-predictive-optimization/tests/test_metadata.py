"""Tests for metadata collector, Inventory CSV parser, and Boto3 listing."""

from __future__ import annotations

import sys
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metadata.boto3_collector import list_object_metadata, metadata_report_from_listing
from src.metadata.collector import inventory_from_lite, metadata_report
from src.metadata.inventory_csv import inventory_summary, parse_inventory_csv

INVENTORY_CSV = """Bucket,Key,Size,LastModifiedDate,StorageClass,IntelligentTieringAccessTier
research-bucket,arch/a.bin,1024,2026-01-01T00:00:00.000Z,STANDARD,
research-bucket,arch/b.bin,2048,2026-02-01T00:00:00.000Z,STANDARD_IA,
research-bucket,arch/c.bin,4096,2025-06-01T00:00:00.000Z,GLACIER,
"""


def test_parse_inventory_csv_counts_classes():
    rows = parse_inventory_csv("unused.csv", text=INVENTORY_CSV)
    assert len(rows) == 3
    assert rows[0]["key"] == "arch/a.bin"
    assert rows[0]["size"] == 1024
    assert rows[1]["storage_class"] == "STANDARD_IA"
    summary = inventory_summary(rows)
    assert summary["n_objects"] == 3
    assert summary["total_bytes"] == 1024 + 2048 + 4096
    assert summary["by_storage_class"]["STANDARD"] == 1
    assert "Inventory" in summary["disclaimer"]


def test_lite_inventory_and_report_from_committed_json():
    rows = inventory_from_lite()
    assert len(rows) >= 1
    report = metadata_report()
    assert report["round"] == "live_lite"
    assert report["region"] == "eu-west-1"
    assert report["listed_key_count"] == 48
    assert "lite" in report["disclaimer"].lower() or "FinOps" in report["disclaimer"]


@mock_aws
def test_boto3_list_object_metadata_moto():
    region = "eu-west-1"
    bucket = "s3-pred-opt-unit-test"
    s3 = boto3.client("s3", region_name=region)
    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={"LocationConstraint": region},
    )
    s3.put_object(Bucket=bucket, Key="std/obj-0.bin", Body=b"x" * 16, StorageClass="STANDARD")
    s3.put_object(
        Bucket=bucket, Key="ia/obj-0.bin", Body=b"y" * 32, StorageClass="STANDARD_IA"
    )
    rows = list_object_metadata(s3, bucket)
    assert len(rows) == 2
    keys = {r["key"] for r in rows}
    assert keys == {"std/obj-0.bin", "ia/obj-0.bin"}
    sizes = {r["key"]: r["size"] for r in rows}
    assert sizes["std/obj-0.bin"] == 16
    assert sizes["ia/obj-0.bin"] == 32
    report = metadata_report_from_listing(rows, bucket=bucket, region=region)
    assert report["n_objects"] == 2
    assert report["total_bytes"] == 48
    assert report["by_storage_class"]["STANDARD"] == 1
    assert report["by_storage_class"]["STANDARD_IA"] == 1
