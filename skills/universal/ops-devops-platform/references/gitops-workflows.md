# GitOps Workflows

*Purpose: Operational patterns for declarative, Git-centric continuous delivery with automated reconciliation, drift detection, and safe rollback mechanisms.*

*Use when:* The user has already chosen a GitOps operating model and needs controller, promotion, reconciliation, or progressive-delivery patterns.

## Table of Contents
- Core Patterns
- Decision Matrices
- Common Anti-Patterns
- Quick Reference
- Implementation Checklists
- Why Continuous Application: Automation Lag
- Edge Cases & Fallbacks

---

## Core Patterns

### Pattern 1: GitOps Continuous Reconciliation

**Use when:** Managing Kubernetes clusters or cloud infrastructure with Git as single source of truth

**Structure:**
```
1. All configuration stored in Git (manifests, Helm charts, Kustomize)
2. GitOps controller (ArgoCD/FluxCD) watches Git repository
3. Controller reconciles cluster state every 30-60 seconds
4. Drift detected automatically (manual kubectl changes flagged)
5. Rollback via git revert (auditable, versioned)
```

**Reconciliation Loop:**
```
Git Repository (Desired State)
       ↓
   [ArgoCD/FluxCD Agent]
       ↓
   Compare with Cluster (Actual State)
       ↓
   Detect Drift? → Alert & Auto-Remediate
       ↓
   Apply Changes if Drift Detected
       ↓
   Health Check & Validation
```

**Checklist:**
- [ ] All manifests in Git (no manual kubectl apply)
- [ ] Branch protection rules enforced (PR reviews required)
- [ ] Drift detection enabled with alerts
- [ ] RBAC limits manual cluster modifications
- [ ] GitOps controller monitors every 30-60s
- [ ] Automated rollback on health check failures
- [ ] Audit log of all changes via Git history

**Benefits:**
- **Auditability:** Full Git history of who changed what and when
- **Reliability:** Automated drift detection prevents configuration drift
- **Velocity:** Deployment via git push (no manual steps)
- **Safety:** Rollback via git revert (instant, tested)

---

### Pattern 2: Multi-Environment Promotion

**Use when:** Managing dev, staging, and production environments with GitOps

**Directory Structure:**
```
gitops-repo/
├── base/                      # Common manifests
│   ├── deployment.yaml
│   └── service.yaml
├── environments/
│   ├── dev/
│   │   └── kustomization.yaml # Overlays for dev
│   ├── staging/
│   │   └── kustomization.yaml # Overlays for staging
│   └── prod/
│       └── kustomization.yaml # Overlays for prod
└── apps/
    ├── payment-api/
    │   ├── base/
    │   └── overlays/
    └── user-service/
        ├── base/
        └── overlays/
```

**Promotion Workflow:**
```
1. Merge PR to main branch → Auto-deploy to dev
2. Tag commit (e.g., v1.2.3) → Auto-deploy to staging
3. Promote tag to prod branch → Auto-deploy to prod
4. Health checks pass → Mark deployment successful
5. Health checks fail → Auto-rollback to previous tag
```

**Checklist:**
- [ ] Environment-specific overlays (Kustomize/Helm values)
- [ ] Automated promotion via Git tags or branches
- [ ] Smoke tests run after each deployment
- [ ] Production requires manual approval (PR merge)
- [ ] Rollback tested in staging before prod rollout

**Anti-Patterns to Avoid:**
- [FAIL] Using kubectl apply directly in production
- [FAIL] Storing secrets in Git (use Sealed Secrets, SOPS, Vault)
- [FAIL] No branch protection (anyone can push to main)
- [FAIL] Manual promotion steps (use automated pipelines)

---

### Pattern 3: ArgoCD Application Sets

**Use when:** Managing 10+ applications or multi-cluster deployments

