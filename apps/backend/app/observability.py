"""Prometheus metrics (Micrometer-compatible names), JSON logging, optional OpenTelemetry tracing."""
import json
import logging
import os
import sys
import time

from prometheus_client import CONTENT_TYPE_LATEST, Histogram, generate_latest

HTTP_REQUESTS = Histogram(
    "http_server_requests_seconds",
    "HTTP server request duration (name matches Spring Micrometer so one PromQL works for all services)",
    ["method", "uri", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
SKIP_PATHS = {"/metrics", "/health", "/ready"}


class JsonFormatter(logging.Formatter):
    def __init__(self, service):
        super().__init__()
        self.service = service

    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service,
        }
        try:
            from opentelemetry import trace

            ctx = trace.get_current_span().get_span_context()
            if ctx.is_valid:
                payload["trace_id"] = format(ctx.trace_id, "032x")
        except Exception:  # tracing is optional
            pass
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging(service):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    logging.getLogger("uvicorn.access").disabled = True  # request logging happens in the metrics middleware


def setup_tracing(app, service):
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return False
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": service}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint.rstrip("/") + "/v1/traces")))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app, excluded_urls="health,ready,metrics")
        return True
    except Exception:
        logging.getLogger(__name__).exception("tracing setup failed; continuing without tracing")
        return False


def install_metrics_middleware(app):
    log = logging.getLogger("http")

    @app.middleware("http")
    async def _metrics(request, call_next):
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            if request.url.path not in SKIP_PATHS:
                route = request.scope.get("route")
                uri = getattr(route, "path", "UNMATCHED")
                HTTP_REQUESTS.labels(request.method, uri, str(status)).observe(time.perf_counter() - start)
                if status >= 500:
                    log.error("request failed method=%s uri=%s status=%s", request.method, uri, status)


def metrics_response():
    from fastapi import Response

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
