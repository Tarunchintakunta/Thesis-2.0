"""Citation gate (offline part): structure of bib/references.bib."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_bib", ROOT / "scripts/check_bib.py")
check_bib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_bib)

ENTRIES = check_bib.parse_bib((ROOT / "bib/references.bib").read_text())


def test_at_least_twenty_recent_entries():
    recent = [e for e in ENTRIES if 2022 <= int(e["year"]) <= 2026]
    assert len(recent) >= 20


def test_keys_unique_and_every_entry_traceable():
    keys = [e["key"] for e in ENTRIES]
    assert len(keys) == len(set(keys))
    for e in ENTRIES:
        assert e.get("doi") or e.get("url"), e["key"]
        assert e.get("title"), e["key"]


def test_baseline_is_bluemke_and_zdanowski():
    base = [e for e in ENTRIES if e.get("doi", "").lower() == "10.24425/ijet.2025.153619"]
    assert len(base) == 1
    assert "Bluemke" in base[0]["author"] and "Zdanowski" in base[0]["author"]


def test_offline_gate_passes():
    assert check_bib.main(["--offline"]) == 0
