<# Creates namespaces + secrets (from local\.env, never from Git) and applies the Argo CD root application. #>
param([string]$GitOpsPath, [switch]$PrivateRepos)
. "$PSScriptRoot\_common.ps1"
Assert-Command kubectl "winget install Kubernetes.kubectl"
$gitops = Get-GitOpsPath $GitOpsPath
$e = Read-DotEnv

function New-K8sSecret($ns, $name, [hashtable]$values) {
    $tmp = New-TemporaryFile
    try {
        Set-Content -Path $tmp -Value ($values.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -Encoding ascii
        kubectl create secret generic $name -n $ns --from-env-file=$tmp --dry-run=client -o yaml | kubectl apply -f -
        if ($LASTEXITCODE -ne 0) { throw "secret $ns/$name failed" }
    } finally { Remove-Item $tmp -Force }
}
foreach ($ns in "cloudops", "monitoring") { kubectl create namespace $ns --dry-run=client -o yaml | kubectl apply -f - }
New-K8sSecret cloudops "cloudops-backend-secrets" @{ JWT_SECRET = $e.JWT_SECRET; VIEWER_PASSWORD = $e.VIEWER_PASSWORD; ADMIN_PASSWORD = $e.ADMIN_PASSWORD;
    WEBHOOK_TOKEN = $e.WEBHOOK_TOKEN; JENKINS_USER = "cloudops-ro"; JENKINS_PASSWORD = $e.JENKINS_RO_PASSWORD }
New-K8sSecret cloudops "chaos-secrets" @{ CHAOS_TOKEN = $e.CHAOS_TOKEN }
New-K8sSecret monitoring "alertmanager-webhook-token" @{ token = $e.WEBHOOK_TOKEN }

if ($PrivateRepos) {   # lets Argo CD read private GitOps repo
    $tmp = New-TemporaryFile
    Set-Content $tmp -Value @("type=git", "url=$($e.GITOPS_REPO_URL)", "username=$($e.GITHUB_USER)", "password=$($e.GITHUB_TOKEN)") -Encoding ascii
    kubectl create secret generic gitops-repo -n argocd --from-env-file=$tmp --dry-run=client -o yaml | kubectl apply -f -
    kubectl label secret gitops-repo -n argocd argocd.argoproj.io/secret-type=repository --overwrite
    Remove-Item $tmp -Force
}
Invoke-Checked { kubectl apply -f (Join-Path $gitops "argocd\project.yaml") } "apply AppProject"
Invoke-Checked { kubectl apply -f (Join-Path $gitops "argocd\root-app-local.yaml") } "apply root app"
Write-Host "Root application applied. Watch: kubectl -n argocd get applications -w" -ForegroundColor Green
Write-Host "kube-prometheus-stack takes several minutes to become Healthy on first sync."
