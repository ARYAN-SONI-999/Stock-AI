from __future__ import annotations

from datetime import datetime, timezone
from statistics import median

from app.services.ml_pipeline.types import CandlePoint, DataQualityReport


def _is_valid(candle: CandlePoint) -> bool:
    return all(v >= 0 for v in (candle.open, candle.high, candle.low, candle.close)) and candle.high >= candle.low


def _clamp_outlier(value: float, lower: float, upper: float) -> float:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def clean_candles(
    candles: list[CandlePoint],
    *,
    split_factor: float = 1.0,
    dividend_adjustment: float = 0.0,
    source_reliability_hint: float = 0.9,
    now: datetime | None = None,
) -> tuple[list[CandlePoint], DataQualityReport]:
    if not candles:
        report = DataQualityReport(
            input_rows=0,
            output_rows=0,
            dropped_rows=0,
            outlier_rows=0,
            freshness_seconds=None,
            source_reliability=0.0,
            corporate_action_factor=1.0,
        )
        return [], report

    sanitized: list[CandlePoint] = [c for c in candles if _is_valid(c)]
    dropped_rows = len(candles) - len(sanitized)
    if not sanitized:
        report = DataQualityReport(
            input_rows=len(candles),
            output_rows=0,
            dropped_rows=dropped_rows,
            outlier_rows=0,
            freshness_seconds=None,
            source_reliability=max(0.0, min(1.0, source_reliability_hint * 0.5)),
            corporate_action_factor=1.0,
        )
        return [], report

    closes = [c.close for c in sanitized]
    mid = median(closes)
    spread = median([abs(c - mid) for c in closes]) or 1.0
    lower, upper = mid - 7.0 * spread, mid + 7.0 * spread

    adjusted_factor = split_factor if split_factor > 0 else 1.0
    outlier_rows = 0
    cleaned: list[CandlePoint] = []
    for candle in sanitized:
        close_adj = (candle.close / adjusted_factor) - dividend_adjustment
        open_adj = (candle.open / adjusted_factor) - dividend_adjustment
        high_adj = (candle.high / adjusted_factor) - dividend_adjustment
        low_adj = (candle.low / adjusted_factor) - dividend_adjustment

        clamped_close = _clamp_outlier(close_adj, lower, upper)
        if clamped_close != close_adj:
            outlier_rows += 1

        cleaned.append(
            CandlePoint(
                timestamp=candle.timestamp,
                open=_clamp_outlier(open_adj, lower, upper),
                high=_clamp_outlier(high_adj, lower, upper),
                low=_clamp_outlier(low_adj, lower, upper),
                close=clamped_close,
                volume=max(0.0, candle.volume) if candle.volume is not None else None,
            )
        )

    latest_ts = cleaned[-1].timestamp
    ref_now = now or datetime.now(timezone.utc)
    freshness_seconds = max(0.0, (ref_now - latest_ts).total_seconds())

    reliability = source_reliability_hint
    if dropped_rows:
        reliability -= min(0.4, dropped_rows / max(1, len(candles)))
    if outlier_rows:
        reliability -= min(0.3, outlier_rows / max(1, len(cleaned)))
    reliability = max(0.0, min(1.0, reliability))

    report = DataQualityReport(
        input_rows=len(candles),
        output_rows=len(cleaned),
        dropped_rows=dropped_rows,
        outlier_rows=outlier_rows,
        freshness_seconds=freshness_seconds,
        source_reliability=reliability,
        corporate_action_factor=adjusted_factor,
    )
    return cleaned, report
