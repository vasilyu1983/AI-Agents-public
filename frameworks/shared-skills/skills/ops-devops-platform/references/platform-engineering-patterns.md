# Platform Engineering Patterns

*Purpose: Operational patterns for building self-service developer platforms that abstract infrastructure complexity and accelerate development velocity.*

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

*This guide focuses on operational, production-ready platform engineering patterns. All practices are actionable and based on real-world implementations.*
