"""Pure functions that turn raw tool responses into the shapes the dashboard needs.
Standard library only, so they can be unit-tested without any third-party dependency."""
import json
import math
import re
from collections import deque
from datetime import datetime, timezone

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]


# ---------- Prometheus ----------
def _num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) or math.isinf(f) else f


def parse_vector(payload):
    out = []
    for r in payload.get("data", {}).get("result", []):
        value = _num(r["value"][1])
        if value is not None:
            out.append({"metric": r.get("metric", {}), "value": value})
    return out


def parse_matrix(payload):
    out = []
    for r in payload.get("data", {}).get("result", []):
        pts = [[float(t), v] for t, raw in r.get("values", []) if (v := _num(raw)) is not None]
        out.append({"metric": r.get("metric", {}), "points": pts})
    return out


# ---------- Trivy ----------
def summarize_trivy(report, top=25):
    counts = {s: 0 for s in SEVERITIES}
    findings = []
    for res in report.get("Results", []) or []:
        for v in res.get("Vulnerabilities", []) or []:
            sev = v.get("Severity", "UNKNOWN")
            sev = sev if sev in counts else "UNKNOWN"
            counts[sev] += 1
            findings.append({
                "id": v.get("VulnerabilityID"), "severity": sev, "package": v.get("PkgName"),
                "installed": v.get("InstalledVersion"), "fixed": v.get("FixedVersion") or "no fix available",
                "title": (v.get("Title") or "")[:140], "target": res.get("Target"),
            })
    findings.sort(key=lambda f: SEVERITIES.index(f["severity"]))
    return {"counts": counts, "total": sum(counts.values()), "findings": findings[:top],
            "created_at": report.get("CreatedAt"), "artifact": report.get("ArtifactName")}


def gate_result(counts, gate_severity):
    """Gate fails if any finding is at or above the configured severity."""
    gate = gate_severity if gate_severity in SEVERITIES else "CRITICAL"
    blocking = sum(counts.get(s, 0) for s in SEVERITIES[: SEVERITIES.index(gate) + 1])
    return {"severity": gate, "passed": blocking == 0, "blocking_findings": blocking}


# ---------- Alertmanager ----------
def normalize_alerts(items):
    out = []
    for a in items or []:
        labels, ann = a.get("labels", {}), a.get("annotations", {})
        out.append({
            "name": labels.get("alertname"), "severity": labels.get("severity", "none"),
            "service": labels.get("job") or labels.get("deployment") or labels.get("pod") or labels.get("namespace"),
            "state": (a.get("status") or {}).get("state", a.get("status", "active")),
            "summary": ann.get("summary", ""), "description": ann.get("description", ""),
            "starts_at": a.get("startsAt"), "ends_at": a.get("endsAt"),
        })
    return out


class AlertHistory:
    """Bounded in-memory log of alerts received through the Alertmanager webhook (lost on restart)."""

    def __init__(self, maxlen=200):
        self._events = deque(maxlen=maxlen)

    def record(self, payload):
        for a in normalize_alerts(payload.get("alerts", [])):
            a["state"] = a["state"] if isinstance(a["state"], str) else "active"
            a["status"] = payload.get("status", "unknown")  # firing | resolved
            self._events.appendleft(a)

    def list(self):
        return list(self._events)


# ---------- Loki ----------
_SERVICE_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
LEVELS = {
    "ERROR": r'"level":"ERROR"',
    "WARN": r'"level":"WARN(ING)?"',
}


def build_logql(namespace, service=None, level=None, text=None):
    """Build a LogQL query from validated parts. Raises ValueError on unsafe input."""
    if not re.match(r"^[a-z0-9-]+$", namespace):
        raise ValueError("invalid namespace")
    selector = f'namespace="{namespace}"'
    if service:
        if not _SERVICE_RE.match(service):
            raise ValueError("invalid service name")
        selector += f', app="{service}"'
    query = "{" + selector + "}"
    if level:
        lv = level.upper()
        if lv not in LEVELS and lv != "INFO":
            raise ValueError("level must be ERROR, WARN or INFO")
        if lv in LEVELS:
            query += f" |~ `{LEVELS[lv]}`"
    if text:
        if "`" in text or len(text) > 200:
            raise ValueError("invalid search text")
        query += f" |= `{text}`"
    return query


def _level_of(line):
    try:
        return str(json.loads(line).get("level", "")).upper()
    except (ValueError, AttributeError):
        return ""


def parse_loki(payload, limit=200):
    lines = []
    for stream in payload.get("data", {}).get("result", []):
        labels = stream.get("stream", {})
        for ts, line in stream.get("values", []):
            lines.append({"ts_ns": int(ts), "service": labels.get("app"), "pod": labels.get("pod"),
                          "level": _level_of(line), "line": line[:1000]})
    lines.sort(key=lambda x: x["ts_ns"], reverse=True)
    for l in lines:
        l["ts"] = datetime.fromtimestamp(l["ts_ns"] / 1e9, tz=timezone.utc).isoformat()
    return lines[:limit]


# ---------- Jenkins ----------
def normalize_builds(job, payload):
    builds = []
    for b in payload.get("builds", []) or []:
        result = "RUNNING" if b.get("building") else (b.get("result") or "UNKNOWN")
        builds.append({
            "job": job, "number": b.get("number"), "result": result, "building": bool(b.get("building")),
            "timestamp": b.get("timestamp"), "duration_ms": b.get("duration"), "url": b.get("url"),
            "description": b.get("description") or "",
        })
    return builds


def image_from_description(desc):
    m = re.search(r"image=(\S+)", desc or "")
    return m.group(1) if m else None


def job_stats(builds):
    done = [b for b in builds if not b["building"]]
    ok = [b for b in done if b["result"] == "SUCCESS"]
    durations = [b["duration_ms"] for b in done if b["duration_ms"]]
    latest_image = next((image_from_description(b["description"]) for b in builds if image_from_description(b["description"])), None)
    return {"success": len(ok), "failed": len([b for b in done if b["result"] in ("FAILURE", "UNSTABLE")]),
            "avg_duration_ms": int(sum(durations) / len(durations)) if durations else None, "latest_image": latest_image}


# ---------- Argo CD ----------
def normalize_argo_app(obj):
    st = obj.get("status", {})
    history = [{"id": h.get("id"), "revision": h.get("revision"), "deployed_at": h.get("deployedAt")}
               for h in st.get("history", []) or []]
    revisions = [h["revision"] for h in history]
    return {
        "name": obj.get("metadata", {}).get("name"),
        "sync": st.get("sync", {}).get("status", "Unknown"),
        "health": st.get("health", {}).get("status", "Unknown"),
        "revision": st.get("sync", {}).get("revision"),
        "images": st.get("summary", {}).get("images", []),
        "operation": (st.get("operationState") or {}).get("phase"),
        "history": sorted(history, key=lambda h: h["deployed_at"] or "", reverse=True)[:10],
        # Heuristic: the same Git revision deployed twice means an earlier version was re-deployed (revert/rollback).
        "redeployed_previous_revision": len(set(revisions)) < len(revisions),
    }
