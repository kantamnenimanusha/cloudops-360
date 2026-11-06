# Architecture

## System overview

The diagram shows the project's application, CI, Kubernetes and observability components. It distinguishes the implemented workflow from integrations that are configured but not actively running.

```mermaid
flowchart LR
    DEV["Developer"] -->|git push| GH["GitHub: cloudops-360"]
    GH --- GITOPS["gitops/: Helm charts, Argo CD apps and environment values"]

    GH -->|checkout| JK["Jenkins CI"]
    JK --> SQ["SonarQube"]
    JK --> TV["Trivy"]
    JK -->|build and push image| REG["Container registry: local / ECR"]

    subgraph K8S["Kubernetes: kind locally / EKS when provisioned"]
        subgraph WL["Application workloads: namespace cloudops"]
            FE["Frontend: React / Nginx"] --> BE["Backend: FastAPI"]
            ORD["Orders service: Spring Boot"] --> INV["Inventory service: FastAPI"]
        end

        subgraph OBS["Observability: namespace monitoring"]
            PROM["Prometheus"]
            AM["Alertmanager"]
            ALLOY["Grafana Alloy"]
            LOKI["Loki"]
            GRAF["Grafana"]
        end

        WL -->|metrics| PROM
        WL -->|logs| ALLOY
        ALLOY --> LOKI
        PROM --> GRAF
        LOKI --> GRAF
        PROM --> AM
    end

    REG -.->|image pull| WL

    ARGO["Argo CD controller: not actively deployed"]
    GITOPS -.->|configuration available; no active reconciliation| ARGO

    JAEG["Jaeger: not deployed / end-to-end tracing unverified"]

```

**Implementation status:**
- Jenkins CI, SonarQube quality checks, Trivy scanning, Kubernetes workloads and the Prometheus/Grafana/Loki/Alloy observability stack have been exercised.
- GitOps Helm charts and Argo CD application definitions are maintained under `gitops/`. Argo CD is not actively reconciling the deployed workloads.
- Jaeger is not deployed in the EKS environment, and end-to-end distributed tracing has not been verified.
- EKS and ECR represent the AWS deployment path; their presence in this architecture does not imply that AWS resources are currently running.

## CI/CD sequence

The CI pipeline validates application changes, performs code quality and security checks, builds container images and publishes successful images to the configured registry.

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant GH as GitHub: cloudops-360
    participant JK as Jenkins
    participant SQ as SonarQube
    participant TV as Trivy
    participant REG as Container registry
    participant K8 as Kubernetes
    participant GO as GitOps configuration

    Dev->>GH: Push application changes
    JK->>GH: Checkout source
    JK->>JK: Build and run unit tests
    JK->>SQ: Submit code for analysis
    SQ-->>JK: Quality gate result
    JK->>TV: Scan dependencies and image
    TV-->>JK: Security scan result
    JK->>JK: Build and tag container image
    JK->>REG: Publish image after successful gates
    Note over GO: Helm charts and environment values are maintained separately under gitops/
    Note over K8: Kubernetes deployment is managed through the configured deployment workflow
```

A failed quality or security gate prevents the pipeline from publishing the affected image. GitOps manifests provide deployment configuration, but Argo CD is not currently performing automatic reconciliation. Do not interpret this diagram as proof of an active automatic GitOps deployment or rollback.

## Observability data flow

The observability stack collects application metrics and logs and makes them available through Grafana. Alertmanager handles configured alert rules and can forward notifications to the backend alert-history integration.

```mermaid
flowchart LR
    APPS["Application services"] -->|Prometheus metrics| PROM["Prometheus"]
    APPS -->|Container and application logs| ALLOY["Grafana Alloy"]
    ALLOY -->|Log forwarding| LOKI["Loki"]

    PROM -->|Metrics queries| GRAF["Grafana"]
    LOKI -->|Log queries| GRAF

    PROM -->|Alert rules| AM["Alertmanager"]
    AM -->|Configured webhook| BE["Backend: alert history"]
    PROM -->|Metrics API| BE
    LOKI -->|Log API| BE
    BE --> UI["CloudOps 360 dashboard"]

    JAEG["Jaeger: not deployed; end-to-end tracing unverified"]
```

**Implementation notes:**
- Prometheus, Grafana, Loki and Alloy have been exercised in the Kubernetes observability setup.
- Alloy collects and forwards logs to Loki. Log persistence is limited by the current ephemeral storage configuration.
- Alertmanager and backend alert-history integration are configured; verify the relevant alert rules and webhook before claiming end-to-end alert delivery.
- FastAPI services expose Prometheus-compatible metrics, while the Orders service uses Micrometer. Confirm metric names before assuming identical metric behavior across every service.
- Jaeger is not deployed in the EKS environment, and end-to-end distributed tracing has not been verified.

## AWS deployment architecture (planned/reference design)

The following diagram illustrates the intended AWS deployment architecture. It describes the infrastructure design and should not be interpreted as confirmation that all resources are currently provisioned or running.

```mermaid
flowchart TB
    USER["Administrator / Developer"]

    subgraph AWS["AWS account: CloudOps 360 deployment"]
        ECR["Amazon ECR: container image registry"]
        S3["Amazon S3: Terraform state storage"]

        subgraph VPC["VPC across two Availability Zones"]
            CI["EC2 CI server: Jenkins and SonarQube"]
            NAT["NAT Gateway: optional"]
            NG["EKS managed node group"]
        end

        CP["Amazon EKS control plane"]
    end

    USER -->|"Restricted management access"| CI
    USER -->|"Restricted Kubernetes API access"| CP
    CI -->|"Publish container images"| ECR
    NG -->|"Pull container images"| ECR
    NG <-->|"Cluster communication"| CP
    CI -.->|"Terraform state backend"| S3
```

**AWS implementation notes:**
- Terraform and Ansible configurations describe infrastructure provisioning and configuration management.
- EC2 is intended to host Jenkins and SonarQube for the AWS deployment design.
- EKS provides the managed Kubernetes control plane and worker-node infrastructure.
- ECR is the intended container image registry.
- S3 is intended for remote Terraform state when the remote backend is configured.
- NAT Gateway is an optional networking component and can contribute to ongoing AWS charges.
- Restrict administrative and Kubernetes API access rather than exposing management endpoints publicly.
- Actual resource existence, deployment status, tagging and costs must be verified independently in the AWS account before describing the environment as deployed.