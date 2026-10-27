<# Removes everything created locally. -KeepVolumes keeps Jenkins/SonarQube data. #>
param([switch]$KeepVolumes)
. "$PSScriptRoot\_common.ps1"
Get-Process kubectl -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
$down = @("compose", "-f", (Join-Path $Root "local\docker-compose.yml"), "--env-file", $EnvFile, "down")
if (-not $KeepVolumes) { $down += "-v" }
docker @down
kind delete cluster --name cloudops
docker rm -f kind-registry 2>$null | Out-Null
Write-Host "Local environment removed." -ForegroundColor Green
