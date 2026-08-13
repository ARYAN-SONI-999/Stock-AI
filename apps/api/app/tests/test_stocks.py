from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_search_stocks_scaffold_response() -> None:
    response = client.get("/api/v1/stocks/?query=rel&limit=10")
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "rel"
    assert payload["results"] == []
