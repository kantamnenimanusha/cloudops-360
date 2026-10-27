# CloudOps 360

A DevOps platform you can run on a Windows laptop for **$0**, then deploy to AWS (EKS) in short, budget-controlled sessions.

**What it is:** a real CI/CD + GitOps + observability pipeline (Jenkins, SonarQube, Trivy, Docker, Argo CD, Helm, Kubernetes,
Prometheus, Grafana, Loki, Jaeger, Alertmanager, Terraform, Ansible) **plus a dashboard** (React + FastAPI) that reads those tools
through their real APIs. If a tool is down, the dashboard says *unavailable* - it never shows invented data.

| Repo (this ZIP) | Purpose |
|---|---|
| `cloudops-360` (this one) | apps, Jenkins pipeline, Terraform, Ansible, scripts, docs |
| `cloudops-360-gitops` (second ZIP) | Helm charts + per-environment values that Argo CD deploys |

> **Honest status:** read [`CHECKLIST.md`](CHECKLIST.md) first. It lists what was actually executed during generation (pure-logic
> tests only) and what has **never been run** (almost everything that needs Docker, Kubernetes, Maven, npm, Terraform or AWS). Expect to fix small issues
> on first run; [`docs/troubleshooting.md`](docs/troubleshooting.md) covers the likely ones.

## 1. Prerequisites (Windows 10/11, 16 GB RAM)

Run `.\scripts\windows\00-check-prereqs.ps1` - it reports what is missing and prints `winget` install commands.
Needed: Docker Desktop (WSL2 backend), kind, kubectl, Helm, Git, Node.js 18+ (20 recommended), Python 3.12, VS Code.
Needed later for AWS only: Terraform >= 1.10, AWS CLI v2, Ansible (use WSL2 Ubuntu for Ansible).

**Give Docker 10-11 GB RAM.** Create `%UserProfile%\.wslconfig`:
```
[wsl2]
memory=11GB
processors=6
```
then `wsl --shutdown` and restart Docker Desktop. (SonarQube ~2.5 GB, Jenkins ~1.5 GB, kind + monitoring ~4-5 GB.)

You also need a GitHub account, two **empty** repositories named `cloudops-360` and `cloudops-360-gitops`, and a fine-grained
personal access token (Contents: read on the first repo, read+write on the second).

## 2. Extract and open

Extract both ZIPs **side by side** (the scripts expect `..\cloudops-360-gitops` next to this folder):
```
C:\work\cloudops-360\
C:\work\cloudops-360-gitops\
```
```powershell
cd C:\work\cloudops-360
code cloudops-360.code-workspace      # opens both repos in one VS Code window
```
`File > Open Folder` on `cloudops-360` in VS Code (or use the provided `.code-workspace` file to open both). Use a PowerShell terminal;
if scripts are blocked: `Set-ExecutionPolicy -Scope Process Bypass`.

## 3. Run the tests first (free, ~5-10 min first time)

```powershell
.\scripts\windows\test-all.ps1
```
Runs pytest (backend, inventory), Vitest (frontend) and `mvn verify` for the Spring Boot service inside a Maven container.

## 4. Bring up the local platform

```powershell
.\scripts\windows\01-configure.ps1 -GitHubUser <your-github-user>   # generates random secrets into git-ignored files, prompts for token
# Push both folders to GitHub (secrets are git-ignored; confirm with `git status` before pushing):
cd ..\cloudops-360-gitops; git init -b main; git add .; git commit -m "Initial GitOps"; git remote add origin https://github.com/<you>/cloudops-360-gitops.git; git push -u origin main
cd ..\cloudops-360;        git init -b main; git add .; git commit -m "Initial commit"; git remote add origin https://github.com/<you>/cloudops-360.git;        git push -u origin main

.\scripts\windows\02-create-cluster.ps1     # kind cluster + local registry (localhost:5001)
.\scripts\windows\03-start-ci.ps1           # SonarQube + Jenkins (several minutes the first time)
.\scripts\windows\04-install-argocd.ps1     # prints the Argo CD admin password
.\scripts\windows\05-build-push-images.ps1  # builds the 4 images once as :0.1.0
.\scripts\windows\06-bootstrap-gitops.ps1   # secrets + Argo CD root app (add -PrivateRepos if your repos are private)
.\scripts\windows\07-port-forward.ps1       # opens all UIs on localhost
```
Watch it converge: `kubectl -n argocd get applications -w` (first sync of the monitoring stack takes 5-10 minutes; transient
"CRD not found" errors resolve themselves through retries).

