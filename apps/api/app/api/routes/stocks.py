from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.core.rate_limit import enforce_rate_limit
from app.schemas.stocks import HistoricalResponse, QuoteResponse, TechnicalResponse
from app.services.cache import cache_client
from app.services.market_data.factory import get_provider
from app.services.technical import compute_basic_technicals, score_technical_signals

router = APIRouter()


@router.get("/")
async def search_stocks(
    request: Request,
    query: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    _rate_limit: None = Depends(enforce_rate_limit),
) -> dict:
    return {
        "query": query,
        "limit": limit,
        "results": [],
        "message": "Stock universe endpoint scaffolded. Ingest instrument master data to populate searchable universe.",
    }


@router.get("/{symbol}")
async def stock_details(symbol: str, exchange: str = "NSE") -> dict:
    return {
        "symbol": symbol.upper(),
        "exchange": exchange,
        "status": "pending_instrument_master",
        "message": "Instrument details are available after instrument master ingestion.",
    }


@router.get("/{symbol}/quote", response_model=QuoteResponse)
async def stock_quote(
    request: Request,
    symbol: str,
    exchange: str = "NSE",
    _rate_limit: None = Depends(enforce_rate_limit),
) -> QuoteResponse:
    cache_key = f"quote:{exchange}:{symbol.upper()}"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return QuoteResponse(**cached)

    provider = get_provider()
    quote = await provider.get_quote(symbol.upper(), exchange=exchange)
    response = QuoteResponse(**quote.__dict__)
    await cache_client.set_json(cache_key, response.model_dump(mode="json"), ttl_seconds=10)
    return response


@router.get("/{symbol}/history", response_model=HistoricalResponse)
async def stock_history(
    request: Request,
    symbol: str,
    exchange: str = "NSE",
    interval: str = Query(default="1day"),
    outputsize: int = Query(default=100, ge=10, le=5000),
    _rate_limit: None = Depends(enforce_rate_limit),
) -> HistoricalResponse:
    cache_key = f"history:{exchange}:{symbol.upper()}:{interval}:{outputsize}"
    cached = await cache_client.get_json(cache_key)
    if cached:
        return HistoricalResponse(**cached)

    provider = get_provider()
    candles, delayed, message = await provider.get_history(
        symbol.upper(),
        exchange=exchange,
        interval=interval,
        outputsize=outputsize,
    )

    response = HistoricalResponse(
        symbol=symbol.upper(),
        interval=interval,
        source=provider.name,
        delayed=delayed,
        candles=[
            {
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
            }
            for candle in candles
        ],
        message=message,
    )
    await cache_client.set_json(cache_key, response.model_dump(mode="json"), ttl_seconds=60)
    return response


@router.get("/{symbol}/technical", response_model=TechnicalResponse)
async def stock_technical(
    request: Request,
    symbol: str,
    exchange: str = "NSE",
    interval: str = Query(default="1day"),
    outputsize: int = Query(default=200, ge=30, le=5000),
    _rate_limit: None = Depends(enforce_rate_limit),
) -> TechnicalResponse:
    provider = get_provider()
    candles, delayed, message = await provider.get_history(
        symbol.upper(),
        exchange=exchange,
        interval=interval,
        outputsize=outputsize,
    )

    if delayed and not candles:
        return TechnicalResponse(
            symbol=symbol.upper(),
            timestamp=datetime.now(timezone.utc),
            metrics={},
            score_breakdown={"trend": 0, "momentum": 0, "volatility": 0, "volume": 0},
            total_score=0,
            delayed=True,
            message=message,
        )

    if not candles:
        raise HTTPException(status_code=404, detail="No historical candles found for requested symbol/timeframe")

    metrics = compute_basic_technicals(candles)
    latest_price = float(candles[-1].close) if candles else None
    breakdown, total_score = score_technical_signals(metrics, latest_price)

    return TechnicalResponse(
        symbol=symbol.upper(),
        timestamp=candles[-1].timestamp,
        metrics=metrics,
        score_breakdown=breakdown,
        total_score=total_score,
        delayed=False,
        message=None,
    )
