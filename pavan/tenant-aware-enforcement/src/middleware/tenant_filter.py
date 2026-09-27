"""Application middleware: extract tenant from JWT and force query filters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from auth.jwt_tokens import TokenClaims, verify_token


class AuthError(Exception):
    pass


class CrossTenantDenied(Exception):
    pass


@dataclass
class RequestContext:
    claims: TokenClaims
    path: str = "/"
    method: str = "GET"


def authenticate(authorization_header: str | None, *, secret: str) -> RequestContext:
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthError("missing_bearer")
    token = authorization_header[7:].strip()
    try:
        claims = verify_token(token, secret=secret)
    except Exception as exc:  # noqa: BLE001 — map all JWT failures
        raise AuthError(f"invalid_token:{exc}") from exc
    return RequestContext(claims=claims)


def enforce_tenant_match(ctx: RequestContext, resource_tenant_id: str) -> None:
    """Deny if resource tenant ≠ JWT tenant (unless role=platform_admin)."""
    if ctx.claims.role == "platform_admin":
        return
    if ctx.claims.tenant_id != resource_tenant_id:
        raise CrossTenantDenied(
            f"jwt_tenant={ctx.claims.tenant_id} resource_tenant={resource_tenant_id}"
        )


def filter_rows(rows: list[dict[str, Any]], tenant_id: str) -> list[dict[str, Any]]:
    """ORM-interceptor stand-in: keep only rows for tenant_id."""
    return [r for r in rows if r.get("tenant_id") == tenant_id]
