from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.market_data.base import Candle, MarketDataProvider

IST = ZoneInfo("Asia/Kolkata")


def normalize_to_ist(candle: Candle) -> Candle:
    ts = candle.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=ZoneInfo("UTC"))
    return Candle(
        timestamp=ts.astimezone(IST),
        open=candle.open,
        high=candle.high,
        low=candle.low,
        close=candle.close,
        volume=candle.volume,
    )


async def fetch_normalized_history(
    provider: MarketDataProvider,
    symbol: str,
    exchange: str,
    interval: str,
    outputsize: int,
) -> tuple[list[Candle], bool, str | None]:
    candles, delayed, message = await provider.get_history(
        symbol=symbol,
        exchange=exchange,
        interval=interval,
        outputsize=outputsize,
    )

    deduped: dict[datetime, Candle] = {}
    for candle in candles:
        normalized = normalize_to_ist(candle)
        deduped[normalized.timestamp] = normalized

    ordered = [deduped[key] for key in sorted(deduped.keys())]
    return ordered, delayed, message
