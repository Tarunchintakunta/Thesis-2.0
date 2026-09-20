"""Live-lite phase mapping for Holm analysis."""
import pandas as pd

from coldstart.live_lite_map import map_live_lite


def test_maps_init_to_package_and_runtime_compare():
    df = pd.DataFrame([
        {"phase": "live_python_init", "runtime": "python", "variant": "optimised",
         "memory_mb": 1024, "cold": True, "error": False, "intended_cold": True, "init_ms": 80},
        {"phase": "live_python_init", "runtime": "python", "variant": "default",
         "memory_mb": 1024, "cold": True, "error": False, "intended_cold": True, "init_ms": 3000},
        {"phase": "live_python_init", "runtime": "python", "variant": "bytecode",
         "memory_mb": 1024, "cold": False, "error": True, "intended_cold": True, "init_ms": None},
        {"phase": "live_python_memory", "runtime": "python", "variant": "optimised",
         "memory_mb": 128, "cold": True, "error": False, "intended_cold": True, "init_ms": 90},
    ])
    out = map_live_lite(df)
    assert set(out["phase"]) >= {"package_size", "runtime_compare", "memory"}
    h1 = out[out["phase"] == "runtime_compare"]
    assert list(h1["variant"].unique()) == ["optimised"]
    pkg = out[out["phase"] == "package_size"]
    assert "bytecode" in set(pkg["variant"])
