import logging

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import Settings
from .observability import install_metrics_middleware, metrics_response, setup_logging, setup_tracing
from .routers import api
from .security import LoginLimiter, authenticate, create_token, decode_token, has_role

SERVICE = "cloudops-backend"


class LoginRequest(BaseModel):
    username: str
    password: str


def create_app(settings: Settings = None) -> FastAPI:
    settings = settings or Settings.from_env()
    problems = settings.validate()
    if problems and settings.env != "test":
        raise RuntimeError("Invalid configuration: " + "; ".join(problems))

    setup_logging(SERVICE)
    app = FastAPI(title="CloudOps 360 API", version=settings.version,
                  description="Read-only aggregation of Prometheus, Kubernetes, Jenkins, Argo CD, Loki, Alertmanager and AWS.")
    app.state.settings = settings
    limiter = LoginLimiter()
    install_metrics_middleware(app)
    setup_tracing(app, SERVICE)
    if settings.allowed_origins:
        app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_methods=["GET", "POST"],
                           allow_headers=["Authorization", "Content-Type"])

    @app.middleware("http")
    async def attach_auth(request: Request, call_next):
        header = request.headers.get("authorization", "")
        claims = decode_token(settings, header[7:]) if header.startswith("Bearer ") else None

        def claims_viewer():
            if not has_role(claims, "viewer"):
                raise HTTPException(401, "authentication required", headers={"WWW-Authenticate": "Bearer"})
            return claims

        def require_admin():
            claims_viewer()
            if not has_role(claims, "admin"):
                raise HTTPException(403, "admin role required")

        request.state.claims_viewer = claims_viewer
        request.state.require_admin = require_admin
        return await call_next(request)

    auth = APIRouter(prefix="/api/v1/auth", tags=["auth"])

    @auth.post("/login")
    def login(body: LoginRequest, request: Request):
        key = request.client.host if request.client else "unknown"
        if limiter.blocked(key):
            raise HTTPException(429, "too many failed attempts; try again later")
        role = authenticate(settings, body.username, body.password)
        if not role:
            limiter.record_failure(key)
            raise HTTPException(401, "invalid credentials")
        limiter.reset(key)
        return {"access_token": create_token(settings, body.username, role), "token_type": "bearer",
                "role": role, "expires_in": settings.token_ttl_minutes * 60}

    @auth.get("/me")
    def me(request: Request):
        c = request.state.claims_viewer()
        return {"username": c["sub"], "role": c["role"]}

    app.include_router(auth)
    app.include_router(api.router)

    @app.get("/health", tags=["ops"])
    def health():
        return {"status": "UP"}

    @app.get("/ready", tags=["ops"])
    def ready():
        return {"status": "UP"}

    @app.get("/metrics", tags=["ops"])
    def metrics():
        return metrics_response()

    @app.get("/api/v1/version", tags=["ops"])
    def version():
        return {"service": SERVICE, "version": settings.version, "commit": settings.commit}

    return app


app = create_app()
