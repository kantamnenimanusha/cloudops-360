# Architecture

## System overview
```mermaid
flowchart LR
    DEV["Developer"] -->|git push| GH["GitHub: app repo + gitops repo"]
    GH -->|poll / webhook| JK["Jenkins"]
    JK --> SQ["SonarQube"]
    JK --> TV["Trivy"]
    JK -->|push image| REG["Registry: local / ECR"]
    JK -->|commit image tag| GH
    GH -->|watched by| ARGO["Argo CD"]
    subgraph K8S["Kubernetes: kind locally / EKS on AWS"]
        ARGO -->|helm sync| WL
        subgraph WL["Workloads (namespace cloudops)"]
            FE["frontend (nginx+React)"] --> BE["backend (FastAPI)"]
            ORD["orders-service (Spring Boot)"] --> INV["inventory-service (FastAPI)"]
        end
        subgraph OBS["Observability (namespace monitoring)"]
            PROM["Prometheus + Alertmanager"]
            LOKI["Loki + Alloy"]
            JAEG["Jaeger"]
            GRAF["Grafana"]
        end
    end
    REG -.->|image pull| WL
    BE -->|read-only| PROM & LOKI & ARGO
    BE -->|read-only API| JK
    BE -->|read-only boto3| AWS["AWS APIs"]
    PROM -->|alert webhook| BE
```

## CI/CD sequence
```mermaid
sequenceDiagram
    autonumber
    actor Dev
    participant GH as GitHub app repo
    participant JK as Jenkins
    participant SQ as SonarQube
    participant TV as Trivy
    participant REG as Registry
    participant GO as GitHub gitops repo
    participant AR as Argo CD
    participant K8 as Kubernetes
    Dev->>GH: git push
    JK->>GH: poll (webhook on AWS)
    JK->>JK: build + unit tests
    JK->>SQ: analysis, wait for quality gate
    JK->>TV: dependency scan (gate)
    JK->>JK: docker build, tag sha-build
    JK->>TV: image scan (gate)
    JK->>REG: push
    JK->>GO: commit new tag to envs/<env>/<app>.yaml
    AR->>GO: detects change
    AR->>K8: rolling update (maxUnavailable 0)
    K8-->>AR: Healthy or Degraded
```
A failed gate stops the pipeline before anything is pushed or deployed. A bad release (never becomes Ready) halts the rollout;
old pods keep serving. Recover with `git revert` in the GitOps repo.

## Observability data flow
```mermaid
flowchart LR
    APPS["orders / inventory / backend"] -->|"/metrics"| PROM["Prometheus"]
    APPS -->|"JSON logs"| ALLOY["Alloy"] --> LOKI["Loki"]
    APPS -->|"OTLP spans"| JAEG["Jaeger"]
    PROM -->|rules| AM["Alertmanager"] -->|webhook| BE["backend (alert history)"]
    PROM & LOKI & JAEG --> GRAF["Grafana (engineers)"]
    PROM & LOKI & AM --> BE --> UI["CloudOps 360 dashboard"]
```
All HTTP services expose the same metric name, `http_server_requests_seconds` (Micrometer's name; the FastAPI services imitate it),
so one PromQL expression works for every service.

## AWS deployment (session-based)
```mermaid
flowchart TB
    ME["You (single IP)"]
    subgraph AWS["AWS account - tagged Project=cloudops360"]
        ECR["ECR (persistent)"]
        S3["S3 Terraform state (persistent)"]
        subgraph VPC["VPC, 2 AZs"]
            CI["CI server EC2: Jenkins + SonarQube (Terraform creates, Ansible configures)"]
            NAT["NAT gateway (optional toggle)"]
            NG["EKS managed node group: 2x t3.large"]
        end
        CP["EKS control plane (AWS-managed)"]
    end
    ME -->|"IP-restricted"| CI
    ME -->|"IP-restricted API endpoint"| CP
    CI -->|push| ECR
    NG -->|pull| ECR
    NG <--> CP
```
