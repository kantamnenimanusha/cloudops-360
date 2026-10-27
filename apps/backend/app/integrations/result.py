"""Every integration returns the same envelope so the UI can distinguish ok / unavailable / not_configured."""
import logging
from datetime import datetime, timezone

log = logging.getLogger("integrations")


class NotConfigured(Exception):
    pass


def _now():
    return datetime.now(timezone.utc).isoformat()


def ok(source, data):
    return {"status": "ok", "source": source, "fetched_at": _now(), "error": None, "data": data}


def not_configured(source, message):
    return {"status": "not_configured", "source": source, "fetched_at": _now(), "error": message, "data": None}


def unavailable(source, exc):
    return {"status": "unavailable", "source": source, "fetched_at": _now(), "error": str(exc)[:300], "data": None}


def safe(source, fn):
    """Run fn(); never raise. Real errors become an explicit 'unavailable' result (never invented data)."""
    try:
        return ok(source, fn())
    except NotConfigured as e:
        return not_configured(source, str(e))
    except Exception as e:  # noqa: BLE001 - boundary: convert every failure into a visible state
        log.warning("integration %s failed: %s", source, e)
        return unavailable(source, e)
