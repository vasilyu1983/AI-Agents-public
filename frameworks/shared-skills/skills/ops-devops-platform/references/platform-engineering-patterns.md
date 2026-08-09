# Platform Engineering Patterns

*Purpose: Operational patterns for building self-service developer platforms that abstract infrastructure complexity and accelerate development velocity.*

*Use when:* The user is designing a platform team operating model, internal developer portal, golden path, or policy layer and you need platform-specific guidance after choosing this domain.

## Table of Contents
- Core Patterns
- Decision Matrices
- Common Anti-Patterns
- Quick Reference
- When NOT to Build an IDP (Expert Judgment)
- Platform-vs-Product-Team Boundary
- Migration Sequencing: CI, IaC, GitOps Adoption Order
- CNCF Platform Engineering Maturity Model
- Policy-as-Code Trajectory (2025-2026)
- OIDC Workload Identity

---

## Core Patterns

### Pattern 1: Golden Path Abstraction

**Use when:** Developers need to deploy services without deep infrastructure knowledge

**Structure:**
```
1. Define service catalog with pre-approved patterns (web app, API, worker, cron)
2. Create self-service portal with form-based provisioning
3. Generate production-ready infrastructure from templates
4. Integrate monitoring, logging, alerting automatically
5. Provide CLI tools for common operations (deploy, scale, rollback)
```

**Checklist:**
- [ ] Service catalog covers 80% of use cases
- [ ] Templates include security and observability by default
- [ ] Documentation with examples for each golden path
- [ ] Onboarding takes <30 minutes for new developers
- [ ] Deployment time reduced from hours to minutes

**Implementation Example:**
```yaml
# Platform API - Service Provisioning
apiVersion: platform.company.com/v1
kind: Service
metadata:
  name: payment-api
spec:
  type: web-api
  language: python
  replicas: 3
  resources:
    preset: medium  # Auto-configures CPU/memory
  monitoring:
    slo:
      latency_p99: 500ms
      error_rate: 0.1%
  database:
    type: postgres
    ha: true
```

**Benefits:**
- Deployment time: 2 hours → 5 minutes (96% reduction)
- Onboarding time: 2 weeks → 1 day
- Configuration errors: Reduced by 80%
- Compliance violations: Near zero (baked into templates)

---

### Pattern 2: Progressive Disclosure UI

**Use when:** Balancing simplicity for common tasks with power for advanced users

**Structure:**
```
1. Simple mode: 3-5 fields for 80% of use cases
2. Advanced mode: Full configuration options
3. Expert mode: Direct YAML/Terraform editing
4. Progressive hints: "Need custom networking? Click here"
5. Escape hatches: Always allow underlying infra access
```

**Checklist:**
- [ ] Simple path requires ≤5 form fields
- [ ] Advanced options hidden behind expandable sections
- [ ] Expert mode shows generated code before apply
- [ ] Every abstraction has an escape hatch
- [ ] Platform doesn't block legitimate edge cases

**Anti-Patterns to Avoid:**
- [FAIL] Forcing all users through complex wizards for simple tasks
- [FAIL] Hiding configuration so deeply that debugging is impossible
- [FAIL] Creating abstractions without escape hatches (vendor lock-in)
- [FAIL] Requiring tickets/approvals for standard operations

---

### Pattern 3: Internal Developer Portal (IDP)

**Use when:** Building centralized hub for platform services

**Components:**
```
┌─────────────────────────────────────────┐
│     Internal Developer Portal           │
├─────────────────────────────────────────┤
│ • Service Catalog (Backstage/Kratix)   │
│ • CI/CD Dashboard (GitLab/GitHub)       │
│ • Observability (Grafana/Datadog)       │
│ • Documentation (Docusaurus/GitBook)    │
│ • API Gateway (Kong/Tyk)                │
│ • Secrets Management (Vault/SOPS)       │
│ • Cost Dashboard (Kubecost/CloudHealth) │
└─────────────────────────────────────────┘
```

