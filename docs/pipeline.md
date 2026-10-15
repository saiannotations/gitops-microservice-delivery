# How the CI pipeline works

File: `.github/workflows/ci.yml`. There is also a `Jenkinsfile` that does the
same thing for Jenkins-based teams — pick one CI system per repo, not both.

## The short version

Every push to `main` (and every pull request) runs the same sequence:

1. **Lint** — `ruff check` makes sure the Python code follows basic style and
   correctness rules. Cheap, fast, catches silly mistakes before tests run.
2. **Test** — `pytest` runs the full test suite in `app/`. If any test fails,
   everything stops here. Nothing gets built, nothing gets deployed.
3. **Build** — Docker builds the image from `docker/Dockerfile`.
4. **Scan** — Trivy scans the built image for known vulnerabilities
   (CVEs). The build **fails** on CRITICAL or HIGH findings. This is the gate
   that caught the fat-base-image problem (issue #2).
5. **Push** — only on pushes to `main`, the image is pushed to GitHub
   Container Registry (GHCR) with two tags: `latest` and the git commit SHA.
   The SHA tag is the important one: it is unique per build, so you can always
   trace a running container back to the exact commit that made it.

Pull requests run steps 1–2 only: you get feedback without pushing images.

## Why each choice

- **GHCR instead of Docker Hub:** it lives next to the code, uses the same
  GitHub login, and private repos get it free. No extra account to manage.
- **SHA tags instead of only `latest`:** `latest` moves, so you can never be
  sure what is actually running. A SHA tag is a fingerprint — ArgoCD deploys
  an exact, traceable artifact.
- **Scan before push, not after:** a vulnerable image should never reach a
  registry where someone might deploy it. Failing fast in CI is cheaper than
  patching in production.
- **Trivy as an action, not a self-hosted scanner:** zero infrastructure to
  maintain, and its vulnerability database updates itself.

## What the pipeline does NOT do

It does not deploy anything. Deployment is ArgoCD's job (see `gitops.md`).
CI builds and verifies artifacts; GitOps delivers them. Keeping those two
responsibilities separate means a CI outage never blocks a rollback, and a
bad deploy never requires re-running CI to undo.
