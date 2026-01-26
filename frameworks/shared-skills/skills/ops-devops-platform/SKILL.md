---
name: ops-devops-platform
description: "Production-grade DevOps and platform engineering patterns: Kubernetes, Terraform, containers, GitOps, CI/CD, observability, incident response, security hardening, and cloud-native operations (AWS, GCP, Azure, Kafka)."
---

# DevOps Engineering — Quick Reference

This skill equips teams with actionable templates, checklists, and patterns for building self-service platforms, automating infrastructure with GitOps, deploying securely with DevSecOps, scaling with Kubernetes, ensuring reliability through SRE practices, and operating production systems with strong observability.

**Modern baseline (2026)**: IaC (Terraform/OpenTofu/Pulumi), GitOps (Argo CD/Flux), Kubernetes (follow upstream supported releases), OpenTelemetry + Prometheus/Grafana, supply-chain security (SBOM + signing + provenance), policy-as-code (OPA/Gatekeeper or Kyverno), and eBPF-powered networking/security/observability (e.g., Cilium + Tetragon).

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Infrastructure as Code | Terraform / OpenTofu | `terraform plan && terraform apply` | Provision cloud resources declaratively |
| GitOps Deployment | Argo CD / Flux | `argocd app sync myapp` | Continuous reconciliation, declarative deployments |
| Container Build | Docker Engine | `docker build -t app:v1 .` | Package applications with dependencies |
| Kubernetes Deployment | kubectl / Helm (Kubernetes) | `kubectl apply -f deploy.yaml` / `helm upgrade app ./chart` | Deploy to K8s cluster, manage releases |
| CI/CD Pipeline | GitHub Actions | Define workflow in `.github/workflows/ci.yml` | Automated testing, building, deploying |
| Security Scanning | Trivy / Falco / Tetragon | `trivy image myapp:latest` | Vulnerability scanning, runtime security, eBPF enforcement |
| Monitoring & Alerts | Prometheus + Grafana | Configure ServiceMonitor and AlertManager | Observability, SLO tracking, incident alerts |
| Load Testing | k6 / Locust | `k6 run load-test.js` | Performance validation, capacity planning |
| Incident Response | PagerDuty / Opsgenie | Configure escalation policies | On-call management, automated escalation |
| Platform Engineering | Backstage / Port | Deploy internal developer portal | Self-service infrastructure, golden paths |

---

## Decision Tree: Choosing DevOps Approach

```text
What do you need to accomplish?
    ├─ Infrastructure provisioning?
    │   ├─ Cloud-agnostic → Terraform or OpenTofu (OSS fork)
    │   ├─ Programming-first → Pulumi (TypeScript/Python/Go)
    │   ├─ AWS-specific → CloudFormation or Terraform/OpenTofu
    │   ├─ GCP-specific → Deployment Manager or Terraform/OpenTofu
    │   └─ Azure-specific → ARM/Bicep or Terraform/OpenTofu
    │
    ├─ Application deployment?
    │   ├─ Kubernetes cluster?
    │   │   ├─ Simple deploy → kubectl apply -f manifests/
    │   │   ├─ Complex app → Helm charts
    │   │   └─ GitOps workflow → ArgoCD or FluxCD
    │   └─ Serverless?
    │       ├─ AWS → Lambda + SAM/Serverless Framework
    │       ├─ GCP → Cloud Functions
    │       └─ Azure → Azure Functions
    │
    ├─ CI/CD pipeline setup?
    │   ├─ GitHub-based → GitHub Actions (template-github-actions.md)
    │   ├─ GitLab-based → GitLab CI
    │   ├─ Enterprise → Jenkins or Tekton
    │   └─ Security-first → Add SAST/DAST/SCA scans (template-ci-cd.md)
    │
    ├─ Observability & monitoring?
    │   ├─ Metrics → Prometheus + Grafana
    │   ├─ Distributed tracing → Jaeger or OpenTelemetry
    │   ├─ Logs → Loki or ELK stack
    │   ├─ eBPF-based → Cilium + Hubble (sidecarless)
    │   └─ Unified platform → Datadog or New Relic
    │
    ├─ Incident management?
    │   ├─ On-call rotation → PagerDuty or Opsgenie
    │   ├─ Postmortem → template-postmortem.md
    │   └─ Communication → template-incident-comm.md
    │
    ├─ Platform engineering?
    │   ├─ Self-service → Backstage or Port (internal developer portal)
    │   ├─ Policy enforcement → OPA/Gatekeeper
    │   └─ Golden paths → Template repositories + automation
    │
    └─ Security hardening?
        ├─ Container scanning → Trivy or Grype
        ├─ Runtime security → Falco or Sysdig
        ├─ Secrets management → HashiCorp Vault or cloud-native KMS
        └─ Compliance → CIS Benchmarks, template-security-hardening.md
```

