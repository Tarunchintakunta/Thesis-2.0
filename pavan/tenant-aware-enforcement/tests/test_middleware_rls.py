from auth.jwt_tokens import issue_token
from db.store import Record, TenantStore
from middleware.tenant_filter import CrossTenantDenied, authenticate, enforce_tenant_match, filter_rows


def test_middleware_blocks_cross_tenant():
    tok = issue_token(sub="u", tenant_id="A", secret="s")
    ctx = authenticate(f"Bearer {tok}", secret="s")
    try:
        enforce_tenant_match(ctx, "B")
        assert False
    except CrossTenantDenied:
        assert True


def test_rls_hides_other_tenant():
    store = TenantStore(rls_enabled=True)
    store.set_config("A")
    store.insert(Record(id="1", tenant_id="A", kind="doc", payload={}))
    store.set_config("B")
    store.insert(Record(id="2", tenant_id="B", kind="doc", payload={}))
    store.set_config("A")
    assert store.get("2") is None
    assert store.get("1") is not None
    assert len(store.list_for_session()) == 1


def test_filter_rows():
    rows = [{"tenant_id": "A"}, {"tenant_id": "B"}]
    assert filter_rows(rows, "A") == [{"tenant_id": "A"}]
