# Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Docker Desktop very slow, containers killed | Docker has too little RAM. Set `.wslconfig` (README section 1). Stop Jenkins/SonarQube while not needed: `docker compose -f local/docker-compose.yml stop` |
| `01-configure.ps1` / scripts "cannot be loaded" | `Set-ExecutionPolicy -Scope Process Bypass` |
| SonarQube exits at start (Elasticsearch) | Check `docker compose ... logs sonarqube`. The compose file disables mmap; if it persists raise Docker memory |
| Jenkins job fails at "Checkout" | `GITHUB_TOKEN` lacks Contents: read on the app repo, or `APP_REPO_URL` is wrong (`local\.env`; recreate Jenkins: `docker compose ... up -d --force-recreate jenkins`) |
| Sonar quality gate fails (coverage on new code) | Real result. Add tests, or in SonarQube UI > Quality Gates adjust the *coverage on new code* condition and document why |
| Trivy gate fails | A fixable CRITICAL vulnerability exists. Update the dependency/base image (preferred) or add a documented entry to `security/.trivyignore` |
| Pods `ImagePullBackOff` for `localhost:5001/...` | Image not pushed (run step 05) or registry not connected to the kind network (re-run `02-create-cluster.ps1`) |
| Argo CD app `ComparisonError` / repo not accessible | Private repo: re-run `06-bootstrap-gitops.ps1 -PrivateRepos`. Public repo: check `__GITHUB_USER__` was replaced and pushed |
| `ServiceMonitor`/`PrometheusRule` "no matches for kind" | Monitoring CRDs not installed yet; Argo retries automatically. Check `kubectl -n argocd get app kube-prometheus-stack` |
| kube-prometheus-stack sync fails with a values/schema error | Chart version `*` pulled a newer chart. Pin `charts.kubePrometheusStack` (add it under `charts:` in `envs/<env>/root.yaml`, or edit `charts/argocd-apps/values.yaml`) to a version you tested; see docs/VERSIONS.md |
| node-exporter pod `CrashLoopBackOff` on kind | `hostRootFsMount.enabled: false` is already set; check `kubectl -n monitoring describe pod` |
| Dashboard pages show "Source unavailable" | Correct behaviour when a tool is down or unreachable; the message names the source and error. Jenkins from kind: `host.docker.internal:8080` must be reachable |
| Dashboard login rejected | Use `VIEWER_PASSWORD`/`ADMIN_PASSWORD` from `local\.env`; secrets were created at step 06 - if you regenerated `.env`, re-run 06 and `kubectl -n cloudops rollout restart deploy/cloudops-backend` |
| Backend crash: "Invalid configuration" | Missing/short secrets. `kubectl -n cloudops logs deploy/cloudops-backend` |
| Orders pod never Ready | Java agent download failed at image build, or inventory-service down (orders readiness does not depend on it - check `kubectl describe pod`) |
| Alert never fires | Needs traffic: run `demo.ps1 -Scenario load` while error/latency injection is on; `for:` is 2 minutes |
| Jenkins cannot push to GitOps repo | Token needs Contents read+write on `cloudops-360-gitops`; branch must be `main` |
| `terraform plan` errors on `cluster_version` | You must set it (no default) to a standard-support version |
| EKS API unreachable from your laptop | Your public IP changed: update `admin_cidrs`, re-apply |
