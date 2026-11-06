# CloudOps 360

A cloud-native DevOps platform combining application services, CI/CD automation, Kubernetes deployment, infrastructure configuration, and observability.

CloudOps 360 is developed to run locally on a Windows machine and can also be deployed to AWS EKS through a separate, budget-controlled deployment process. Local development does not require AWS resources.

## What is CloudOps 360?

CloudOps 360 brings together a set of DevOps tools and application services:

- **Application:** React frontend, FastAPI backend, Inventory service, and Spring Boot Orders service.

- **CI/CD:** Jenkins and SonarQube.

- **Containers and orchestration:** Docker, Kubernetes, and Helm.

- **Observability:** Prometheus, Grafana, Grafana Alloy, and Loki.

- **Infrastructure automation:** Terraform and Ansible.

- **Security configuration:** Gitleaks and Trivy-related pipeline configuration.

- **GitOps configuration:** Helm charts, Argo CD application definitions, and environment-specific values maintained under `gitops/`.

The React dashboard communicates with backend integrations and displays information from connected tools. If an integration is unavailable, its status is reported as unavailable rather than being represented by fabricated data.

### Repository structure

| Directory | Purpose |

|---|---|

| `apps/` | Frontend, backend, Inventory service, and Orders service |

| `gitops/` | Helm charts, Argo CD application definitions, and environment-specific Kubernetes configuration |

| `infra/` | Terraform and Ansible infrastructure configuration |

| `scripts/` | Windows setup, verification, deployment, and cleanup scripts |

| `docs/` | Architecture, deployment, troubleshooting, demo, cost, and learning documentation |

See [Architecture](docs/architecture.md) for the system diagrams and implementation status.

## Project verification status

The following components have been implemented and exercised during development.

| Area | Verification status |

|---|---|

| Backend API | Automated tests executed successfully |

| Inventory service | Automated tests executed successfully |

| Orders service | Maven tests executed successfully |

| Jenkins CI | Orders-service pipeline build completed successfully |

| SonarQube | Integrated into the CI quality-gate workflow |

| Kubernetes | Cluster and application deployment work performed |

| Prometheus and Grafana | Metrics and dashboards verified |

| Loki and Alloy | Log collection and viewing pipeline verified |

| GitOps configuration | Helm charts and environment values consolidated under `gitops/`; active Argo CD reconciliation not verified |

| Terraform and Ansible | Configuration and automation files included; not every AWS operation has been independently verified |

### Current deployment limitations

The repository contains configuration for more integrations than have been verified as active services.

- **Argo CD:** Argo CD is not currently installed in the EKS cluster. The `gitops/` directory contains deployment configuration, but automatic Argo CD reconciliation is not active.

- **Jaeger and distributed tracing:** OpenTelemetry-related instrumentation and exporter configuration exist in parts of the source and configuration. End-to-end trace collection and display have not been verified. The Orders service's Jaeger exporter was disabled in the deployed workload, and Jaeger is not deployed in the EKS cluster.

- **Loki storage:** The deployed Loki configuration uses ephemeral storage. Logs may not survive pod recreation or cluster replacement.

- **Alloy discovery:** Alloy is configured to discover Kubernetes pods and forward container logs to Loki. Its configuration includes relabelling for the `cloudops` namespace; verify the deployed target selection before treating that namespace as an exclusive collection boundary.

- **AWS automation:** Terraform and Ansible files are included, but their presence does not mean every infrastructure operation has been tested.

See [CHECKLIST.md](CHECKLIST.md) for the detailed verification record and [docs/troubleshooting.md](docs/troubleshooting.md) for troubleshooting guidance.

Verification status describes work performed during development. It does not imply that every integration is production-ready.

---

## 1. Prerequisites

For local development on Windows 10/11:

- Windows 10/11 with WSL2.

- Docker Desktop using the WSL2 backend.

- kind.

- kubectl.

- Helm.

- Git.

- Node.js 18 or later (Node.js 20 recommended).

- Python 3.12.

- VS Code.

- PowerShell.

For AWS deployment only:

- AWS CLI v2.

- Terraform 1.10 or later.

- Ansible (WSL2 Ubuntu is recommended).

### Docker and WSL2 resources

A machine with 16 GB RAM is recommended for running the local platform.

Docker Desktop may need approximately 10 to 11 GB of memory for Jenkins, SonarQube, kind, and monitoring components together. Adjust this according to your machine's available memory.

Example `%UserProfile%\.wslconfig`:

```ini

[wsl2]

memory=11GB

processors=6

```

After changing the file, run:

