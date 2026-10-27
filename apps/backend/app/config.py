"""All configuration comes from environment variables. No secrets have defaults."""
import os
from dataclasses import dataclass, field


def _csv(value):
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    env: str = "dev"
    version: str = "dev"
    commit: str = "unknown"
    jwt_secret: str = ""
    token_ttl_minutes: int = 60
    viewer_password: str = ""
    admin_password: str = ""
    webhook_token: str = ""
    allowed_origins: list = field(default_factory=list)
    prometheus_url: str = ""
    alertmanager_url: str = ""
    loki_url: str = ""
    jenkins_url: str = ""
    jenkins_user: str = ""
    jenkins_password: str = ""
    jenkins_jobs: list = field(default_factory=list)
    argocd_namespace: str = "argocd"
    monitored_namespace: str = "cloudops"
    enable_aws: bool = False
    aws_region: str = ""
    trivy_gate_severity: str = "CRITICAL"

    @classmethod
    def from_env(cls):
        e = os.environ.get
        return cls(
            env=e("APP_ENV", "dev"),
            version=e("APP_VERSION", "dev"),
            commit=e("GIT_COMMIT", "unknown"),
            jwt_secret=e("JWT_SECRET", ""),
            token_ttl_minutes=int(e("TOKEN_TTL_MINUTES", "60")),
            viewer_password=e("VIEWER_PASSWORD", ""),
            admin_password=e("ADMIN_PASSWORD", ""),
            webhook_token=e("WEBHOOK_TOKEN", ""),
            allowed_origins=_csv(e("ALLOWED_ORIGINS", "")),
            prometheus_url=e("PROMETHEUS_URL", "").rstrip("/"),
            alertmanager_url=e("ALERTMANAGER_URL", "").rstrip("/"),
            loki_url=e("LOKI_URL", "").rstrip("/"),
            jenkins_url=e("JENKINS_URL", "").rstrip("/"),
            jenkins_user=e("JENKINS_USER", ""),
            jenkins_password=e("JENKINS_PASSWORD", ""),
            jenkins_jobs=_csv(e("JENKINS_JOBS", "orders-service,inventory-service,cloudops-backend,cloudops-frontend")),
            argocd_namespace=e("ARGOCD_NAMESPACE", "argocd"),
            monitored_namespace=e("MONITORED_NAMESPACE", "cloudops"),
            enable_aws=e("ENABLE_AWS", "false").lower() == "true",
            aws_region=e("AWS_REGION", ""),
            trivy_gate_severity=e("TRIVY_GATE_SEVERITY", "CRITICAL").upper(),
        )

    def validate(self):
        problems = []
        if len(self.jwt_secret) < 32:
            problems.append("JWT_SECRET must be set and at least 32 characters")
        for name in ("viewer_password", "admin_password"):
            if len(getattr(self, name)) < 12:
                problems.append(f"{name.upper()} must be set and at least 12 characters")
        if self.viewer_password and self.viewer_password == self.admin_password:
            problems.append("VIEWER_PASSWORD and ADMIN_PASSWORD must differ")
        return problems
