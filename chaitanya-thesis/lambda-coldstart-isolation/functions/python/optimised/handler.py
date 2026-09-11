"""Cold-start study workload - Python, OPTIMISED package (standard library only).

Same work in every runtime and variant:
  * iterated SHA-256: h = seed; repeat n times: h = sha256(h) (raw bytes); digest = hex(h)
  * a tiny JSON transform: count and sum the integer items
Warmer pings ({"warmer": true}) return straight away.
"""
import hashlib


def digest(seed: str, n: int) -> str:
    h = seed.encode("utf-8")
    for _ in range(n):
        h = hashlib.sha256(h).digest()
    return h.hex()


def lambda_handler(event, context=None):
    if event.get("warmer"):
        return {"ok": True, "warmer": True}
    n = int(event.get("iterations", 1000))
    items = [int(x) for x in event.get("items", [])]
    return {"ok": True, "digest": digest(str(event.get("seed", "thesis")), n), "n": n,
            "items": len(items), "items_total": sum(items)}