---

## When to Use This Skill

Claude should invoke this skill when users request:

- Platform engineering patterns (self-service developer platforms, internal tools)
- GitOps workflows (ArgoCD, FluxCD, declarative infrastructure management)
- Infrastructure as Code patterns (Terraform, K8s manifests, policy as code)
- CI/CD pipelines with DevSecOps (GitHub Actions, security scanning, SAST/DAST/SCA)
- SRE incident management, escalation, and postmortem templates
- eBPF-based observability (Cilium, Hubble, kernel-level insights, OpenTelemetry)
- Kubernetes operational patterns (day-2 operations, resource management, workload placement)
- Cloud-native monitoring (Prometheus, Grafana, unified observability platforms)
- Team workflow, communication, handover guides, and runbooks

---

## Resources (Best Practices Guides)

Operational best practices by domain:

- **DevOps/SRE Operations**: [references/devops-best-practices.md](references/devops-best-practices.md) - Core patterns for safe infrastructure changes, deployments, and incident response
- **Platform Engineering**: [references/platform-engineering-patterns.md](references/platform-engineering-patterns.md) - Self-service platforms, golden paths, internal developer portals, policy as code
- **GitOps Workflows**: [references/gitops-workflows.md](references/gitops-workflows.md) - Continuous reconciliation, multi-environment promotion, ArgoCD/FluxCD patterns, progressive delivery
- **SRE Incident Management**: [references/sre-incident-management.md](references/sre-incident-management.md) - Severity classification, escalation procedures, blameless postmortems, alert correlation, and runbooks
- **Operational Standards**: [references/operational-patterns.md](references/operational-patterns.md) - Platform engineering blueprints, CI/CD safety, SLOs, and reliability drills

Each guide includes:
- Checklists for completeness and safety
- Common anti-patterns and remediations
- Step-by-step patterns for safe rollout, rollback, and verification
- Decision matrices (e.g., deployment, escalation, monitoring strategy)
- Real-world examples and edge case handling

---

## Templates (Copy-Paste Ready)

Production templates organized by tech stack:

### AWS Cloud
- [assets/aws/template-aws-ops.md](assets/aws/template-aws-ops.md) - AWS service operations and best practices
- [assets/aws/template-aws-terraform.md](assets/aws/template-aws-terraform.md) - Terraform modules for AWS infrastructure
- [assets/aws/template-cost-optimization.md](assets/aws/template-cost-optimization.md) - AWS cost optimization strategies

### GCP Cloud
- [assets/gcp/template-gcp-ops.md](assets/gcp/template-gcp-ops.md) - GCP service operations
- [assets/gcp/template-gcp-terraform.md](assets/gcp/template-gcp-terraform.md) - Terraform modules for GCP

### Azure Cloud
- [assets/azure/template-azure-ops.md](assets/azure/template-azure-ops.md) - Azure service operations

### Kubernetes
- [assets/kubernetes/template-kubernetes-ops.md](assets/kubernetes/template-kubernetes-ops.md) - Day-to-day K8s operations
- [assets/kubernetes/template-ha-dr.md](assets/kubernetes/template-ha-dr.md) - High availability and disaster recovery
- [assets/kubernetes/template-platform-api.md](assets/kubernetes/template-platform-api.md) - Platform API patterns
- [assets/kubernetes/template-k8s-deploy.yaml](assets/kubernetes/template-k8s-deploy.yaml) - Deployment manifests

### Docker
- [assets/docker/template-docker-ops.md](assets/docker/template-docker-ops.md) - Container build, security, and operations

### Kafka
- [assets/kafka/template-kafka-ops.md](assets/kafka/template-kafka-ops.md) - Kafka cluster operations and streaming

### Terraform & IaC
- [assets/terraform-iac/template-iac-terraform.md](assets/terraform-iac/template-iac-terraform.md) - Infrastructure as Code patterns
- [assets/terraform-iac/template-module.md](assets/terraform-iac/template-module.md) - Reusable Terraform modules
- [assets/terraform-iac/template-env-promotion.md](assets/terraform-iac/template-env-promotion.md) - Environment promotion strategies

