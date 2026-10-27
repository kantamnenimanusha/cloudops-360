# Versions: what is pinned, what is not, what to verify

Nothing below was verified against a live registry while generating the project (no network access). Verify, run, then pin.

| Component | Where | Current setting | Action |
|---|---|---|---|
| Spring Boot | `apps/orders-service/pom.xml` | 3.5.0 | `mvn versions:display-parent-updates`; Trivy may flag CVEs in older releases - upgrade rather than ignore |
| Java | pom, Dockerfile | 21 | LTS |
| Python base image | Dockerfiles | `python:3.12-slim` | ok |
| Python deps | `requirements*.txt` | lower bounds only | after a green run: `pip freeze > constraints.txt` and use `-c` |
| Node / npm deps | `package.json` | caret ranges, no lockfile | run `npm install` once and commit `package-lock.json`, then switch Dockerfile/Jenkins to `npm ci` |
| nginx image | frontend Dockerfile | `nginxinc/nginx-unprivileged:1.27-alpine` | verify tag exists |
| SonarQube | `local/docker-compose.yml` | `sonarqube:community` (floating) | pin to the tag you tested |
| Jenkins | `ci/jenkins/Dockerfile` | `jenkins/jenkins:lts-jdk21`; plugins unpinned | pin plugin versions via `jenkins-plugin-cli` output |
| Argo CD | `04-install-argocd.ps1` | `stable` manifest | pin to a release tag |
| kube-prometheus-stack, metrics-server charts | `charts/argocd-apps/values.yaml` | `*` | **pin** after first success |
| Loki / Alloy / Jaeger images | `charts/observability-extras/values.yaml` | 3.2.0 / v1.5.1 / 1.62.0 (from memory) | `docker pull` each; bump to current. Jaeger v1 all-in-one is legacy: check the current v2 deployment model |
| Terraform / AWS provider | `versions` blocks | `>= 1.10`, `>= 5.60 < 7` | `terraform init -upgrade`, commit `.terraform.lock.hcl` |
| EKS Kubernetes version | `terraform.tfvars` | **no default** | choose a standard-support version |
| EC2 AMI | ci_server module | resolved from Canonical's SSM parameter (Ubuntu 24.04) | ok |
