-- Initial schema for StockMind AI Phase 1-3 foundation
CREATE TABLE IF NOT EXISTS exchanges (
  id BIGSERIAL PRIMARY KEY,
  code VARCHAR(16) UNIQUE NOT NULL,
  name VARCHAR(128) NOT NULL,
  timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata'
);

CREATE TABLE IF NOT EXISTS sectors (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(128) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS instruments (
  id BIGSERIAL PRIMARY KEY,
  symbol VARCHAR(32) NOT NULL,
  name VARCHAR(255) NOT NULL,
  isin VARCHAR(32),
  exchange_id BIGINT NOT NULL REFERENCES exchanges(id),
  sector_id BIGINT REFERENCES sectors(id),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_symbol_exchange UNIQUE(symbol, exchange_id)
);

CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments(symbol);
CREATE INDEX IF NOT EXISTS idx_instruments_name ON instruments(name);
CREATE INDEX IF NOT EXISTS idx_instruments_isin ON instruments(isin);

CREATE TABLE IF NOT EXISTS ohlcv (
  id BIGSERIAL PRIMARY KEY,
  instrument_id BIGINT NOT NULL REFERENCES instruments(id),
  timeframe VARCHAR(16) NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  open NUMERIC(18,6) NOT NULL,
  high NUMERIC(18,6) NOT NULL,
  low NUMERIC(18,6) NOT NULL,
  close NUMERIC(18,6) NOT NULL,
  volume BIGINT,
  source VARCHAR(64) NOT NULL,
  CONSTRAINT uq_ohlcv_key UNIQUE(instrument_id, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_lookup ON ohlcv(instrument_id, timeframe, ts DESC);

CREATE TABLE IF NOT EXISTS model_versions (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  version VARCHAR(64) NOT NULL,
  training_start TIMESTAMPTZ NOT NULL,
  training_end TIMESTAMPTZ NOT NULL,
  feature_set_version VARCHAR(64) NOT NULL,
  artifact_uri TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_metrics (
  id BIGSERIAL PRIMARY KEY,
  model_version_id BIGINT NOT NULL REFERENCES model_versions(id),
  metric_name VARCHAR(64) NOT NULL,
  metric_value NUMERIC(18,8) NOT NULL,
  horizon VARCHAR(32) NOT NULL,
  regime VARCHAR(32),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS predictions (
  id BIGSERIAL PRIMARY KEY,
  instrument_id BIGINT NOT NULL REFERENCES instruments(id),
  horizon VARCHAR(32) NOT NULL,
  direction VARCHAR(16) NOT NULL,
  base_price NUMERIC(18,6) NOT NULL,
  lower_range NUMERIC(18,6) NOT NULL,
  upper_range NUMERIC(18,6) NOT NULL,
  confidence NUMERIC(8,6) NOT NULL,
  model_version VARCHAR(64) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS prediction_outcomes (
  id BIGSERIAL PRIMARY KEY,
  prediction_id BIGINT UNIQUE NOT NULL REFERENCES predictions(id),
  actual_price NUMERIC(18,6) NOT NULL,
  absolute_error NUMERIC(18,6) NOT NULL,
  directional_hit BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolios (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  name VARCHAR(128) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS portfolio_positions (
  id BIGSERIAL PRIMARY KEY,
  portfolio_id BIGINT NOT NULL REFERENCES portfolios(id),
  instrument_id BIGINT NOT NULL REFERENCES instruments(id),
  quantity NUMERIC(18,6) NOT NULL,
  average_price NUMERIC(18,6) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS watchlists (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  name VARCHAR(128) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS watchlist_items (
  id BIGSERIAL PRIMARY KEY,
  watchlist_id BIGINT NOT NULL REFERENCES watchlists(id),
  instrument_id BIGINT NOT NULL REFERENCES instruments(id),
  sort_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_watchlist_instrument UNIQUE(watchlist_id, instrument_id)
);

CREATE TABLE IF NOT EXISTS alerts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  instrument_id BIGINT NOT NULL REFERENCES instruments(id),
  alert_type VARCHAR(64) NOT NULL,
  condition_json TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
