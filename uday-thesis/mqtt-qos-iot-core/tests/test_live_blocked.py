import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_live_script_blocks_without_ready_or_formal():
    """Without READY latch historically NO — after YES, dry-validate should pass gates.
    Formal must never be accepted by argparse."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_live.py"), "--scale", "formal"],
        capture_output=True,
        text=True,
    )
    # argparse rejects formal
    assert r.returncode != 0


def test_live_dry_validate_when_ready():
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_live.py"),
            "--scale",
            "smoke",
            "--dry-validate",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    status = (ROOT / "STATUS.md").read_text(encoding="utf-8")
    ready = "READY_FOR_AWS" in status and "YES" in status.split("READY_FOR_AWS", 1)[1][:40]
    if ready:
        assert r.returncode == 0, r.stderr + r.stdout
        data = json.loads(r.stdout)
        assert data["dry_validate"] is True
        assert data["scale"] == "smoke"
        assert data["n_specs"] == 4
    else:
        assert r.returncode == 2
        assert "BLOCKED" in (r.stdout + r.stderr)


def test_free_tier_guard_lite_ok_formal_blocked():
    ok = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "assert_free_tier_guard.py"), "--mode", "lite"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    bad = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "assert_free_tier_guard.py"), "--mode", "formal"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert bad.returncode == 1
    assert "BLOCKED" in (bad.stdout + bad.stderr)


def test_plan_free_tier_reconciliation():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "plan_free_tier.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["reconciliation"]["lite_free_tier_safe"] is True
    assert data["reconciliation"]["formal_blocked"] is True
    assert data["scales"]["lite"]["headroom_pct"] > 90
    assert data["scales"]["smoke"]["iot_messages_upper"] < data["scales"]["lite"]["iot_messages_upper"]


def test_check_ready_gates():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_ready_for_aws.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    data = json.loads(r.stdout)
    assert "gates" in data
    assert data["gates"]["tags"]["ok"] is True
    assert data["gates"]["destroy_hook"]["ok"] is True
    assert data["gates"]["cost_plan"]["ok"] is True
