import base64
import json
import os
import re

import joblib

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
_ml_detector = joblib.load(os.path.join(_MODEL_DIR, "ml_detector.joblib"))

# Kept identical to src/models/detectors.RULE_PATTERNS -- duplicated here
# (rather than importing the training package) so the Lambda has no
# dependency beyond joblib/scikit-learn.
RULE_PATTERNS = [
    re.compile(r'mode\s*=\s*"0?777"'),
    re.compile(r'protocol\s*=\s*"http"'),
    re.compile(r'hash_algorithm\s*=\s*"(sha1|md5)"'),
    re.compile(r'ingress_cidr\s*=\s*"0\.0\.0\.0/0"'),
]
ML_THRESHOLD = 0.8


def _rule_based_flag(snippet):
    return any(p.search(snippet) for p in RULE_PATTERNS)


def _predict(snippet):
    rule_hit = _rule_based_flag(snippet)
    ml_prob = float(_ml_detector.predict_proba([snippet])[0])
    is_misconfigured = rule_hit or ml_prob > ML_THRESHOLD
    return is_misconfigured, rule_hit, ml_prob


def lambda_handler(event, context):
    """Kinesis-triggered handler: scans each incoming IaC snippet with the
    hybrid detector (comment-independent rule layer + high-confidence ML
    fallback) and reports whether it looks misconfigured."""
    results = []

    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        try:
            submission = json.loads(payload)
            snippet = submission.get("snippet", "")
            is_misconfigured, rule_hit, ml_prob = _predict(snippet)
            results.append({
                "resource_id": submission.get("resource_id", "unknown"),
                "misconfigured": is_misconfigured,
                "rule_triggered": rule_hit,
                "ml_confidence": round(ml_prob, 4),
            })
        except Exception as e:
            print(f"Failed to process record: {e}")

    print(f"Processed {len(results)} records.")
    return {"statusCode": 200, "body": json.dumps({"message": "Success", "results": results})}
