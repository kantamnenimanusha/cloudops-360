import time

from .http import get_json
from .result import NotConfigured
from ..parsers import parse_matrix, parse_vector


def _base(s):
    if not s.prometheus_url:
        raise NotConfigured("PROMETHEUS_URL is not set")
    return s.prometheus_url


def instant(s, expr):
    payload = get_json(f"{_base(s)}/api/v1/query", params={"query": expr})
    if payload.get("status") != "success":
        raise RuntimeError(payload.get("error", "prometheus query failed"))
    return parse_vector(payload)


def series(s, expr, minutes=60, step=60):
    end = time.time()
    payload = get_json(f"{_base(s)}/api/v1/query_range",
                       params={"query": expr, "start": end - minutes * 60, "end": end, "step": step})
    if payload.get("status") != "success":
        raise RuntimeError(payload.get("error", "prometheus query failed"))
    return parse_matrix(payload)
