---
name: ops-devops-platform
description: Production-grade DevOps patterns with Kubernetes 1.34+, Terraform 1.9+, Docker 27+, ArgoCD/FluxCD GitOps, SRE, eBPF-based observability, AI-driven monitoring, CI/CD security, and cloud-native operations (AWS, GCP, Azure, Kafka).
---

# DevOps Engineering — Quick Reference

This skill equips Claude with actionable templates, checklists, and patterns for building self-service platforms, automating infrastructure with GitOps, deploying securely with DevSecOps, scaling with Kubernetes, ensuring reliability through SRE practices, and operating production systems with AI-driven observability.

**Modern Best Practices (December 2025)**: Kubernetes 1.34 (in-place Pod resource updates GA, 1.35 releasing Dec 17), Docker 27 with BuildKit optimizations, Terraform 1.9+ with improved provider ecosystem, ArgoCD 2.14/FluxCD 2.5 GitOps patterns, eBPF-based observability (Cilium, Hubble), and AI-driven AIOps for incident correlation.

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Infrastructure as Code | Terraform 1.9+ | `terraform plan && terraform apply` | Provision cloud resources declaratively |
| GitOps Deployment | ArgoCD / FluxCD | `argocd app sync myapp` | Continuous reconciliation, declarative deployments |
| Container Build | Docker 27+ | `docker build -t app:v1 .` | Package applications with dependencies |
| Kubernetes Deployment | kubectl / Helm (K8s 1.34+) | `kubectl apply -f deploy.yaml` / `helm upgrade app ./chart` | Deploy to K8s cluster, manage releases |
| CI/CD Pipeline | GitHub Actions | Define workflow in `.github/workflows/ci.yml` | Automated testing, building, deploying |
| Security Scanning | Trivy / Falco | `trivy image myapp:latest` | Vulnerability scanning, runtime security |
| Monitoring & Alerts | Prometheus + Grafana | Configure ServiceMonitor and AlertManager | Observability, SLO tracking, incident alerts |
| Load Testing | k6 / Locust | `k6 run load-test.js` | Performance validation, capacity planning |
| Incident Response | PagerDuty / Opsgenie | Configure escalation policies | On-call management, automated escalation |
| Platform Engineering | Backstage / Port | Deploy internal developer portal | Self-service infrastructure, golden paths |

---

## Decision Tree: Choosing DevOps Approach

