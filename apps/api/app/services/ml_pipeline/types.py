from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class CandlePoint:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None


@dataclass(slots=True)
class DataQualityReport:
    input_rows: int
    output_rows: int
    dropped_rows: int
    outlier_rows: int
    freshness_seconds: float | None
    source_reliability: float
    corporate_action_factor: float


@dataclass(slots=True)
class FeatureRow:
    timestamp: datetime
    close: float
    features: dict[str, float]
    regime: str
    symbol: str
    sector: str | None = None


@dataclass(slots=True)
class PredictionDecision:
    direction: str
    probability_up_raw: float
    probability_up_calibrated: float
    confidence: float
    abstained: bool
    interval_low: float
    interval_high: float
    regime: str
    explanation: dict[str, float] = field(default_factory=dict)