**Checklist:**
- [ ] Single sign-on (SSO) across all tools
- [ ] Unified search across docs, services, APIs
- [ ] Role-based access control (RBAC) integrated
- [ ] Real-time status dashboard for all services
- [ ] Cost attribution per team/service
- [ ] Self-service provisioning without tickets

**Popular Tools:**
- **Backstage** (Spotify): Open-source IDP with plugin ecosystem
- **Port**: Commercial platform with Backstage compatibility
- **Kratix**: GitOps-native platform for multi-cluster management
- **Humanitec**: Application-centric platform orchestration

---

### Pattern 4: Policy as Code Enforcement

**Use when:** Ensuring security, cost, and compliance guardrails

**Structure:**
```
1. Define policies in code (OPA, Gatekeeper, Kyverno)
2. Enforce at multiple layers:
   - Git pre-commit hooks (client-side)
   - CI/CD pipeline validation (build-time)
   - Admission controller (runtime)
3. Block non-compliant changes automatically
4. Provide clear error messages with remediation steps
5. Audit all policy violations for compliance
```

**Policy Examples:**
```rego
# OPA Policy: Require resource limits
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "Deployment"
  not input.request.object.spec.template.spec.containers[_].resources.limits
  msg := "All containers must have resource limits defined"
}

# OPA Policy: Prevent privileged containers
deny[msg] {
  input.request.kind.kind == "Pod"
  input.request.object.spec.containers[_].securityContext.privileged == true
  msg := "Privileged containers are not allowed in production"
}
```

**Checklist:**
- [ ] Policies cover security, cost, compliance
- [ ] Enforcement at commit, build, and runtime
- [ ] Clear error messages with examples
- [ ] Policy exceptions require approval workflow
- [ ] All violations logged and auditable

---

## Decision Matrices

| Scenario | Tool Choice | Enforcement Layer | Validation |
|----------|-------------|-------------------|------------|
| Security policies | OPA Gatekeeper | Kubernetes admission | Block deploy if violated |
| Cost guardrails | Kubecost + OPA | CI/CD + runtime | Alert if >budget, block if critical |
| Compliance (PCI/SOX) | Cloud Custodian | Cloud API layer | Auto-remediate violations |
| Developer experience | Backstage IDP | Portal UI | Feedback loop via surveys |

---

## Common Anti-Patterns

### Anti-Pattern 1: Over-Abstraction
- **Problem:** Platform abstracts so much that debugging becomes impossible
- **Example:** "Black box" deployment system where logs/metrics are hidden
- **Remedy:** Always provide access to underlying infrastructure (kubectl, AWS console)

### Anti-Pattern 2: Ticket-Driven Operations
- **Problem:** Requiring tickets for standard operations (deploy, scale, rollback)
- **Example:** "Submit JIRA ticket for new environment (2-day SLA)"
- **Remedy:** Self-service for 90% of operations, tickets only for exceptional cases

### Anti-Pattern 3: No Escape Hatches
- **Problem:** Platform forces users into rigid patterns with no flexibility
- **Example:** "You can only use our 3 approved templates, no customization allowed"
- **Remedy:** Progressive disclosure: simple defaults + advanced customization + expert mode

### Anti-Pattern 4: Siloed Tools
- **Problem:** Separate portals for CI/CD, monitoring, docs, secrets
- **Example:** 7 different logins, no unified search, duplicate data entry
- **Remedy:** Single IDP with SSO, unified search, and integrated dashboards

---

## Quick Reference

### Platform Maturity Model

**Level 1 - Ad Hoc** (Manual operations, no self-service):
- Developers wait days/weeks for infrastructure
- Configuration via tickets and manual steps
- High error rate, slow deployment velocity

**Level 2 - Scripted** (Scripts and runbooks, limited self-service):
- Some automation via scripts
- Developers can deploy with help from ops
- Inconsistent configurations, tribal knowledge

**Level 3 - Platform** (Self-service platform, golden paths):
- 80% of deployments self-service
- Golden paths with best practices baked in
- Deployment time <15 minutes

