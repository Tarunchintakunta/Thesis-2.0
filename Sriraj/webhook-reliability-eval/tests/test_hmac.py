from ingestion.hmac_auth import sign, verify


def test_sign_verify_roundtrip():
    secret = "s3cret"
    body = b'{"event_id":"evt-1"}'
    ts = "1700000000"
    sig = sign(secret, body, ts)
    assert verify(secret, body, sig, ts, now=1700000000).ok


def test_bad_signature_rejected():
    secret = "s3cret"
    body = b"{}"
    ts = "1700000000"
    assert not verify(secret, body, "nope", ts, now=1700000000).ok


def test_skew_rejected():
    secret = "s3cret"
    body = b"{}"
    ts = "100"
    sig = sign(secret, body, ts)
    assert verify(secret, body, sig, ts, now=10_000, max_skew_s=60).reason == "timestamp_skew"
