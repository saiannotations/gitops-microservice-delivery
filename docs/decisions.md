# Architecture decisions

Short records of the important "why did we do it this way?" choices, written
so a new team member (or a recruiter) understands the reasoning without
needing the full context.

## 1. GitHub Actions as the primary CI, Jenkinsfile as documented alternative

**Decision:** the live pipeline is GitHub Actions; the Jenkinsfile is kept as
a tested-equivalent alternative, not run in parallel.

**Why:** running two CI systems on one repo doubles maintenance and risks
double-pushing images with the same tag. GitHub Actions was chosen as primary
because the code already lives on GitHub (no extra server to maintain), but
many enterprises standardize on Jenkins — showing both proves the pipeline
design is portable, not tool-locked.

## 2. ArgoCD pull-based GitOps instead of CI pushing to the cluster

**Decision:** CI never touches the cluster. It builds images; ArgoCD pulls
changes from git into the cluster.

**Why:** if CI pushes, then CI credentials can change production — a wide
blast radius. With pull-based GitOps, the cluster only needs read access to
git, every deploy is a reviewed commit, and rollbacks are just "sync to the
older commit". It also means a CI outage never blocks a rollback.

## 3. Helm for packaging, one chart with per-environment values

**Decision:** a single Helm chart; environments differ only through
`values-dev/staging/prod.yaml`.

**Why:** one chart means one thing to maintain and test. Environment drift
(like "prod has this annotation but staging doesn't") becomes visible as a
diff between small values files instead of hidden inside copied templates.

## 4. Automated sync with prune and self-heal on all environments

**Decision:** ArgoCD syncs automatically everywhere, including prod.

**Why:** manual syncs get forgotten (this exact failure is repo issue #4).
Prod stays safe not through manual gates but through the promotion process:
prod only ever receives image tags that already survived dev and staging,
and every change is still a reviewed git commit. Prune removes resources
deleted from git; self-heal reverts anyone's hand-applied hotfixes so git
stays the truth.

## 5. Trivy scan as a blocking CI gate

**Decision:** the build fails on CRITICAL/HIGH vulnerabilities; the image is
only pushed if the scan passes.

**Why:** scanning after push is too late — someone can deploy the vulnerable
image in between. Blocking in CI makes security the default instead of a
chore, and it is what caught the base-image problem in this repo's own
history.

## 6. Slim, non-root, multi-stage images

**Decision:** `python:3.12-slim`, dependencies built in a separate stage,
app runs as UID 1000, with a HEALTHCHECK.

**Why:** smaller images pull faster, have fewer CVEs to patch, and non-root
limits what an attacker can do if the app is compromised. The healthcheck
lets Kubernetes restart only truly-stuck containers instead of guessing.
