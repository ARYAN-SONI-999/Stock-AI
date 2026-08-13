from app.core.config import settings
from app.services.market_data.base import MarketDataProvider
from app.services.market_data.providers.twelve_data import TwelveDataProvider
from app.services.market_data.providers.unavailable import UnavailableProvider


def get_provider() -> MarketDataProvider:
    if settings.twelve_data_api_key:
        return TwelveDataProvider()
    return UnavailableProvider()
