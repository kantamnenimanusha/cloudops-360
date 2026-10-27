from .http import get_json
from .result import NotConfigured
from ..parsers import normalize_alerts


def active_alerts(s):
    if not s.alertmanager_url:
        raise NotConfigured("ALERTMANAGER_URL is not set")
    return normalize_alerts(get_json(f"{s.alertmanager_url}/api/v2/alerts", params={"active": "true", "silenced": "false"}))
