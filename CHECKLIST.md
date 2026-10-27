# Implementation checklist and verification status

Legend: **EXECUTED** = actually run in the generation sandbox (Python 3.12, Node 22, JRE 21; no network, no Docker, no Maven/Terraform/Helm/kubectl).
**STATIC** = parsed/compiled only (syntax valid, behaviour not run). **UNVERIFIED** = written, never executed anywhere. **MISSING** = not built.

## Verification actually performed (final audit)
| Check | Result |
|---|---|
| Backend pure-logic tests (`test_parsers.py` 15 incl. parametrized, `test_security.py` 5), run with a throwaway pytest shim (real pytest not installable offline) | **EXECUTED - 20 passed** |
| Inventory store tests (`test_store.py`, 5), same shim | **EXECUTED - 5 passed** |
| Backend integration modules (Prometheus, Alertmanager, Loki, Jenkins incl. Trivy artifacts, not-configured and tool-down paths) exercised against a **stubbed `httpx`** | **EXECUTED - 9/9 logic checks** (real HTTP, FastAPI routes and `tests/test_api.py` NOT run) |
| Frontend `utils.ts` functions (5 assertions, types stripped, plain Node) | **EXECUTED - passed** (Vitest itself not run) |
| `api.ts`, `utils.ts` syntax via Node type-stripping | STATIC - ok (`.tsx` files could not be parsed: no TypeScript/JSX parser offline) |
| All 28 Python files parse and byte-compile; 49 relative imports resolve to real names; every third-party import has a requirements entry | STATIC - ok |
| 53 YAML/JSON/XML files parse (compose, kind, JCasC, Ansible, chart values, env values, alert rules, dashboard JSON, pom.xml) | STATIC - ok |
| Helm templates: block balance, `include` targets, `.Files.Get` targets; every Application's values file exists for local+aws; exactly one `tag:` line per workload file (what Jenkins rewrites) | STATIC - ok. **Never rendered (no `helm`)** |
| Terraform: module sources, passed arguments vs declared variables, referenced outputs, bracket balance | STATIC - ok. **Never `validate`d (no `terraform`)** |
| PowerShell: referenced scripts exist, `Join-Path` targets exist in the right repo, ASCII-only, brace balance | STATIC - ok. **Never executed (no PowerShell)** |
| Java: 18 files, type names match file names, package/imports of in-repo classes resolve, brackets balanced | STATIC - ok. **Never compiled (no `javac`/Maven)** |
| Secret scan (AWS keys, GitHub/Slack tokens, private keys, JWTs, literal credential assignments) over 187 files; no `.env`/`*.tfvars`/`*.pem`/state files present | **0 findings**. Only non-secret test fixtures (`APP_ENV=test`) contain password-like strings |
| Audit defects found and fixed | Jenkinsfile built `apps/<job>` (wrong for backend/frontend) -> explicit job-to-directory map; `pydantic` made an explicit requirement; GitOps README added |
| **Not run anywhere:** FastAPI/pytest API tests (18), JUnit tests (16), Vitest, `vite build`, every Docker build, Jenkins pipeline, SonarQube, Trivy, Helm rendering, Argo CD sync, Prometheus/Loki/Jaeger, Terraform, Ansible, PowerShell scripts, any AWS call | **UNVERIFIED** |

## Components
| Requirement | Status |
|---|---|
| React frontend, 9 pages, login, explicit unavailable/not-configured states | UNVERIFIED (never built: `npm install`/`vite build` not run) |
| FastAPI backend: JWT auth + roles, login throttling, read-only integrations (Prometheus, Kubernetes, Argo CD CRDs, Jenkins, Loki, Alertmanager, AWS, Trivy artifacts), webhook receiver | Core logic EXECUTED; HTTP layer + `tests/test_api.py` (11 tests) UNVERIFIED (FastAPI not installable offline) |
| FastAPI inventory service + chaos endpoints + `tests/test_api.py` (7 tests) | Store EXECUTED; API UNVERIFIED |
| Spring Boot orders service, JUnit tests (16), JaCoCo, Micrometer, OTel agent | UNVERIFIED (no `javac`/Maven offline; never compiled) |
| Dockerfiles x4 (non-root, multi-stage) | UNVERIFIED |
| Jenkins image + Configuration-as-Code + 4 jobs + Jenkinsfile (tests, Sonar gate, Trivy fs+image gates, push, GitOps commit, optional rollout check) | UNVERIFIED |
| SonarQube (Java service only) | UNVERIFIED; quality gate may fail first run on coverage - see troubleshooting |
| Trivy dependency + image scans, JSON archived, shown on Security page | UNVERIFIED |
| Helm: generic hardened app chart, app-of-apps, cluster-config, observability-extras | STATIC for YAML; Go templates never rendered (no `helm`) |
| Argo CD AppProject + root apps (local, aws) | UNVERIFIED |
| Prometheus/Alertmanager/Grafana via kube-prometheus-stack values, 8 alert rules, dashboard, webhook receiver | UNVERIFIED; chart version is `*` (unpinned) |
| Loki + Alloy + Jaeger (own manifests) | UNVERIFIED; image tags chosen from memory |
| OpenTelemetry tracing (Java agent, Python SDK) exporting directly to Jaeger | UNVERIFIED. **Deviation from Phase 0:** no separate OTel Collector (saves RAM) |
| Terraform: bootstrap, network, ecr, budget, eks (+IRSA), ci_server; persistent + session roots | UNVERIFIED (`terraform validate` never run) |
| Ansible: common, docker, java, ci_stack roles | UNVERIFIED (never run; idempotence not demonstrated) |
| Windows scripts (00-08, demo, test-all, cleanup, aws checks) | UNVERIFIED (never run in PowerShell) |
| Security: no committed secrets, random secrets, RBAC read-only, non-root pods, PSA labels, IP-restricted AWS endpoints, gitleaks config | Designed; UNVERIFIED at runtime |
| Docs: README, architecture, AWS guide, demos, cost, troubleshooting, learning/interview guides | Written |

## Known gaps / deviations (be aware)
- Alert history is in backend memory (lost on restart); Loki/Jaeger storage is ephemeral (`emptyDir`/in-memory).
- SonarQube analyses the Java service only; Python/React rely on tests + Trivy.
- No ALB/Ingress and no External Secrets Operator (Phase 0 marked both optional): dashboard is reached via `kubectl port-forward`; secrets are created by script.
- Chart/image versions are unpinned or unverified: see `docs/VERSIONS.md`. Pin them after the first successful run.
- The hostname/URL placeholders `__GITHUB_USER__` (and, for AWS only, `__ECR_REGISTRY__` etc.) are replaced by scripts, not by hand.
- `terraform apply`, `ansible-playbook`, and any AWS spend are never run by any script automatically.
