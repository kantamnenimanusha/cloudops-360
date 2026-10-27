import json

import pytest

from app import parsers as p


def test_parse_vector_drops_nan():
    payload = {"data": {"result": [
        {"metric": {"job": "a"}, "value": [1, "0.5"]}, {"metric": {"job": "b"}, "value": [1, "NaN"]}]}}
    assert p.parse_vector(payload) == [{"metric": {"job": "a"}, "value": 0.5}]


def test_parse_matrix():
    payload = {"data": {"result": [{"metric": {}, "values": [[1, "1"], [2, "NaN"], [3, "3"]]}]}}
    assert p.parse_matrix(payload)[0]["points"] == [[1.0, 1.0], [3.0, 3.0]]


REPORT = {"ArtifactName": "x", "Results": [{"Target": "pom.xml", "Vulnerabilities": [
    {"VulnerabilityID": "CVE-1", "Severity": "HIGH", "PkgName": "a", "InstalledVersion": "1", "FixedVersion": "2"},
    {"VulnerabilityID": "CVE-2", "Severity": "CRITICAL", "PkgName": "b", "InstalledVersion": "1"},
    {"VulnerabilityID": "CVE-3", "Severity": "WEIRD", "PkgName": "c", "InstalledVersion": "1"}]}]}


def test_summarize_trivy_counts_and_order():
    s = p.summarize_trivy(REPORT)
    assert s["counts"]["CRITICAL"] == 1 and s["counts"]["HIGH"] == 1 and s["counts"]["UNKNOWN"] == 1
    assert s["findings"][0]["id"] == "CVE-2"
    assert s["findings"][0]["fixed"] == "no fix available"


def test_summarize_trivy_empty():
    assert p.summarize_trivy({})["total"] == 0


def test_gate_result():
    counts = {"CRITICAL": 0, "HIGH": 3, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    assert p.gate_result(counts, "CRITICAL")["passed"] is True
    assert p.gate_result(counts, "HIGH")["passed"] is False
    assert p.gate_result(counts, "bogus")["severity"] == "CRITICAL"


def test_normalize_alerts():
    a = p.normalize_alerts([{"labels": {"alertname": "X", "severity": "critical", "job": "orders-service"},
                             "annotations": {"summary": "s"}, "status": {"state": "active"}, "startsAt": "t"}])
    assert a[0]["name"] == "X" and a[0]["service"] == "orders-service" and a[0]["state"] == "active"


def test_alert_history_records_and_bounds():
    h = p.AlertHistory(maxlen=2)
    for i in range(3):
        h.record({"status": "resolved", "alerts": [{"labels": {"alertname": f"A{i}"}}]})
    assert [e["name"] for e in h.list()] == ["A2", "A1"] and h.list()[0]["status"] == "resolved"


def test_build_logql_ok():
    q = p.build_logql("cloudops", "orders-service", "error", "timeout")
    assert q == '{namespace="cloudops", app="orders-service"} |~ `"level":"ERROR"` |= `timeout`'


@pytest.mark.parametrize("kw", [{"service": 'a"} or {x="'}, {"service": "UPPER"}, {"text": "bad`tick"}, {"level": "debug"}])
def test_build_logql_rejects_injection(kw):
    with pytest.raises(ValueError):
        p.build_logql("cloudops", **kw)


def test_parse_loki_sorted_and_levels():
    payload = {"data": {"result": [{"stream": {"app": "a", "pod": "p"}, "values": [
        ["1000000000", json.dumps({"level": "INFO"})], ["2000000000", json.dumps({"level": "ERROR"})]]}]}}
    lines = p.parse_loki(payload)
    assert lines[0]["level"] == "ERROR" and lines[1]["level"] == "INFO"


def test_builds_and_stats():
    payload = {"builds": [
        {"number": 3, "result": None, "building": True, "timestamp": 3, "duration": 0, "description": ""},
        {"number": 2, "result": "FAILURE", "building": False, "timestamp": 2, "duration": 100, "description": ""},
        {"number": 1, "result": "SUCCESS", "building": False, "timestamp": 1, "duration": 300, "description": "image=reg/x:abc-1"}]}
    builds = p.normalize_builds("j", payload)
    assert builds[0]["result"] == "RUNNING"
    st = p.job_stats(builds)
    assert st == {"success": 1, "failed": 1, "avg_duration_ms": 200, "latest_image": "reg/x:abc-1"}


def test_normalize_argo_detects_redeploy():
    obj = {"metadata": {"name": "a"}, "status": {"sync": {"status": "Synced", "revision": "r1"},
           "health": {"status": "Healthy"}, "history": [
               {"id": 1, "revision": "r1", "deployedAt": "2026-01-01"}, {"id": 2, "revision": "r2", "deployedAt": "2026-01-02"},
               {"id": 3, "revision": "r1", "deployedAt": "2026-01-03"}]}}
    app = p.normalize_argo_app(obj)
    assert app["redeployed_previous_revision"] is True and app["history"][0]["id"] == 3
