# API

Base path: `/api/v1`

## Implemented endpoints
- `GET /health/`
- `GET /stocks/`
- `GET /stocks/{symbol}`
- `GET /stocks/{symbol}/quote`
- `GET /stocks/{symbol}/history`
- `GET /stocks/{symbol}/technical`

All market data endpoints explicitly return delayed/unavailable messages when provider data is not available.
