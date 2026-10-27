import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..integrations import alertmanager, aws, jenkins, kube, loki, prometheus
from ..integrations.result import NotConfigured, safe
from ..parsers import AlertHistory, gate_result, normalize_argo_app

log = logging.getLogger("api")
router = APIRouter(prefix="/api/v1")
alert_history = AlertHistory()


def settings(request: Request):
    return request.app.state.settings


def viewer(request: Request):
    return request.state.claims_viewer()


def _services(s):
    rows = prometheus.instant(s, f'up{{namespace="{s.monitored_namespace}"}}')
    by_job = {}
    for r in rows:
        job = r["metric"].get("job", "unknown")
        by_job[job] = by_job.get(job, True) and r["value"] == 1
    return [{"name": k, "up": v} for k, v in sorted(by_job.items())]


def _apps(s):
    return [normalize_argo_app(o) for o in kube.list_argo_apps(s.argocd_namespace)]


def _single(s, expr):
    rows = prometheus.instant(s, expr)
    return {"percent": round(rows[0]["value"], 1)} if rows else {"percent": None}


@router.get("/overview")
def overview(s=Depends(settings), _=Depends(viewer)):
    def nodes():
        n = kube.list_nodes()
        return {"total": len(n), "ready": sum(1 for x in n if x["ready"])}

    def recent_deploys():
        rows = [{"app": a["name"], **h, "sync": a["sync"], "health": a["health"]} for a in _apps(s) for h in a["history"]]
        return sorted(rows, key=lambda r: r["deployed_at"] or "", reverse=True)[:8]

    def pipelines():
        rows = [b for j in jenkins.all_jobs(s) for b in j["builds"]]
        return sorted(rows, key=lambda b: b["timestamp"] or 0, reverse=True)[:8]

    return {
        "services": safe("prometheus:up", lambda: _services(s)),
        "nodes": safe("kubernetes:nodes", nodes),
        "cpu": safe("prometheus:node_exporter", lambda: _single(s, '100 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100')),
        "memory": safe("prometheus:node_exporter", lambda: _single(s, "100 * (1 - sum(node_memory_MemAvailable_bytes) / sum(node_memory_MemTotal_bytes))")),
        "deployments": safe("argocd:applications", recent_deploys),
        "alerts": safe("alertmanager:/api/v2/alerts", lambda: alertmanager.active_alerts(s)),
        "pipelines": safe("jenkins:/api/json", pipelines),
    }


@router.get("/infrastructure")
def infrastructure(s=Depends(settings), _=Depends(viewer)):
    def node_util():
        cpu = {r["metric"].get("instance"): r["value"] for r in prometheus.instant(
            s, '100 - avg by (instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100')}
        mem = {r["metric"].get("instance"): r["value"] for r in prometheus.instant(
            s, "100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)")}
        return [{"instance": i, "cpu_percent": round(cpu[i], 1), "memory_percent": round(mem.get(i, float("nan")), 1)} for i in cpu]

    def cloudwatch():
        ids = [i["id"] for i in aws.ec2_instances(s) if i["state"] == "running"]
        return aws.ec2_cpu(s, ids)

    return {
        "ec2": safe("aws:ec2:DescribeInstances", lambda: aws.ec2_instances(s)),
        "ecr": safe("aws:ecr:DescribeRepositories", lambda: aws.ecr_repositories(s)),
        "cloudwatch_ec2_cpu": safe("aws:cloudwatch:GetMetricStatistics", cloudwatch),
        "nodes": safe("kubernetes:nodes", kube.list_nodes),
        "node_utilization": safe("prometheus:node_exporter", node_util),
    }


@router.get("/kubernetes")
def kubernetes_view(namespace: str = Query(default=None, pattern=r"^[a-z0-9-]{1,63}$"), s=Depends(settings), _=Depends(viewer)):
    ns = namespace or s.monitored_namespace

    def usage():
        cpu = {r["metric"].get("pod"): r["value"] for r in prometheus.instant(
            s, f'sum by (pod)(rate(container_cpu_usage_seconds_total{{namespace="{ns}",container!=""}}[5m]))')}
        mem = {r["metric"].get("pod"): r["value"] for r in prometheus.instant(
            s, f'sum by (pod)(container_memory_working_set_bytes{{namespace="{ns}",container!=""}})')}
        return [{"pod": p, "cpu_cores": round(cpu.get(p, 0), 4), "memory_bytes": mem.get(p)} for p in sorted(set(cpu) | set(mem))]

    return {
        "namespace": ns,
        "namespaces": safe("kubernetes:namespaces", kube.list_namespaces),
        "deployments": safe("kubernetes:deployments", lambda: kube.list_deployments(ns)),
        "pods": safe("kubernetes:pods", lambda: kube.list_pods(ns)),
        "usage": safe("prometheus:cadvisor", usage),
    }