| UI | URL | Login |
|---|---|---|
| **CloudOps 360 dashboard** | http://localhost:8088 | `viewer` + `VIEWER_PASSWORD` from `local\.env` |
| Argo CD | https://localhost:8081 | `admin` + password from step 04 |
| Grafana | http://localhost:3000 | `admin` + `.\scripts\windows\grafana-password.ps1` |
| Prometheus / Alertmanager / Jaeger | :9090 / :9093 / :16686 | none (localhost only) |
| Jenkins | http://localhost:8080 | `admin` + `JENKINS_ADMIN_PASSWORD` |
| SonarQube | http://localhost:9000 | `admin` + `SONAR_ADMIN_PASSWORD` |

## 5. See it work

1. **Pipeline:** Jenkins > `orders-service` > *Build with Parameters* > Build. Stages: tests, SonarQube gate, Trivy, image, push, GitOps commit.
   Then watch Argo CD roll out the new tag and the dashboard's *CI/CD*, *Security*, *Deployments* pages update.
2. **Metrics/logs/traces:** `.\scripts\windows\demo.ps1 -Scenario load`, then Grafana "CloudOps 360 - Services", the dashboard *Logs* page, Jaeger (service `orders-service`).
3. **Failure + alert:** `demo.ps1 -Scenario errors` then `load` -> alert goes Pending -> Firing -> appears on the *Alerts* page; `-Scenario reset` -> resolved.
   More scenarios: [`docs/demo-guide.md`](docs/demo-guide.md).

## 6. Deploy to AWS (only after everything works locally)

Never automatic. Follow [`docs/aws-deployment.md`](docs/aws-deployment.md): it states the cost of each step, uses `terraform plan` before
every apply, and ends with `terraform destroy` + `aws-cleanup-check.ps1`. Typical session cost is a few dollars; **leaving it running costs roughly $10/day**.

## 6b. What you must configure manually

| What | Where |
|---|---|
| Install the tools in section 1; give Docker 10-11 GB RAM | your machine |
| Create two empty GitHub repos + a fine-grained token (Contents read on the app repo, read+write on the GitOps repo) | github.com |
| Run `01-configure.ps1` once and enter the token when prompted (never type it into a file) | PowerShell |
| Push both repos **after** `01-configure.ps1` (it fills in your GitHub user name) | PowerShell |
| First SonarQube login: the script changes the default admin password and creates Jenkins' token automatically; if that step prints a warning, do it in the UI and put the token in `local\.env` as `SONAR_TOKEN` | http://localhost:9000 |
| Pin third-party versions after the first green run | `docs/VERSIONS.md` |
| AWS: account plan/credits check, IAM user with MFA, `aws configure sso`, Kubernetes version in standard support, your public IP as `/32`, an EC2 key pair, a unique state-bucket name, budget e-mail | `docs/aws-deployment.md` |

## 7. Cleanup

```powershell
.\scripts\windows\cleanup-local.ps1          # removes kind cluster, registry, Jenkins/SonarQube containers and volumes
.\scripts\windows\aws-cleanup-check.ps1 -Region <region>   # read-only: lists anything on AWS that still costs money
```

## 8. Troubleshooting

See [`docs/troubleshooting.md`](docs/troubleshooting.md). First things to check: Docker memory, `kubectl get pods -A`,
`kubectl -n argocd get applications`, `docker compose -f local/docker-compose.yml --env-file local/.env logs <service>`.

## 9. Repository map

```
apps/{frontend,backend,orders-service,inventory-service}   source + tests + Dockerfiles
ci/jenkins/                 Jenkins image, Configuration-as-Code, Jenkinsfile
local/                      docker-compose (Jenkins, SonarQube), kind config
infra/terraform/            bootstrap | persistent (ECR, budget) | session (VPC, EKS, CI server)
infra/ansible/              CI server configuration
security/  .gitleaks.toml   scan policy, secret scanning config
scripts/windows/            every command you run (PowerShell)
docs/                       architecture, AWS guide, demos, cost, troubleshooting, learning + interview guides
```

## Security notes
No secrets are committed: `01-configure.ps1` generates them into git-ignored files; Kubernetes Secrets are created from those files at
bootstrap; AWS uses IAM roles (instance profile, IRSA), never access keys. Local Jenkins mounts the Docker socket (equivalent to host root) -
acceptable on your own laptop only. Run `gitleaks detect` before pushing.
