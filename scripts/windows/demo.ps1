<#
 Controlled demonstrations. The failures are SIMULATED by token-protected endpoints in the demo apps; how Kubernetes,
 Prometheus and Alertmanager react is REAL. Usage: .\demo.ps1 -Scenario load|errors|latency|notready|crash|reset
#>
param([Parameter(Mandatory = $true)][ValidateSet("load", "errors", "latency", "notready", "crash", "reset")][string]$Scenario,
      [ValidateSet("orders-service", "inventory-service")][string]$Target = "orders-service", [int]$Seconds = 120)
. "$PSScriptRoot\_common.ps1"
$e = Read-DotEnv
$headers = @{ "X-Chaos-Token" = $e.CHAOS_TOKEN }
$port = if ($Target -eq "orders-service") { 18080 } else { 18000 }
$remote = if ($Target -eq "orders-service") { 8080 } else { 8000 }
$pf = Start-Process kubectl -ArgumentList @("port-forward", "-n", "cloudops", "svc/$Target", "${port}:${remote}") -WindowStyle Hidden -PassThru
Start-Sleep 4
$base = "http://localhost:$port"
try {
    switch ($Scenario) {
        "load" {
            Write-Host "Generating traffic against orders-service for $Seconds s (orders -> inventory -> traces/logs/metrics)..."
            $end = (Get-Date).AddSeconds($Seconds); $n = 0
            while ((Get-Date) -lt $end) {
                try {
                    Invoke-RestMethod -Method Post -Uri "$base/api/orders" -ContentType "application/json" -Body '{"sku":"SKU-1001","quantity":1,"customer":"demo"}' | Out-Null
                    Invoke-RestMethod "$base/api/orders" | Out-Null
                } catch { }
                $n++; Start-Sleep -Milliseconds 250
            }
            Write-Host "Sent ~$n request pairs. Look at Grafana 'CloudOps 360 - Services' and Jaeger (service: orders-service)."
        }
        "errors"   { Invoke-RestMethod -Method Post -Uri "$base/chaos/errors?rate=0.6" -Headers $headers; Write-Host "60% of $Target API calls now fail. Run '.\demo.ps1 -Scenario load' and watch alert CloudOpsHighErrorRate (Pending -> Firing)." }
        "latency"  { Invoke-RestMethod -Method Post -Uri "$base/chaos/latency?ms=1500" -Headers $headers; Write-Host "$Target now adds 1.5 s latency. Run load; alert CloudOpsHighLatencyP95 should fire after ~2 min." }
        "notready" { Invoke-RestMethod -Method Post -Uri "$base/chaos/ready?value=false" -Headers $headers; Write-Host "Readiness now fails: watch 'kubectl get pods -n cloudops -w' (READY 0/1) while liveness stays OK - pod is NOT restarted." }
        "crash"    { Invoke-RestMethod -Method Post -Uri "$base/chaos/crash" -Headers $headers; Write-Host "Process exits in 0.5 s. Watch RESTARTS increase and alert CloudOpsPodRestarting." }
        "reset"    { Invoke-RestMethod -Method Post -Uri "$base/chaos/reset" -Headers $headers; Write-Host "Chaos state reset on $Target." }
    }
} finally { Stop-Process -Id $pf.Id -Force -ErrorAction SilentlyContinue }
