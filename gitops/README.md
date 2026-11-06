# cloudops-360-gitops

Desired state of the CloudOps 360 cluster. **Argo CD watches this repository**; Jenkins only ever changes one line here
(the `image.tag` of one app) after a build passes its quality and security gates.

```
argocd/                         AppProject + the "root" Application (one per environment) - applied once by scripts
charts/argocd-apps/             app-of-apps: renders every Argo CD Application for an environment
charts/cloudops-app/            ONE hardened chart reused by all 4 workloads (release name = app name)
charts/cluster-config/          cloudops namespace (Pod Security labels) + read-only ServiceAccount for Jenkins
charts/observability-extras/    Loki, Alloy, Jaeger, PrometheusRule alerts, Grafana dashboard and observability configuration
envs/local/  envs/aws/          values per environment (image repository + tag, env vars, third-party chart values)
```

## Before first use
### Configuration scripts

The PowerShell scripts are maintained in the separate `cloudops-360` application repository, under `scripts/windows/`. They are not stored in this GitOps repository.

- `..\cloudops-360\scripts\windows\01-configure.ps1` configures repository-specific values.
- `..\cloudops-360\scripts\windows\06-bootstrap-gitops.ps1` bootstraps GitOps secrets from local, git-ignored configuration files.
- `..\cloudops-360\scripts\windows\aws-configure-gitops.ps1` substitutes AWS deployment placeholders in the AWS environment values.

Run these scripts from the application repository and review their instructions before execution. Never commit real credentials or generated secret files.
Do not hand-edit `image.tag` lines: Jenkins rewrites them (`sed` expects exactly one `tag:` line per workload file).

## Sync order and pinning
Applications are annotated with sync waves (0: cluster-config, kube-prometheus-stack, metrics-server; 1: observability-extras; 2: workloads).
Argo CD does not wait for child Applications by default, so ordering is enforced mostly by automatic retries (`retry` with backoff):
transient "no matches for kind ServiceMonitor" errors during the first sync are expected and clear themselves.
Third-party chart versions are `*` in `charts/argocd-apps/values.yaml` - pin them after your first successful sync (see `docs/VERSIONS.md` in the app repo).

## Tooling and observability

Helm packages and renders the Kubernetes charts in this repository. Argo CD uses these charts and the environment-specific values to reconcile the cluster with the GitOps desired state.

The observability configuration includes Prometheus metrics and alerting, Grafana dashboards, Loki log aggregation, Alloy log collection, and Jaeger tracing. OpenTelemetry instrumentation supports application telemetry, including distributed tracing where configured. These components serve different purposes and are retained as part of the project architecture.

**Deployment status:** Prometheus metrics, Grafana dashboards and the Loki/Alloy log pipeline have been exercised in the development environment. The repository also contains Jaeger and OpenTelemetry-related configuration, but distributed tracing has not been verified end to end. Argo CD is not currently installed in the EKS cluster, so this repository is not actively reconciled by an Argo CD controller. Configuration files describe intended deployment state; their presence alone does not mean a component is running.

## Rollback
`git revert <commit>` + push to restore the previous GitOps configuration. Once Argo CD is installed and configured, it can reconcile the reverted state automatically. Until then, deployment changes must be applied manually.

## Secrets
None live here. Kubernetes Secrets (`cloudops-backend-secrets`, `chaos-secrets`, `alertmanager-webhook-token`) are created by `..\cloudops-360\scripts\windows\06-bootstrap-gitops.ps1` in the separate application repository (`cloudops-360/scripts/windows/`), using git-ignored local files.


<!-- cloudops360:helm-architecture -->
## Helm in this repository (for beginners)

**Helm** is a package manager and template engine for Kubernetes. Many services need almost identical YAML (a Deployment, a Service, probes, limits). Instead of copying that YAML, a **chart** keeps it once as templates with placeholders, and a **values file** fills the placeholders in for one service in one environment.

- `Chart.yaml` names and describes the chart. `values.yaml` holds its defaults. `templates/` holds the Kubernetes YAML templates.
- Charts in this repository:
  - `charts/argocd-apps/` - App-of-apps - renders every Argo CD Application for one environment
  - `charts/cloudops-app/` - Generic, hardened chart used for all four CloudOps 360 workloads (release name = app name)
  - `charts/cluster-config/` - Namespace with Pod Security labels and a read-only ServiceAccount for Jenkins rollout verification
  - `charts/observability-extras/` - Loki (logs), Alloy (log shipper), Jaeger (traces), alert rules and Grafana dashboards for CloudOps 360
- Environment values live in `envs/<environment>/<name>.yaml`. Environments found: `aws`, `local`. A values file overrides the chart defaults.
- Argo CD can render and sync these Helm charts when it is installed and configured. Argo CD is not currently installed in the CloudOps 360 EKS cluster; these files describe the intended GitOps configuration, not an active reconciliation loop.

Safe, read-only commands (they never touch the cluster):

```powershell
helm lint charts\cloudops-app
helm template orders-service charts\cloudops-app -f envs\local\orders-service.yaml --namespace cloudops
```

## How this repository fits the architecture

This repository stores Kubernetes desired-state configuration. The intended GitOps workflow uses **Argo CD**, but Argo CD is not currently installed in the CloudOps 360 EKS cluster, so this repository is not actively reconciled by Argo CD.

1. Intended future workflow: Jenkins builds, tests, scans and pushes an image, then updates the image tag in the relevant environment values file.
2. Once Argo CD is installed and connected, it can detect the change and render the chart with that values file.
3. Kubernetes can perform a rolling update after the configuration is applied; Argo CD health reporting would be available only after Argo CD is configured.
4. A Git-based rollback could revert the image-tag change; applying that rollback still requires a deployment or an active GitOps controller.

- `argocd/` holds the Argo CD project and the root application that bootstraps everything else (app-of-apps).
- This repository contains no PowerShell scripts. The helper scripts live in the application repository under `scripts\windows\`; from this folder they are at `..\cloudops-360\scripts\windows\`.
- Secrets are not stored here. Kubernetes Secrets are created from local, git-ignored files by the application repository's bootstrap script.
- AWS-specific values in `envs/aws/` that still look like `__PLACEHOLDER__` are intentionally unfilled until a real deployment is authorized.
