```markdown
# GitOps Template (ArgoCD / Flux)

*Purpose: A practical template for designing, operating, and troubleshooting GitOps workflows with ArgoCD or Flux.*

---

# 1. Overview

**Service / System:**  
[name]

**GitOps Tool:**  
- [ ] ArgoCD  
- [ ] Flux  

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-cluster  

**Scope:**  
- [ ] New GitOps app  
- [ ] Promotion flow  
- [ ] Rollback flow  
- [ ] Multi-tenant setup  
- [ ] Multi-cluster sync  

---

# 2. Repo & Structure

## 2.1 Git Layout

Common patterns:

- **App repo** (code)  
- **Ops/Env repo** (manifests, Helm releases, Kustomize)

Example:

```

app-repo/
  src/
  Dockerfile
  ...

ops-repo/
  apps/
    app1/
      base/
      overlays/
        dev/
        staging/
        prod/
  clusters/
    prod-eu1/
    prod-us1/

```

Checklist:
- [ ] Separation of code vs infra state  
- [ ] Environments defined as overlays  
- [ ] Kustomize or Helm used consistently  

---

# 3. ArgoCD Configuration

## 3.1 Application CR Example

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app1-prod
spec:
  project: default
  source:
    repoURL: https://github.com/org/ops-repo.git
    path: apps/app1/overlays/prod
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: app1-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Checklist:

- [ ] Source points to env overlay  
- [ ] Automated sync only if desired  
- [ ] SelfHeal enabled for true GitOps  
- [ ] Prune enabled once safe  

---

# 4. Flux Configuration

## 4.1 GitRepository + Kustomization Example

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: ops-repo
spec:
  url: https://github.com/org/ops-repo.git
  branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: app1-prod
spec:
  interval: 1m
  path: ./apps/app1/overlays/prod
  prune: true
  sourceRef:
    kind: GitRepository
    name: ops-repo
```

Checklist:

- [ ] Interval set appropriately  
- [ ] Prune true when ready  
- [ ] SourceRef points to repo object  

---

# 5. Promotion Workflow

## 5.1 Git-based Promotion

Flow:

1. Build image from app repo  
2. Tag image with SHA  
3. Update `values.yaml` / Kustomize patch in ops repo  
4. Open PR to ops repo (dev → staging → prod)  
5. Merge PR → GitOps tool syncs  

Checklist:

- [ ] Promotion via Git, not kubectl  
- [ ] Image tags immutable  
- [ ] PR reviewed and approved  
- [ ] CI validates manifests before merge  

---

# 6. Rollback Workflow

GitOps rollback is **git revert**:

```
git revert <commit>
git push
```

ArgoCD/Flux will sync to the reverted state.

Checklist:

- [ ] Revert tested in non-prod  
- [ ] Rollback < 2–3 minutes  
- [ ] SLOs monitored during rollback  

---

# 7. Sync & Health Checks

## ArgoCD

- Sync status: Synced / OutOfSync  
- Health: Healthy / Degraded  

Commands:

```
argocd app list
argocd app get app1-prod
argocd app sync app1-prod
```

## Flux

Commands:

```
flux get kustomizations
flux reconcile kustomization app1-prod
```

Checklist:

- [ ] No manual kubectl in prod for managed resources  
- [ ] Sync failures alerted  
- [ ] Drift from Git resolved via Git, not cluster edits  

---

# 8. Security & Access

Checklist:

- [ ] GitOps tool uses least-privilege SA  
- [ ] Read-only access to manifests for developers (write via PR)  
- [ ] Secrets handled with SOPS/SealedSecrets  
- [ ] No plain-text secrets in ops repo  

---

# 9. Troubleshooting

## Common Issues

- **OutOfSync**: changes made manually → fix via Git  
- **Degraded**: manifests applied but app failing → check K8s events  
- **Permissions**: GitOps SA cannot apply resource → update RBAC  
- **Sync loops**: tool fighting manual changes → block kubectl changes in prod  

---

# 10. Final GitOps Checklist

- [ ] Desired state in Git only  
- [ ] No manual prod edits  
- [ ] Auditable PRs for all changes  
- [ ] Rollbacks via commits  
- [ ] Alerts for sync/health issues  
- [ ] Secrets encrypted at rest  

---

# END

```
