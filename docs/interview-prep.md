# Interview preparation

**30-second pitch.** "CloudOps 360 is an end-to-end DevOps platform. Pushing code triggers Jenkins to test, scan (SonarQube, Trivy) and build an immutable image,
then commit the new tag to a GitOps repo; Argo CD deploys it to Kubernetes; Prometheus, Loki and Jaeger observe it; a dashboard aggregates the real tool APIs.
Infrastructure on AWS is Terraform; I ran it in short, destroyed sessions to stay within a $150 budget."

**Be ready to explain**
- Why GitOps (pull vs push, audit trail, rollback by revert, no cluster credentials in CI).
- Failed *build* vs failed *deployment*, and what each leaves running.
- Why immutable tags and a separate GitOps repo (no CI loop; reviewable deployments).
- Readiness vs liveness vs startup probes, and what `maxUnavailable: 0` buys you.
- Least privilege here: read-only ClusterRole for the backend, IRSA instead of keys, ECR pull-only nodes / push-only CI, IP-restricted endpoints, non-root pods.
- Cost decisions: session-based AWS, public subnets vs NAT trade-off, EKS extended-support trap, t3.large for pod density.
- Honest limitations: in-memory alert history, ephemeral Loki/Jaeger storage, no HTTPS/ALB, Sonar on the Java service only, chaos endpoints are demo-only and token-gated.
- What you would do next in production: private nodes + NAT/VPC endpoints, External Secrets, ALB + TLS, durable log/trace storage, signed images, policy-as-code.

**Do not claim** anything you have not run: the checklist file shows what you verified yourself.