```text
What do you need to accomplish?
    ├─ Infrastructure provisioning?
    │   ├─ Cloud-agnostic → Terraform (multi-cloud support)
    │   ├─ AWS-specific → CloudFormation or Terraform
    │   ├─ GCP-specific → Deployment Manager or Terraform
    │   └─ Azure-specific → ARM templates or Terraform
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
- SRE incident management, AI-driven alerting, escalation, or postmortem templates
- eBPF-based observability (Cilium, Hubble, kernel-level insights, OpenTelemetry)
- Kubernetes operational patterns (day-2 operations, resource management, workload placement)
- Cloud-native monitoring (Prometheus, Grafana, unified observability platforms)
- Team workflow, communication, handover guides, and runbooks

---

## Resources (Best Practices Guides)

Operational best practices by domain:

- **DevOps/SRE Operations**: [resources/devops-best-practices.md](resources/devops-best-practices.md) - Core patterns for safe infrastructure changes, deployments, and incident response
- **Platform Engineering**: [resources/platform-engineering-patterns.md](resources/platform-engineering-patterns.md) - Self-service platforms, golden paths, internal developer portals, policy as code
- **GitOps Workflows**: [resources/gitops-workflows.md](resources/gitops-workflows.md) - Continuous reconciliation, multi-environment promotion, ArgoCD/FluxCD patterns, progressive delivery
- **SRE Incident Management**: [resources/sre-incident-management.md](resources/sre-incident-management.md) - Severity classification, escalation procedures, blameless postmortems, AI-driven correlation
- **Operational Standards**: [resources/operational-patterns.md](resources/operational-patterns.md) - Platform engineering blueprints, CI/CD safety, SLOs, and reliability drills

Each guide includes:
- Checklists for completeness and safety
- Common anti-patterns and remediations
- Step-by-step patterns for safe rollout, rollback, and verification
- Decision matrices (e.g., deployment, escalation, monitoring strategy)
- Real-world examples and edge case handling

---

## Templates (Copy-Paste Ready)

Production templates organized by tech stack (27 templates total):

### AWS Cloud
- [templates/aws/template-aws-ops.md](templates/aws/template-aws-ops.md) - AWS service operations and best practices
- [templates/aws/template-aws-terraform.md](templates/aws/template-aws-terraform.md) - Terraform modules for AWS infrastructure
- [templates/aws/template-cost-optimization.md](templates/aws/template-cost-optimization.md) - AWS cost optimization strategies

### GCP Cloud
- [templates/gcp/template-gcp-ops.md](templates/gcp/template-gcp-ops.md) - GCP service operations
- [templates/gcp/template-gcp-terraform.md](templates/gcp/template-gcp-terraform.md) - Terraform modules for GCP

### Azure Cloud
- [templates/azure/template-azure-ops.md](templates/azure/template-azure-ops.md) - Azure service operations

### Kubernetes
- [templates/kubernetes/template-kubernetes-ops.md](templates/kubernetes/template-kubernetes-ops.md) - Day-to-day K8s operations
- [templates/kubernetes/template-ha-dr.md](templates/kubernetes/template-ha-dr.md) - High availability and disaster recovery
- [templates/kubernetes/template-platform-api.md](templates/kubernetes/template-platform-api.md) - Platform API patterns
- [templates/kubernetes/template-k8s-deploy.yaml](templates/kubernetes/template-k8s-deploy.yaml) - Deployment manifests

### Docker
- [templates/docker/template-docker-ops.md](templates/docker/template-docker-ops.md) - Container build, security, and operations

### Kafka
- [templates/kafka/template-kafka-ops.md](templates/kafka/template-kafka-ops.md) - Kafka cluster operations and streaming

### Terraform & IaC
- [templates/terraform-iac/template-iac-terraform.md](templates/terraform-iac/template-iac-terraform.md) - Infrastructure as Code patterns
- [templates/terraform-iac/template-module.md](templates/terraform-iac/template-module.md) - Reusable Terraform modules
- [templates/terraform-iac/template-env-promotion.md](templates/terraform-iac/template-env-promotion.md) - Environment promotion strategies

### CI/CD Pipelines
- [templates/cicd-pipelines/template-ci-cd.md](templates/cicd-pipelines/template-ci-cd.md) - General CI/CD patterns
- [templates/cicd-pipelines/template-github-actions.md](templates/cicd-pipelines/template-github-actions.md) - GitHub Actions workflows
- [templates/cicd-pipelines/template-gitops.md](templates/cicd-pipelines/template-gitops.md) - GitOps deployment patterns
- [templates/cicd-pipelines/template-release-safety.md](templates/cicd-pipelines/template-release-safety.md) - Safe release practices

### Monitoring & Observability
- [templates/monitoring-observability/template-slo.md](templates/monitoring-observability/template-slo.md) - Service level objectives
- [templates/monitoring-observability/template-alert-rules.md](templates/monitoring-observability/template-alert-rules.md) - Alert configuration
- [templates/monitoring-observability/template-observability-slo.md](templates/monitoring-observability/template-observability-slo.md) - Observability patterns
- [templates/monitoring-observability/template-loadtest-perf.md](templates/monitoring-observability/template-loadtest-perf.md) - Load testing and performance

### Incident Response
- [templates/incident-response/template-postmortem.md](templates/incident-response/template-postmortem.md) - Incident postmortems
- [templates/incident-response/template-incident-comm.md](templates/incident-response/template-incident-comm.md) - Incident communication
- [templates/incident-response/template-incident-response.md](templates/incident-response/template-incident-response.md) - Incident response procedures

### Security
- [templates/security/template-security-hardening.md](templates/security/template-security-hardening.md) - Security hardening checklists

---

## Navigation

**Resources**
- [resources/operational-patterns.md](resources/operational-patterns.md)
- [resources/sre-incident-management.md](resources/sre-incident-management.md)
- [resources/devops-best-practices.md](resources/devops-best-practices.md)
- [resources/platform-engineering-patterns.md](resources/platform-engineering-patterns.md)
- [resources/gitops-workflows.md](resources/gitops-workflows.md)

**Shared Utilities** (Centralized patterns — extract, don't duplicate)
- [../_shared/utilities/config-validation.md](../_shared/utilities/config-validation.md) — Zod 3.24+, secrets management (Vault, 1Password, Doppler)
- [../_shared/utilities/resilience-utilities.md](../_shared/utilities/resilience-utilities.md) — p-retry v6, circuit breaker, OTel spans
- [../_shared/utilities/logging-utilities.md](../_shared/utilities/logging-utilities.md) — pino v9 + OpenTelemetry integration
- [../_shared/utilities/observability-utilities.md](../_shared/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics
- [../_shared/utilities/testing-utilities.md](../_shared/utilities/testing-utilities.md) — Test factories, fixtures, mocks
- [../_shared/resources/code-quality-operational-playbook.md](../_shared/resources/code-quality-operational-playbook.md) — Canonical coding rules & review protocols

**Templates**
- [templates/incident-response/template-postmortem.md](templates/incident-response/template-postmortem.md)
- [templates/incident-response/template-incident-comm.md](templates/incident-response/template-incident-comm.md)
- [templates/incident-response/template-incident-response.md](templates/incident-response/template-incident-response.md)
- [templates/docker/template-docker-ops.md](templates/docker/template-docker-ops.md)
- [templates/security/template-security-hardening.md](templates/security/template-security-hardening.md)
- [templates/azure/template-azure-ops.md](templates/azure/template-azure-ops.md)
- [templates/gcp/template-gcp-terraform.md](templates/gcp/template-gcp-terraform.md)
- [templates/gcp/template-gcp-ops.md](templates/gcp/template-gcp-ops.md)
- [templates/cicd-pipelines/template-release-safety.md](templates/cicd-pipelines/template-release-safety.md)
- [templates/cicd-pipelines/template-gitops.md](templates/cicd-pipelines/template-gitops.md)
- [templates/cicd-pipelines/template-ci-cd.md](templates/cicd-pipelines/template-ci-cd.md)
- [templates/cicd-pipelines/template-github-actions.md](templates/cicd-pipelines/template-github-actions.md)
- [templates/kafka/template-kafka-ops.md](templates/kafka/template-kafka-ops.md)
- [templates/aws/template-aws-terraform.md](templates/aws/template-aws-terraform.md)
- [templates/aws/template-aws-ops.md](templates/aws/template-aws-ops.md)
- [templates/aws/template-cost-optimization.md](templates/aws/template-cost-optimization.md)
- [templates/monitoring-observability/template-slo.md](templates/monitoring-observability/template-slo.md)
- [templates/monitoring-observability/template-loadtest-perf.md](templates/monitoring-observability/template-loadtest-perf.md)
- [templates/monitoring-observability/template-alert-rules.md](templates/monitoring-observability/template-alert-rules.md)
- [templates/monitoring-observability/template-observability-slo.md](templates/monitoring-observability/template-observability-slo.md)
- [templates/kubernetes/template-k8s-deploy.yaml](templates/kubernetes/template-k8s-deploy.yaml)
- [templates/kubernetes/template-platform-api.md](templates/kubernetes/template-platform-api.md)
- [templates/kubernetes/template-kubernetes-ops.md](templates/kubernetes/template-kubernetes-ops.md)
- [templates/kubernetes/template-ha-dr.md](templates/kubernetes/template-ha-dr.md)
- [templates/terraform-iac/template-env-promotion.md](templates/terraform-iac/template-env-promotion.md)
- [templates/terraform-iac/template-iac-terraform.md](templates/terraform-iac/template-iac-terraform.md)
- [templates/terraform-iac/template-module.md](templates/terraform-iac/template-module.md)

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

**AI/ML Operations:**
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md) — ML model deployment, monitoring, and lifecycle management
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md) — ML security, governance, and compliance

---

## Operational Deep Dives

See [resources/operational-patterns.md](resources/operational-patterns.md) for:
- Platform engineering blueprints and GitOps reconciliation checklists
- DevSecOps CI/CD gates, SLO/SLI playbooks, and rollout verification steps
- Observability patterns (eBPF), AIOps incident handling, and reliability drills

---

## External Resources

See [data/sources.json](data/sources.json) for 45+ curated sources organized by tech stack:
- **Cloud Platforms**: AWS, GCP, Azure documentation and best practices
- **Container Orchestration**: Kubernetes, Helm, Kustomize, Docker
- **Infrastructure as Code**: Terraform, CloudFormation, ARM templates
- **CI/CD & GitOps**: GitHub Actions, GitLab CI, Jenkins, ArgoCD, FluxCD
- **Streaming**: Apache Kafka, Confluent, Strimzi
- **Monitoring**: Prometheus, Grafana, Datadog, OpenTelemetry, Jaeger
- **SRE**: Google SRE books, incident response patterns
- **Security**: OWASP DevSecOps, CIS Benchmarks, Trivy, Falco
- **Tools**: kubectl, k9s, stern, Cosign, Syft, Terragrunt

---

*Use this skill as a hub for safe, modern, and production-grade DevOps patterns. All templates and patterns are operational—no theory or book summaries.*
```
