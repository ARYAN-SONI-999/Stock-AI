import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.market_data.factory import get_provider

router = APIRouter()


@router.websocket("/quotes/{symbol}")
async def quote_stream(websocket: WebSocket, symbol: str) -> None:
    await websocket.accept()
    provider = get_provider()

    try:
        while True:
            quote = await provider.get_quote(symbol.upper())
            await websocket.send_json({
                "symbol": quote.symbol,
                "exchange": quote.exchange,
                "price": float(quote.price) if quote.price is not None else None,
                "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
                "delayed": quote.delayed,
                "message": quote.message,
                "source": quote.source,
            })
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        return
