# DEPLOYMENT

For local development:
1. Copy `.env.example` to `.env` and fill secrets.
2. Run `docker compose up --build`.

Services:
- web: Next.js app
- api: FastAPI app
- worker: Celery worker
- database: PostgreSQL/TimescaleDB
- redis: Redis
