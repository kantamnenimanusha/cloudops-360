import logging
import os

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from . import chaos
from .observability import install_metrics_middleware, metrics_response, setup_logging, setup_tracing
from .store import InsufficientStock, Store, UnknownSku

SERVICE = "inventory-service"
VERSION = os.getenv("APP_VERSION", "dev")
COMMIT = os.getenv("GIT_COMMIT", "unknown")

setup_logging(SERVICE)
log = logging.getLogger(SERVICE)
app = FastAPI(title="Inventory Service", version=VERSION)
store = Store()
install_metrics_middleware(app)
setup_tracing(app, SERVICE)
app.include_router(chaos.router)


class ReserveRequest(BaseModel):
    quantity: int = Field(ge=1, le=1000)


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(response: Response):
    if not chaos.state["ready"]:
        response.status_code = 503
        return {"status": "DOWN", "reason": "readiness disabled via chaos endpoint (demo)"}
    return {"status": "UP"}


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.get("/version")
def version():
    return {"service": SERVICE, "version": VERSION, "commit": COMMIT}


@app.get("/items")
async def list_items():
    await chaos.apply_chaos()
    return store.list()


@app.get("/items/{sku}")
async def get_item(sku: str):
    await chaos.apply_chaos()
    try:
        return store.get(sku)
    except UnknownSku:
        raise HTTPException(404, f"unknown sku {sku}")


@app.post("/items/{sku}/reserve")
async def reserve(sku: str, body: ReserveRequest):
    await chaos.apply_chaos()
    try:
        result = store.reserve(sku, body.quantity)
    except UnknownSku:
        raise HTTPException(404, f"unknown sku {sku}")
    except InsufficientStock:
        raise HTTPException(409, f"insufficient stock for {sku}")
    log.info("reserved sku=%s quantity=%s remaining=%s", sku, body.quantity, result["remaining"])
    return result
