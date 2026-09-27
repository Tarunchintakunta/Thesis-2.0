"""JWT tenant/role claims (HS256 for local; RS256-ready interface)."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import jwt

DEFAULT_ALG = "HS256"
DEFAULT_SECRET = "local-dev-only-change-me"  # never a real AWS secret


@dataclass(frozen=True)
class TokenClaims:
    sub: str
    tenant_id: str
    role: str
    exp: int
    iat: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "sub": self.sub,
            "tenant_id": self.tenant_id,
            "role": self.role,
            "exp": self.exp,
            "iat": self.iat,
        }


def issue_token(
    *,
    sub: str,
    tenant_id: str,
    role: str = "member",
    ttl_s: int = 900,
    secret: str = DEFAULT_SECRET,
    now: int | None = None,
) -> str:
    ts = int(now if now is not None else time.time())
    payload = {
        "sub": sub,
        "tenant_id": tenant_id,
        "role": role,
        "iat": ts,
        "exp": ts + ttl_s,
    }
    return jwt.encode(payload, secret, algorithm=DEFAULT_ALG)


def verify_token(token: str, *, secret: str = DEFAULT_SECRET) -> TokenClaims:
    data = jwt.decode(token, secret, algorithms=[DEFAULT_ALG])
    if "tenant_id" not in data or "sub" not in data:
        raise jwt.InvalidTokenError("missing tenant_id/sub")
    return TokenClaims(
        sub=str(data["sub"]),
        tenant_id=str(data["tenant_id"]),
        role=str(data.get("role", "member")),
        exp=int(data["exp"]),
        iat=int(data["iat"]),
    )