### CI/CD Pipelines
- [assets/cicd-pipelines/template-ci-cd.md](assets/cicd-pipelines/template-ci-cd.md) - General CI/CD patterns
- [assets/cicd-pipelines/template-github-actions.md](assets/cicd-pipelines/template-github-actions.md) - GitHub Actions workflows
- [assets/cicd-pipelines/template-gitops.md](assets/cicd-pipelines/template-gitops.md) - GitOps deployment patterns
- [assets/cicd-pipelines/template-release-safety.md](assets/cicd-pipelines/template-release-safety.md) - Safe release practices

### Monitoring & Observability
- [assets/monitoring-observability/template-slo.md](assets/monitoring-observability/template-slo.md) - Service level objectives
- [assets/monitoring-observability/template-alert-rules.md](assets/monitoring-observability/template-alert-rules.md) - Alert configuration
- [assets/monitoring-observability/template-observability-slo.md](assets/monitoring-observability/template-observability-slo.md) - Observability patterns
- [assets/monitoring-observability/template-loadtest-perf.md](assets/monitoring-observability/template-loadtest-perf.md) - Load testing and performance

### Incident Response
- [assets/incident-response/template-postmortem.md](assets/incident-response/template-postmortem.md) - Incident postmortems
- [assets/incident-response/template-runbook-starter.md](assets/incident-response/template-runbook-starter.md) - Runbook starter template
- [assets/incident-response/template-incident-comm.md](assets/incident-response/template-incident-comm.md) - Incident communication
- [assets/incident-response/template-incident-response.md](assets/incident-response/template-incident-response.md) - Incident response procedures

### Security
- [assets/security/template-security-hardening.md](assets/security/template-security-hardening.md) - Security hardening checklists

---

## Navigation

**Resources**
- [references/operational-patterns.md](references/operational-patterns.md)
- [references/sre-incident-management.md](references/sre-incident-management.md)
- [references/devops-best-practices.md](references/devops-best-practices.md)
- [references/platform-engineering-patterns.md](references/platform-engineering-patterns.md)
- [references/gitops-workflows.md](references/gitops-workflows.md)

**Shared Utilities** (Centralized patterns — extract, don't duplicate)
- [../software-clean-code-standard/utilities/config-validation.md](../software-clean-code-standard/utilities/config-validation.md) — Zod 3.24+, secrets management (Vault, 1Password, Doppler)
- [../software-clean-code-standard/utilities/resilience-utilities.md](../software-clean-code-standard/utilities/resilience-utilities.md) — p-retry v6, circuit breaker, OTel spans
- [../software-clean-code-standard/utilities/logging-utilities.md](../software-clean-code-standard/utilities/logging-utilities.md) — pino v9 + OpenTelemetry integration
- [../software-clean-code-standard/utilities/observability-utilities.md](../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics
- [../software-clean-code-standard/utilities/testing-utilities.md](../software-clean-code-standard/utilities/testing-utilities.md) — Test factories, fixtures, mocks
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) — Canonical clean code rules (`CC-*`) for citation

**Templates**
- [assets/incident-response/template-postmortem.md](assets/incident-response/template-postmortem.md)
- [assets/incident-response/template-runbook-starter.md](assets/incident-response/template-runbook-starter.md)
- [assets/incident-response/template-incident-comm.md](assets/incident-response/template-incident-comm.md)
- [assets/incident-response/template-incident-response.md](assets/incident-response/template-incident-response.md)
- [assets/docker/template-docker-ops.md](assets/docker/template-docker-ops.md)
- [assets/security/template-security-hardening.md](assets/security/template-security-hardening.md)
- [assets/azure/template-azure-ops.md](assets/azure/template-azure-ops.md)
- [assets/gcp/template-gcp-terraform.md](assets/gcp/template-gcp-terraform.md)
- [assets/gcp/template-gcp-ops.md](assets/gcp/template-gcp-ops.md)
- [assets/cicd-pipelines/template-release-safety.md](assets/cicd-pipelines/template-release-safety.md)
- [assets/cicd-pipelines/template-gitops.md](assets/cicd-pipelines/template-gitops.md)
- [assets/cicd-pipelines/template-ci-cd.md](assets/cicd-pipelines/template-ci-cd.md)
- [assets/cicd-pipelines/template-github-actions.md](assets/cicd-pipelines/template-github-actions.md)
- [assets/kafka/template-kafka-ops.md](assets/kafka/template-kafka-ops.md)
- [assets/aws/template-aws-terraform.md](assets/aws/template-aws-terraform.md)
- [assets/aws/template-aws-ops.md](assets/aws/template-aws-ops.md)
- [assets/aws/template-cost-optimization.md](assets/aws/template-cost-optimization.md)
- [assets/monitoring-observability/template-slo.md](assets/monitoring-observability/template-slo.md)
- [assets/monitoring-observability/template-loadtest-perf.md](assets/monitoring-observability/template-loadtest-perf.md)
- [assets/monitoring-observability/template-alert-rules.md](assets/monitoring-observability/template-alert-rules.md)
- [assets/monitoring-observability/template-observability-slo.md](assets/monitoring-observability/template-observability-slo.md)
- [assets/kubernetes/template-k8s-deploy.yaml](assets/kubernetes/template-k8s-deploy.yaml)
- [assets/kubernetes/template-platform-api.md](assets/kubernetes/template-platform-api.md)
- [assets/kubernetes/template-kubernetes-ops.md](assets/kubernetes/template-kubernetes-ops.md)
- [assets/kubernetes/template-ha-dr.md](assets/kubernetes/template-ha-dr.md)
- [assets/terraform-iac/template-env-promotion.md](assets/terraform-iac/template-env-promotion.md)
- [assets/terraform-iac/template-iac-terraform.md](assets/terraform-iac/template-iac-terraform.md)
- [assets/terraform-iac/template-module.md](assets/terraform-iac/template-module.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## Related Skills

**Operations & Infrastructure:**
- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) — Resilience, chaos engineering, and failure handling patterns
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database tuning, high availability, and migrations
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md) — Monitoring, tracing, profiling, and performance optimization
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md) — Production debugging, log analysis, and root cause investigation

