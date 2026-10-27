import httpx
import pytest
from fastapi.testclient import TestClient

from app.integrations import http as ihttp
from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def token(client, user, pw):
    r = client.post("/api/v1/auth/login", json={"username": user, "password": pw})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def mock_http(routes):
    """Route table: substring of URL -> JSON payload (or an httpx.Response)."""
    def handler(request):
        for needle, payload in routes.items():
            if needle in str(request.url):
                return payload if isinstance(payload, httpx.Response) else httpx.Response(200, json=payload)
        return httpx.Response(404, json={})
    ihttp.client_factory = lambda: httpx.Client(transport=httpx.MockTransport(handler))


def test_health_and_metrics(client):
    assert client.get("/health").json() == {"status": "UP"}
    assert "http_server_requests_seconds" in client.get("/metrics").text or client.get("/metrics").status_code == 200


def test_protected_endpoints_require_token(client):
    for path in ["/api/v1/overview", "/api/v1/cicd", "/api/v1/alerts", "/api/v1/logs", "/api/v1/auth/me"]:
        assert client.get(path).status_code == 401, path


def test_login_rejects_bad_credentials(client):
    assert client.post("/api/v1/auth/login", json={"username": "viewer", "password": "wrong-password"}).status_code == 401


def test_admin_endpoint_authorization(client):
    assert client.get("/api/v1/admin/diagnostics", headers=token(client, "viewer", "viewer-password-1")).status_code == 403
    r = client.get("/api/v1/admin/diagnostics", headers=token(client, "admin", "admin-password-22"))
    assert r.status_code == 200 and r.json()["integrations"]["prometheus"] is True


def test_cicd_reads_jenkins(client):
    mock_http({"/job/orders-service/api/json": {"builds": [
        {"number": 7, "result": "SUCCESS", "building": False, "timestamp": 1, "duration": 5000, "description": "image=r/x:abc-7"}]}})
    r = client.get("/api/v1/cicd", headers=token(client, "viewer", "viewer-password-1")).json()
    job = r["jobs"]["data"][0]
    assert r["jobs"]["status"] == "ok" and job["success"] == 1 and job["latest_image"] == "r/x:abc-7"


def test_unreachable_tool_is_reported_unavailable_not_faked(client):
    def boom(request):
        raise httpx.ConnectError("refused")
    ihttp.client_factory = lambda: httpx.Client(transport=httpx.MockTransport(boom))
    r = client.get("/api/v1/alerts", headers=token(client, "viewer", "viewer-password-1")).json()
    assert r["active"]["status"] == "unavailable" and r["active"]["data"] is None


def test_security_gate_from_trivy_artifact(client):
    report = {"Results": [{"Target": "pom.xml", "Vulnerabilities": [{"VulnerabilityID": "CVE-1", "Severity": "CRITICAL", "PkgName": "a", "InstalledVersion": "1"}]}]}
    mock_http({"trivy-fs.json": report, "trivy-image.json": httpx.Response(404, json={})})
    r = client.get("/api/v1/security", headers=token(client, "viewer", "viewer-password-1")).json()
    row = r["reports"]["data"][0]
    assert row["fs"]["gate"]["passed"] is False and row["image"] is None


def test_logs_rejects_injection(client):
    h = token(client, "viewer", "viewer-password-1")
    assert client.get("/api/v1/logs", params={"service": 'x"} or {y="'}, headers=h).status_code == 422


def test_logs_query(client):
    mock_http({"/loki/api/v1/query_range": {"data": {"result": [{"stream": {"app": "orders-service", "pod": "p"}, "values": [["1700000000000000000", "{\"level\":\"ERROR\"}"]]}]}}})
    r = client.get("/api/v1/logs", params={"service": "orders-service", "level": "error"}, headers=token(client, "viewer", "viewer-password-1")).json()
    assert r["status"] == "ok" and r["data"]["lines"][0]["level"] == "ERROR"


def test_alert_webhook_auth_and_history(client):
    payload = {"status": "firing", "alerts": [{"labels": {"alertname": "CloudOpsServiceDown", "severity": "critical", "job": "orders-service"}}]}
    assert client.post("/api/v1/webhooks/alertmanager", json=payload).status_code == 401
    assert client.post("/api/v1/webhooks/alertmanager", json=payload, headers={"Authorization": "Bearer hook-token"}).status_code == 200
    mock_http({"/api/v2/alerts": []})
    r = client.get("/api/v1/alerts", headers=token(client, "viewer", "viewer-password-1")).json()
    assert r["history"]["data"][0]["name"] == "CloudOpsServiceDown"


def test_aws_not_configured_when_disabled(client):
    mock_http({})
    r = client.get("/api/v1/infrastructure", headers=token(client, "viewer", "viewer-password-1")).json()
    assert r["ec2"]["status"] == "not_configured"
