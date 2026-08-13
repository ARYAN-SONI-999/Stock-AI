from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.stocks import router as stocks_router
from app.api.routes.ws import router as ws_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
api_router.include_router(ws_router, prefix="/ws", tags=["ws"])
