# StockMind AI

StockMind AI is an incremental, production-oriented Indian stock intelligence platform.

## Phase 1-3 Baseline Included
- Monorepo structure (`apps/web`, `apps/api`, `ml`, `docs`, `packages`)
- FastAPI backend foundation with stock endpoints
- Market data provider abstraction with explicit delayed/unavailable handling
- Initial normalized SQL schema and migration script
- Next.js frontend shell
- Docker Compose local stack (web/api/worker/postgres/redis)
- CI workflow skeleton for lint/test/build
- Baseline technical-analysis scoring endpoint scaffold

## Local Development
1. Copy `/home/runner/work/Stock-AI/Stock-AI/.env.example` to `.env` and configure secrets.
2. Start services:
   ```bash
   docker compose up --build
   ```
3. Web app: `http://localhost:3000`
4. API docs: `http://localhost:8000/docs`

## Safety Principles
- No fabricated market data.
- No guaranteed prediction claims.
- Historical performance and future uncertainty must always be separated.