**ApplicationSet Example:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices
spec:
  generators:
  - git:
      repoURL: https://github.com/company/gitops-repo
      revision: HEAD
      directories:
      - path: apps/*
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/company/gitops-repo
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

**Checklist:**
- [ ] ApplicationSet for dynamic app generation
- [ ] Multi-cluster support configured
- [ ] Health checks defined per application
- [ ] Automated pruning of deleted resources
- [ ] Self-healing enabled for drift remediation

**Benefits:**
- **Scalability:** Manage 100+ apps with a single ApplicationSet
- **Consistency:** Same deployment pattern across all apps
- **Multi-cluster:** Deploy to dev, staging, prod clusters

---

### Pattern 4: Progressive Delivery with Argo Rollouts

**Use when:** Canary or blue-green deployments with automated rollback

**Canary Rollout Example:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: payment-api
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10      # 10% traffic to canary
      - pause: {duration: 5m}
      - setWeight: 25      # 25% traffic to canary
      - pause: {duration: 5m}
      - setWeight: 50      # 50% traffic to canary
      - pause: {duration: 5m}
      # If metrics good, promote to 100%
      canaryService: payment-api-canary
      stableService: payment-api-stable
      trafficRouting:
        istio:
          virtualService:
            name: payment-api
  analysis:
    templates:
    - templateName: success-rate
      clusterScope: true
    args:
    - name: service-name
      value: payment-api
```

**Analysis Template (Prometheus Metrics):**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
  - name: success-rate
    interval: 1m
    successCondition: result[0] >= 0.95  # 95% success rate required
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[2m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))
```

**Checklist:**
- [ ] Canary steps defined (10% → 25% → 50% → 100%)
- [ ] Analysis templates validate metrics (error rate, latency)
- [ ] Automated rollback if metrics degrade
- [ ] Traffic routing via Istio/Linkerd/NGINX
- [ ] Promotion requires metrics passing for 15+ minutes

**Benefits:**
- **Safety:** Gradual rollout with automated validation
- **Velocity:** No manual testing required (metrics-driven)
- **Reliability:** Instant rollback if metrics fail

---

## Decision Matrices

| Scenario | GitOps Tool | Deployment Strategy | Validation |
|----------|-------------|---------------------|------------|
| Single cluster, simple apps | FluxCD | Rolling update | Basic health checks |
| Multi-cluster, 50+ apps | ArgoCD ApplicationSets | Blue-green | Smoke tests + metrics |
| High-risk prod deploy | Argo Rollouts + Flagger | Canary (10→25→50→100%) | Prometheus analysis |
| Infra as Code (Terraform) | FluxCD + Terraform Controller | Apply with plan review | Terraform plan validation |

---

## Common Anti-Patterns

### Anti-Pattern 1: Secrets in Git
- **Problem:** Committing API keys, passwords, certificates to Git
- **Risk:** Credential leaks, compliance violations
- **Remedy:** Use Sealed Secrets (Bitnami), SOPS, External Secrets Operator, or Vault

**Example with Sealed Secrets:**
```bash
# Encrypt secret
kubectl create secret generic api-key --from-literal=key=secret123 --dry-run=client -o yaml \
  | kubeseal -o yaml > sealed-secret.yaml

# Commit sealed-secret.yaml to Git (safe)
git add sealed-secret.yaml
git commit -m "Add encrypted API key"
```

### Anti-Pattern 2: No Branch Protection
- **Problem:** Direct pushes to main branch bypass review
- **Risk:** Untested changes, human errors, security issues
- **Remedy:** Enforce PR reviews, status checks, signed commits

**GitHub Branch Protection Rules:**
```yaml
# .github/branch-protection.yml
main:
  required_pull_request_reviews:
    required_approving_review_count: 2
  required_status_checks:
    strict: true
    contexts:
      - ci/terraform-plan
      - ci/kustomize-validate
      - security/trivy-scan
  enforce_admins: true
  required_signatures: true
```

### Anti-Pattern 3: Manual kubectl in Production
- **Problem:** Ad-hoc kubectl apply bypasses GitOps workflow
- **Risk:** Configuration drift, no audit trail, rollback impossible
- **Remedy:** RBAC restrictions + automated drift detection

**Prevent Manual Changes:**
```yaml
# ArgoCD Project with sync policy
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
spec:
  syncWindows:
  - kind: allow
    schedule: '0 9-17 * * 1-5'  # Only during business hours
    duration: 8h
    applications:
    - '*'
  clusterResourceWhitelist:
  - group: '*'
    kind: '*'
```

### Anti-Pattern 4: No Rollback Plan
- **Problem:** Deployment fails, no tested rollback procedure
- **Risk:** Extended downtime, scrambling to fix manually
- **Remedy:** Git revert tested in staging, automated rollback on health check failure

---

## Quick Reference

### GitOps Tools Comparison

| Feature | ArgoCD | FluxCD | Jenkins X |
|---------|--------|--------|-----------|
| UI Dashboard | [OK] Rich UI | [FAIL] CLI-only | [OK] Basic UI |
| Multi-cluster | [OK] Native | [OK] Via Flux bootstrap | [OK] Native |
| Helm support | [OK] Native | [OK] Via Helm Controller | [OK] Native |
| Kustomize | [OK] Native | [OK] Via Kustomize Controller | [OK] Native |
| RBAC | [OK] Advanced | [WARNING] Basic | [OK] Advanced |
| Canary/Blue-Green | [OK] Argo Rollouts | [OK] Flagger | [OK] Native |
| GitHub/GitLab integration | [OK] Webhooks | [OK] Webhooks | [OK] Native |
| Learning curve | Medium | Low | High |
| Best for | Enterprise, multi-cluster | Lightweight, GitOps purists | Jenkins users |

### Common GitOps Commands

**ArgoCD:**
```bash
# Sync application manually
argocd app sync payment-api

# View sync status
argocd app get payment-api

# Rollback to previous revision
argocd app rollback payment-api 42

# List all applications
argocd app list
```

**FluxCD:**
```bash
# Bootstrap Flux on cluster
flux bootstrap github --owner=company --repository=gitops-repo

# Reconcile immediately (instead of waiting for interval)
flux reconcile kustomization apps

# Check source status
flux get sources git

# Suspend/resume reconciliation
flux suspend kustomization apps
flux resume kustomization apps
```

**kubectl:**
```bash
# View ArgoCD app status
kubectl get applications -n argocd

# View Flux resources
kubectl get kustomizations -n flux-system
kubectl get helmreleases -n flux-system

# Check GitOps sync errors
kubectl describe application payment-api -n argocd
```

---

## Progressive Rollout Workflow

**Week 1-2: GitOps Pilot**
- [ ] Deploy ArgoCD/FluxCD to non-prod cluster
- [ ] Migrate 2-3 low-risk applications
- [ ] Test rollback and drift detection
- [ ] Document learnings and gotchas

**Week 3-4: Expand to Staging**
- [ ] Migrate all staging applications
- [ ] Implement multi-environment promotion
- [ ] Set up automated testing pipeline
- [ ] Train team on GitOps workflows

**Week 5-8: Production Rollout**
- [ ] Migrate production apps (low-risk first)
- [ ] Enable drift alerts and automated remediation
- [ ] Implement progressive delivery (canary/blue-green)
- [ ] Run game days to test rollback procedures

**Week 9+: Optimization**
- [ ] Tune sync intervals (balance load vs. latency)
- [ ] Optimize Git repository structure
- [ ] Implement ApplicationSets for dynamic apps
- [ ] Measure DORA metrics (lead time, deployment frequency)

---

## Why Continuous Application: Automation Lag

The patterns above describe *how* reconciliation works. This section is the argument for *why* the reconciliation interval must stay short, and why a pipeline that applies only when code changes is not equivalent.

Source: Morris, *Infrastructure as Code* 2e — Ch20 "Team Workflows" (pp. 349–351) and Ch12 "Managing Changes to Servers" (pp. 192–193).

### The definition

> "Automation lag is the time that passes between instances of running an automated process, such as applying infrastructure code. The longer it's been since the last time the process ran, the more likely it will fail."

Morris's point is that this holds **even when nothing in your code changed**: "Things change over time, even when nobody has consciously made a change." His four causes:

- "Someone has changed another part of the system, such as a dependency, in a way that only breaks when your code is reapplied."
- "An upgrade or configuration change to a tool or service used to apply your code might be incompatible with your code."
- "Applying unchanged code might nevertheless bring in updates to transitive dependencies, such as operating system packages."
- "Someone may have made an manual fix or improvement that they neglected to fold back into the code. Reapplying your code reverts the fix." *(quoted as printed)*

The corollary, in his words: **"the more frequently you apply infrastructure code, the less likely it is to fail. When failures do occur, you can discover the cause more quickly, because less has changed since the last successful run."**

### The causal loop

Read the last cause together with the consequences, and the failure mode is self-reinforcing:

```text
long gap since last apply
        ↓
next apply is large and unpredictable
        ↓
fear of running it
        ↓
"just this once" ad hoc manual fix (faster, feels safer)
        ↓
drift — the fix is not in the code
        ↓
next apply is now even more likely to fail (it will revert the fix)
        ↓
more fear  ──────────► back to the top
```

Each manual fix makes the automated path *more* dangerous, which makes the next manual fix more attractive. Continuous application breaks the loop by keeping the gap — and therefore the size of each apply — small enough that nobody is afraid of it.

### The apply-on-change antipattern

Ch12 names the habit directly. **"With the apply on change antipattern, configuration code is only applied to a server when there is a specific change to apply."** Also known as *ad hoc automation*. In its extreme form, "you only apply code to the server that you specifically intend to change."

Morris's diagnosis of the origin is worth keeping, because it explains why the habit survives good tooling: "The apply on change antipattern is an extension of this way of working" — logging in and making the change by hand — "that happens to use an Infrastructure as Code tool instead of a manual command or on-off script." The tool is being used as "a scripting tool with awkward syntax."

*Applicability:* "Applying code only as needed for a specific change may be fine for a single temporary server. But it's not a suitable method for sustainably managing a group of servers."

*Consequences:* "If you only apply configuration code to make a specific change, you may have long gaps where the code is never applied to a particular server instance. When you finally do apply the code, it might fail because of other differences on the server than the one you meant to change."

He then names the second-order problem — applying to *some* instances and not others. A performance fix applied to one server later arrives at the others "as a side effect of applying the code for the new change. The earlier change might have unexpected effects on other servers. Worse, the person applying the code may have forgotten about the performance optimization, so they take much longer to discover the cause of any problems it creates."

That is the batching failure in one sentence: **applying only on change does not avoid the risky batch, it defers and hides it.** The batch still lands — later, larger, and attributed to the wrong change.

### The fix: apply continuously

> "A core strategy for eliminating configuration drift is to continuously apply infrastructure code to instances, even when the code hasn't changed."

Morris notes the precedent — Chef and Puppet "are designed to reapply configuration on a schedule, usually hourly" — and places GitOps in the same lineage: "The GitOps methodology involves continuously applying code from a source code branch to each environment."

The alternative he offers is immutable infrastructure, which "solves the problem of configuration drift in a different way. Rather than applying configuration code frequently to an infrastructure instance, you only apply it once, when you create the instance. When the code changes, you make a new instance and swap it out for the old one." But this does not exempt you: **"Automation lag is still potentially an issue, so teams that use immutable infrastructure tend to rebuild instances frequently."** An image built six months ago and never rebuilt has the same lag problem as a stack never reapplied.

### GitOps-as-branches-only

Morris's caution applies directly to teams adopting the patterns in this file:

> "Some teams describe their process as GitOps, but only implement the branches for environments practice without continuously synchronizing code to environments. This makes it to easy to fall into an ad hoc change process, and bad habits of copying, pasting, and editing code changes for each environment, per the copy-paste antipattern." *(quoted as printed)*

The distinction he draws is between the two halves of GitOps: defining systems as code in branches, **and** "continuously synchronizing code to systems … Rather than having a build server job or pipeline stage apply the code when it changes, GitOps uses a service that continuously compares the code to the system, reducing configuration drift."

A repo with `env/stage` and `env/prod` branches, and a pipeline that applies on merge, has adopted only the first half. It is apply-on-change with Git branches — and it inherits every consequence above. **The reconciliation loop is not an implementation detail of GitOps; it is the half that does the work.**

One further note from Morris, relevant to Pattern 2 (Multi-Environment Promotion) above: "GitOps discourages the use of delivery artifacts, instead promoting code changes by merging them to source code branches." That is a genuine tension with artifact-based promotion — see [../assets/terraform-iac/template-env-promotion.md](../assets/terraform-iac/template-env-promotion.md), which promotes pinned module versions. Both are defensible; what is not defensible is branch-based promotion *without* continuous sync.

### Checklist

- [ ] Reconciliation runs on an interval, not only on commit
- [ ] Interval is short enough that a failed apply points at a small window of change
- [ ] Alert fires when any environment has not successfully synced within N intervals — lag is monitored, not assumed
- [ ] Self-heal enabled, so drift is corrected rather than accumulating until the next intentional change
- [ ] No environment is reachable by an out-of-band apply path that bypasses the controller
- [ ] Manual break-glass fixes have a mandatory fold-back-into-code step with an owner
- [ ] Immutable images/AMIs are rebuilt on a cadence, not only when their definition changes
- [ ] "We do GitOps" is verified against continuous sync, not just the presence of environment branches

---

## Edge Cases & Fallbacks

**Scenario:** GitOps controller is down
- **Fallback:** Manual kubectl access with emergency RBAC role
- **Detection:** Alert if controller hasn't synced in 10 minutes
- **Prevention:** Run controller in HA mode (3 replicas)

**Scenario:** Git repository is unavailable
- **Fallback:** Cluster continues running with last known good state
- **Detection:** Alert if sync fails for 5 consecutive attempts
- **Prevention:** Mirror Git repo to multiple locations (GitHub + GitLab)

**Scenario:** Bad commit breaks production
- **Immediate Action:**
  ```bash
  # Revert bad commit
  git revert abc123
  git push origin main

  # ArgoCD auto-syncs within 60 seconds
  argocd app sync payment-api --async
  ```
- **Post-incident:** Review why CI checks didn't catch the issue

**Scenario:** Drift detected (manual kubectl change)
- **Alert:** "Deployment payment-api out of sync: replicas changed from 10 to 15"
- **Action:** ArgoCD auto-remediates (self-heal: true)
- **Audit:** Check kubectl audit logs to find who made manual change
- **Prevention:** Tighten RBAC, educate team on GitOps workflow

---

*This guide focuses on operational, production-ready GitOps patterns. All practices are actionable and based on real-world implementations with ArgoCD and FluxCD.*
