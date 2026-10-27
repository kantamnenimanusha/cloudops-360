<#
 OPTIONAL. Lets the Jenkins "Verify rollout" stage run kubectl. Uses a ServiceAccount that can only get/list/watch
 deployments, replicasets and pods in the cloudops namespace (defined in the GitOps cluster-config chart) - NOT cluster-admin.
 The token lasts 24 h; re-run this script to renew it.
#>
. "$PSScriptRoot\_common.ps1"
$token = (kubectl -n cloudops create token jenkins-verifier --duration=24h)
if (-not $token) { throw "Could not create token. Is the 'cluster-config' Argo CD application synced (kubectl -n cloudops get sa jenkins-verifier)?" }
$internal = (kind get kubeconfig --internal --name cloudops | Out-String)
$server = [regex]::Match($internal, 'server:\s*(\S+)').Groups[1].Value
$ca = [regex]::Match($internal, 'certificate-authority-data:\s*(\S+)').Groups[1].Value
$cfg = @"
apiVersion: v1
kind: Config
clusters:
- name: kind
  cluster:
    server: $server
    certificate-authority-data: $ca
users:
- name: jenkins-verifier
  user:
    token: $token
contexts:
- name: ctx
  context:
    cluster: kind
    user: jenkins-verifier
    namespace: cloudops
current-context: ctx
"@
$tmp = New-TemporaryFile
try {
    Set-Content -Path $tmp -Value $cfg -Encoding ascii
    docker exec cloudops-jenkins mkdir -p /var/jenkins_home/.kube
    docker cp $tmp cloudops-jenkins:/var/jenkins_home/.kube/config
    docker network connect kind cloudops-jenkins 2>$null
} finally { Remove-Item $tmp -Force }
docker exec cloudops-jenkins kubectl get deploy -n cloudops
Write-Host "Done. Enable the VERIFY_ROLLOUT build parameter in Jenkins to use it." -ForegroundColor Green