**Security & Compliance:**
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Application-layer security patterns and OWASP best practices

**Software Development:**
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Service-level design and integration patterns
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design, scalability, and architectural patterns
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — RESTful API design and versioning
- [../git-workflow/SKILL.md](../git-workflow/SKILL.md) — Git branching strategies and CI/CD integration

**Optional: AI/Automation (Related Skills):**
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md) — ML model deployment, monitoring, and lifecycle management

---

## Cost Governance & Capacity Planning

**[assets/cost-governance/template-cost-governance.md](assets/cost-governance/template-cost-governance.md)** — Production cost control for cloud infrastructure.

### Key Sections

- **Cost Governance Framework** — Tagging strategy, budget alerts, anomaly detection
- **Cloud Cost Optimization** — Right-sizing, reserved capacity, storage tiering
- **Kubernetes Cost Control** — Resource requests/limits, quotas, autoscaler config
- **Capacity Planning** — Utilization baseline, growth projections, scaling triggers
- **FinOps Practices** — Monthly review agenda, optimization workflow

---

## Do / Avoid

### GOOD: Do

- Tag all resources at creation time
- Set budget alerts before hitting limits
- Review right-sizing recommendations monthly
- Use spot/preemptible for fault-tolerant workloads
- Set Kubernetes resource requests on all pods
- Enable cluster autoscaler with scale-down
- Document capacity planning assumptions
- Run postmortems after every incident

### BAD: Avoid

- Deploying without cost tags
- Running dev resources 24/7
- Over-provisioning "just in case"
- Ignoring reserved capacity opportunities
- Disabling scale-down to "avoid disruption"
- Alert fatigue (too many low-priority alerts)
- Snowflake infrastructure (manual, undocumented)
- "Clickops" drift (changes outside IaC)

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No tagging** | Can't attribute costs | Enforce tags in CI/CD |
| **Dev runs 24/7** | 70% waste | Scheduled shutdown |
| **Over-provisioned** | Paying for unused capacity | Monthly right-sizing |
| **No reservations** | Paying on-demand premium | 60-70% coverage target |
| **Alert fatigue** | Real issues missed | SLO-based alerting, tuned thresholds |
| **Snowflake infra** | Undocumented, unreproducible | Everything in Terraform/IaC |
| **No postmortems** | Same incidents repeat | Blameless postmortem for every SEV1/2 |

---

## Optional: AI/Automation (AIOps)

> Note: AI can assist with analysis and triage, but infrastructure/cost/incident decisions require human approval and an audit trail (especially anything destructive or irreversible).

