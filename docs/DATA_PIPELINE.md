# DATA PIPELINE

Data ingestion uses a provider abstraction (`MarketDataProvider`) and must:
- enforce retry/rate-limit aware fetching,
- deduplicate candles,
- normalize timestamps to IST presentation,
- mark stale or unavailable data explicitly.
