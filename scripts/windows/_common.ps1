# Shared helpers dot-sourced by the other scripts.
$ErrorActionPreference = "Stop"
$script:Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$script:EnvFile = Join-Path $Root "local\.env"
$script:GitOpsDefault = (Join-Path (Split-Path $Root -Parent) "cloudops-360-gitops")
$script:Apps = @("orders-service", "inventory-service", "cloudops-backend", "cloudops-frontend")
$script:AppDirs = @{ "orders-service" = "orders-service"; "inventory-service" = "inventory-service"; "cloudops-backend" = "backend"; "cloudops-frontend" = "frontend" }

function Assert-Command($name, $hint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { throw "Missing '$name'. $hint" }
}
function Invoke-Checked([scriptblock]$Block, $What) {
    & $Block
    if ($LASTEXITCODE -ne 0) { throw "FAILED: $What (exit code $LASTEXITCODE)" }
}
function Read-DotEnv([string]$Path = $script:EnvFile) {
    if (-not (Test-Path $Path)) { throw "$Path not found. Run scripts\windows\01-configure.ps1 first." }
    $map = @{}
    Get-Content $Path | Where-Object { $_ -match '^\s*[^#\s][^=]*=' } | ForEach-Object {
        $k, $v = $_ -split '=', 2
        $map[$k.Trim()] = $v.Trim()
    }
    return $map
}
function Set-DotEnvValue([string]$Key, [string]$Value, [string]$Path = $script:EnvFile) {
    $lines = @(Get-Content $Path)
    $found = $false
    $lines = $lines | ForEach-Object { if ($_ -match "^$Key=") { $found = $true; "$Key=$Value" } else { $_ } }
    if (-not $found) { $lines += "$Key=$Value" }
    Set-Content -Path $Path -Value $lines -Encoding ascii
}
function New-Secret([int]$Bytes = 32) {
    $b = New-Object byte[] $Bytes
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
    return ([Convert]::ToBase64String($b)).TrimEnd('=').Replace('+', 'A').Replace('/', 'B')
}
function Get-GitOpsPath { param([string]$Path) if ($Path) { return (Resolve-Path $Path).Path } else { return (Resolve-Path $script:GitOpsDefault).Path } }
