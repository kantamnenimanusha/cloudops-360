# Cost management

| Item | When it costs | Control |
|---|---|---|
| EKS control plane | $0.10/h while the cluster exists (6x if the K8s version is in extended support) | create only in sessions; `terraform destroy` |
| Worker nodes (2x t3.large) + EBS | per hour while running | same |
| CI server (t3.large) | per hour while running | same (`create_ci_server=false` for sessions that do not need it) |
| Public IPv4 addresses | $0.005/h each, even when idle | destroyed with the session |
| NAT gateway (optional) | $0.045/h + $0.045/GB (US East prices; vary by region) | `private_nodes=false` by default |
| ALB (not created by default) | $0.0225/h + usage | not used; access via port-forward |
| ECR, S3 state, budget | cents/month | persistent stack; images expire (keep last 15) |

Planned total for the project: roughly $35-45 against $150. Internal ceiling: $75. Budget alerts (e-mail) at $25/$50/$75 actual and 100% forecast
*notify only*. Run `aws-cleanup-check.ps1` after every session. All prices above must be re-verified in the AWS Pricing Calculator for your region before the first apply.
