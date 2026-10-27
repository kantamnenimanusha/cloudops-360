# Learning guide: how the pieces fit

1. **Git is the source of truth.** App code lives in `cloudops-360`; the *desired state of the cluster* lives in `cloudops-360-gitops`.
2. **Jenkins (CI) proves a change is good** - tests, SonarQube quality gate, Trivy vulnerability gate - and produces an immutable image tagged `<git-sha>-<build>`.
   Its only write to the cluster's world is one commit: the new tag in `envs/<env>/<app>.yaml`.
3. **Argo CD (CD) makes the cluster match Git.** It pulls (no cluster credentials in CI), shows Synced/Healthy, keeps history, and self-heals manual drift.
   Rollback = `git revert`.
4. **Kubernetes keeps the app available**: readiness gates traffic, liveness restarts hung processes, rolling updates with `maxUnavailable: 0`
   keep old pods until new ones are Ready, an HPA adds pods under CPU load.
5. **Observability answers three questions:** *that* something is wrong (metrics -> alerts), *what* happened (logs), *where* (traces).
6. **Terraform vs Ansible vs Helm:** Terraform creates cloud resources (VPC, EKS, ECR); Ansible configures a server's insides (Docker, Jenkins stack);
   Helm packages Kubernetes manifests.
7. **Why a dashboard on top?** One read-only place to see all of the above, with every number traceable to a tool (the `source:` footer on each panel).

Try: change the greeting version in `VersionController`, push, and follow the change through Jenkins -> GitOps commit -> Argo CD -> `GET /api/version`.
