<# READ-ONLY. Lists AWS resources that keep costing money. Run it after EVERY AWS session. Creates/deletes nothing. #>
param([Parameter(Mandatory = $true)][string]$Region)
$ErrorActionPreference = "Continue"
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) { throw "AWS CLI not installed." }
$found = 0
function Section($title, $items) {
    $items = @($items | Where-Object { $_ -and $_ -ne "None" })
    if ($items.Count -gt 0) { Write-Host "[COSTING] $title" -ForegroundColor Red; $items | ForEach-Object { "   $_" }; $script:found += $items.Count }
    else { Write-Host "[clean]   $title" -ForegroundColor Green }
}
Section "EKS clusters (control plane ~`$0.10/h)"        ((aws eks list-clusters --region $Region --query "clusters[]" --output text) -split "\s+")
Section "EC2 instances running/pending"                 (aws ec2 describe-instances --region $Region --filters Name=instance-state-name,Values=running,pending --query "Reservations[].Instances[].[InstanceId,InstanceType]" --output text)
Section "NAT gateways (available)"                      ((aws ec2 describe-nat-gateways --region $Region --filter Name=state,Values=available --query "NatGateways[].NatGatewayId" --output text) -split "\s+")
Section "Load balancers (ALB/NLB)"                      ((aws elbv2 describe-load-balancers --region $Region --query "LoadBalancers[].LoadBalancerName" --output text) -split "\s+")
Section "Elastic IPs"                                   ((aws ec2 describe-addresses --region $Region --query "Addresses[].PublicIp" --output text) -split "\s+")
Section "Unattached EBS volumes"                        ((aws ec2 describe-volumes --region $Region --filters Name=status,Values=available --query "Volumes[].VolumeId" --output text) -split "\s+")
Section "Secrets Manager secrets (~`$0.40/month each)"  ((aws secretsmanager list-secrets --region $Region --query "SecretList[].Name" --output text) -split "\s+")
Write-Host "`nECR repositories (pennies): " -NoNewline; aws ecr describe-repositories --region $Region --query "repositories[].repositoryName" --output text
Write-Host "`n$found billable-looking item(s) found." -ForegroundColor $(if ($found) { "Red" } else { "Green" })
Write-Host "Also check Billing > Cost Explorer, and remember: charges can lag by several hours."
