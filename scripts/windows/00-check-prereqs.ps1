<# Verifies the tools needed for the local (free) part of CloudOps 360. Installs nothing. #>
. "$PSScriptRoot\_common.ps1"
$ok = $true
function Check($cmd, $versionArgs, $installHint) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $v = (& $cmd @versionArgs 2>&1 | Select-Object -First 1)
        Write-Host ("[ OK ] {0,-10} {1}" -f $cmd, $v) -ForegroundColor Green
    } else {
        Write-Host ("[MISS] {0,-10} install: {1}" -f $cmd, $installHint) -ForegroundColor Red
        $script:ok = $false
    }
}
Check docker  @("--version")          "winget install Docker.DockerDesktop"
Check kind    @("--version")          "winget install Kubernetes.kind"
Check kubectl @("version", "--client") "winget install Kubernetes.kubectl"
Check helm    @("version", "--short") "winget install Helm.Helm"
Check git     @("--version")          "winget install Git.Git"
Check node    @("--version")          "winget install OpenJS.NodeJS.LTS  (Node 18+; 20 recommended)"
Check python  @("--version")          "winget install Python.Python.3.12"
Write-Host "--- optional (needed only for AWS phases) ---"
foreach ($t in @(@("terraform", "winget install Hashicorp.Terraform"), @("aws", "winget install Amazon.AWSCLI"))) {
    if (Get-Command $t[0] -ErrorAction SilentlyContinue) { Write-Host "[ OK ] $($t[0])" -ForegroundColor Green } else { Write-Host "[skip] $($t[0]) not installed yet: $($t[1])" -ForegroundColor Yellow }
}
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $mem = docker info --format '{{.MemTotal}}' 2>$null
    if ($mem) {
        $gb = [math]::Round([double]$mem / 1GB, 1)
        $color = if ($gb -ge 10) { "Green" } else { "Yellow" }
        Write-Host "Docker has $gb GB RAM available." -ForegroundColor $color
        if ($gb -lt 10) { Write-Host "Recommended >= 10 GB. Create %UserProfile%\.wslconfig with:`n[wsl2]`nmemory=11GB`nprocessors=6`nthen run: wsl --shutdown" -ForegroundColor Yellow }
    } else { Write-Host "Docker daemon is not running - start Docker Desktop." -ForegroundColor Red; $ok = $false }
}
if (-not $ok) { exit 1 }
Write-Host "`nPrerequisites satisfied." -ForegroundColor Green
