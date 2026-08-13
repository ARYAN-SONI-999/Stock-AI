from statistics import mean

from app.services.market_data.base import Candle


def _safe_float(value: float | int | None) -> float | None:
    return float(value) if value is not None else None


def compute_basic_technicals(candles: list[Candle]) -> dict[str, float | None]:
    closes = [float(c.close) for c in candles]
    volumes = [float(c.volume) for c in candles if c.volume is not None]

    if not closes:
        return {
            "sma_20": None,
            "sma_50": None,
            "price_change_pct": None,
            "volatility_20": None,
            "avg_volume_20": None,
        }

    sma_20 = mean(closes[-20:]) if len(closes) >= 20 else mean(closes)
    sma_50 = mean(closes[-50:]) if len(closes) >= 50 else mean(closes)
    price_change_pct = ((closes[-1] / closes[-2]) - 1) * 100 if len(closes) > 1 else 0.0

    recent = closes[-20:] if len(closes) >= 20 else closes
    returns = []
    for idx in range(1, len(recent)):
        if recent[idx - 1] != 0:
            returns.append((recent[idx] / recent[idx - 1]) - 1)
    volatility = (sum((r - (sum(returns) / len(returns))) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0.0

    return {
        "sma_20": _safe_float(round(sma_20, 4)),
        "sma_50": _safe_float(round(sma_50, 4)),
        "price_change_pct": _safe_float(round(price_change_pct, 4)),
        "volatility_20": _safe_float(round(volatility, 6)),
        "avg_volume_20": _safe_float(round(mean(volumes[-20:]), 4)) if volumes else None,
    }


def score_technical_signals(metrics: dict[str, float | None], latest_price: float | None) -> tuple[dict[str, int], int]:
    score = {
        "trend": 0,
        "momentum": 0,
        "volatility": 0,
        "volume": 0,
    }

    sma20 = metrics.get("sma_20")
    sma50 = metrics.get("sma_50")
    delta = metrics.get("price_change_pct")
    vol = metrics.get("volatility_20")

    if latest_price is not None and sma20 is not None and latest_price > sma20:
        score["trend"] += 15
    if sma20 is not None and sma50 is not None and sma20 > sma50:
        score["trend"] += 10
    if delta is not None:
        score["momentum"] += 10 if delta > 0 else -10
    if vol is not None:
        score["volatility"] += 5 if vol < 0.03 else -5
    if metrics.get("avg_volume_20") is not None:
        score["volume"] += 5

    total = max(0, min(100, 50 + sum(score.values())))
    return score, total
