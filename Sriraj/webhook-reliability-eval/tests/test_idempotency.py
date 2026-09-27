from idempotency.store import InMemoryIdempotencyStore, idempotency_key


def test_key_stable():
    a = idempotency_key("src", "evt-1", b"{}")
    b = idempotency_key("src", "evt-1", b"{}")
    assert a == b
    assert a != idempotency_key("src", "evt-2", b"{}")


def test_claim_suppresses_duplicate():
    store = InMemoryIdempotencyStore()
    c1 = store.claim("k1")
    c2 = store.claim("k1")
    assert c1.is_new and not c2.is_new
    store.complete("k1")
    assert store.get("k1") == "COMPLETE"
