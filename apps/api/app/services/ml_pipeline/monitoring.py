from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DriftAlert:
    name: str
    score: float
    threshold: float
    triggered: bool


class PredictionMonitor:
    def __init__(self) -> None:
        self.predictions: list[dict] = []
        self.outcomes: list[dict] = []

    def log_prediction(self, payload: dict) -> None:
        self.predictions.append(payload)

    def log_outcome(self, payload: dict) -> None:
        self.outcomes.append(payload)

    def detect_feature_drift(self, baseline: list[float], recent: list[float], threshold: float = 0.2) -> DriftAlert:
        if not baseline or not recent:
            return DriftAlert(name="feature_drift", score=0.0, threshold=threshold, triggered=False)

        baseline_mean = sum(baseline) / len(baseline)
        recent_mean = sum(recent) / len(recent)
        denom = max(1e-9, abs(baseline_mean))
        score = abs(recent_mean - baseline_mean) / denom
        return DriftAlert(name="feature_drift", score=round(score, 6), threshold=threshold, triggered=score >= threshold)

    def performance_alerts(
        self,
        *,
        min_directional_accuracy: float = 0.53,
        max_mape: float = 0.03,
        current_directional_accuracy: float,
        current_mape: float,
    ) -> list[str]:
        alerts: list[str] = []
        if current_directional_accuracy < min_directional_accuracy:
            alerts.append("Directional accuracy below threshold")
        if current_mape > max_mape:
            alerts.append("MAPE above threshold")
        return alerts
