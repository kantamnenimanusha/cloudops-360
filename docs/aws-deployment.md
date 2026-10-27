# AWS deployment guide (billable - read fully before starting)

**Rules:** nothing here runs automatically. Every `apply` is preceded by a `plan` you read. You destroy at the end of each session.
Forgetting to destroy costs roughly **$10 per day** (EKS control plane $0.10/h + 2x t3.large + CI server + public IPv4 addresses).

## 0. Before spending anything
1. Billing console: confirm your credit balance, expiry date and which services credits cover. New accounts may be on the *Free plan*,
   which restricts some services; if EKS is blocked, upgrade to the Paid plan (unused credits are kept).
2. Create an IAM Identity Center or IAM user with MFA for daily work; never use the root user; never create access keys for CI (roles are used).
3. Install Terraform (>= 1.10) and AWS CLI; run `aws configure sso` (or `aws configure` for a restricted IAM user) and `aws sts get-caller-identity`.
4. **Verify the current price** of everything in the AWS Pricing Calculator for your region (EKS, t3.large, public IPv4, NAT gateway, ALB if used).
5. Pick a Kubernetes version that is in **standard** support: https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
   (extended support costs about 6x more per hour for the control plane).

## 1. One-time, near-free: state bucket, ECR, budget alerts
```powershell
cd infra\terraform\bootstrap
terraform init
terraform plan  -var region=<region> -var state_bucket_name=<globally-unique-name>
terraform apply -var region=<region> -var state_bucket_name=<globally-unique-name>   # review the plan first

cd ..\envs\persistent
copy terraform.tfvars.example terraform.tfvars   # edit: region, budget_email
copy backend.tf.example backend.tf               # edit: bucket, region
terraform init; terraform plan; terraform apply  # ECR repositories + budget alerts at $25/$50/$75
```
Confirm the budget e-mail subscription. Cost: cents per month.

## 2. Session: create -> use -> destroy
```powershell
cd infra\terraform\envs\session
copy terraform.tfvars.example terraform.tfvars   # set cluster_version, admin_cidrs=["<your-ip>/32"], key_name
copy backend.tf.example backend.tf
terraform init
terraform plan -out tfplan        # READ IT. Expect ~35 resources. Estimated cost: ~$0.40-0.45/hour
terraform apply tfplan            # ~15 minutes
terraform output
```
Then:
```powershell
aws eks update-kubeconfig --region <region> --name cloudops360
kubectl get nodes                                  # 2 nodes Ready

# Fill the AWS values in the GitOps repo, commit and push
..\..\..\..\scripts\windows\aws-configure-gitops.ps1 -EcrRegistry <ecr_registry> -Region <region> -BackendRoleArn <backend_role_arn> -CiPrivateIp <ci_server_private_ip>

# Configure the CI server (from WSL2 Ubuntu; ansible is not supported natively on Windows)
cd infra/ansible; cp inventory.ini.example inventory.ini   # edit IP/key
ansible-galaxy collection install -r requirements.yml
ansible-playbook playbooks/site.yml --extra-vars @secrets.yml   # secrets.yml is git-ignored (github_user, github_token, repo URLs, passwords)
ansible-playbook playbooks/site.yml --extra-vars @secrets.yml   # run twice: second run must show changed=0
```
Install Argo CD on EKS (same manifest as locally), create namespaces/secrets (reuse the logic of `06-bootstrap-gitops.ps1`
with your kubectl context pointing at EKS), then `kubectl apply -f ..\cloudops-360-gitops\argocd\project.yaml` and `root-app-aws.yaml`.
Push images with Jenkins on the CI server (`REGISTRY=<ecr_registry>`, `AWS_REGION=<region>`, `GITOPS_ENV=aws`) - first run uses the 0.1.0 tags,
so build once with those parameters. Jenkins SCM polling is used (no webhook) because the CI server IP changes every session.

## 3. End every session
```powershell
cd infra\terraform\envs\session
terraform destroy                 # read the list; type yes
..\..\..\..\scripts\windows\aws-cleanup-check.ps1 -Region <region>   # must show [clean] everywhere except ECR (pennies)
```
Check Cost Explorer the next day (billing data lags).

## Optional hardening experiment
Set `private_nodes = true` for one session: nodes move to private subnets behind one NAT gateway (~$0.05/h plus data processing).
Compare the security posture and cost in your write-up.