**Level 4 - Product** (Developer portal, policy-driven):
- Unified developer portal (IDP)
- Policy as code for security/compliance
- Deployment time <5 minutes
- Platform team measures developer satisfaction

**Level 5 - Optimized** (Optional: AI/Automation, continuous improvement):
- Predictive scaling and cost optimization
- Optional automation-assisted incident response and remediation (human-approved)
- Platform continuously learns from usage patterns
- Developer satisfaction >90%

### Key Metrics for Platform Teams

**Deployment Metrics:**
- Lead time for changes: <1 hour (target: <15 min)
- Deployment frequency: Daily (target: Multiple per day)
- MTTR (Mean Time to Recovery): <15 min (target: <5 min)
- Change failure rate: <5% (target: <1%)

**Developer Experience Metrics:**
- Onboarding time: <1 day (target: <4 hours)
- Time to first deploy: <30 min (target: <10 min)
- Self-service adoption: >80% (target: >90%)
- Developer satisfaction: >80% (target: >90%)
- Ticket volume: Decreasing trend

**Cost & Efficiency Metrics:**
- Infrastructure cost per service: Tracked and decreasing
- Resource utilization: >60% (target: >70%)
- Over-provisioning waste: <10%

---

## Progressive Rollout Pattern

**Use when:** Introducing new platform features or changes

**Structure:**
```
1. Alpha (Week 1-2): Platform team dogfoods new feature
2. Beta (Week 3-4): Friendly teams opt-in for testing
3. GA (Week 5+): Gradual rollout to all teams
4. Deprecation: 6-month notice before removing old features
```

**Checklist:**
- [ ] Alpha testing with platform team
- [ ] Beta testing with 2-3 friendly teams
- [ ] Collect feedback and iterate
- [ ] Comprehensive documentation before GA
- [ ] Deprecation warnings with migration guide
- [ ] Old features supported for 6 months minimum

---

## Edge Cases & Fallbacks

**Scenario:** Platform portal is down
- **Fallback:** Direct access to underlying tools (kubectl, Terraform, AWS console)
- **Communication:** Status page with ETA and workaround instructions

**Scenario:** Automated provisioning fails
- **Fallback:** Manual provisioning via runbook
- **Post-incident:** Postmortem and automated testing improvements

**Scenario:** Policy blocks legitimate use case
- **Fallback:** Exception approval workflow (1-hour SLA for emergency)
- **Post-incident:** Update policy to allow legitimate pattern

**Scenario:** Breaking change required in platform API
- **Fallback:** Versioned APIs (v1, v2) with 6-month deprecation period
- **Migration:** Automated migration tool where possible

---

## When NOT to Build an IDP (Expert Judgment)

Source (industry-reported, not official Backstage/CNCF statistics — treat figures as approximate, unverified precision): https://backstage.io/docs/ ; multiple 2026 practitioner write-ups on Backstage adoption plateaus.

A top platform lead's first move is almost never "stand up Backstage." The checklist version of this skill (service catalog, golden paths, self-service portal) makes an IDP look like a default good idea. It is not always one — and the failure mode is expensive because it looks like progress for 6-12 months before the cost shows up.

**Do not build (or buy) an IDP when:**