```powershell

wsl --shutdown

```

Restart Docker Desktop afterwards.

### Check prerequisites

From the application repository, run:

```powershell

.\scripts\windows\00-check-prereqs.ps1

```

The script checks the required tools and reports missing dependencies.

---

## 2. Clone and open the repository

The application source, infrastructure configuration, documentation, and GitOps manifests are maintained in a single GitHub repository.

Clone the repository:

```powershell

git clone -b upgrade/spring-boot-4.0.9 https://github.com/kantamnenimanusha/cloudops-360.git

cd cloudops-360

## 3. Run the application tests

Run the project test script:

```powershell

.\scripts\windows\test-all.ps1

```

The script is intended to run:

- Backend and Inventory service tests using pytest.

- Frontend tests using Vitest.

- Orders service verification using Maven.

Individual services can also be tested separately using their respective project instructions.

The test results recorded in this repository's verification section reflect the tests executed during development. Run the test script again after making changes to verify the current checkout.

---

## 4. Local platform setup

The repository includes PowerShell scripts for configuring and starting the local development environment.

Before running them, inspect the scripts and their prerequisites. Configuration scripts may generate local secrets, create containers, and create Kubernetes resources.

### Configure local settings

```powershell

.\scripts\windows\01-configure.ps1 -GitHubUser kantamnenimanusha

```

This script is intended to generate local configuration and secrets in git-ignored files. Follow its prompts and never commit access tokens or generated credentials.

Before committing or pushing any changes, inspect:

```powershell

git status

```

### Local Kubernetes cluster

The repository includes a kind cluster setup script:

```powershell

.\scripts\windows\02-create-cluster.ps1

```

The script is intended to create a local Kubernetes cluster and registry.

### Jenkins and SonarQube

Start the local CI services:

```powershell

.\scripts\windows\03-start-ci.ps1

```

This script starts the local Jenkins and SonarQube environment. Initial startup may take several minutes.

### Additional local deployment scripts

The repository includes additional scripts for image building, optional Argo CD installation, GitOps bootstrapping, and port-forwarding. These scripts describe the intended local workflow; inspect their prerequisites and configuration before running them.

```powershell

.\scripts\windows\04-install-argocd.ps1

.\scripts\windows\05-build-push-images.ps1

.\scripts\windows\06-bootstrap-gitops.ps1

.\scripts\windows\07-port-forward.ps1

```

These scripts represent the intended local deployment workflow. Their presence should not be interpreted as proof that the complete workflow has been verified end to end.

In particular, the published EKS environment does not currently have Argo CD installed or actively reconciling the companion GitOps repository.

### Local service access

The following endpoints are associated with the local platform configuration. A service is accessible only when its corresponding component is running and its port-forwarding or local port mapping is active.

| Component | Local endpoint |

|---|---|

| CloudOps 360 dashboard | `http://localhost:8088` |

| Jenkins | `http://localhost:8080` |

| SonarQube | `http://localhost:9000` |

| Grafana | `http://localhost:3000` |

| Prometheus | `http://localhost:9090` |

| Alertmanager | `http://localhost:9093` |

| Argo CD | `https://localhost:8081` when installed and running |

Credentials are generated or configured locally. Refer to `local/.env` and the relevant password scripts for the applicable credentials. Do not publish these values.

Jaeger is not listed as an active service because end-to-end tracing has not been verified.

---

## 5. CI/CD and observability

### Jenkins and SonarQube

Jenkins is used to automate the Orders service build workflow. The Orders service pipeline has completed successfully during development.

SonarQube is integrated into the CI quality-gate workflow.

The repository also contains security scanning and image-building configuration. Do not assume that every configured pipeline stage or the complete automated deployment chain has been verified simply because the configuration exists.

### Kubernetes and GitOps

Kubernetes is used to run the application workloads. Helm charts and environment-specific configuration are maintained in the companion GitOps repository.

The intended architecture supports GitOps deployment through Argo CD. However, Argo CD is not currently installed in the EKS cluster, so automatic reconciliation is not active there.

### Metrics and dashboards

Prometheus collects metrics, and Grafana provides dashboards for monitoring the deployed services.

Metrics and dashboards have been exercised during development.

### Centralized logging with Grafana Alloy and Loki

Grafana Alloy is configured to discover Kubernetes pods, collect container logs using `loki.source.kubernetes`, and forward them to Loki using `loki.write`.

The Alloy configuration includes relabelling for the `cloudops` namespace. Verify the actual target selection in the deployed configuration before describing it as an exclusive namespace restriction.

