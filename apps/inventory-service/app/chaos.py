"""Controlled failure injection for DEMONSTRATIONS ONLY.
Disabled unless CHAOS_ENABLED=true AND a CHAOS_TOKEN is configured. The failures are simulated;
the infrastructure reaction (probes, restarts, alerts) is real."""
import asyncio
import hmac
import os
import random
import threading

from fastapi import APIRouter, Header, HTTPException

state = {"error_rate": 0.0, "latency_ms": 0, "ready": True}
router = APIRouter(prefix="/chaos", tags=["chaos (demo only)"])


def enabled():
    return os.getenv("CHAOS_ENABLED", "false").lower() == "true" and bool(os.getenv("CHAOS_TOKEN"))


def _guard(token):
    if not enabled():
        raise HTTPException(404, "not found")
    if not token or not hmac.compare_digest(token, os.environ["CHAOS_TOKEN"]):
        raise HTTPException(401, "invalid chaos token")


async def apply_chaos():
    """Called by API handlers: injects latency / errors according to current state."""
    if state["latency_ms"]:
        await asyncio.sleep(state["latency_ms"] / 1000)
    if state["error_rate"] and random.random() < state["error_rate"]:
        raise HTTPException(500, "chaos: injected error")


@router.get("/state")
def get_state(x_chaos_token: str = Header(default="")):
    _guard(x_chaos_token)
    return state


@router.post("/errors")
def set_errors(rate: float, x_chaos_token: str = Header(default="")):
    _guard(x_chaos_token)
    state["error_rate"] = min(max(rate, 0.0), 1.0)
    return state


@router.post("/latency")
def set_latency(ms: int, x_chaos_token: str = Header(default="")):
    _guard(x_chaos_token)
    state["latency_ms"] = min(max(ms, 0), 10000)
    return state


@router.post("/ready")
def set_ready(value: bool, x_chaos_token: str = Header(default="")):
    _guard(x_chaos_token)
    state["ready"] = value
    return state


@router.post("/reset")
def reset(x_chaos_token: str = Header(default="")):
    _guard(x_chaos_token)
    state.update(error_rate=0.0, latency_ms=0, ready=True)
    return state


@router.post("/crash")
def crash(x_chaos_token: str = Header(default="")):
    _guard(x_chaos_token)
    threading.Timer(0.5, lambda: os._exit(1)).start()
    return {"crashing": True}
