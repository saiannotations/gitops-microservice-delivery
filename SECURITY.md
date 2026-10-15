# Security policy

## Reporting a vulnerability

This is a portfolio project, but reports are still welcome. Open a GitHub
issue titled `[security]` and describe what you found. Do not post exploit
code; a clear description and steps to reproduce are enough.

## What this repo already does

- CI scans every built image with Trivy and fails the build on CRITICAL or
  HIGH vulnerabilities.
- The final container image runs as a non-root user on a slim base image.
- Kubernetes manifests set `runAsNonRoot`, a read-only-style `seccompProfile`,
  and resource limits.
- No secrets are committed anywhere in this repo. Anything that looks like a
  credential is a placeholder (for example `ghcr-credentials` in the
  Jenkinsfile is a Jenkins credential ID, not a password).
