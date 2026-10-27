# Security configuration

- `.trivyignore` - documented, reviewed exceptions only.
- Jenkins gate: fails on **fixable** vulnerabilities at/above `TRIVY_GATE_SEVERITY` (default CRITICAL). The full HIGH+CRITICAL
  JSON report is always archived (`reports/trivy-fs.json`, `reports/trivy-image.json`) and shown on the Security page.
- If the first pipeline run fails the gate, that is a real finding: bump the dependency/base image (preferred) or document an
  exception here. Use the `TRIVY_GATE_SEVERITY` build parameter to demonstrate gate behaviour, not to hide findings.
- `.gitleaks.toml` (repo root) configures secret scanning; run `gitleaks detect` before every push.
