from __future__ import annotations

import math
from dataclasses import dataclass

from app.services.ml_pipeline.types import FeatureRow, PredictionDecision


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, x))))


@dataclass(slots=True)
class LinearBaselineModel:
    weights: dict[str, float]
    bias: float = 0.0

    def predict_proba_up(self, row: FeatureRow) -> float:
        z = self.bias
        for key, value in row.features.items():
            z += self.weights.get(key, 0.0) * value
        return _sigmoid(z)


@dataclass(slots=True)
class TreeHeuristicModel:
    def predict_proba_up(self, row: FeatureRow) -> float:
        score = 0.0
        f = row.features
        if f.get("sma5_sma20_ratio", 1.0) > 1.0:
            score += 0.8
        if f.get("momentum_5d", 0.0) > 0:
            score += 0.6
        if f.get("volatility_20", 0.0) > 0.05:
            score -= 0.8
        if f.get("event_sentiment", 0.0) > 0:
            score += 0.3
        return _sigmoid(score)


@dataclass(slots=True)
class SequenceMomentumModel:
    def predict_proba_up(self, row: FeatureRow) -> float:
        f = row.features
        seq_score = (1.5 * f.get("momentum_1d", 0.0)) + (1.1 * f.get("momentum_5d", 0.0))
        seq_score += 0.4 * f.get("sma20_sma60_ratio", 1.0)
        seq_score -= 2.0 * f.get("volatility_20", 0.0)
        return _sigmoid(seq_score)


@dataclass(slots=True)
class EnsemblePredictor:
    linear: LinearBaselineModel
    tree: TreeHeuristicModel
    sequence: SequenceMomentumModel
    abstain_confidence_threshold: float = 0.55
    calibration_temperature: float = 1.2

    def _calibrate(self, p: float) -> float:
        p = min(1 - 1e-6, max(1e-6, p))
        logit = math.log(p / (1 - p))
        return _sigmoid(logit / self.calibration_temperature)

    def predict(self, row: FeatureRow) -> PredictionDecision:
        p_linear = self.linear.predict_proba_up(row)
        p_tree = self.tree.predict_proba_up(row)
        p_sequence = self.sequence.predict_proba_up(row)
        p_raw = (0.4 * p_linear) + (0.3 * p_tree) + (0.3 * p_sequence)
        p_calibrated = self._calibrate(p_raw)

        confidence = max(p_calibrated, 1 - p_calibrated)
        abstained = confidence < self.abstain_confidence_threshold
        direction = "ABSTAIN" if abstained else ("UP" if p_calibrated >= 0.5 else "DOWN")

        range_width = 0.02 + min(0.05, row.features.get("volatility_20", 0.0) * 2)
        interval_low = row.close * (1 - range_width)
        interval_high = row.close * (1 + range_width)

        explanation: dict[str, float] = {}
        for key, value in row.features.items():
            contribution = abs(self.linear.weights.get(key, 0.0) * value)
            if contribution > 0:
                explanation[key] = round(contribution, 6)

        return PredictionDecision(
            direction=direction,
            probability_up_raw=round(p_raw, 6),
            probability_up_calibrated=round(p_calibrated, 6),
            confidence=round(confidence, 6),
            abstained=abstained,
            interval_low=round(interval_low, 6),
            interval_high=round(interval_high, 6),
            regime=row.regime,
            explanation=explanation,
        )


def build_default_ensemble() -> EnsemblePredictor:
    return EnsemblePredictor(
        linear=LinearBaselineModel(
            weights={
                "sma5_sma20_ratio": 0.9,
                "sma20_sma60_ratio": 0.8,
                "momentum_1d": 1.6,
                "momentum_5d": 1.2,
                "volatility_20": -2.8,
                "volume_pressure": 0.4,
                "market_return": 0.7,
                "sector_return": 0.6,
                "event_sentiment": 0.9,
            },
            bias=-0.2,
        ),
        tree=TreeHeuristicModel(),
        sequence=SequenceMomentumModel(),
    )
