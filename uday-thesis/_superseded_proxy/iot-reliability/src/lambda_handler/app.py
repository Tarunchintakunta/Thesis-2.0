import base64
import json
import os

import joblib
import numpy as np

DECISION_NAMES = {0: "KEEP_LOCAL", 1: "PARTIAL_OFFLOAD", 2: "FULL_OFFLOAD"}

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
_metadata = json.load(open(os.path.join(_MODEL_DIR, "metadata.json")))
FEATURES = _metadata["features"]
SITES = _metadata["sites"]

# Federated ensemble: one Random Forest per site, loaded once per warm
# Lambda container. No raw telemetry from any site is ever pooled -- only
# these already-trained, site-local models are combined at inference time.
_site_models = {site: joblib.load(os.path.join(_MODEL_DIR, f"{site}.joblib")) for site in SITES}


def _predict(record):
    x = np.array([[record.get(f, 0.0) for f in FEATURES]])
    probs = np.mean([m.predict_proba(x) for m in _site_models.values()], axis=0)
    decision = int(probs.argmax(axis=1)[0])
    return DECISION_NAMES[decision], probs[0].tolist()


def lambda_handler(event, context):
    """Kinesis-triggered handler: applies the federated ensemble decision
    model to each incoming QoS telemetry record and returns a traffic
    offload decision (Keep Local / Partial Offload / Full Offload)."""
    results = []

    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        try:
            telemetry = json.loads(payload)
            decision, probs = _predict(telemetry)
            results.append({
                "node_id": telemetry.get("node_id", "unknown"),
                "decision": decision,
                "probabilities": {DECISION_NAMES[i]: round(p, 4) for i, p in enumerate(probs)},
            })
        except Exception as e:
            print(f"Failed to process record: {e}")

    print(f"Processed {len(results)} records.")
    return {"statusCode": 200, "body": json.dumps({"message": "Success", "results": results})}