- **Fewer than ~15-20 engineers, or fewer than ~5-8 services.** A wiki page plus 2-3 Terraform/Helm templates and a runbook covers the same ground with no maintenance team. An IDP's fixed cost (someone owns it, forever) doesn't amortize below this scale.
- **No one is willing to own it as a product.** Backstage and comparable portals are frameworks, not installable products — they require sustained engineering (commonly TypeScript/React) to build and maintain plugins, and reported adoption commonly plateaus around ~10% (proof-of-concept level) when a team stands one up as a side project rather than staffing 2-3 dedicated engineers for roughly a year. If no one will make that commitment, don't start; a stalled IDP is worse than no IDP because it consumes credibility along with budget.
- **The service catalog would go stale immediately.** Catalog data sourced from YAML committed alongside service code degrades within weeks without automated ingestion (CI-driven catalog updates, not manual edits) — a stale "source of truth" actively misleads engineers and on-call responders, which is worse than no catalog.
- **The underlying golden paths don't exist yet.** A portal in front of inconsistent, undocumented deployment patterns just gives inconsistency a UI. Golden paths (Pattern 1) must exist and be used successfully via CLI/PR templates *before* a portal is layered on top — the portal is a distribution mechanism for an already-working path, not a substitute for having one.
- **Plugin/version churn will outpace the team's capacity to track it.** Upgrades across major Backstage plugin API versions are a frequently cited pain point; if the team cannot dedicate ongoing capacity to this, the maintenance debt compounds silently until an upgrade is skipped for a year and becomes a rewrite.

**Build (or adopt a managed alternative like Port) when:** golden paths already work and are used, the org is large enough that "who do I ask" is itself a cost, and a team will treat the portal as a permanent product with an owner, a roadmap, and a deprecation policy for stale plugins — not a hackathon project.

**What a checklist misses that judgment catches:** the checklist says "build a service catalog, add SSO, add unified search." It does not say "stop and check whether anyone will still be feeding this catalog in 18 months." The catalog-staleness failure mode is not a bug to fix later — it is the dominant reason IDPs are abandoned, and it is entirely predictable at design time from who is named as the owner.

---

## Platform-vs-Product-Team Boundary

A platform team and a product (stream-aligned) team have a specific, narrow relationship, and getting the boundary wrong is one of the most common platform-engineering failures — independent of tooling choice.

**Platform team owns:** the paved road (golden paths, CI/CD templates, base infrastructure modules, the observability stack, the policy layer) as a product with an internal API contract (see `assets/kubernetes/template-platform-api.md`). It is accountable for that contract's reliability and for reducing toil across every team that consumes it.

