# ☁️ CloudOps 360

### An End-to-End Cloud-Native DevOps Platform

**Automating application delivery, container orchestration, infrastructure management, and observability through an integrated DevOps workflow.**

<p align="center">
  <img src="https://img.shields.io/badge/Platform-CloudOps%20360-blue?style=for-the-badge" alt="CloudOps 360"/>
  <img src="https://img.shields.io/badge/CI%2FCD-Jenkins-red?style=for-the-badge&logo=jenkins" alt="Jenkins"/>
  <img src="https://img.shields.io/badge/Containers-Docker-2496ED?style=for-the-badge&logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/Orchestration-Kubernetes-326CE5?style=for-the-badge&logo=kubernetes" alt="Kubernetes"/>
  <img src="https://img.shields.io/badge/Monitoring-Prometheus-orange?style=for-the-badge&logo=prometheus" alt="Prometheus"/>
  <img src="https://img.shields.io/badge/Dashboards-Grafana-F46800?style=for-the-badge&logo=grafana" alt="Grafana"/>
</p>

<p align="center">
  <a href="#-project-overview">Overview</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-technology-stack">Tech Stack</a> •
  <a href="#-end-to-end-workflow">Workflow</a> •
  <a href="#-screenshots-and-demonstration">Screenshots</a> •
  <a href="#-installation-and-setup">Setup</a>
