<# Fills the AWS environment values in the GitOps repo from `terraform output` values. Changes local files only. #>
param(
    [Parameter(Mandatory = $true)][string]$EcrRegistry,       # terraform output ecr_registry
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$BackendRoleArn,    # terraform output backend_role_arn
    [Parameter(Mandatory = $true)][string]$CiPrivateIp,       # terraform output ci_server_private_ip
    [string]$GitOpsPath
)
. "$PSScriptRoot\_common.ps1"
$gitops = Get-GitOpsPath $GitOpsPath
$map = @{ "__ECR_REGISTRY__" = $EcrRegistry; "__AWS_REGION__" = $Region; "__BACKEND_ROLE_ARN__" = $BackendRoleArn; "__CI_SERVER_PRIVATE_IP__" = $CiPrivateIp }
Get-ChildItem (Join-Path $gitops "envs\aws") -Filter *.yaml | ForEach-Object {
    $t = Get-Content $_.FullName -Raw
    foreach ($k in $map.Keys) { $t = $t.Replace($k, $map[$k]) }
    Set-Content -Path $_.FullName -Value $t -NoNewline -Encoding utf8
}
Write-Host "Updated envs/aws. Review with 'git diff', commit and push the GitOps repo." -ForegroundColor Green
