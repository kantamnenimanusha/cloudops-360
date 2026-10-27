import os

os.environ["CHAOS_ENABLED"] = "true"
os.environ["CHAOS_TOKEN"] = "test-token"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)
H = {"X-Chaos-Token": "test-token"}


def test_health_and_ready():
    assert client.get("/health").json() == {"status": "UP"}
    assert client.get("/ready").status_code == 200


def test_items_and_reserve():
    assert client.get("/items").status_code == 200
    r = client.post("/items/SKU-1002/reserve", json={"quantity": 2})
    assert r.status_code == 200 and r.json()["reserved"] == 2


def test_errors_mapped():
    assert client.get("/items/NOPE").status_code == 404
    assert client.post("/items/SKU-1003/reserve", json={"quantity": 99}).status_code == 409
    assert client.post("/items/SKU-1001/reserve", json={"quantity": 0}).status_code == 422


def test_metrics_exposed_with_micrometer_names():
    client.get("/items")
    assert "http_server_requests_seconds_count" in client.get("/metrics").text


def test_chaos_requires_token():
    assert client.post("/chaos/errors?rate=1").status_code == 401
    assert client.post("/chaos/errors?rate=1", headers={"X-Chaos-Token": "bad"}).status_code == 401


def test_chaos_error_injection_and_reset():
    assert client.post("/chaos/errors?rate=1", headers=H).status_code == 200
    assert client.get("/items").status_code == 500
    client.post("/chaos/reset", headers=H)
    assert client.get("/items").status_code == 200


def test_chaos_readiness():
    client.post("/chaos/ready?value=false", headers=H)
    assert client.get("/ready").status_code == 503
    assert client.get("/health").status_code == 200  # liveness unaffected
    client.post("/chaos/reset", headers=H)
    assert client.get("/ready").status_code == 200
