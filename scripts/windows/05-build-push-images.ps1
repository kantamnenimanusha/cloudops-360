<# Builds the four images once and pushes them to the local registry as :0.1.0 so the first GitOps sync has something to pull.
   After this, Jenkins produces immutable <git-sha>-<build> tags. #>
param([string]$Tag = "0.1.0", [string]$Registry = "localhost:5001")
. "$PSScriptRoot\_common.ps1"
Assert-Command docker "Install Docker Desktop."
$sha = (git -C $Root rev-parse --short=8 HEAD 2>$null); if (-not $sha) { $sha = "unknown" }
foreach ($app in $Apps) {
    $dir = Join-Path $Root "apps\$($AppDirs[$app])"
    $image = "$Registry/cloudops/${app}:$Tag"
    Write-Host "=== $app -> $image" -ForegroundColor Cyan
    Invoke-Checked { docker build -t $image --build-arg APP_VERSION=$Tag --build-arg GIT_COMMIT=$sha $dir } "build $app"
    Invoke-Checked { docker push $image } "push $app"
}
Write-Host "Done. Verify: curl http://localhost:5001/v2/_catalog" -ForegroundColor Green
