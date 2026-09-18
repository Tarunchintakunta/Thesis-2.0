import base64
import json
import os
from collections import defaultdict, deque

import torch

from src.models.mhsa_model import MHSAFused
from src.data.telemetry_simulator import METRIC_NAMES

LEVEL_NAMES = ["none", "L1", "L2"]

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
_metadata = json.load(open(os.path.join(_MODEL_DIR, "metadata.json")))
SEQ_LENGTH = _metadata["seq_length"]

_model = MHSAFused(seq_length=SEQ_LENGTH)
_model.load_state_dict(torch.load(os.path.join(_MODEL_DIR, "mhsa_fused.pt"), map_location="cpu"))
_model.eval()

# Per-node rolling history, kept in memory across warm Lambda invocations.
# A cold start (or a node not seen in `seq_length` steps) just means fewer
# predictions until enough history has accumulated -- there's no
# persistence layer here, which is a known simplification (see README).
_node_history = defaultdict(lambda: deque(maxlen=SEQ_LENGTH))


def _predict(history_window):
    with torch.no_grad():
        x = torch.FloatTensor([list(history_window)])  # (1, seq_length, 4)
        logits = _model(x)  # (1, 4, 3)
        preds = logits.argmax(dim=-1).squeeze(0).tolist()
    return {metric: LEVEL_NAMES[level] for metric, level in zip(METRIC_NAMES, preds)}


def lambda_handler(event, context):
    """Kinesis-triggered handler: buffers per-node telemetry into a rolling
    `seq_length`-step window and runs the trained MHSA-Fused model once
    enough history exists, predicting a violation level per metric."""
    predictions = []

    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        try:
            telemetry = json.loads(payload)
            node_id = telemetry.get("node_id", "unknown")

            metrics = [telemetry.get(m, 0.0) for m in METRIC_NAMES]
            _node_history[node_id].append(metrics)

            if len(_node_history[node_id]) < SEQ_LENGTH:
                predictions.append({"node_id": node_id, "status": "WARMING_UP",
                                     "history_len": len(_node_history[node_id])})
                continue

            result = _predict(_node_history[node_id])
            overall = "HEALTHY" if all(v == "none" for v in result.values()) else "RISK"
            predictions.append({"node_id": node_id, "status": overall, "predictions": result})
        except Exception as e:
            print(f"Failed to process record: {e}")

    print(f"Processed {len(predictions)} records.")
    return {"statusCode": 200, "body": json.dumps({"message": "Success", "results": predictions})}
