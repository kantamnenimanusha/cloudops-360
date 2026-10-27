<# Opens local ports for every UI (each in its own hidden window). Stop them with: Get-Process kubectl | Stop-Process #>
. "$PSScriptRoot\_common.ps1"
$forwards = @(
    @("argocd", "svc/argocd-server", "8081:443"),
    @("monitoring", "svc/kube-prometheus-stack-grafana", "3000:80"),
    @("monitoring", "svc/kube-prometheus-stack-prometheus", "9090:9090"),
    @("monitoring", "svc/kube-prometheus-stack-alertmanager", "9093:9093"),
    @("monitoring", "svc/jaeger", "16686:16686"),
    @("cloudops", "svc/cloudops-frontend", "8088:8080"),
    @("cloudops", "svc/cloudops-backend", "8000:8000")
)
foreach ($f in $forwards) {
    Start-Process kubectl -ArgumentList @("port-forward", "-n", $f[0], $f[1], $f[2]) -WindowStyle Hidden
}
Write-Host @"
Argo CD      https://localhost:8081   (admin / password printed by 04-install-argocd.ps1)
Grafana      http://localhost:3000    (admin / password: run .\scripts\windows\grafana-password.ps1)
Prometheus   http://localhost:9090
Alertmanager http://localhost:9093
Jaeger       http://localhost:16686
CloudOps 360 http://localhost:8088    (viewer / VIEWER_PASSWORD from local\.env)
Backend API  http://localhost:8000/docs
Jenkins      http://localhost:8080   SonarQube http://localhost:9000
"@
