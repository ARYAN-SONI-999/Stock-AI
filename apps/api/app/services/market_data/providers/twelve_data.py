from datetime import datetime
from decimal import Decimal

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.market_data.base import Candle, MarketDataProvider, Quote


class TwelveDataProvider(MarketDataProvider):
    name = "twelve_data"
    base_url = "https://api.twelvedata.com"

    def __init__(self) -> None:
        self.api_key = settings.twelve_data_api_key

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
    async def _request(self, endpoint: str, params: dict[str, str | int]) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Quote:
        if not self.api_key:
            return Quote(
                symbol=symbol,
                exchange=exchange,
                price=None,
                open=None,
                high=None,
                low=None,
                close=None,
                volume=None,
                timestamp=None,
                delayed=True,
                source=self.name,
                message="Data delayed / unavailable: market data provider key is missing.",
            )

        payload = await self._request(
            "quote",
            {"symbol": f"{symbol}:{exchange}", "apikey": self.api_key},
        )

        if payload.get("status") == "error":
            return Quote(
                symbol=symbol,
                exchange=exchange,
                price=None,
                open=None,
                high=None,
                low=None,
                close=None,
                volume=None,
                timestamp=None,
                delayed=True,
                source=self.name,
                message=f"Data delayed / unavailable: {payload.get('message', 'provider error')}",
            )

        return Quote(
            symbol=symbol,
            exchange=exchange,
            price=Decimal(payload["close"]),
            open=Decimal(payload["open"]),
            high=Decimal(payload["high"]),
            low=Decimal(payload["low"]),
            close=Decimal(payload["close"]),
            volume=int(payload["volume"]) if payload.get("volume") else None,
            timestamp=datetime.fromisoformat(payload["datetime"]),
            delayed=False,
            source=self.name,
        )

    async def get_history(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: str = "1day",
        outputsize: int = 100,
    ) -> tuple[list[Candle], bool, str | None]:
        if not self.api_key:
            return [], True, "Data delayed / unavailable: market data provider key is missing."

        payload = await self._request(
            "time_series",
            {
                "symbol": f"{symbol}:{exchange}",
                "interval": interval,
                "outputsize": min(outputsize, 5000),
                "apikey": self.api_key,
            },
        )

        if payload.get("status") == "error":
            return [], True, f"Data delayed / unavailable: {payload.get('message', 'provider error')}"

        candles = [
            Candle(
                timestamp=datetime.fromisoformat(row["datetime"]),
                open=Decimal(row["open"]),
                high=Decimal(row["high"]),
                low=Decimal(row["low"]),
                close=Decimal(row["close"]),
                volume=int(row["volume"]) if row.get("volume") else None,
            )
            for row in payload.get("values", [])
        ]

        deduped = {
            candle.timestamp: candle
            for candle in candles
        }
        ordered = [deduped[key] for key in sorted(deduped.keys())]
        return ordered, False, None
