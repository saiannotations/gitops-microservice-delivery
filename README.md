# gitops-microservice-delivery

A complete, working example of how a small Python service gets from a developer's
laptop to production **safely and automatically**. This is a portfolio project
that shows the whole DevOps loop in one place: code, containers, Kubernetes,
CI/CD, GitOps, monitoring, and automation.

**No step here is fake.** Every pipeline, chart, manifest, and playbook in this
repo is written as if it runs against a real cluster. Where something is a
placeholder (like a registry password), it says so.

## What lives here

| Folder | What it is, in plain English |
|---|---|
| `app/` | A tiny "orders" API written in Python (FastAPI), plus its tests |
| `docker/` | The recipe (Dockerfile) that packages the API into a container image |
| `helm/` | A Helm chart: the Kubernetes "installer" for the API, with settings per environment |
| `.github/workflows/` | The CI pipeline: every push runs tests, builds the image, scans it for known security holes, and pushes it to the container registry |
| `gitops/` | ArgoCD manifests: the robot that watches this repo and keeps the cluster matching it (GitOps) |
| `observability/` | Monitoring: what to watch (ServiceMonitor), when to wake someone up (alert rules), and a Grafana dashboard |
| `ansible/` | A playbook that builds a fresh cluster from scratch: namespaces, ArgoCD, metrics |
| `docs/` | Longer explanations, written for humans: pipeline, GitOps, observability, runbooks, and why each big decision was made |
| `Jenkinsfile` | The same pipeline written for Jenkins, for teams that don't use GitHub Actions |

## How a change reaches production

```
git push ──▶ GitHub Actions ──▶ tests pass ──▶ image built ──▶ scanned ──▶ pushed to GHCR
                                                                    │
                                                                    ▼
                                            ArgoCD sees the new image tag in git ──▶ syncs dev ──▶ (promote) ──▶ syncs staging ──▶ (promote) ──▶ syncs prod
                                                                    │
                                                                    ▼
                                            Prometheus watches it ──▶ alerts fire if it misbehaves ──▶ Grafana shows it all
```

1. You push code. GitHub Actions runs the linter and the test suite.
2. If tests pass, it builds a container image, scans it for vulnerabilities with
   Trivy, and pushes it to GitHub Container Registry (GHCR).
3. ArgoCD is watching the `gitops/` folder. When the image tag there changes,
   it syncs the change into the cluster — dev first, then staging, then prod
   (each promotion is a deliberate git commit, so every deploy is traceable).
4. Prometheus scrapes the app's metrics. If error rates spike or the pods
   crash-loop, an alert fires with a link to the runbook that tells you what to do.
5. If prod breaks, the rollback procedure in `docs/runbook.md` gets you back to
   the last good version in minutes.

## Try it locally

```bash
# 1. Run the tests
pip install -r app/requirements.txt
pytest app/

# 2. Build and run the container
docker build -f docker/Dockerfile -t orders-api:local .
docker run -p 8000:8000 orders-api:local

# 3. Hit the API
curl localhost:8000/health
curl -X POST localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item": "laptop", "quantity": 2, "price": 999.99}'
```

## Repo layout

```
app/                    Python service + tests
docker/                 Dockerfile
helm/                   Helm chart (templates + values per environment)
  values-dev.yaml
  values-staging.yaml
  values-prod.yaml
.github/workflows/ci.yml
gitops/                 ArgoCD Application manifests (app-of-apps)
observability/          ServiceMonitor, PrometheusRule alerts, Grafana dashboard
ansible/                Cluster bootstrap playbook
docs/
  pipeline.md           How CI works, step by step
  gitops.md             How GitOps promotion works
  observability.md      What we monitor and why
  runbook.md            Incident runbook + production rollback procedure
  decisions.md          Architecture decisions, in plain English
Jenkinsfile             Equivalent Jenkins declarative pipeline
SECURITY.md             How to report a vulnerability
```

## The short version for recruiters

This repo demonstrates: Python microservice development with tests ·
multi-stage Docker builds · Helm chart authoring · GitHub Actions CI with
image scanning · ArgoCD GitOps with per-environment promotion · Prometheus
alerting and Grafana dashboards · Ansible cluster bootstrapping · Jenkins
declarative pipelines · incident runbooks and rollback procedures.

Built as a sequence of small, reviewable commits with tracked issues, the way
real platform work happens.
