"""Read-only Kubernetes access (get/list/watch only; see the ClusterRole in the GitOps chart)."""
from .result import NotConfigured

_cache = {}


def _clients():
    if not _cache:
        try:
            from kubernetes import client, config
        except ImportError as e:  # pragma: no cover
            raise NotConfigured("kubernetes client library not installed") from e
        try:
            config.load_incluster_config()
        except Exception:  # noqa: BLE001 - fall back to local kubeconfig for host-side development
            try:
                config.load_kube_config()
            except Exception as e:  # noqa: BLE001
                raise NotConfigured(f"no Kubernetes configuration available: {e}") from e
        _cache["core"] = client.CoreV1Api()
        _cache["apps"] = client.AppsV1Api()
        _cache["custom"] = client.CustomObjectsApi()
    return _cache


def list_namespaces():
    return sorted(n.metadata.name for n in _clients()["core"].list_namespace().items)


def list_nodes():
    out = []
    for n in _clients()["core"].list_node().items:
        ready = any(c.type == "Ready" and c.status == "True" for c in n.status.conditions or [])
        out.append({"name": n.metadata.name, "ready": ready, "kubelet_version": n.status.node_info.kubelet_version,
                    "cpu": n.status.capacity.get("cpu"), "memory": n.status.capacity.get("memory"),
                    "instance_type": (n.metadata.labels or {}).get("node.kubernetes.io/instance-type")})
    return out


def list_deployments(namespace):
    out = []
    for d in _clients()["apps"].list_namespaced_deployment(namespace).items:
        out.append({"name": d.metadata.name, "namespace": namespace, "desired": d.spec.replicas or 0,
                    "ready": d.status.ready_replicas or 0, "available": d.status.available_replicas or 0,
                    "unavailable": d.status.unavailable_replicas or 0,
                    "images": [c.image for c in d.spec.template.spec.containers]})
    return out


def list_pods(namespace):
    out = []
    for p in _clients()["core"].list_namespaced_pod(namespace).items:
        statuses = p.status.container_statuses or []
        containers = []
        for cs in statuses:
            state = "running" if cs.state.running else ("waiting: " + (cs.state.waiting.reason or "") if cs.state.waiting
                                                         else ("terminated: " + (cs.state.terminated.reason or "")))
            containers.append({"name": cs.name, "ready": cs.ready, "restarts": cs.restart_count, "image": cs.image, "state": state})
        out.append({"name": p.metadata.name, "phase": p.status.phase, "node": p.spec.node_name,
                    "ready": bool(statuses) and all(c["ready"] for c in containers),
                    "restarts": sum(c["restarts"] for c in containers), "containers": containers,
                    "started": p.status.start_time.isoformat() if p.status.start_time else None})
    return out


def list_argo_apps(namespace):
    res = _clients()["custom"].list_namespaced_custom_object("argoproj.io", "v1alpha1", namespace, "applications")
    return res.get("items", [])
