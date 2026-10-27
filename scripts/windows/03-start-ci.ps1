<# Starts SonarQube, bootstraps its admin password + analysis token, then starts Jenkins. #>
. "$PSScriptRoot\_common.ps1"
Assert-Command docker "Install Docker Desktop."
$compose = @("compose", "-f", (Join-Path $Root "local\docker-compose.yml"), "--env-file", $EnvFile)

Write-Host "Starting SonarQube (first start takes 2-4 minutes)..."
Invoke-Checked { docker @compose up -d sonarqube } "start sonarqube"
$e = Read-DotEnv
$base = "http://localhost:9000"
$deadline = (Get-Date).AddMinutes(8)
do {
    Start-Sleep 5
    try { $status = (Invoke-RestMethod "$base/api/system/status").status } catch { $status = "starting" }
    Write-Host "  sonarqube: $status"
} while ($status -ne "UP" -and (Get-Date) -lt $deadline)
if ($status -ne "UP") { throw "SonarQube did not become UP. Check: docker compose -f local/docker-compose.yml logs sonarqube" }

if (-not $e.SONAR_TOKEN) {
    $new = $e.SONAR_ADMIN_PASSWORD
    $cred = { param($p) @{ Authorization = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:$p")) } }
    try {   # first run: default password is still in place
        Invoke-RestMethod -Method Post -Uri "$base/api/users/change_password" -Headers (& $cred "admin") `
            -Body @{ login = "admin"; previousPassword = "admin"; password = $new } | Out-Null
        Write-Host "SonarQube admin password changed from the default."
    } catch { Write-Host "Admin password already changed (or change failed) - continuing." }
    $tok = Invoke-RestMethod -Method Post -Uri "$base/api/user_tokens/generate" -Headers (& $cred $new) -Body @{ name = "jenkins-$(Get-Date -Format yyyyMMddHHmmss)" }
    Set-DotEnvValue "SONAR_TOKEN" $tok.token
    Write-Host "Created SonarQube token for Jenkins (stored in local\.env)."
}

Write-Host "Building and starting Jenkins (first build downloads plugins: several minutes)..."
Invoke-Checked { docker @compose up -d --build jenkins } "start jenkins"
Write-Host "SonarQube: http://localhost:9000  (admin / SONAR_ADMIN_PASSWORD in local\.env)"
Write-Host "Jenkins:   http://localhost:8080  (admin / JENKINS_ADMIN_PASSWORD in local\.env)"