@router.get("/cicd")
def cicd(s=Depends(settings), _=Depends(viewer)):
    return {"jobs": safe("jenkins:/api/json", lambda: jenkins.all_jobs(s))}


@router.get("/security")
def security(s=Depends(settings), _=Depends(viewer)):
    def reports():
        out = []
        for job in s.jenkins_jobs:
            row = {"job": job}
            for kind in ("fs", "image"):
                rep = jenkins.trivy_report(s, job, kind)
                row[kind] = None if rep is None else {**rep, "gate": gate_result(rep["counts"], s.trivy_gate_severity)}
            out.append(row)
        return out

    return {"gate_severity": s.trivy_gate_severity, "reports": safe("jenkins:artifact reports/trivy-*.json", reports)}


@router.get("/monitoring")
def monitoring(minutes: int = Query(default=60, ge=5, le=360), s=Depends(settings), _=Depends(viewer)):
    ns = s.monitored_namespace
    rate = f'sum by (job)(rate(http_server_requests_seconds_count{{namespace="{ns}"}}[5m]))'
    err = (f'sum by (job)(rate(http_server_requests_seconds_count{{namespace="{ns}",status=~"5.."}}[5m]))'
           f' / sum by (job)(rate(http_server_requests_seconds_count{{namespace="{ns}"}}[5m]))')
    p95 = f'histogram_quantile(0.95, sum by (job, le)(rate(http_server_requests_seconds_bucket{{namespace="{ns}"}}[5m])))'

    def by_job(expr):
        return [{"service": r["metric"].get("job"), "value": r["value"]} for r in prometheus.instant(s, expr)]

    def ranged(expr):
        return [{"service": r["metric"].get("job"), "points": r["points"]} for r in prometheus.series(s, expr, minutes)]

    return {
        "request_rate": safe("prometheus", lambda: by_job(rate)),
        "error_ratio": safe("prometheus", lambda: by_job(err)),
        "latency_p95_seconds": safe("prometheus", lambda: by_job(p95)),
        "availability_1h": safe("prometheus", lambda: by_job(f'avg_over_time(up{{namespace="{ns}"}}[1h])')),
        "request_rate_series": safe("prometheus", lambda: ranged(rate)),
        "latency_p95_series": safe("prometheus", lambda: ranged(p95)),
    }


@router.get("/logs")
def logs(service: str = Query(default=None), level: str = Query(default=None), q: str = Query(default=None),
         minutes: int = Query(default=30, ge=1, le=360), s=Depends(settings), _=Depends(viewer)):
    try:
        from ..parsers import build_logql
        build_logql(s.monitored_namespace, service, level, q)  # validate early -> 422 rather than 'unavailable'
    except ValueError as e:
        raise HTTPException(422, str(e))
    return safe("loki:/loki/api/v1/query_range", lambda: loki.query_logs(s, service, level, q, minutes))


@router.get("/alerts")
def alerts(s=Depends(settings), _=Depends(viewer)):
    return {"active": safe("alertmanager:/api/v2/alerts", lambda: alertmanager.active_alerts(s)),
            "history": {"status": "ok", "source": "alertmanager webhook (in-memory, lost on restart)",
                        "fetched_at": None, "error": None, "data": alert_history.list()}}


@router.get("/deployments")
def deployments(s=Depends(settings), _=Depends(viewer)):
    return {"applications": safe("argocd:applications.argoproj.io", lambda: _apps(s))}


@router.post("/webhooks/alertmanager", include_in_schema=False)
async def alertmanager_webhook(request: Request, s=Depends(settings)):
    import hmac

    auth = request.headers.get("authorization", "")
    if not s.webhook_token or not hmac.compare_digest(auth, f"Bearer {s.webhook_token}"):
        raise HTTPException(401, "invalid webhook token")
    payload = await request.json()
    alert_history.record(payload)
    for a in payload.get("alerts", []):
        log.info("alertmanager %s alert=%s severity=%s", payload.get("status"), a.get("labels", {}).get("alertname"),
                 a.get("labels", {}).get("severity"))
    return {"received": len(payload.get("alerts", []))}


@router.get("/admin/diagnostics")
def diagnostics(request: Request, s=Depends(settings)):
    request.state.require_admin()
    return {"version": s.version, "commit": s.commit, "env": s.env, "monitored_namespace": s.monitored_namespace,
            "integrations": {"prometheus": bool(s.prometheus_url), "alertmanager": bool(s.alertmanager_url),
                             "loki": bool(s.loki_url), "jenkins": bool(s.jenkins_url), "aws": s.enable_aws}}
