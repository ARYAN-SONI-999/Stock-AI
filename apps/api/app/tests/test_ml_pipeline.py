from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.services.ml_pipeline import CandlePoint, build_walk_forward_splits, clean_candles


client = TestClient(app)


def test_prediction_endpoint_returns_guarded_payload_without_data() -> None:
    response = client.get("/api/v1/stocks/RELIANCE/prediction")
    assert response.status_code == 200
    payload = response.json()
    assert payload["direction"] == "ABSTAIN"
    assert payload["abstained"] is True
    assert "confidence" in payload


def test_data_quality_reports_freshness_and_reliability() -> None:
    now = datetime.now(timezone.utc)
    candles = [
        CandlePoint(timestamp=now - timedelta(days=2), open=100, high=102, low=99, close=101, volume=1000),
        CandlePoint(timestamp=now - timedelta(days=1), open=101, high=103, low=100, close=102, volume=1100),
    ]
    cleaned, report = clean_candles(candles, now=now)

    assert len(cleaned) == 2
    assert report.freshness_seconds is not None
    assert report.freshness_seconds >= 0
    assert 0 <= report.source_reliability <= 1


def test_walk_forward_split_generation() -> None:
    splits = build_walk_forward_splits(
        total_rows=120,
        train_size=60,
        val_size=20,
        test_size=20,
        step_size=10,
    )

    assert len(splits) == 3
    assert splits[0].train_start == 0
    assert splits[-1].test_end == 120
