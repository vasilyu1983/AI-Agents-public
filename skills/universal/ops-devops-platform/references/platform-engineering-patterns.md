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

Source: [Backstage framework overview](https://backstage.io/docs/overview/what-is-backstage/). Adoption percentages and staffing-duration estimates in earlier guidance are unverified; measure portal use and budget maintenance capacity in the target organization.

Check whether a portal solves a measured discovery or delivery problem before committing to its integration and maintenance cost.

**Do not build (or buy) an IDP when:**

- **Fewer than ~15-20 engineers, or fewer than ~5-8 services.** A wiki page plus 2-3 Terraform/Helm templates and a runbook covers the same ground with no maintenance team. An IDP's fixed cost (someone owns it, forever) doesn't amortize below this scale.
- **No one will own integration, maintenance, and adoption.** Backstage is a framework for building developer portals. Name the owner, estimate integration and upgrade work, and test use with the target teams before expanding the portal.
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

### Measuring the cognitive load you claim to be reducing

The bullet above justifies the platform by cognitive load, which raises the obvious question: measured how? Team Topologies 2e (2025) supplies an instrument, and a correction to the way most teams reason about the number.

**The four-cluster model.** The authors' account of its origin: *"To address these issues, we worked with Dr. Laura Weis, an expert in organizational psychology, to devise a scientific model for systematically assessing cognitive load in knowledge-intensive teams at large (not restricted to teams working in technology). We found more than twenty drivers of team cognitive load arranged into four clusters: team characteristics, work practices and processes, task characteristics, and work environments and tools."*

The motivation for going beyond the classic intrinsic/extrinsic/germane split is stated plainly: *"because there is no clean 'split' between intrinsic, extrinsic, and germane types of cognitive load, we run the risk of overlooking drivers of team cognitive load that are not as visible or overinvest in solutions that address consequences rather than the causes of excessive cognitive load on teams."*

That is the failure this closes for a platform team. A platform built against a guessed cause is an expensive solution to a symptom. Note the four clusters: only one of them — *work environments and tools* — is squarely what a platform can fix. If the dominant drivers turn out to sit in *team characteristics* or *work practices and processes*, a new internal developer portal will not move them, and the honest response is an enabling team or a boundary change instead. Worth registering that the survey has diagnostic value on its own: the authors report that first-time respondents "often convey that the questions alone made them realize how many factors that can impact their cognitive load were not even on their radar."

The instrument built on this model is named **Teamperature**, a tool developed by Aleix and the Team Topologies team. It supports "looking at team cognitive load trends and evolution over time (at the team, group, and even organizational level)" — trend over time being the useful signal, not a single reading.

**Load is a river, not a bucket.** The book explicitly rejects the intuition that a platform's goal is to drive cognitive load toward zero:

> *"A misguided view would see the load as a bucket that we fill with water, and once it's full, the team should never be asked to learn new things or take on new responsibilities. A river analogy is more on point. You don't want an overflow causing disaster, but the river level is expected to change over time. Also, our goal should not be to always lower the level; otherwise, we end up with no flow!"*

A temporary increase is framed as a *"necessary evil"* that teams "might need as long as there's a clear objective" — increased service ownership, improved productivity, or modernizing a system. What must be avoided instead is *"continuously increasing the team's cognitive load by demanding more ownership without adequate guidance and support, piling on responsibilities and expecting everything else to stay the same, or standing still while the number of tools, services, frameworks, and processes the team must handle proliferates without adequate platforms to handle some of that complexity."*

For a platform team, that last clause is the actual mandate — and the metric is the trend line under a growing estate, not an absolute floor.

**Load shifts upward before it drops — assess leadership too.** The Creditas case in the book is the correction most reorganizations miss. Creditas identified *"Leadership overload: The leadership team itself was struggling with cognitive load, including lack of solution alignment, team alignment, and role overload"* among its key drivers, and the book judges that *"The decision to assess leadership cognitive load proved crucial. It avoided common but ineffective approaches like changing processes, reorganizing the tribe, or laying off employees instead of addressing the actual problems."*

Then, on executing the change: *"Shortly after announcing the new direction, Creditas found that team cognitive load wasn't decreasing — it was simply shifting to new drivers"* — lack of role clarity, ineffective processes, and high task complexity from newly end-to-end responsibilities. The lesson as a Creditas leader states it: *"We learned to expect [that] team cognitive load might intensify before you are able to address it. Failing to assess cognitive load and make a focused plan based on the resulting data would have prevented the initiative from succeeding."* Their response was two enabling teams (one facilitating leadership–product collaboration, one upskilling developers on mobile to reduce task complexity); after two months, assessments "showed significant improvement across all three drivers."

The commentary generalizes it: *"Many companies jump into reorgs — for example creating new platforms — with loosely defined improvement goals and little to no data on whether those will really address the main bottlenecks to flow,"* and identifies leadership load as *"a frequent bottleneck in itself due to decision-making overload and difficulties in prioritization."*

**What this means operationally for a platform rollout:**

- Baseline cognitive load across all four clusters *before* building, so you know whether a platform is the right intervention at all.
- Assess the leadership layer, not only the stream-aligned teams. If leadership is the bottleneck, a platform will not clear it.
- Expect the number to get worse mid-transition. Budget enabling-team capacity for that window rather than reading the rise as failure and reversing course.
- Track the trend, not a target floor. "Load went up while the team absorbed end-to-end ownership" can be a success; "load stayed flat while the estate doubled" already is one.
- Treat a platform roadmap unsupported by driver data the way you would treat an outage response with no telemetry.

*Source: Skelton & Pais, Team Topologies, 2nd edition (2025) — cognitive load assessment discussion and the Creditas case study. Figures reported in third-party summaries of this case are not reproduced here; only what the book itself states is quoted above.*

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

Sources: [Kyverno release history](https://kyverno.io/blog/2026/02/02/announcing-kyverno-release-1.17/) and [migration guide](https://kyverno.io/docs/guides/migration-to-cel/). Select the deployed and target documentation versions before using API types or scheduling migration.

### Kubernetes ValidatingAdmissionPolicy (CEL) — stable since k8s 1.30

Kubernetes-native `ValidatingAdmissionPolicy` using the Common Expression Language (CEL) reached **stable (GA)** in Kubernetes 1.30. It runs directly in the API server without a webhook round-trip, reducing admission latency and eliminating webhook availability as a failure mode.

For new policies that can be expressed in CEL, `ValidatingAdmissionPolicy` is the preferred admission mechanism over external webhook-based solutions.

### Kyverno CEL policy migration

The named release announcement promoted CEL policy types to `v1`; it also published an estimated legacy-policy removal schedule. Treat that schedule as historical planning evidence. Check the target release's migration guide, API definitions, and release notes for supported types and the actual removal boundary.

- **New policies:** prefer supported CEL types for validation, mutation, generation, and image verification when they cover the required behavior.
- **Existing legacy policies:** inventory `ClusterPolicy` and other affected types; map rules and exceptions to replacements using the target migration guide. Test syntax, admission outcomes, background behavior, and policy exceptions before promotion.
- **Upgrade gate:** finish required migration before upgrading to a release that removes a type; retain a tested rollback path.

### Policy layer recommendation

| Use case | Recommended approach |
|----------|---------------------|
| New Kubernetes admission policies | Supported Kyverno CEL types or native `ValidatingAdmissionPolicy`, according to required features |
| Existing Kyverno `ClusterPolicy` | Check the target removal boundary, migrate and compare policy outcomes before upgrade |
| Non-Kubernetes policy (IAM, cloud resources) | OPA/Rego when it covers the target platform and policy workflow |
| Image signature verification | Check the target `ImageValidatingPolicy` API and supported verification behavior |

Avoid copying a planned release date into an upgrade deadline without checking the target release documentation.

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
