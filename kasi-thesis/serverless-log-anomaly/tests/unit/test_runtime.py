import re

from tests.conftest import HEALTH, POST

T0 = 1_780_272_000.0


def messages(em):
    return [m for _, m in em.sorted_lines()]


def test_one_invocation_writes_start_app_end_report(emulator):
    emulator.invoke(T0, POST)
    lines = messages(emulator)
    assert lines[0].startswith("START RequestId: ")
    assert lines[1].startswith("[INFO]\t")
    assert lines[2].startswith("END RequestId: ")
    assert lines[3].startswith("REPORT RequestId: ")
    rid = re.search(r"RequestId: (\S+)", lines[0]).group(1)
    assert all(rid in line for line in lines)


def test_first_call_is_cold_then_warm(emulator):
    first = emulator.invoke(T0, HEALTH)
    second = emulator.invoke(T0 + 5, HEALTH)
    assert first["cold"] and not second["cold"]
    reports = [m for m in messages(emulator) if m.startswith("REPORT")]
    assert "Init Duration" in reports[0]
    assert "Init Duration" not in reports[1]


def test_idle_environment_is_reclaimed(emulator):
    emulator.invoke(T0, HEALTH)
    later = emulator.invoke(T0 + 2000, HEALTH)  # idle longer than 900 s
    assert later["cold"]


def test_concurrency_limit_throttles(emulator):
    emulator.runtime_cfg["reserved_concurrency"] = 1
    emulator.invoke(T0, HEALTH)  # cold start keeps the only environment busy
    rec = emulator.invoke(T0 + 0.01, HEALTH)
    assert rec["throttled"] and rec["status"] == 429
    assert len([m for m in messages(emulator) if m.startswith("START")]) == 1


def test_hang_becomes_a_task_timeout(emulator, fault_cfg):
    fault_cfg["dependency_timeout"].update(p_hang=1.0)
    emulator.set_fault("dependency_timeout")
    rec = emulator.invoke(T0, POST)
    assert rec["timeout"] and rec["error"]
    lines = messages(emulator)
    assert any("Task timed out after 3.00 seconds" in m for m in lines)
    report = [m for m in lines if m.startswith("REPORT")][0]
    assert "Duration: 3000.00 ms" in report and "Status: timeout" in report
    assert not any(m.startswith("[INFO]") for m in lines)  # killed before it could log
    assert emulator.invoke(T0 + 10, HEALTH)["cold"]  # environment was thrown away


def test_memory_exhaustion_kills_the_process(emulator, fault_cfg):
    fault_cfg["resource_exhaustion"].update(ws_mean_mb=400, ws_sd_mb=1)
    emulator.set_fault("resource_exhaustion")
    rec = emulator.invoke(T0, POST)
    assert rec["killed"] and rec["status"] == 502
    lines = messages(emulator)
    assert any("Runtime exited with error: signal: killed" in m for m in lines)
    assert "Runtime.ExitError" in lines
    report = [m for m in lines if m.startswith("REPORT")][0]
    assert "Memory Size: 128 MB" in report and "Max Memory Used: 128 MB" in report


def test_metrics_record_every_request(emulator):
    for i in range(5):
        emulator.invoke(T0 + i, POST)
    assert len(emulator.metrics) == 5
    assert {m["status"] for m in emulator.metrics} == {201}


def test_fault_is_cleared(emulator):
    emulator.set_fault("config_error")
    assert emulator.invoke(T0, POST)["status"] == 500
    emulator.set_fault(None)
    assert emulator.invoke(T0 + 1, POST)["status"] == 201
