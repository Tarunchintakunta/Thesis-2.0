"""In-memory + optional SQLite store with RLS-style tenant policies."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Record:
    id: str
    tenant_id: str
    kind: str
    payload: dict[str, Any]


@dataclass
class TenantStore:
    """Shared-schema store. When rls_enabled, every read/write requires tenant_id session GUC."""

    rls_enabled: bool = True
    _rows: dict[str, Record] = field(default_factory=dict)
    _session_tenant: str | None = None

    def set_config(self, tenant_id: str | None) -> None:
        """Analogous to SET LOCAL app.current_tenant = ..."""
        self._session_tenant = tenant_id

    def insert(self, rec: Record) -> None:
        if self.rls_enabled:
            if self._session_tenant is None:
                raise PermissionError("RLS: missing tenant context")
            if rec.tenant_id != self._session_tenant:
                raise PermissionError("RLS: cross-tenant insert denied")
        self._rows[rec.id] = rec

    def get(self, rec_id: str) -> Record | None:
        rec = self._rows.get(rec_id)
        if rec is None:
            return None
        if self.rls_enabled:
            if self._session_tenant is None:
                raise PermissionError("RLS: missing tenant context")
            if rec.tenant_id != self._session_tenant:
                return None  # RLS filters out — not found
        return rec

    def list_for_session(self) -> list[Record]:
        if self.rls_enabled and self._session_tenant is None:
            raise PermissionError("RLS: missing tenant context")
        if not self.rls_enabled:
            return list(self._rows.values())
        tid = self._session_tenant
        return [r for r in self._rows.values() if r.tenant_id == tid]

    def bypass_list_all_admin(self) -> list[Record]:
        """Superuser-style bypass — used only to seed / measure leakage in tests."""
        return list(self._rows.values())


def init_sqlite_rls(path: str = ":memory:") -> sqlite3.Connection:
    """Optional SQLite demo of tenant discriminator (Postgres RLS SQL lives in sql/)."""
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          kind TEXT NOT NULL,
          body TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant_id)"
    )
    conn.commit()
    return conn
