import os

os.environ.update({
    "APP_ENV": "test", "JWT_SECRET": "t" * 40, "VIEWER_PASSWORD": "viewer-password-1",
    "ADMIN_PASSWORD": "admin-password-22", "WEBHOOK_TOKEN": "hook-token",
    "PROMETHEUS_URL": "http://prom.test", "ALERTMANAGER_URL": "http://am.test", "LOKI_URL": "http://loki.test",
    "JENKINS_URL": "http://jenkins.test", "JENKINS_JOBS": "orders-service",
})
