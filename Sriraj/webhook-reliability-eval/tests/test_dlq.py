from dlq.queue import InMemoryQueue


def test_redrive_to_dlq():
    dlq = InMemoryQueue("dlq")
    q = InMemoryQueue("main", max_receive_count=2, visibility_timeout_s=0, dlq=dlq)
    q.send({"event": {"event_id": "e1"}})
    m1 = q.receive(1)[0]
    assert q.fail(m1.message_id) == "retry"
    m2 = q.receive(1)[0]
    assert q.fail(m2.message_id) == "dlq"
    assert dlq.depth() == 1
    assert q.depth() == 0


def test_replay():
    dlq = InMemoryQueue("dlq")
    q = InMemoryQueue("main", max_receive_count=1, dlq=dlq)
    dlq.send({"event": {"event_id": "e2"}})
    n = q.replay_from_dlq()
    assert n == 1 and q.depth() == 1 and dlq.depth() == 0
