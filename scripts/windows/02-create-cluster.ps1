<# Creates the local kind cluster and a local image registry (localhost:5001) wired into it. Free. #>
. "$PSScriptRoot\_common.ps1"
Assert-Command kind "winget install Kubernetes.kind"; Assert-Command kubectl "winget install Kubernetes.kubectl"
$regName = "kind-registry"; $regPort = 5001

if (-not (docker ps -a --format '{{.Names}}' | Select-String -SimpleMatch $regName)) {
    Invoke-Checked { docker run -d --restart=always -p "127.0.0.1:${regPort}:5000" --network bridge --name $regName registry:2 } "start registry"
} else { docker start $regName | Out-Null }

if (-not (kind get clusters 2>$null | Select-String -SimpleMatch "cloudops")) {
    Invoke-Checked { kind create cluster --config (Join-Path $Root "local\kind-config.yaml") } "create kind cluster"
} else { Write-Host "kind cluster 'cloudops' already exists." }

# Tell containerd on every node that localhost:5001 means the registry container
foreach ($node in (kind get nodes --name cloudops)) {
    docker exec $node mkdir -p "/etc/containerd/certs.d/localhost:${regPort}" | Out-Null
    $toml = "[host.`"http://${regName}:5000`"]"
    docker exec $node sh -c "echo '$toml' > /etc/containerd/certs.d/localhost:${regPort}/hosts.toml"
}
if (-not ((docker inspect -f '{{json .NetworkSettings.Networks.kind}}' $regName) -ne 'null')) { docker network connect kind $regName }
kubectl config use-context kind-cloudops | Out-Null
kubectl get nodes
Write-Host "Cluster ready. Registry: localhost:$regPort" -ForegroundColor Green
