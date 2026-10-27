# Demonstrations

Failures are **simulated** by token-protected endpoints in the demo apps (`CHAOS_ENABLED`, `CHAOS_TOKEN`). How Kubernetes, Prometheus and
Alertmanager react is **real**. Always finish with `.\scripts\windows\demo.ps1 -Scenario reset`.

| # | Scenario | Commands | What you should observe | Evidence |
|---|---|---|---|---|
| 1 | Normal operation | `demo.ps1 -Scenario load` | request rate in Grafana; trace orders->inventory in Jaeger; log lines on dashboard *Logs* | screenshots |
| 2 | Code change -> automatic deploy | edit `apps/orders-service/...VersionController`, `git push`; wait for Jenkins poll (<=2 min) | build SUCCESS; GitOps commit by `cloudops-ci`; Argo CD Synced/Healthy; `/api/version` shows new tag | Jenkins + Argo CD + dashboard *Deployments* |
| 3 | Error spike + alert | `demo.ps1 -Scenario errors`, then `-Scenario load` | `CloudOpsHighErrorRate` Pending -> Firing (~2-3 min); appears on *Alerts*; `reset` -> resolved | Alertmanager UI, dashboard |
| 4 | Not-ready pod | `demo.ps1 -Scenario notready` | `kubectl get pods -n cloudops -w`: READY 0/1, no restart, traffic stops reaching it; `CloudOpsPodNotReady` after 2 min | kubectl output |
| 5 | Crash + restart | `demo.ps1 -Scenario crash` | RESTARTS increments; `CloudOpsPodRestarting` | kubectl + Alertmanager |
| 6 | Bad release + rollback | in the GitOps repo set a non-existent image tag for `orders-service`, push | Argo CD Progressing/Degraded; old pod keeps serving (`maxUnavailable: 0`); `git revert` -> Healthy; *Deployments* shows "previous revision re-deployed" | Argo CD history |
| 7 | Security gate | run Jenkins with `TRIVY_GATE_SEVERITY=LOW` | pipeline fails at the Trivy stage if fixable LOW+ findings exist; nothing is pushed or deployed | Jenkins log, *Security* page |

Format for your write-up: initial state -> action -> expected behaviour -> observed behaviour -> evidence -> final state.
