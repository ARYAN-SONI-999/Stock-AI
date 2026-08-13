# ARCHITECTURE

StockMind AI is organized as a monorepo with `apps/web` (Next.js UI), `apps/api` (FastAPI backend), and `ml/` modules for training/evaluation/backtesting pipelines.

Phase 1-3 goals implemented in this baseline:
- Service-oriented split between UI, API, and background worker.
- Provider abstraction for market data with explicit unavailable/delayed handling.
- Initial normalized schema for instruments, ohlcv, predictions, and portfolio entities.
- Dockerized local environment for web, api, worker, PostgreSQL/TimescaleDB, Redis.
