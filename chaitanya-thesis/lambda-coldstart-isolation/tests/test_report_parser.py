"""Isolation gate: the parser must separate REPORT lines with and without Init Duration."""
import base64

from coldstart.report_parser import parse_log_text, parse_report

COLD = ("REPORT RequestId: 3f5a2c1e-8b7d-4e2a-9f1c-0a1b2c3d4e5f\tDuration: 12.34 ms\t"
        "Billed Duration: 13 ms\tMemory Size: 512 MB\tMax Memory Used: 71 MB\tInit Duration: 245.67 ms\t")
WARM = ("REPORT RequestId: 9e8d7c6b-5a4f-4e3d-8c2b-1a0f9e8d7c6b\tDuration: 3.01 ms\t"
        "Billed Duration: 4 ms\tMemory Size: 512 MB\tMax Memory Used: 72 MB\t")
XRAY = ("REPORT RequestId: 11111111-2222-4333-8444-555555555555\tDuration: 101.50 ms\t"
        "Billed Duration: 102 ms\tMemory Size: 128 MB\tMax Memory Used: 90 MB\tInit Duration: 512.00 ms\t\n"
        "XRAY TraceId: 1-66a1b2c3-0123456789abcdef01234567\tSegmentId: 0123456789abcdef\tSampled: true\t")


def test_cold_line_has_init():
    r = parse_report(COLD)
    assert r is not None and r.cold
    assert r.init_ms == 245.67
    assert r.duration_ms == 12.34 and r.billed_ms == 13
    assert r.memory_mb == 512 and r.max_memory_used_mb == 71
    assert r.request_id == "3f5a2c1e-8b7d-4e2a-9f1c-0a1b2c3d4e5f"


def test_warm_line_has_no_init():
    r = parse_report(WARM)
    assert r is not None and not r.cold
    assert r.init_ms is None
    assert r.duration_ms == 3.01


def test_xray_suffix_does_not_break_parsing():
    r = parse_report(XRAY)
    assert r.cold and r.init_ms == 512.0 and r.memory_mb == 128


def test_space_separated_line_from_console_copy():
    line = ("REPORT RequestId: abcd-ef01 Duration: 1.00 ms Billed Duration: 1 ms "
            "Memory Size: 128 MB Max Memory Used: 40 MB")
    r = parse_report(line)
    assert r is not None and not r.cold and r.billed_ms == 1


def test_non_report_lines_are_ignored():
    assert parse_report("START RequestId: abc Version: $LATEST") is None
    assert parse_report("END RequestId: abc") is None
    assert parse_report("") is None
    assert parse_report("REPORT RequestId: abc Duration: garbage") is None


def test_log_text_with_mixed_lines():
    text = "\n".join(["START RequestId: x Version: $LATEST", "some print output", "END RequestId: x",
                      COLD, WARM, XRAY])
    reps = parse_log_text(text)
    assert [r.cold for r in reps] == [True, False, True]


def test_tail_log_result_roundtrip():
    # boto3 invoke(LogType="Tail") returns the last 4 KB of the log base64-encoded
    tail = base64.b64encode(("START RequestId: y\n" + WARM + "\n").encode()).decode()
    reps = parse_log_text(base64.b64decode(tail).decode())
    assert len(reps) == 1 and not reps[0].cold


def test_to_dict_carries_cold_flag():
    d = parse_report(COLD).to_dict()
    assert d["cold"] is True and d["init_ms"] == 245.67
    d = parse_report(WARM).to_dict()
    assert d["cold"] is False and d["init_ms"] is None
