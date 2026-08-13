from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Quote:
    symbol: str
    exchange: str
    price: Decimal | None
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal | None
    volume: int | None
    timestamp: datetime | None
    delayed: bool
    source: str
    message: str | None = None


@dataclass
class Candle:
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int | None


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Quote:
        raise NotImplementedError

    @abstractmethod
    async def get_history(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: str = "1day",
        outputsize: int = 100,
    ) -> tuple[list[Candle], bool, str | None]:
        raise NotImplementedError