The deployed Loki configuration uses ephemeral storage, so log retention across pod or cluster replacement is not guaranteed.

### Distributed tracing

OpenTelemetry-related instrumentation and exporter configuration exist in parts of the source and configuration.

However, distributed tracing to Jaeger is not an active, verified capability of the deployed environment. The Orders service's Jaeger exporter was disabled in the deployed workload, and Jaeger is not deployed in the EKS cluster.

---

## 6. AWS deployment

AWS deployment is optional. The project can be explored locally without provisioning AWS infrastructure.

The AWS deployment configuration is maintained under `infra/terraform/` and `infra/ansible/`. Deployment guidance is available in:

- [docs/aws-deployment.md](docs/aws-deployment.md)

- [docs](docs/)

### Before provisioning AWS resources

1. Check your AWS account plan, available credits, and credit expiry.

2. Review the cost implications of every resource.

3. Configure AWS authentication using the documented method.

4. Check the Kubernetes version and AWS region.

5. Review Terraform configuration and state management.

6. Run `terraform plan` before applying infrastructure changes.

7. Use short deployment sessions and monitor resource usage.

AWS services such as EKS, EC2, load balancers, NAT gateways, storage, and related resources may incur charges.

The actual cost depends on the resources, region, configuration, and time they remain active. Do not rely on a fixed daily cost estimate.

**Never run Terraform apply or provision billable resources without reviewing the plan and explicitly deciding to proceed.**

---

## 7. Cleanup

### Local cleanup

The repository includes a local cleanup script:

```powershell

.\scripts\windows\cleanup-local.ps1

```

According to the script's intended purpose, it removes the local kind cluster, registry, Jenkins/SonarQube containers, and associated volumes.

Review the script before running it. Removing volumes may delete locally stored Jenkins, SonarQube, or other platform data.

### AWS cleanup checks

The repository also includes a read-only AWS cleanup check:

```powershell

.\scripts\windows\aws-cleanup-check.ps1 -Region <region>

```

This is intended to list AWS resources that may still incur costs.

A cleanup check is not the same as resource deletion. Before deleting anything in AWS:

1. Inventory resources created specifically for this project.

2. Distinguish project resources from unrelated account resources.

3. Review dependencies and persistent data.

4. Confirm the exact resources to be deleted.

5. Perform cleanup and verify the result.

Do not delete unrelated AWS resources.

---

## 8. Security notes

- Local secrets are intended to be generated into git-ignored files.

- Do not commit `.env` files, private keys, access tokens, passwords, or Kubernetes credentials.

- Kubernetes Secrets should be created from local configuration during the relevant bootstrap process.

- AWS workloads should use IAM roles and appropriate workload identity mechanisms rather than hard-coded access keys.

- Local Jenkins mounts the Docker socket. Access to the Docker socket can provide privileges equivalent to root access on the host. Use this configuration only in a trusted local development environment.

- Run secret scanning before publishing repository changes.

Example:

```powershell

gitleaks detect

```

Review any findings before pushing.

---

## 9. Repository map

```text

cloudops-360/

│

├── apps/

│   ├── frontend/          React application

│   ├── backend/           FastAPI backend

│   ├── inventory-service/ Inventory service

│   └── orders-service/    Spring Boot service

│

├── ci/

│   └── jenkins/           Jenkins image, configuration, and pipeline

│

├── local/                 Docker Compose and local cluster configuration

│

├── infra/

│   ├── terraform/         AWS infrastructure configuration

│   └── ansible/           Server configuration automation

│

├── security/              Security scanning configuration

│

├── scripts/

│   └── windows/           PowerShell setup, test, and cleanup scripts

│

├── docs/                  Architecture, deployment, troubleshooting,

│                          demos, cost, and learning documentation

│

├── CHECKLIST.md           Project verification record

└── README.md              Project documentation

```

---

## 10. Further documentation

Refer to the following files for additional information:

- `CHECKLIST.md` — development and verification checklist.

- `docs/troubleshooting.md` — troubleshooting guidance.

- `docs/aws-deployment.md` — AWS deployment instructions.

- `docs/demo-guide.md` — available demonstration scenarios.

- `docs/VERSIONS.md` — third-party version information.

---

## Project objective

CloudOps 360 was developed to bring together application development, CI/CD, containerization, Kubernetes, infrastructure automation, and observability in one practical DevOps project.

The focus is on understanding how these tools fit together, how application services are built and deployed, how monitoring and logging work, and how infrastructure can be managed responsibly.

**The documentation distinguishes implemented functionality, verified behaviour, and configuration that remains inactive or unverified.**