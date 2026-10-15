# What we monitor and why

## The philosophy

Monitor symptoms users feel (errors, slowness), not just machine stats (CPU).
Every alert in this repo answers "is the service hurting users right now?"
and links to a runbook section that says what to do about it.

## The pieces

- `observability/servicemonitor.yaml` — tells Prometheus to scrape the app's
  `/metrics` endpoint every 30 seconds. (The app would need a Prometheus
  client library to actually expose these metrics — the scrape config and
  dashboards are written against the standard metric names so they work as
  soon as instrumentation is added.)
- `observability/prometheusrule.yaml` — three alerts:
  - **OrdersApiHighErrorRate** (critical): 5xx rate above 5% for 5 minutes.
    Users are seeing failures; treat it as urgent.
  - **OrdersApiPodsCrashLooping** (critical): pods restarting repeatedly.
    The service is partially or fully down.
  - **OrdersApiHighLatency** (warning): the slowest 5% of requests take over
    a second for 10 minutes. Users are annoyed but not blocked.
- `observability/grafana-dashboard.yaml` — a dashboard (request rate, error
  rate, p95 latency, pod restarts, CPU/memory) shipped as a ConfigMap that
  the Grafana sidecar loads automatically.

## Why these thresholds

- 5% errors for 5 minutes: short enough to catch real incidents fast, long
  enough that a single bad deploy's first minute doesn't page everyone
  before the rollout finishes.
- Crash-loop alert has no `for:` delay: a crash-looping pod is never normal.
- Latency is a warning, not critical: slow is better than down, and paging
  someone at 3am for slowness creates alert fatigue — the thing that makes
  people ignore the critical alerts later.

## What is NOT here (yet)

Log aggregation (Loki/ELK), distributed tracing, and SLO burn-rate alerts.
Those are the natural next steps once the service is real; the current setup
is the minimum that lets one person sleep at night.
