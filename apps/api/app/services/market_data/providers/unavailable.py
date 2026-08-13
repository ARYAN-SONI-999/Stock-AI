from app.services.market_data.base import MarketDataProvider, Quote


class UnavailableProvider(MarketDataProvider):
    name = "unavailable"

    async def get_quote(self, symbol: str, exchange: str = "NSE") -> Quote:
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
            message="Data delayed / unavailable.",
        )

    async def get_history(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: str = "1day",
        outputsize: int = 100,
    ) -> tuple[list, bool, str | None]:
        return [], True, "Data delayed / unavailable."
