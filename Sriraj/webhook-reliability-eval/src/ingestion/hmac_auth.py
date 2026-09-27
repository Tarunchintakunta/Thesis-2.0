"""API Gateway–style HMAC-SHA256 webhook authentication."""
from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    reason: str = ""


def sign(secret: str, body: bytes, timestamp: str | None = None) -> str:
    """Return hex HMAC-SHA256 over optional timestamp + body (Stripe-like)."""
    ts = timestamp if timestamp is not None else str(int(time.time()))
    msg = f"{ts}.".encode("utf-8") + body
    return hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()


def verify(
    secret: str,
    body: bytes,
    signature: str,
    timestamp: str,
    *,
    max_skew_s: int = 300,
    now: float | None = None,
) -> AuthResult:
    """Verify HMAC-SHA256 signature and timestamp skew."""
    if not secret:
        return AuthResult(False, "missing_secret")
    if not signature or not timestamp:
        return AuthResult(False, "missing_headers")
    try:
        ts = int(timestamp)
    except ValueError:
        return AuthResult(False, "bad_timestamp")
    clock = now if now is not None else time.time()
    if abs(clock - ts) > max_skew_s:
        return AuthResult(False, "timestamp_skew")
    expected = sign(secret, body, timestamp)
    if not hmac.compare_digest(expected, signature):
        return AuthResult(False, "bad_signature")
    return AuthResult(True, "ok")
