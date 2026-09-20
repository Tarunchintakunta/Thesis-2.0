"""PROXY: MLPRegressor + NimbusGuard-framed EMA/hysteresis policies.

Binding CA2 predictor is LSTM (``src/models/lstm_predictor.py``); binding
baseline is Kubernetes HPA (``src/k8s/adaptive_engine.py``), not NimbusGuard.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor

from src.data.workload_simulator import calculate_desired_pods, POD_CAPACITY

LOOKBACK_WINDOW = 10
TARGET_UTILIZATION = 0.70


def train_predictor(workload, seed):
    """Lightweight feed-forward regressor predicting the next-step workload
    from the past LOOKBACK_WINDOW steps. Replaces the original TensorFlow
    model with scikit-learn's MLPRegressor -- same modelling idea (a small
    2-hidden-layer dense network), no heavy DL framework dependency."""
    X, y = [], []
    for i in range(len(workload) - LOOKBACK_WINDOW):
        X.append(workload[i:i + LOOKBACK_WINDOW])
        y.append(workload[i + LOOKBACK_WINDOW])
    X, y = np.array(X), np.array(y)

    model = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=2000, random_state=seed)
    model.fit(X, y)
    return model


def run_reactive_hpa(workload):
    """Standard Horizontal Pod Autoscaler: scales based on the current
    (already-observed) load only, with no foresight."""
    pods = []
    current_pods = calculate_desired_pods(workload[0], TARGET_UTILIZATION)
    for t in range(len(workload)):
        pods.append(current_pods)
        current_pods = calculate_desired_pods(workload[t], TARGET_UTILIZATION)
    return np.array(pods)


def run_aggressive_paks(workload, model):
    """Baseline reproduction: an unfiltered proactive scaler that acts
    immediately on every raw prediction, matching the trade-off NimbusGuard
    (Wanigasooriya & Ekanayake, IEEE ICOIN 2026) reports for its DQN+LSTM
    agent -- better SLA compliance than reactive HPA, but at the cost of a
    higher average replica count and roughly double the scaling events
    (more thrashing / over-provisioning)."""
    pods = []
    for t in range(LOOKBACK_WINDOW):
        pods.append(calculate_desired_pods(workload[t], TARGET_UTILIZATION))

    for t in range(LOOKBACK_WINDOW, len(workload)):
        history = workload[t - LOOKBACK_WINDOW:t].reshape(1, -1)
        predicted_load = model.predict(history)[0] * 1.05  # small safety buffer
        pods.append(calculate_desired_pods(predicted_load, TARGET_UTILIZATION))
    return np.array(pods)


class StabilityAwareController:
    """Improvement: targets the exact trade-off NimbusGuard's own Discussion
    section names -- proactive scaling that is 'the most agile and least
    stable system' -- without giving up the foresight that makes it beat
    reactive HPA on SLA violations in the first place.

    Two changes on top of the aggressive policy:
      - exponential smoothing of the raw next-step predictions, so a single
        noisy prediction doesn't trigger a scaling action on its own.
      - a hysteresis + cooldown rule: only act on a smoothed prediction if
        it implies a pod count that differs from the current one, and at
        least `cooldown_steps` have passed since the last scaling action
        (this is the same "expanding the action space" / stability idea
        NimbusGuard's own future-work section gestures at, implemented as
        a simple rule rather than a second RL agent).

    Kept as a small stateful object (not a pure function) so the exact same
    logic can drive both the batch simulation, one step at a time, and a
    Lambda handler tracking state per node across warm invocations.
    """

    def __init__(self, initial_pods, smoothing=0.4, hysteresis_pods=1, cooldown_steps=2):
        self.smoothing = smoothing
        self.hysteresis_pods = hysteresis_pods
        self.cooldown_steps = cooldown_steps
        self.current_pods = initial_pods
        self.smoothed_pred = None
        self.steps_since_last_scale = cooldown_steps  # allow scaling immediately if needed

    def step(self, raw_pred):
        self.smoothed_pred = raw_pred if self.smoothed_pred is None else (
            self.smoothing * raw_pred + (1 - self.smoothing) * self.smoothed_pred
        )
        desired = calculate_desired_pods(self.smoothed_pred, TARGET_UTILIZATION)

        self.steps_since_last_scale += 1
        if abs(desired - self.current_pods) > self.hysteresis_pods and self.steps_since_last_scale >= self.cooldown_steps:
            self.current_pods = desired
            self.steps_since_last_scale = 0
        return self.current_pods


def run_stability_aware_paks(workload, model):
    pods = []
    for t in range(LOOKBACK_WINDOW):
        pods.append(calculate_desired_pods(workload[t], TARGET_UTILIZATION))

    controller = StabilityAwareController(initial_pods=pods[-1])
    for t in range(LOOKBACK_WINDOW, len(workload)):
        history = workload[t - LOOKBACK_WINDOW:t].reshape(1, -1)
        raw_pred = model.predict(history)[0] * 1.05
        pods.append(controller.step(raw_pred))
    return np.array(pods)
