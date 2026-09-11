"""One-shot init benchmark for a built Python package.

    python -s -S scripts/bench/python_bench.py build/python-default payloads/fixed_payload.json

-s -S keeps the venv's site-packages off sys.path, so only the package folder
(and the standard library) can be imported - like the Lambda sandbox.
Prints one JSON line with epoch-microsecond timestamps; localbench.py does the maths.
"""
import json
import sys
import time

pkg, payload_path = sys.argv[1], sys.argv[2]
sys.path.insert(0, pkg)

import handler  # noqa: E402  (this import is the "init phase")

t_init = time.time_ns() // 1000
with open(payload_path, encoding="utf-8") as fh:
    event = json.load(fh)
out = handler.lambda_handler(event)
t_done = time.time_ns() // 1000
print(json.dumps({"t_init_us": t_init, "t_done_us": t_done,
                  "digest": out["digest"], "items_total": out["items_total"]}))
