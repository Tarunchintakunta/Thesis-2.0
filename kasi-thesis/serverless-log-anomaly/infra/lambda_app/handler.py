"""Orders API - the sample serverless application whose logs are studied.

API Gateway (HTTP API) -> this Lambda (Python) -> DynamoDB table (TABLE_NAME).

Routes: POST /orders, GET /orders/{id}, GET /orders, GET /health.

Each invocation writes exactly one structured JSON log line (CloudWatch
compatible): route, status, latency_ms, cold_start, error_type, memory_mb,
downstream_ms (+ the error text when something failed). The Lambda runtime
adds the START / END / REPORT lines around it.

The same file is deployed to LocalStack/AWS (infra/lambda_app/template.yaml)
and imported by the local runtime emulator (src/logad/collect/runtime.py),
which swaps ``clock`` for a virtual clock and passes a fake table.
"""
import json
import logging
import os
import time
import uuid

from botocore.exceptions import ClientError, ConnectTimeoutError, ReadTimeoutError

LOG = logging.getLogger("orders")
LOG.setLevel(logging.INFO)

_COLD_START = True  # module state lives as long as the execution environment
_TABLE = None
clock = time.perf_counter  # replaced by the emulator's virtual clock


def get_table():
    global _TABLE
    if _TABLE is None:
        import boto3
        from botocore.config import Config

        cfg = Config(connect_timeout=1, read_timeout=2, retries={"max_attempts": 1})
        endpoint = os.environ.get("AWS_ENDPOINT_URL") or None  # LocalStack
        _TABLE = boto3.resource("dynamodb", config=cfg, endpoint_url=endpoint).Table(os.environ["TABLE_NAME"])
    return _TABLE


def _chaos_delay():
    """Live-mode dependency_timeout injection: a slow proxy in front of DynamoDB."""
    delay_ms = int(os.environ.get("DOWNSTREAM_DELAY_MS", "0") or 0)
    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)


def lambda_handler(event, context, table=None):
    global _COLD_START
    cold, _COLD_START = _COLD_START, False
    route = event.get("routeKey", "GET /health")
    t0 = clock()
    d0 = t0
    downstream = 0.0
    status, error_type, message = 200, None, None

    try:
        tbl = table
        if tbl is None and route != "GET /health":
            tbl = get_table()
        if route == "POST /orders":
            body = json.loads(event.get("body") or "{}")
            item = {
                "order_id": body.get("order_id") or str(uuid.uuid4()),
                "items": int(body.get("items", 1)),
                "amount_cents": int(body.get("amount_cents", 100)),
            }
            _chaos_delay()
            d0 = clock()
            tbl.put_item(Item=item)
            downstream += clock() - d0
            status = 201
        elif route == "GET /orders/{id}":
            order_id = (event.get("pathParameters") or {}).get("id", "")
            _chaos_delay()
            d0 = clock()
            resp = tbl.get_item(Key={"order_id": order_id})
            downstream += clock() - d0
            status = 200 if "Item" in resp else 404
        elif route == "GET /orders":
            _chaos_delay()
            d0 = clock()
            tbl.scan(Limit=20)
            downstream += clock() - d0
            status = 200
        elif route == "GET /health":
            status = 200
        else:
            status = 404
    except ClientError as exc:
        downstream += clock() - d0
        error_type = exc.response.get("Error", {}).get("Code", "ClientError")
        status = 500
        message = str(exc)
    except (ReadTimeoutError, ConnectTimeoutError) as exc:
        downstream += clock() - d0
        error_type = "DownstreamTimeout"
        status = 504
        message = str(exc)

    record = {
        "route": route,
        "status": status,
        "latency_ms": round((clock() - t0) * 1000.0, 2),
        "cold_start": cold,
        "error_type": error_type,
        "memory_mb": int(getattr(context, "memory_limit_in_mb", 0) or 0),
        "downstream_ms": round(downstream * 1000.0, 2),
    }
    if message:
        record["error"] = message
    LOG.log(logging.ERROR if error_type else logging.INFO, json.dumps(record))
    return {"statusCode": status, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"status": status})}
