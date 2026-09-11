"""Cold-start study workload - Python, DEFAULT package (unpruned dependencies).

Identical work to functions/python/optimised/handler.py. The only difference is
the package: heavy libraries the function never uses are bundled and imported
at module level - the common "import everything at the top" pattern. That is
exactly what the init phase has to pay for on a cold start.
"""
import hashlib

# unused on purpose (see requirements.txt) - do not remove, this IS the treatment
import boto3  # noqa: F401  (bundled copy, bigger than relying on the runtime's)
import requests  # noqa: F401
import sympy  # noqa: F401


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