</p>

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Project Objectives](#-project-objectives)
3. [Architecture](#-architecture)
4. [Technology Stack](#-technology-stack)
5. [Application Architecture](#-application-architecture)
6. [End-to-End Workflow](#-end-to-end-workflow)
7. [CI/CD Pipeline](#-cicd-pipeline)
8. [Containerization and Kubernetes](#-containerization-and-kubernetes)
9. [GitOps](#-gitops)
10. [Infrastructure as Code](#-infrastructure-as-code)
11. [Monitoring and Observability](#-monitoring-and-observability)
12. [Logging Architecture](#-logging-architecture)
13. [Security](#-security)
14. [Screenshots and Demonstration](#-screenshots-and-demonstration)
15. [Installation and Setup](#-installation-and-setup)
16. [Testing and Verification](#-testing-and-verification)
17. [Troubleshooting](#-troubleshooting)
18. [Repository Structure](#-repository-structure)
19. [Limitations and Future Improvements](#-limitations-and-future-improvements)
20. [Learning Outcomes](#-learning-outcomes)
21. [Author](#-author)

---

## 🚀 Project Overview

CloudOps 360 is a cloud-native DevOps platform developed to bring together application development, continuous integration, containerization, deployment automation, infrastructure management, and observability in one integrated project.

In traditional application environments, development, testing, deployment, infrastructure management, and monitoring can operate as separate activities. This makes application delivery harder to manage and troubleshooting more time-consuming.

CloudOps 360 demonstrates how these activities can be organised into a connected DevOps workflow.

The platform combines a multi-service application with DevOps tools and cloud-native technologies to demonstrate how application components can be built, tested, containerised, and managed through an organised deployment workflow, with monitoring and logging capabilities.

### What does CloudOps 360 do?

- Provides a web-based application built with React and backend services.
- Uses Jenkins to automate application build and CI/CD activities.
- Integrates SonarQube into the code-quality workflow.
- Uses Docker to package application services into containers.
- Uses Kubernetes and Helm for container orchestration and deployment configuration.
- Maintains infrastructure automation using Terraform and Ansible.
- Uses Prometheus and Grafana for monitoring and visualisation.
- Uses Grafana Alloy and Loki for log collection and exploration.
- Maintains Helm charts, Argo CD application definitions, and environment-specific deployment configuration under the `gitops/` directory.
- Includes security-related configuration and practices for handling application and deployment workflows.

The project is intended as a hands-on demonstration of how different DevOps practices and tools can work together.

> **Project status:** This repository contains implemented application and DevOps components at different levels of verification. Not every optional integration or cloud deployment workflow is currently active. Refer to the testing and limitations sections for the verified status of individual components.

---

## 🎯 Project Objectives

The main objectives of CloudOps 360 are:

1. **Automate application delivery:** Understand how source-code changes move through a CI/CD pipeline.
2. **Improve code quality:** Integrate automated code analysis into the development workflow.
3. **Containerise services:** Package application components into Docker images.
4. **Orchestrate deployments:** Use Kubernetes to manage containerised workloads.
5. **Automate infrastructure:** Maintain reusable infrastructure configuration through Terraform.
6. **Automate configuration:** Use Ansible for server configuration tasks.
7. **Monitor applications:** Collect metrics and visualise system behaviour.
8. **Centralise logs:** Collect and query application and infrastructure logs.
9. **Understand GitOps:** Maintain deployment configuration in version control and understand declarative deployment practices.
10. **Improve troubleshooting:** Understand how build failures, deployment issues, metrics, and logs can be investigated.

---

## 🏗️ Architecture

CloudOps 360 brings together the application layer, CI/CD workflow, deployment environment, infrastructure automation, and observability components.

### High-Level System Architecture

```mermaid
flowchart TB
    DEV["Developer"]
    GIT["GitHub Repository<br/>cloudops-360"]

    subgraph APP["Application Layer"]
        FE["React Frontend"]
        BE["FastAPI Backend"]
        INV["Inventory Service"]
        ORD["Spring Boot Orders Service"]
    end

    subgraph CICD["CI/CD and Quality"]
        JEN["Jenkins"]
        SONAR["SonarQube"]
        DOCKER["Docker Image Build"]
    end

    subgraph DEPLOY["Container Orchestration"]
        K8S["Kubernetes"]
        HELM["Helm Configuration"]
        PODS["Application Workloads"]
    end

    subgraph OBS["Observability"]
        PROM["Prometheus"]
        ALERT["Alertmanager"]
        GRAF["Grafana"]
        ALLOY["Grafana Alloy"]
        LOKI["Loki"]
    end

    subgraph INFRA["Infrastructure Automation"]
        TF["Terraform"]
        ANS["Ansible"]
    end

    ARGO["Argo CD<br/>Not active in EKS"]

    DEV --> GIT
    GIT --> JEN
    JEN --> SONAR
    JEN --> DOCKER
    DOCKER --> K8S
    HELM --> K8S
    K8S --> PODS

    FE --> BE
    BE --> INV
    BE --> ORD

    PODS --> PROM
    PROM --> GRAF
    PROM --> ALERT
    PODS --> ALLOY
    ALLOY --> LOKI
    LOKI --> GRAF

    GIT -.-> ARGO
    ARGO -.-> K8S

    TF -.-> K8S
    ANS -.-> K8S
```

*The diagram represents the project's component relationships and intended architecture. The Argo CD, Terraform, and Ansible connections indicate intended responsibilities or configuration, not proof of active deployment or automatic execution. Actual deployment paths depend on the available manifests, scripts, and runtime configuration.*

### Architecture Layers

| Layer | Components | Responsibility |
|---|---|---|
| Source control | GitHub | Stores application source and configuration |
| Application | React, FastAPI, Spring Boot | Provides application functionality |
| CI/CD | Jenkins | Automates build and pipeline stages |
| Code quality | SonarQube | Analyses source code |
| Containerisation | Docker | Packages applications |
| Orchestration | Kubernetes | Manages container workloads |
| Deployment configuration | Helm, GitOps manifests | Defines Kubernetes application configuration |
| Infrastructure | Terraform | Defines infrastructure as code |
| Configuration management | Ansible | Automates server configuration |
| Monitoring | Prometheus | Collects metrics |
| Alerting | Alertmanager | Handles configured alerts |
| Visualisation | Grafana | Displays metrics and logs |
| Logging | Alloy and Loki | Collects and makes logs available for querying |

---

## 🧰 Technology Stack

### Application Development

| Technology | Purpose |
|---|---|
| React | Builds the frontend user interface |
| JavaScript | Frontend application logic |
| FastAPI | Provides Python-based backend APIs |
| Python | Backend and service implementation |
| Spring Boot | Implements the Orders service |
| Java | Orders service programming language |
| Maven | Builds and tests the Java application |

### DevOps and Deployment

| Technology | Purpose |
|---|---|
| Git and GitHub | Version control and source-code management |
| Jenkins | Continuous integration and delivery automation |
| SonarQube | Static code analysis and quality checks |
| Docker | Application containerisation |
| Kubernetes | Container orchestration |
| Helm | Kubernetes package and deployment configuration |
| Argo CD | GitOps controller configuration; active EKS reconciliation not currently verified |

### Infrastructure and Configuration

| Technology | Purpose |
|---|---|
| Terraform | Infrastructure as Code |
| Ansible | Configuration management and automation |
| AWS | Optional cloud deployment target |
| PowerShell | Windows automation and project scripts |
| Linux | Server and automation environment |

### Monitoring and Logging

| Technology | Purpose |
|---|---|
| Prometheus | Metrics collection |
| Grafana | Monitoring dashboards and data visualisation |
| Grafana Alloy | Telemetry collection and forwarding |
| Loki | Log aggregation and querying |
| Alertmanager | Alert handling where configured |

---

## 🖥️ Application Architecture

CloudOps 360 contains a frontend and multiple backend services.

### 1. Frontend – React

The frontend provides the user-facing application interface.

Its responsibilities include:

- Rendering application pages and components.
- Communicating with backend APIs.
- Presenting application information.
- Providing a user interface for interacting with the platform.

### 2. Backend – FastAPI

The FastAPI backend acts as an API layer for the application.

Its responsibilities include:

- Exposing backend endpoints.
- Handling application requests.
- Managing application configuration.
- Integrating with supporting services and configured DevOps endpoints.
- Providing diagnostic information about configured integrations.

### 3. Inventory Service

The Inventory service is implemented using Python and FastAPI.

It represents a separate service responsible for inventory-related application functionality.

### 4. Orders Service

The Orders service is implemented using Java and Spring Boot.

It provides a separate service boundary for order-related functionality and is included in the Jenkins CI/CD workflow.

### Application Request Flow

```mermaid
flowchart TD
    USER["User"]
    FRONT["React Frontend"]
    API["FastAPI Backend"]
    INV["Inventory Service"]
    ORD["Orders Service"]

    USER --> FRONT
    FRONT --> API
    API --> INV
    API --> ORD
    INV --> API
    ORD --> API
    API --> FRONT
    FRONT --> USER
```

*This is a logical application interaction diagram. Individual API routes and communication methods should be checked against the source code before treating every arrow as a confirmed runtime call.*

---

## 🔄 End-to-End Workflow

The intended DevOps workflow follows this sequence:

```mermaid
flowchart TD
    A["Developer makes code changes"]
    B["Push changes to GitHub"]
    C["Jenkins pipeline starts"]
    D["Checkout source code"]
    E["Build and run tests"]
    F["SonarQube code analysis"]
    G["Quality checks"]
    H["Build Docker image"]
    I["Image publication / registry step"]
    J["Kubernetes deployment configuration"]
    K["Application workloads"]
    L["Prometheus metrics"]
    M["Grafana dashboards"]
    N["Alloy log collection"]
    O["Loki log storage and querying"]

    A --> B --> C --> D --> E --> F --> G --> H --> I
    I --> J
    J -.-> K
    K --> L --> M
    K --> N --> O
```

### Workflow Explanation

1. **Development:** A developer makes changes to the application or supporting configuration.
2. **Version control:** Changes are stored in GitHub.
3. **Continuous integration:** Jenkins checks out the relevant source code and runs configured pipeline stages.
4. **Testing:** Automated tests validate application components.
5. **Code quality:** SonarQube analyses source code and provides quality information.
6. **Containerisation:** Docker packages application services into container images where configured.
7. **Deployment configuration:** Kubernetes manifests and Helm charts define how containerised workloads should run.
8. **Monitoring:** Prometheus collects available metrics and Grafana displays them.
9. **Logging:** Alloy collects configured logs and forwards them to Loki for querying and exploration.

The exact pipeline stages, image publication process, and deployment triggers depend on the Jenkinsfile and deployment configuration in the repository. The diagram does not imply that every build automatically triggers a Kubernetes deployment.

---

## ⚙️ CI/CD Pipeline

Jenkins is used as the CI/CD automation server in CloudOps 360.

The pipeline automates application delivery tasks and integrates code-quality checks.

### Jenkins Pipeline Responsibilities

- Source-code checkout.
- Application build.
- Automated test execution.
- SonarQube analysis.
- Quality-gate integration.
- Container image build and related delivery steps where configured.

### CI/CD Workflow

```mermaid
flowchart TD
    A["GitHub Source Code"]
    B["Jenkins"]
    C["Checkout"]
    D["Build"]
    E["Run Tests"]
    F["SonarQube Analysis"]
    G{"Quality Check"}
    H["Docker Image Build"]
    I["Image Delivery Step"]
    J["Deployment Workflow"]

    A --> B --> C --> D --> E --> F --> G
    G -->|Pass| H
    G -->|Fail| X["Pipeline reports failure"]
    H --> I --> J
```

### Jenkins

Jenkins automates the pipeline so that repeatable build and verification activities can be executed consistently.

### SonarQube

SonarQube is integrated into the CI quality-check workflow.

It helps analyse source code and identify potential quality issues. The pipeline uses its quality-check integration to make code-quality feedback part of the build process.

<badge color="success">Verified evidence</badge>

The `orders-service` Jenkins pipeline completed successfully in build **#16** after resolving a SonarQube credential issue.

*This does not mean that every possible pipeline stage or every service has been independently verified.*

---

## 🐳 Containerization and Kubernetes

### Docker

Docker is used to package application components into container images.

Containerisation provides:

- Consistent application packaging.
- Isolation between services.
- Repeatable execution environments.
- A standard image format for deployment.

Each service can be built and managed independently according to its Dockerfile and build configuration.

### Kubernetes

Kubernetes manages containerised workloads and provides orchestration capabilities.

The project includes Kubernetes deployment work and configuration for running application components.

Core Kubernetes concepts used in the project include:

| Kubernetes Resource | Purpose |
|---|---|
| Pod | Runs one or more containers |
| Deployment | Manages application pod replicas and updates |
| Service | Provides network access to selected pods |
| Namespace | Organises cluster resources |
| ConfigMap | Stores non-sensitive configuration |
| Secret | Stores sensitive configuration values |
| Helm | Packages and manages Kubernetes configuration |

Only resources present in the actual deployment manifests should be considered implemented.

### Deployment Flow

```mermaid
flowchart TD
    A["Application Source"]
    B["Dockerfile"]
    C["Docker Image"]
    D["Image Registry"]
    E["Kubernetes Manifests / Helm"]
    F["Kubernetes Deployment"]
    G["Application Pods"]
    H["Kubernetes Service"]
    I["Application Access"]

    A --> B --> C --> D --> E --> F --> G --> H --> I
```

*This represents the standard deployment flow. The exact registry, image-publishing process, and deployment trigger depend on the configured environment.*

---

## 🔁 GitOps

GitOps is a deployment-management approach in which the desired application and infrastructure configuration is maintained in version control.

CloudOps 360 maintains its GitOps configuration within the `gitops/` directory of the main repository. This includes Helm charts, Argo CD application definitions, and environment-specific Kubernetes configuration.

### GitOps Directory Structure

```text
gitops/
├── argocd/
├── charts/
└── envs/
```

The GitOps configuration is maintained alongside the application source code in the same GitHub repository. This keeps application development and deployment configuration organised under one version-controlled project.

### Intended GitOps Workflow

1. Application and deployment configuration are maintained in GitHub.
2. Helm charts define Kubernetes application resources.
3. Environment-specific values customise deployments.
4. Argo CD can monitor the Git repository and reconcile the desired cluster state when installed and configured.

### Current GitOps Status

GitOps configuration is maintained in the repository, but Argo CD is not installed in the EKS environment described by this project.

Therefore:

- GitOps manifests and Helm charts are available in `gitops/`.
- Active Argo CD reconciliation is not currently claimed.
- Automatic deployment triggered by GitOps synchronisation has not been verified.
- The presence of GitOps configuration should not be confused with an active GitOps controller.

---

## ☁️ Infrastructure as Code

Infrastructure as Code allows infrastructure configuration to be defined and maintained through version-controlled files.

### Terraform

Terraform is included for defining infrastructure resources.

Its purpose is to:

- Describe infrastructure declaratively.
- Maintain reusable configuration.
- Review planned changes before applying them.
- Support repeatable infrastructure provisioning.

Typical Terraform workflow:

```mermaid
flowchart TD
    A["Terraform Configuration"]
    B["terraform init"]
    C["terraform validate"]
    D["terraform plan"]
    E{"Review Plan"}
    F["terraform apply"]
    G["Provisioned Resources"]

    A --> B --> C --> D --> E
    E -->|Approved| F --> G
    E -->|Not Approved| H["Revise Configuration"]
```

Example commands:

```powershell
terraform init
terraform validate
terraform plan
```

Do not run `terraform apply` against a real AWS account without reviewing the plan, permissions, budget, and resource impact.

### Ansible

Ansible is used for configuration-management automation.

It can automate tasks such as:

- Installing required packages.
- Configuring Linux servers.
- Managing services.
- Applying repeatable configuration through playbooks.

Example command pattern:

```bash
ansible-playbook -i inventory.ini playbook.yml
```

Use the actual inventory and playbook names present in the repository.

### AWS Deployment

AWS is an optional deployment target.

Terraform and Ansible configuration should not be treated as proof that all infrastructure has been provisioned successfully.

Refer to the infrastructure files and their verification status before attempting cloud deployment.

---

## 📊 Monitoring and Observability

Monitoring helps understand the health and performance of applications and infrastructure.

CloudOps 360 uses Prometheus and Grafana as its monitoring and visualisation components.

### Prometheus

Prometheus collects metrics from configured targets.

Metrics can help identify:

- Application availability.
- Service behaviour.
- Resource utilisation.
- Performance changes.
- Potential operational issues.

The actual metrics depend on the exporters and scrape targets configured in the project.

### Grafana

Grafana provides dashboards for visualising metrics.

It allows collected data to be presented through graphs, panels, and dashboards.

### Monitoring Flow

```mermaid
flowchart LR
    APP["Application / Cluster"]
    TARGET["Configured Metrics Targets"]
    PROM["Prometheus"]
    GRAF["Grafana Dashboard"]

    APP --> TARGET --> PROM --> GRAF
```

Prometheus metrics and Grafana dashboards have been checked in the project environment.

### Alerting

Alertmanager is included in the project's monitoring configuration where configured.

It is intended to receive and manage alerts generated by Prometheus alert rules. Its complete alert-delivery workflow should be verified against the active rules, routes, receivers, and webhook configuration before claiming end-to-end alerting.

---

## 📝 Logging Architecture

Logging provides information about application and system activity.

CloudOps 360 uses Grafana Alloy and Loki for its log-collection workflow.

### Grafana Alloy

Alloy is used as the telemetry collection and forwarding component.

It can discover and collect logs from configured sources and forward them to Loki.

### Loki

Loki is the log aggregation system.

It stores log data and makes it available for querying and exploration through Grafana.

### Logging Flow

```mermaid
flowchart TD
    A["Application Containers"]
    B["Kubernetes Pod Logs"]
    C["Grafana Alloy"]
    D["Loki"]
    E["Grafana"]
    F["Log Exploration"]

    A --> B --> C --> D --> E --> F
```

### Logging Status and Limitation

The Alloy and Loki log collection and viewing workflow has been verified.

The current Loki configuration uses ephemeral storage. This means log data may not survive pod or cluster replacement.

The Alloy configuration also needs to be interpreted according to its actual discovery and relabelling rules. Do not assume that collection is restricted exclusively to the `cloudops` namespace without verifying the active targets.

---

## 🔐 Security

Security is an important part of a DevOps workflow.

CloudOps 360 includes security-related configuration and practices such as:

- Keeping sensitive environment files out of version control.
- Using configuration files for environment-specific settings.
- Integrating code-quality checks into CI/CD.
- Maintaining secret-scanning configuration.
- Including container security scanning configuration where present.
- Avoiding the storage of credentials in source code.

### Important Security Consideration

The local Jenkins setup mounts the Docker socket. Access to the Docker socket can provide privileges equivalent to root access on the host.

This setup should therefore be used only in a trusted local development environment and not exposed as an unrestricted shared service.

Before publishing changes:

```powershell
git status
```

Review staged and unstaged files carefully and ensure that secrets, private keys, local environment files, and credentials are not committed.

---

## 📸 Screenshots and Demonstration

This section showcases the major components of the CloudOps 360 platform through screenshots captured from the local development environment.

### 1. CloudOps Dashboard

Shows the application dashboard and its service overview.

<!-- Add screenshot: docs/images/cloudops-dashboard.png -->

### 2. Jenkins CI/CD Pipeline

Shows the Jenkins pipeline execution and build stages.

<!-- Add screenshot: docs/images/jenkins-pipeline.png -->

### 3. SonarQube Code Analysis

Shows code quality analysis and quality gate results.

<!-- Add screenshot: docs/images/sonarqube-analysis.png -->

### 4. Kubernetes Workloads

Shows the Kubernetes deployments, pods, and services.

<!-- Add screenshot: docs/images/kubernetes-workloads.png -->

### 5. Grafana Monitoring Dashboard

Shows application and infrastructure monitoring metrics.

<!-- Add screenshot: docs/images/grafana-dashboard.png -->

### 6. Prometheus Targets

Shows the monitoring targets and their scrape status.

<!-- Add screenshot: docs/images/prometheus-targets.png -->

### 7. Loki Log Monitoring

Shows application logs collected and queried through Loki.

<!-- Add screenshot: docs/images/loki-logs.png -->

Screenshots will be added after capturing and verifying each component in the running environment. They will represent actual project execution rather than illustrative images.

---

## 🛠️ Installation and Setup

The project has been developed with a Windows-based local workflow using PowerShell, Docker Desktop, and supporting DevOps tools.

### Prerequisites

Install the tools required by the parts of the project you intend to run.

| Tool | Purpose |
|---|---|
| Git | Clone and manage the repository |
| Docker Desktop | Build and run containers |
| WSL2 | Linux environment for Docker Desktop |
| kubectl | Interact with Kubernetes |
| kind | Local Kubernetes cluster, where used |
| Helm | Manage Kubernetes charts |
| Python | Run Python services and tests |
| Node.js and npm | Run the React frontend |
| Java | Build and run the Orders service |
| Maven | Java build and test automation |
| AWS CLI | Optional AWS operations |
| Terraform | Infrastructure as Code |
| Ansible | Configuration management |

The repository includes a prerequisite-check script:

```powershell
.\scripts\windows\00-check-prereqs.ps1
```

Review its output and install any missing dependencies.

### Step 1: Clone the Main Repository

```powershell
git clone -b upgrade/spring-boot-4.0.9 https://github.com/kantamnenimanusha/cloudops-360.git

cd cloudops-360
```

### Step 2: Review the Project Structure

```powershell
Get-ChildItem
```

Read the configuration and documentation before starting services.

### Step 3: Configure the Local Environment

The project contains a local configuration script:

```powershell
.\scripts\windows\01-configure.ps1 -GitHubUser YOUR_GITHUB_USERNAME
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

Review the script before executing it. It may generate local configuration and secrets, so never commit the resulting sensitive files.

### Step 4: Run Tests

The repository provides a test script:

```powershell
.\scripts\windows\test-all.ps1
```

This is intended to run the configured test suites for the backend, inventory service, frontend, and Orders service.

Check the script output to confirm which test suites completed successfully.

### Step 5: Local Infrastructure and Deployment

The repository contains additional scripts for local cluster creation, CI services, image building, GitOps configuration, and port forwarding.

Review each script and its prerequisites before running it.

The main local setup scripts are:

```powershell
.\scripts\windows\02-create-cluster.ps1
.\scripts\windows\03-start-ci.ps1
```

The GitOps configuration is already maintained under the `gitops/` directory in this repository. There is no need to clone or manually copy a separate GitOps repository.

Scripts for Argo CD installation, image building, GitOps bootstrapping, and port forwarding are optional workflows. Run them only when intentionally testing those components and after reviewing their prerequisites.

Argo CD is not currently installed in the EKS environment described in the project verification notes. The availability of deployment scripts and manifests does not indicate that GitOps synchronization is active.

### Step 6: Verify the Environment

Use the appropriate commands for the components you have started.

```powershell
docker ps
kubectl get nodes
kubectl get pods -A
kubectl get services -A
```

For a local Kubernetes environment, these commands help verify cluster and workload status.

---

## 🧪 Testing and Verification

Testing is used to validate application functionality and reduce the risk of regressions.

### Test Technologies

| Component | Testing Tool |
|---|---|
| FastAPI backend | pytest |
| Inventory service | pytest |
| Frontend | Vitest |
| Orders service | Maven tests |

### Known Verification Evidence

| Component | Known result | Status |
|---|---|---|
| Backend API | Backend test suite executed successfully in recorded runs | Verified in recorded runs |
| Inventory service | 12 tests passed in a recorded run | Verified in that run |
| Orders service | 13 tests, 0 failures, 0 errors in a recorded run | Verified in that run |
| Jenkins Orders pipeline | Build #16 completed successfully after a SonarQube credential fix | Verified |
| SonarQube | Integrated into the CI quality-check workflow | Integration verified |
| Kubernetes | Cluster and application deployment work performed | Deployment work verified; current state may vary |
| Prometheus | Metrics and dashboards checked | Verified |
| Grafana | Monitoring dashboards checked | Verified |
| Alloy and Loki | Log collection and viewing checked | Verified |
| Argo CD | Not installed in the EKS environment described | Not active there |
| Jaeger | Not deployed in EKS; end-to-end tracing not verified | Not verified |
| Terraform and Ansible | Configuration files available | Not all infrastructure operations verified |
| AWS deployment | Optional configuration exists | Not claimed as fully deployed |

Test results are historical evidence from recorded runs. Re-run the tests in the current environment before using the results as a new release certification.

---

## 🧯 Troubleshooting

### Docker Desktop resource issues

If Docker containers fail to start or become unstable:

- Check Docker Desktop resource allocation.
- Check WSL2 memory settings.
- Close unnecessary containers and applications.
- Restart Docker Desktop after changing WSL configuration.

### Kubernetes pods not starting

Check pod status:

```powershell
kubectl get pods -A
```

Inspect a specific pod:

```powershell
kubectl describe pod <pod-name> -n <namespace>
```

Review logs:

```powershell
kubectl logs <pod-name> -n <namespace>
```

### Jenkins pipeline failure

Check:

- Jenkins console output.
- Source checkout configuration.
- Tool versions.
- Build and test output.
- SonarQube credentials and connectivity.
- Docker image build logs.

### Application connectivity issues

Check:

- Whether the required containers are running.
- Whether Kubernetes services exist.
- Whether the correct ports are exposed.
- Whether environment variables are configured.
- Whether the backend endpoints are reachable.

### Monitoring or logging issues

Check:

```powershell
kubectl get pods -A
kubectl get services -A
```

Also inspect the Prometheus targets, Alloy logs, Loki availability, and Grafana data-source configuration.

---

## 📁 Repository Structure

CloudOps 360 follows a single-repository structure that keeps application source code, deployment configuration, infrastructure automation, and documentation together.

```text
cloudops-360/
│
├── apps/
│   ├── backend/             # FastAPI backend
│   ├── frontend/            # React frontend
│   ├── inventory-service/   # Inventory microservice
│   └── orders-service/      # Spring Boot microservice
│
├── gitops/
│   ├── argocd/              # Argo CD application definitions
│   ├── charts/              # Helm charts
│   ├── envs/                # Environment-specific configuration
│   └── README.md            # GitOps documentation
│
├── docs/
│   ├── architecture.md      # System architecture and workflows
│   └── images/              # Project screenshots
│
├── infra/                   # Infrastructure as Code and automation
├── scripts/                 # Setup, verification, and utility scripts
│
├── .gitignore
└── README.md
```

### Directory Responsibilities

| Directory | Purpose |
|---|---|
| `apps/` | Contains the application frontend, backend, and microservices. |
| `gitops/` | Contains Helm charts, Argo CD definitions, and environment configuration. |
| `docs/` | Contains architecture documentation and project screenshots. |
| `infra/` | Contains infrastructure automation configuration. |
| `scripts/` | Contains setup, verification, and utility scripts. |

The directory tree is a high-level overview rather than an exhaustive listing of every project file. Additional configuration and support files may exist at the repository root and inside individual directories.

The GitOps configuration is maintained inside the main repository. The presence of Argo CD manifests does not mean that an Argo CD controller is actively synchronising the cluster.

---

## ⚠️ Limitations and Future Improvements

CloudOps 360 demonstrates the integration of application development, CI/CD, containerization, Kubernetes, infrastructure automation, and observability. However, some components represent planned capabilities or configurations that have not yet been fully deployed or verified.

### Current Limitations

- **GitOps synchronization:** GitOps manifests and Helm charts are maintained in the `gitops/` directory. Argo CD is not currently installed in the EKS environment, so active reconciliation and automatic GitOps-based deployment have not been verified.
- **AWS deployment:** Terraform and Ansible configurations are included, but the complete AWS infrastructure deployment workflow has not been independently verified end to end.
- **Distributed tracing:** Jaeger is not currently deployed as an active tracing component. End-to-end distributed tracing has not been verified.
- **Log persistence:** Loki uses ephemeral storage, so collected logs may not survive pod replacement or restarts.
- **Jenkins security:** The local Jenkins setup uses Docker socket access. This grants Jenkins significant control over the Docker host and is suitable only for a trusted local development environment.
- **Production readiness:** The project is a learning and portfolio implementation. It requires additional security hardening, persistent storage, access controls, and operational validation before production use.

### Future Improvements

- Deploy and configure Argo CD to enable verified GitOps synchronization.
- Complete and validate the AWS infrastructure deployment using Terraform.
- Introduce persistent storage for Loki.
- Deploy Jaeger and verify end-to-end distributed tracing.
- Strengthen Jenkins security and credential management.
- Add automated deployment and rollback verification.
- Improve monitoring, alerting, and operational documentation.

These improvements represent future work and should not be interpreted as already implemented functionality.

---

## 🎓 Learning Outcomes

Working on CloudOps 360 provides practical exposure to:

- Version control and collaborative development using Git and GitHub.
- CI/CD pipeline creation and troubleshooting with Jenkins.
- Code-quality integration using SonarQube.
- Containerisation using Docker.
- Kubernetes workloads and service management.
- Helm-based deployment configuration.
- Infrastructure as Code using Terraform.
- Configuration management using Ansible.
- Monitoring using Prometheus and Grafana.
- Log collection and analysis using Alloy and Loki.
- Understanding GitOps principles and deployment configuration.
- Debugging and troubleshooting across application and infrastructure layers.

The project brings these concepts together in one practical environment and helps demonstrate how DevOps tools support the application lifecycle.

---

## 👩‍💻 Author

**Manusha Kantamaneni**

Computer Science and Engineering | DevOps and Cloud Technology Enthusiast

- GitHub: [kantamnenimanusha](https://github.com/kantamnenimanusha)
- LinkedIn: [Manusha Kantamaneni](https://www.linkedin.com/in/manusha-kantamneni-47634b375/)

---

## ⭐ Acknowledgement

CloudOps 360 is a hands-on learning project focused on understanding and integrating DevOps, cloud-native technologies, automation, and observability practices.

Thank you for visiting the repository!

If you find the project useful, feel free to explore the code, review the documentation, and share feedback.

---

<p align="center">
  <b>CloudOps 360 — Bringing Development, Deployment, and Observability Together.</b>
</p>
