<# Creates the local kind cluster and a local image registry (localhost:5001) wired into it. Free. #>
. "$PSScriptRoot\_common.ps1"
Assert-Command kind "winget install Kubernetes.kind"; Assert-Command kubectl "winget install Kubernetes.kubectl"
$regName = "kind-registry"; $regPort = 5001

if (-not (docker ps -a --format '{{.Names}}' | Select-String -SimpleMatch $regName)) {
    Invoke-Checked { docker run -d --restart=always -p "127.0.0.1:${regPort}:5000" --network bridge --name $regName registry:2 } "start registry"
} else { docker start $regName | Out-Null }

$clusters = @()

try {
    $clusters = @(kind get clusters 2>$null)
} catch {
    # No existing Kind clusters; continue with cluster creation.
    $clusters = @()
}

if ($clusters -notcontains "cloudops") {
    Invoke-Checked {
        kind create cluster --config (Join-Path $Root "local\kind-config.yaml")
    } "create kind cluster"
} else {
    Write-Host "kind cluster 'cloudops' already exists."
}

# Connect the local registry to the Kind Docker network.
$registryKindNetwork = docker inspect -f '{{json .NetworkSettings.Networks.kind}}' $regName

if ($registryKindNetwork -eq 'null') {
    docker network connect kind $regName

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to connect registry to Kind network."
    }
}

# Configure containerd on each Kubernetes node.
$hostsFile = Join-Path $Root "hosts.toml"

if (-not (Test-Path $hostsFile)) {
    throw "Registry configuration file not found: $hostsFile"
}

foreach ($node in (kind get nodes --name cloudops)) {

    docker exec $node mkdir -p "/etc/containerd/certs.d/localhost:${regPort}"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create registry configuration directory on $node"
    }

    docker cp $hostsFile "${node}:/etc/containerd/certs.d/localhost:${regPort}/hosts.toml"

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to copy registry configuration to $node"
    }

    Write-Host "Registry configuration applied to $node" -ForegroundColor Green
}
kubectl config use-context kind-cloudops | Out-Null
kubectl get nodes
Write-Host "Cluster ready. Registry: localhost:$regPort" -ForegroundColor Green
