import time

from .http import get_json
from .result import NotConfigured
from ..parsers import build_logql, parse_loki


def query_logs(s, service=None, level=None, text=None, minutes=60, limit=200):
    if not s.loki_url:
        raise NotConfigured("LOKI_URL is not set")
    query = build_logql(s.monitored_namespace, service, level, text)
    end = int(time.time() * 1e9)
    payload = get_json(f"{s.loki_url}/loki/api/v1/query_range", params={
        "query": query, "start": end - minutes * 60 * int(1e9), "end": end, "limit": limit, "direction": "backward"})
    return {"query": query, "lines": parse_loki(payload, limit)}
