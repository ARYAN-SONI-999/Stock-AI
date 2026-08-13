from __future__ import annotations

from statistics import mean

from app.services.ml_pipeline.types import CandlePoint, FeatureRow


EPS = 1e-9


def _sma(values: list[float], window: int) -> float:
    if not values:
        return 0.0
    recent = values[-window:] if len(values) >= window else values
    return mean(recent)


def _returns(values: list[float]) -> list[float]:
    out: list[float] = []
    for i in range(1, len(values)):
        if values[i - 1] != 0:
            out.append((values[i] / values[i - 1]) - 1.0)
    return out


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return (sum((v - m) ** 2 for v in values) / (len(values) - 1)) ** 0.5


def _last_event_sentiment(events: list[dict], ts) -> float:
    eligible = [e for e in events if e.get("timestamp") and e["timestamp"] <= ts]
    if not eligible:
        return 0.0
    return float(eligible[-1].get("sentiment", 0.0))


def build_feature_rows(
    candles: list[CandlePoint],
    *,
    symbol: str,
    sector: str | None = None,
    market_context: dict | None = None,
    events: list[dict] | None = None,
) -> list[FeatureRow]:
    market_context = market_context or {}
    events = events or []

    closes = [c.close for c in candles]
    volumes = [float(c.volume or 0.0) for c in candles]
    rows: list[FeatureRow] = []

    for i in range(30, len(candles)):
        hist_close = closes[: i + 1]
        hist_volume = volumes[: i + 1]
        rets = _returns(hist_close[-21:])

        sma_5 = _sma(hist_close, 5)
        sma_20 = _sma(hist_close, 20)
        sma_60 = _sma(hist_close, 60)
        vol_20 = _stdev(rets)
        avg_vol_20 = _sma(hist_volume, 20)

        close_now = hist_close[-1]
        momentum_1d = ((hist_close[-1] / hist_close[-2]) - 1.0) if len(hist_close) > 1 and hist_close[-2] != 0 else 0.0
        momentum_5d = ((hist_close[-1] / hist_close[-6]) - 1.0) if len(hist_close) > 5 and hist_close[-6] != 0 else 0.0

        regime = "high_vol" if vol_20 > 0.03 else "normal_vol"
        market_return = float(market_context.get("index_return", 0.0))
        sector_return = float(market_context.get("sector_return", 0.0))
        sentiment = _last_event_sentiment(events, candles[i].timestamp)

        rows.append(
            FeatureRow(
                timestamp=candles[i].timestamp,
                close=close_now,
                symbol=symbol,
                sector=sector,
                regime=regime,
                features={
                    "sma5_sma20_ratio": sma_5 / (sma_20 + EPS),
                    "sma20_sma60_ratio": sma_20 / (sma_60 + EPS),
                    "momentum_1d": momentum_1d,
                    "momentum_5d": momentum_5d,
                    "volatility_20": vol_20,
                    "volume_pressure": (hist_volume[-1] / (avg_vol_20 + EPS)) - 1.0,
                    "market_return": market_return,
                    "sector_return": sector_return,
                    "event_sentiment": sentiment,
                },
            )
        )

    return rows
