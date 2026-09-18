import base64
import json
import os
from collections import defaultdict, deque

import joblib
import numpy as np

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
_predictor = joblib.load(os.path.join(_MODEL_DIR, "workload_predictor.joblib"))

LOOKBACK_WINDOW = 10
TARGET_UTILIZATION = 0.70
POD_CAPACITY = 100.0


def _calculate_desired_pods(load):
    return int(np.clip(np.ceil(load / (POD_CAPACITY * TARGET_UTILIZATION)), 1, 100))


class _StabilityAwareState:
    """Same rule as src.models.scalers.StabilityAwareController, kept as a
    plain in-Lambda class (no cross-module import of the training-time
    package) so this handler has no dependency beyond joblib/numpy."""

    def __init__(self, initial_pods, smoothing=0.4, hysteresis_pods=1, cooldown_steps=2):
        self.smoothing = smoothing
        self.hysteresis_pods = hysteresis_pods
        self.cooldown_steps = cooldown_steps
        self.current_pods = initial_pods
        self.smoothed_pred = None
        self.steps_since_last_scale = cooldown_steps

    def step(self, raw_pred):
        self.smoothed_pred = raw_pred if self.smoothed_pred is None else (
            self.smoothing * raw_pred + (1 - self.smoothing) * self.smoothed_pred
        )
        desired = _calculate_desired_pods(self.smoothed_pred)
        self.steps_since_last_scale += 1
        if abs(desired - self.current_pods) > self.hysteresis_pods and self.steps_since_last_scale >= self.cooldown_steps:
            self.current_pods = desired
            self.steps_since_last_scale = 0
        return self.current_pods


# Per-node rolling workload history and controller state, kept in memory
# across warm Lambda invocations.
_node_history = defaultdict(lambda: deque(maxlen=LOOKBACK_WINDOW))
_node_controllers = {}


def lambda_handler(event, context):
    """Kinesis-triggered handler: buffers per-node workload telemetry and,
    once enough history exists, applies the trained predictor + the
    stability-aware controller to recommend a target pod count."""
    results = []

    for record in event["Records"]:
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        try:
            telemetry = json.loads(payload)
            node_id = telemetry.get("node_id", "unknown")
            load = float(telemetry.get("requests_per_sec", 0.0))

            _node_history[node_id].append(load)

            if len(_node_history[node_id]) < LOOKBACK_WINDOW:
                results.append({"node_id": node_id, "status": "WARMING_UP",
                                 "history_len": len(_node_history[node_id])})
                continue

            window = np.array(_node_history[node_id]).reshape(1, -1)
            raw_pred = _predictor.predict(window)[0] * 1.05

            if node_id not in _node_controllers:
                _node_controllers[node_id] = _StabilityAwareState(initial_pods=_calculate_desired_pods(load))
            desired_pods = _node_controllers[node_id].step(raw_pred)

            results.append({"node_id": node_id, "status": "OK",
                             "predicted_load_rps": round(float(raw_pred), 2),
                             "desired_pods": desired_pods})
        except Exception as e:
            print(f"Failed to process record: {e}")

    print(f"Processed {len(results)} records.")
    return {"statusCode": 200, "body": json.dumps({"message": "Success", "results": results})}
