from matching.matcher import match_logs


def test_loss_and_duplicate_and_latency():
    log = [
        {"msg_id": "a", "ts_log_ms": 0},
        {"msg_id": "b", "ts_log_ms": 10},
        {"msg_id": "c", "ts_log_ms": 20},
    ]
    delivered = [
        {"msg_id": "a", "ts_ingest_ms": 5, "delivery_id": "1"},
        {"msg_id": "a", "ts_ingest_ms": 15, "delivery_id": "2"},
        {"msg_id": "b", "ts_ingest_ms": 21, "delivery_id": "3"},
    ]
    m = match_logs(log, delivered)
    assert m.n_published == 3
    assert m.n_lost == 1
    assert m.lost_ids == ["c"]
    assert m.n_duplicate_ids == 1
    assert m.n_delivered_unique == 2
    assert m.n_delivery_copies == 3
    assert m.loss_rate == 1 / 3
    assert m.duplicate_id_rate == 1 / 3
    assert m.latency_mean_ms == (5 + 11) / 2


def test_empty_log():
    m = match_logs([], [])
    assert m.n_published == 0
    assert m.loss_rate == 0.0
