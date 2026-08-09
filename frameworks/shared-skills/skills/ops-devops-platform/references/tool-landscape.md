# Tool Landscape (2026)

*Use when:* A user wants a current tool comparison, asks what is still relevant in 2026, or needs a shortlist before you dive into a specific domain reference.

## Table of Contents
- IaC and cloud provisioning
- CI/CD and GitOps delivery
- Platform engineering
- Observability and runtime security
- Streaming and data-plane operations
- Recommendation defaults

---

## IaC and Cloud Provisioning

- **Terraform / OpenTofu**: Default when you want broad ecosystem support, cross-cloud coverage, and declarative review-first workflows. As of mid-2026 these are no longer feature-identical: OpenTofu (MPL-2.0, Linux Foundation, CNCF project since April 2025) has shipped state encryption, early variable evaluation, provider `for_each` iteration, an `-exclude` flag, and OCI registry support ahead of Terraform's BSL-licensed binary. Choose OpenTofu by default for new work unless a specific HashiCorp-only integration (e.g. HCP Terraform-specific features) is required; re-verify feature parity before assuming either tool has "caught up."
- **Pulumi**: Choose when the team genuinely benefits from general-purpose languages, richer abstractions, or tighter integration with existing application code.
- **CloudFormation / Bicep / AWS CDK**: Choose when cloud-provider-native fit matters more than portability.
- **Terragrunt**: Use for large Terraform/OpenTofu estates that need DRY composition, environment layering, and shared backend/state conventions.

### Quick rule

- Default to Terraform or OpenTofu unless a provider-native workflow or programming-first model clearly reduces complexity.

---

## CI/CD and GitOps Delivery

- **GitHub Actions**: Strong default for GitHub-centric teams, especially when OIDC/workload identity can eliminate long-lived cloud credentials.
- **GitLab CI**: Good fit when source control, package registry, security scanning, and delivery are already centered on GitLab.
- **Jenkins / Tekton**: Use when you need deep enterprise customization, self-hosted runners, or Kubernetes-native pipeline primitives.
- **Dagger**: Use when teams want portable pipeline logic as code that can run locally and in CI.
- **Argo CD / Flux**: Default GitOps controllers for Kubernetes delivery. Argo CD usually wins on UI and multi-app ergonomics; Flux stays lean and composable.
- **Codefresh**: Consider when you want a commercial platform layered on GitOps workflows rather than operating everything yourself.

### Quick rule

- Prefer a hosted CI system plus GitOps controller before introducing a platform layer or pipeline SDK.

---

## Platform Engineering

- **Backstage**: Default open-source portal when you want service catalog, plugin ecosystem, and broad community adoption.
- **Port**: Good fit when the team wants a managed portal/control-plane experience with less platform code to own.
- **Kratix**: Useful when you want GitOps-native platform APIs and multi-cluster promise delivery rather than a portal-first experience.
- **Team Topologies**: Use as an organizational lens, not as a tooling decision.

### Quick rule

- Start with Backstage for open extensibility, Port for faster managed rollout, or Kratix for API/control-plane-first platform design.

---

## Observability and Runtime Security

- **OpenTelemetry**: Treat as the telemetry standard and collection pipeline, not as the tracing backend itself.
- **Prometheus + Grafana**: Strong default for Kubernetes-native metrics, dashboards, and alerting.
- **Datadog**: Use when a unified managed platform outweighs the cost or lock-in trade-off.
- **Jaeger**: Use as a tracing backend or troubleshooting tool, typically alongside OpenTelemetry instrumentation.
- **Cilium + Hubble / Tetragon**: Use when eBPF-based networking, service visibility, and runtime signals matter enough to justify kernel-level tooling.
- **Falco**: Use for runtime threat detection and policy-driven alerts.

### Quick rule

- Default to OpenTelemetry plus either Prometheus/Grafana or a vendor suite, then add Jaeger, Cilium/Tetragon, or Falco only when the operational problem justifies them.

---

## Streaming and Data-Plane Operations

- **Apache Kafka**: Default open ecosystem choice for event streaming and durable logs.
- **Confluent Platform**: Consider when governance, enterprise operations, and managed platform capabilities outweigh OSS minimalism.
- **Strimzi**: Use when Kafka will run on Kubernetes and you want an operator-managed model.

### Quick rule

- Choose Kafka first, then decide whether you want the operator model (Strimzi) or the broader commercial platform model (Confluent).

---

## Recommendation Defaults

- Default to fewer systems with clearer ownership. Add platform layers only when they remove real toil or risk.
- Prefer official docs plus release notes before recommending a tool with fast-moving versions or licensing.
- Call out deprecations explicitly. Do not preserve declining tools in recommendations just because older runbooks still mention them.
- For broad comparison questions, use this file first, then open the domain-specific reference that matches the chosen direction.
