from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Instrument(BaseModel):
    symbol: str
    exchange: str
    name: str
    isin: str | None = None
    sector: str | None = None


class QuoteResponse(BaseModel):
    symbol: str
    exchange: str
    price: Decimal | None
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal | None = None
    volume: int | None = None
    timestamp: datetime | None
    delayed: bool
    source: str
    message: str | None = None


class Candle(BaseModel):
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int | None = None


class HistoricalResponse(BaseModel):
    symbol: str
    interval: str
    source: str
    delayed: bool
    candles: list[Candle]
    message: str | None = None


class TechnicalResponse(BaseModel):
    symbol: str
    timestamp: datetime | None
    metrics: dict[str, float | None]
    score_breakdown: dict[str, int]
    total_score: int
    delayed: bool
    message: str | None = None