**Product team owns:** what runs on the paved road — business logic, service-specific scaling decisions within the platform's guardrails, and on-call for their own service's behavior (not the platform's behavior).

**Judgment calls a checklist won't make for you:**

- **If the platform team is fielding tickets to change application-specific behavior, the boundary has already broken** — that's a sign the "self-service" interface doesn't actually cover the product team's real use cases, and the platform team is silently absorbing product-team toil instead of fixing the interface.
- **If a product team is hand-rolling its own CI pipeline or provisioning because the platform's golden path doesn't fit,** that is a signal to extend the golden path, not to mandate compliance — a golden path that doesn't cover a real use case will get bypassed regardless of policy.
- **Team Topologies' framing applies directly here:** platform teams exist to reduce cognitive load for stream-aligned teams. If a platform team's own roadmap is driven by internal platform elegance rather than measured reduction in product-team toil or lead time, it has drifted from serving its actual customers.
- **A platform team without a product owner and a roadmap is not a platform team — it is a shared-infrastructure team that will be treated as a cost center and understaffed.** Insist on a platform-as-product operating model (internal customers, a feedback loop, a deprecation policy) as a precondition, not an optional nicety.

---

## Migration Sequencing: CI, IaC, GitOps Adoption Order

A common mistake in platform build-outs is doing these in the wrong order, or trying to do them simultaneously in a team that has never operated any of them.

**Recommended sequence, and why each step is a precondition for the next:**

1. **CI first (automated build, test, and artifact production).** Nothing else in this sequence is safe without a CI system that already runs tests and produces immutable artifacts on every change. Skipping this and going straight to "GitOps" just automates the deployment of unvalidated changes faster.
2. **IaC second, once CI can gate it.** Introduce Terraform/OpenTofu (or Pulumi) for infrastructure once there is a CI pipeline that can run `plan`/`validate` on every change and require review before `apply`. IaC without CI-gated review is clickops with extra steps — it does not deliver the audit and drift-prevention benefits IaC is supposed to provide.
3. **GitOps third, once IaC and CI are both routine.** GitOps controllers (Argo CD/Flux) reconcile *declared* state — they assume the declared state (in Git, produced by IaC/CI) is already trustworthy. Introducing a GitOps controller before the team has a working CI-gated IaC habit just moves the "did anyone review this" problem into the cluster instead of solving it.
4. **Golden paths and self-service platform layer last.** Only template and abstract patterns that have already been proven manually across at least a few real services. Templating an unproven pattern locks in whatever mistakes exist in that first attempt and propagates them to every team that adopts the golden path.

**Anti-pattern:** adopting GitOps and an internal developer platform in the same quarter a team first adopts CI. The GitOps/IDP layer will inherit every gap in the CI foundation (no test gate, no artifact provenance) and the team will spend the next year debugging platform tooling instead of the actual missing foundation.

**When to compress the sequence:** a team joining an org that already has mature CI and IaC conventions elsewhere can adopt GitOps and IaC together, because the review/gating culture and tooling patterns already exist to import. The sequencing risk is about *organizational readiness*, not tool dependency graphs — skip steps only when the underlying discipline (review culture, testing habits) is already present, not just when the tools are technically compatible.

---

---

## CNCF Platform Engineering Maturity Model

Source: https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/

The CNCF TAG App Delivery Platform Engineering Maturity Model provides a standard vocabulary for assessing and advancing a platform engineering practice. It is vendor-neutral and widely referenced in procurement and platform team charters.

### Structure: five aspects × four levels

The model evaluates platform engineering across five aspects, each independently progressing through four maturity levels.

**Five aspects:**

| Aspect | What it covers |
|--------|---------------|
| **Investment** | Organizational commitment — budget, headcount, executive sponsorship, and platform team identity |
| **Adoption** | How broadly internal teams use the platform — awareness, onboarding paths, and self-service uptake |
| **Interfaces** | How the platform exposes capabilities — APIs, CLIs, portals, and documentation quality |
| **Operations** | How the platform is maintained — reliability, change management, incident response, and SLOs |
| **Measurement** | How the platform team knows it is succeeding — developer satisfaction, DORA metrics, cost attribution, and feedback loops |

**Four levels (lowest to highest):**

| Level | Descriptor | Characteristics |
|-------|-----------|----------------|
| 1 | **Provisional** | Ad hoc, tribal knowledge, reactive — no formal platform investment; capabilities exist as side-projects |
| 2 | **Operationalized** | Repeatable but manual — platform has an owner, golden paths exist, but adoption is limited and measurement is sparse |
| 3 | **Scalable** | Self-service at scale — platform serves the majority of teams, interfaces are stable, SLOs are defined and measured |
| 4 | **Optimizing** | Continuous improvement — platform team operates as a product, measures developer satisfaction, and iterates based on signal |

### Usage

Assess each aspect independently — a team can be Scalable on Interfaces while still Provisional on Measurement. Use the model to identify the highest-leverage improvement: a team with Operationalized Investment but Scalable Interfaces should next focus on Investment or Measurement, not on adding more interface features.

Replace the informal five-level maturity model in the Quick Reference section above with this CNCF model when communicating externally or responding to platform engineering assessments.

---

## Policy-as-Code Trajectory (2025–2026)

Source: https://kyverno.io/blog/2026/02/02/announcing-kyverno-release-1.17/

### Kubernetes ValidatingAdmissionPolicy (CEL) — stable since k8s 1.30

Kubernetes-native `ValidatingAdmissionPolicy` using the Common Expression Language (CEL) reached **stable (GA)** in Kubernetes 1.30. It runs directly in the API server without a webhook round-trip, reducing admission latency and eliminating webhook availability as a failure mode.

For new policies that can be expressed in CEL, `ValidatingAdmissionPolicy` is the preferred admission mechanism over external webhook-based solutions.

### Kyverno 1.17 — CEL APIs at v1 GA (February 2026)

Kyverno 1.17 (February 2026) promoted CEL-based policy types (`ValidatingPolicy`, `ImageValidatingPolicy`) to **v1 GA**. The legacy `ClusterPolicy` resource type is planned for removal at approximately Kyverno v1.20 (estimated October 2026).

Operational implications:

- **New policies:** write using CEL-based types (`ValidatingPolicy`, `MutatingPolicy`, `ImageValidatingPolicy`). These are the stable API surface.
- **Existing `ClusterPolicy` resources:** plan migration before the v1.20 removal window. Kyverno provides migration tooling.
- **Timeframe:** treat the October 2026 estimate as a target, not a hard date; track the Kyverno release cadence for the actual deprecation schedule.

### Policy layer recommendation (2026)

| Use case | Recommended approach |
|----------|---------------------|
| New Kubernetes admission policies | Kyverno v1 CEL types or `ValidatingAdmissionPolicy` (native) |
| Existing Kyverno `ClusterPolicy` | Migrate before Kyverno v1.20; run both in parallel during transition |
| Non-Kubernetes policy (IAM, cloud resources) | OPA/Rego remains the standard; no equivalent CEL migration pressure here |
| Image signature verification | Kyverno `ImageValidatingPolicy` (v1 GA in 1.17) |

### Anti-Pattern

Writing new `ClusterPolicy` resources in 2026 when `ValidatingPolicy` is now GA. Incurs migration debt before the v1.20 removal window.

---

## OIDC Workload Identity

Source: https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/

### Principle

OIDC federation and SPIFFE/SPIRE are the 2025–2026 default for workload authentication. Long-lived service-account keys and static CI credentials are an audit finding in regulated environments and a compromise surface in all environments.

### CI/CD: OIDC federation to cloud

GitHub Actions, GitLab CI, and most major CI platforms can exchange a short-lived OIDC token for cloud provider credentials with no long-lived secret stored anywhere:

```yaml
# GitHub Actions — AWS OIDC federation (no stored AWS keys)
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
# The OIDC token is automatically issued; no AWS_ACCESS_KEY_ID in secrets
```

Equivalent patterns exist for GCP Workload Identity Federation and Azure Federated Identity Credentials.

### Service-to-service: SPIFFE / SPIRE

SPIFFE (Secure Production Identity Framework for Everyone) defines a standard for workload identity via SVIDs (SPIFFE Verifiable Identity Documents). SPIRE is the reference implementation.

Key concepts:

- **SPIFFE ID** — a URI of the form `spiffe://trust-domain/path` uniquely identifying a workload.
- **SVID** — a short-lived X.509 certificate or JWT encoding the SPIFFE ID, issued automatically by SPIRE.
- **Trust domain** — the administrative boundary; workloads in different trust domains federate via SPIRE federation.

SPIRE integrates with Kubernetes (via the SPIRE k8s workload attestor), Envoy (via SDS), and Istio. mTLS between services is established using auto-rotated SVIDs, eliminating the need for manual certificate management.

### When to use each

| Scenario | Recommended mechanism |
|----------|----------------------|
| CI pipeline to cloud provider (AWS, GCP, Azure) | OIDC federation (GitHub Actions / GitLab OIDC) |
| Service-to-service inside a cluster | SPIFFE/SPIRE SVIDs via service mesh (Istio/Envoy) |
| Cross-cluster or cross-cloud service identity | SPIRE with trust domain federation |
| Legacy application that cannot use OIDC or mTLS | Vault AppRole or AWS instance profile — document as technical debt |

### Anti-Patterns

- Static AWS access keys or GCP service account JSON files stored as CI secrets — rotate immediately; replace with OIDC federation.
- Long-lived Kubernetes `ServiceAccount` tokens mounted as files — use projected token volumes with short expiry (default since k8s 1.21).
- Manually managed TLS certificates for service-to-service auth — replace with SPIRE SVIDs or service-mesh mTLS.

---

*This guide focuses on operational, production-ready platform engineering patterns. All practices are actionable and based on real-world implementations.*