### AIOps Capabilities (2026)

**Self-Healing Systems:**
- AI-powered anomaly detection to predict failures before they happen
- Automated remediation flows that trigger rollbacks or config changes
- Intelligent test selection and risk-based change scoring in CI/CD
- Causal graph analysis for instant root cause identification

**Automated Operations:**
- Unused resource detection and notification
- Right-sizing recommendation generation
- Alert summarization and correlation (reduce noise by 90%+)
- Runbook step suggestions and automated execution

### AI-Assisted Analysis

- Cost trend prediction and anomaly detection
- Incident pattern identification across services
- Post-mortem theme extraction
- Capacity planning predictions

### Platform Engineering + AI

Platform teams increasingly embed AI capabilities directly into the platform:
- Multi-agent orchestration for code generation, security validation, deployment
- Intelligent defaults and guardrails that scale across teams

### Bounded Claims

- AI recommendations need validation before action
- Automated deletions require approval workflow
- Cost predictions are estimates, not guarantees
- Runbook suggestions need SRE verification
- Self-healing actions should have human-defined policies and audit trails

---

## Operational Deep Dives

See [references/operational-patterns.md](references/operational-patterns.md) for:
- Platform engineering blueprints and GitOps reconciliation checklists
- DevSecOps CI/CD gates, SLO/SLI playbooks, and rollout verification steps
- Observability patterns (eBPF), incident noise reduction, and reliability drills

---

## External Resources

See [data/sources.json](data/sources.json) for curated sources organized by tech stack:
- **Cloud Platforms**: AWS, GCP, Azure documentation and best practices
- **Container Orchestration**: Kubernetes, Helm, Kustomize, Docker
- **Infrastructure as Code**: Terraform, OpenTofu, Pulumi, CloudFormation, ARM templates
- **CI/CD & GitOps**: GitHub Actions, GitLab CI, Jenkins, ArgoCD, FluxCD
- **Streaming**: Apache Kafka, Confluent, Strimzi
- **Monitoring**: Prometheus, Grafana, Datadog, OpenTelemetry, Jaeger, Cilium/Hubble, Tetragon
- **SRE**: Google SRE books, incident response patterns
- **Security**: OWASP DevSecOps, CIS Benchmarks, Trivy, Falco
- **Tools**: kubectl, k9s, stern, Cosign, Syft, Terragrunt

---

*Use this skill as a hub for safe, modern, and production-grade DevOps patterns. All templates and patterns are operational—no theory or book summaries.*

---

## Trend Awareness Protocol

When users ask recommendation questions about DevOps, platform engineering, or cloud infrastructure, validate time-sensitive details (versions, deprecations, licensing, major releases) against primary sources.

### Trigger Conditions

- "What's the best tool for [Kubernetes/IaC/CI-CD/monitoring]?"
- "What should I use for [container orchestration/GitOps/observability]?"
- "What's the latest in DevOps/platform engineering?"
- "Current best practices for [Terraform/ArgoCD/Prometheus]?"
- "Is [tool/approach] still relevant in 2026?"
- "[Kubernetes] vs [alternative]?" or "[ArgoCD] vs [FluxCD]?"
- "Best cloud provider for [use case]?"
- "What orchestration/monitoring tool should I use?"

### Minimum Verification (Preferred Order)

1. Check the official docs + release notes linked in [data/sources.json](data/sources.json) for the specific tools you recommend.
2. If internet access is available, confirm recent releases, breaking changes, and deprecations from those release pages.
3. If internet access is not available, state that versions may have changed and focus on stable selection criteria (operational fit, ecosystem, maturity, team skills, compliance).

### What to Report

After searching, provide:

- **Current landscape**: What tools/approaches are popular NOW (not 6 months ago)
- **Emerging trends**: New tools, patterns, or practices gaining traction
- **Deprecated/declining**: Tools/approaches losing relevance or support
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- Kubernetes versions and ecosystem tools (1.33+, Cilium, Gateway API)
- Infrastructure as Code (Terraform, OpenTofu, Pulumi, CDK)
- GitOps platforms (ArgoCD, FluxCD, Codefresh)
- Observability stacks (OpenTelemetry, Grafana stack, Datadog)
- Platform engineering tools (Backstage, Port, Kratix)
- CI/CD platforms (GitHub Actions, GitLab CI, Dagger)
- Cloud-native security (Falco, Trivy, policy engines)
