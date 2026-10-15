# How GitOps delivery works here

## The idea in one paragraph

Git is the single source of truth for what should be running. ArgoCD is a
controller that lives in the cluster, watches this repo, and continuously
makes the cluster match it. Nobody runs `kubectl apply` by hand to deploy —
you change git, and the robot does the rest. Because every change is a git
commit, every deploy is traceable: you can always answer "what is running in
prod, and who changed it?"

## The pieces

- `gitops/root-app.yaml` — the "app of apps". You apply this one file to a
  fresh cluster and ArgoCD discovers and manages the three environment apps
  below it.
- `gitops/apps/dev.yaml`, `staging.yaml`, `prod.yaml` — one ArgoCD
  Application per environment. Each points at the `helm/` folder in this repo
  and renders it with that environment's values file
  (`helm/values-dev.yaml`, etc.).
- Sync policy is **automated with prune and self-heal**: when git changes,
  ArgoCD syncs by itself; resources deleted from git get removed from the
  cluster; anyone's manual `kubectl` edits get reverted to match git.

## How a release moves through environments

1. CI finishes and pushes a new image tagged with the commit SHA.
2. A developer (or automation) updates the image tag in the environment's
   values file and commits. **Dev first.**
3. ArgoCD syncs dev automatically. Tests/smoke checks run against dev.
4. The same tag is committed to `values-staging.yaml`, then verified.
5. Finally the tag is committed to `values-prod.yaml`. Prod only ever gets a
   tag that already proved itself in staging.

This is deliberately boring: no special deploy tool, no chat-ops command,
just git commits moving left to right. The promotion history is the git log.

## If something goes wrong

ArgoCD shows the app as OutOfSync or Degraded. Start with
`docs/runbook.md` — the rollback procedure syncs the prod app back to the
last known-good git revision, which takes minutes because the old image is
still in the registry.
