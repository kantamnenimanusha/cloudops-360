<# Runs every automated test suite. Maven runs inside a container, so no local JDK/Maven is needed. #>
. "$PSScriptRoot\_common.ps1"
$results = [ordered]@{}
function Run($name, [scriptblock]$block) {
    Write-Host "`n=== $name ===" -ForegroundColor Cyan
    try { & $block; $results[$name] = if ($LASTEXITCODE -eq 0) { "PASS" } else { "FAIL" } } catch { Write-Host $_; $results[$name] = "FAIL" }
}
foreach ($svc in @("inventory-service", "backend")) {
    Run "pytest: $svc" {
        Push-Location (Join-Path $Root "apps\$svc")
        try {
            if (-not (Test-Path .venv)) { python -m venv .venv }
            & .\.venv\Scripts\python.exe -m pip install -q -r requirements-dev.txt
            & .\.venv\Scripts\python.exe -m pytest -q
        } finally { Pop-Location }
    }
}
Run "vitest: frontend" {
    Push-Location (Join-Path $Root "apps\frontend")
    try { npm install --no-audit --no-fund; npm test } finally { Pop-Location }
}
Run "maven verify: orders-service (in Docker)" {
    $dir = (Join-Path $Root "apps\orders-service")
    docker run --rm -v "${dir}:/w" -v cloudops-m2:/root/.m2 -w /w maven:3.9-eclipse-temurin-21 mvn -B -ntp verify
}
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
$results.GetEnumerator() | ForEach-Object { Write-Host ("{0,-45} {1}" -f $_.Key, $_.Value) -ForegroundColor $(if ($_.Value -eq "PASS") { "Green" } else { "Red" }) }
if ($results.Values -contains "FAIL") { exit 1 }
