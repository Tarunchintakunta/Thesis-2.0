import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_live_script_exits_blocked():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_live.py")],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2
    assert "BLOCKED" in (r.stdout + r.stderr)
