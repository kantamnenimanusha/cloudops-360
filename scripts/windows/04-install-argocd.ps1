<# Installs Argo CD into the cluster (stable release manifest). #>
. "$PSScriptRoot\_common.ps1"
Assert-Command kubectl "winget install Kubernetes.kubectl"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
Invoke-Checked { kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml } "install argocd"
Invoke-Checked { kubectl -n argocd rollout status deploy/argocd-server --timeout=300s } "argocd-server rollout"
Invoke-Checked { kubectl -n argocd rollout status deploy/argocd-repo-server --timeout=300s } "argocd-repo-server rollout"
$pw = kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}'
$plain = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($pw))
Write-Host "Argo CD admin password (change it after first login): $plain" -ForegroundColor Yellow
Write-Host "UI: run scripts\windows\07-port-forward.ps1 then open https://localhost:8081 (accept the self-signed certificate)"
