# Incident runbook: orders-api

This is the page you open when something is wrong in production. It assumes
you can run `kubectl` and know which namespace the app lives in
(`orders-prod`), and nothing else.

## How you find out something is wrong

Prometheus alerts (defined in `observability/prometheusrule.yaml`) fire into
your alerting channel. Each alert links back to its section here.

---

## High error rate (OrdersApiHighErrorRate)

**What it means:** more than 5% of requests have returned 5xx errors for 5 minutes.

1. Check the Grafana "orders-api overview" dashboard: is the spike on all
   endpoints or just one (for example only `POST /orders`)?
2. Look at the recent pods: `kubectl get pods -n orders-prod` and
   `kubectl logs -l app.kubernetes.io/name=orders-api -n orders-prod --tail=100`.
   A stack trace repeated across pods usually points at a bad deploy or a bad
   config value, not at traffic.
3. Check whether the spike lines up with the last deploy:
   `kubectl rollout history deployment/orders-api-prod -n orders-prod`.
   If yes, go to [Rolling back a bad deploy](#rolling-back-a-bad-deploy).
4. If it does not line up with a deploy, check dependencies (in this demo
   there are none; in a real service this is where you check the database).

## Crash-looping pods (OrdersApiPodsCrashLooping)

**What it means:** pods keep restarting.

1. `kubectl describe pod <name> -n orders-prod` — read the "Last State" section.
   `OOMKilled` means it ran out of memory (raise the memory limit in
   `helm/values-prod.yaml`); `Error` with a Python traceback usually means a
   config or code problem.
2. `kubectl logs <name> -n orders-prod --previous` shows the logs from the
   crashed run.
3. If every new pod crashes the same way right after a deploy, roll back
   (below) — the new image is broken.

## High latency (OrdersApiHighLatency)

**What it means:** the slowest 5% of requests take longer than 1 second.

1. Check the HPA: `kubectl get hpa -n orders-prod`. If replicas are already at
   max and CPU is pegged, the service needs more capacity (raise
   `autoscaling.maxReplicas`) or the new code is slower (profile it).
2. Check whether latency started with a deploy; if so, roll back.

---

## Rolling back a bad deploy

**When to use this:** the error-rate or crash-loop alert fired right after a
deploy, and the dashboard shows the problem started with the new version.

### Option A: roll back with ArgoCD (preferred)

1. Open the ArgoCD UI (or use the CLI) and find the `orders-api-prod` app.
2. Open its history and pick the last revision where everything was green.
   Write down that commit SHA — you will need it for the follow-up.
3. Sync the app to that revision. ArgoCD redeploys the old, known-good
   version. Because sync is automated with self-heal, confirm the app shows
   Synced and Healthy afterwards.
4. Watch the alerts: `OrdersApiHighErrorRate` should stop firing within a few
   minutes. Confirm on the Grafana dashboard that the 5xx rate is back near zero.

### Option B: roll back with Helm (if ArgoCD is unavailable)

1. List revisions: `helm history orders-api-prod -n orders-prod`.
2. Roll back: `helm rollback orders-api-prod <previous-revision> -n orders-prod`.
3. Verify: `kubectl rollout status deployment/orders-api-prod -n orders-prod`
   and `curl https://orders.example.com/health`.

### After the rollback

1. **Freeze deploys to prod** until the root cause is understood. Say so in
   the team channel so nobody promotes behind you.
2. **Open a GitHub issue** describing what the bad deploy did (which alert
   fired, which revision was bad, which revision you rolled back to).
3. **Write down a timeline** while it is fresh: when the deploy went out, when
   the alert fired, when you rolled back. Paste it into the issue.
4. Only re-deploy the fix after it has passed CI and staging.

## Who to call

This is a demo repo, so: the person who merged the deploy. In a real team,
this section lists the on-call rotation and the escalation path.
