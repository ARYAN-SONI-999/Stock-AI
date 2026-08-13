from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Exchange(Base):
    __tablename__ = "exchanges"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")


class Sector(Base):
    __tablename__ = "sectors"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)


class Instrument(Base, TimestampMixin):
    __tablename__ = "instruments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    isin: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id"), index=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sectors.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("symbol", "exchange_id", name="uq_symbol_exchange"),)


class Ohlcv(Base):
    __tablename__ = "ohlcv"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    timeframe: Mapped[str] = mapped_column(String(16), index=True)
    ts: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    open: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    high: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    low: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    close: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    source: Mapped[str] = mapped_column(String(64))

    __table_args__ = (UniqueConstraint("instrument_id", "timeframe", "ts", name="uq_ohlcv_key"),)


class Prediction(Base, TimestampMixin):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    horizon: Mapped[str] = mapped_column(String(32), index=True)
    direction: Mapped[str] = mapped_column(String(16))
    base_price: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    lower_range: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    upper_range: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    confidence: Mapped[Numeric] = mapped_column(Numeric(8, 6))
    model_version: Mapped[str] = mapped_column(String(64), index=True)


class PredictionOutcome(Base):
    __tablename__ = "prediction_outcomes"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"), unique=True, index=True)
    actual_price: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    absolute_error: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    directional_hit: Mapped[bool] = mapped_column(Boolean)


class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    version: Mapped[str] = mapped_column(String(64), index=True)
    training_start: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    training_end: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    feature_set_version: Mapped[str] = mapped_column(String(64))
    artifact_uri: Mapped[str] = mapped_column(Text)


class ModelMetric(Base, TimestampMixin):
    __tablename__ = "model_metrics"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"), index=True)
    metric_name: Mapped[str] = mapped_column(String(64), index=True)
    metric_value: Mapped[Numeric] = mapped_column(Numeric(18, 8))
    horizon: Mapped[str] = mapped_column(String(32), index=True)
    regime: Mapped[str | None] = mapped_column(String(32), nullable=True)


class Portfolio(Base, TimestampMixin):
    __tablename__ = "portfolios"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))


class PortfolioPosition(Base, TimestampMixin):
    __tablename__ = "portfolio_positions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"), index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    quantity: Mapped[Numeric] = mapped_column(Numeric(18, 6))
    average_price: Mapped[Numeric] = mapped_column(Numeric(18, 6))


class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlists"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))


class WatchlistItem(Base, TimestampMixin):
    __tablename__ = "watchlist_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    watchlist_id: Mapped[int] = mapped_column(ForeignKey("watchlists.id"), index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (UniqueConstraint("watchlist_id", "instrument_id", name="uq_watchlist_instrument"),)


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), index=True)
    alert_type: Mapped[str] = mapped_column(String(64), index=True)
    condition_json: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
