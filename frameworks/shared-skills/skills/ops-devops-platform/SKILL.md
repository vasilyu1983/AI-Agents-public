---
name: ops-devops-platform
description: "Designs DevOps and platform engineering systems. Use when planning Kubernetes, Terraform, GitOps, CI/CD, observability, incident response, or cloud-native operations."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# DevOps and Platform Engineering

Use this skill for platform, infrastructure, CI/CD, GitOps, observability, and incident-operating-model design. Keep the output operational: target architecture, rollout path, guardrails, ownership, and artifacts.

## Quick Reference

| Need | Starting Direction |
|------|--------------------|
| infrastructure provisioning | Terraform, OpenTofu, Pulumi, or cloud-native IaC |
| cluster or app deployment | GitOps first for steady-state, direct tooling for local iteration |
| CI/CD | protected pipelines plus workload identity and supply-chain controls — see [supply-chain-security](references/supply-chain-security.md) |
| observability | OpenTelemetry plus metrics, logs, traces, and SLO-based alerting |
| platform engineering | golden paths, policy-as-code, and self-service interfaces |
| incident operations | runbooks, severity model, escalation, and postmortems |

## Workflow

1. classify the dominant problem:
   - provisioning
   - deployment
   - CI/CD
   - observability
   - platform engineering
   - security hardening
   - incident operations
2. choose the smallest viable toolchain that matches the runtime and team skill
3. load the relevant reference and template set
4. verify version-sensitive or vendor-sensitive claims before final guidance
5. finish with concrete operational outputs: plan, controls, owners, and artifacts

## Decision Rules

| Situation | Rule |
|-----------|------|
| any infrastructure change | IaC first; no clickops |
| steady-state production reconciliation | GitOps (Argo CD / Flux) over push-based deploys |
| CI credentials | workload identity (OIDC) over long-lived secrets |
| alerting | SLO burn-rate alerts; suppress raw host-metric noise |
| new environments | platform template + policy guard; no snowflakes |
| supply-chain integrity | SLSA build track + cosign keyless signing |
| drift | detect via reconciler or `terraform plan` in CI; never discover by accident |

## Related Routing

- service-level retries, deadlines, and chaos engineering -> [qa-resilience](../qa-resilience/SKILL.md)
- telemetry implementation details -> [qa-observability](../qa-observability/SKILL.md)
- backend service design -> [software-backend](../software-backend/SKILL.md)
- system architecture -> [software-architecture-design](../software-architecture-design/SKILL.md)
- appsec-specific design -> [software-security-appsec](../software-security-appsec/SKILL.md)
- Git branch and PR workflow policy -> [dev-git-workflow](../dev-git-workflow/SKILL.md)

---

## Guardrails

| Domain | Do | Anti-pattern to avoid |
|--------|----|-----------------------|
| Provisioning | all material changes in IaC; explicit promotion gates | clickops drift; untagged infrastructure |
| Delivery | protected pipelines; artifact provenance; rollback + smoke checks | pipelines without identity boundaries |
| Platform | golden paths before self-service; policy-as-code that reduces variation | tools shipped without adoption path or ownership |
| Observability | define SLOs first; join logs/traces/metrics on shared trace ID | alert fatigue from raw host-metric thresholds |
| Incidents | postmortems feed runbooks and platform changes | postmortems that stop at narrative |
| Cost | tagging + budget alerts at resource creation; monthly right-sizing | unmanaged snowflake environments; unreviewed reservations |

---

## Navigation

### Reference routing

| Load when… | Reference |
|------------|-----------|
| supply-chain, SBOM, signing, SLSA | [references/supply-chain-security.md](references/supply-chain-security.md) |
| DORA's five metrics and team archetypes (Elite/High/Medium/Low tiers are retired), AI-adoption instability tax, general DevOps best practices | [references/devops-best-practices.md](references/devops-best-practices.md) |
| GitLab CI — parent/child pipelines, MR variable traps, env-export pattern | [references/gitlab-ci-patterns.md](references/gitlab-ci-patterns.md) |
| choosing a tool (IaC, GitOps, CI, policy, observability) | [references/tool-landscape.md](references/tool-landscape.md) |
| golden paths, internal developer portal, platform maturity, when NOT to build an IDP, platform-vs-product boundary, CI/IaC/GitOps adoption sequencing | [references/platform-engineering-patterns.md](references/platform-engineering-patterns.md) |
| GitOps multi-env promotion, Argo CD / Flux patterns | [references/gitops-workflows.md](references/gitops-workflows.md) |
| on-call, severity model, escalation, postmortems | [references/sre-incident-management.md](references/sre-incident-management.md) |
| day-2 operational runbooks, environment hygiene | [references/operational-patterns.md](references/operational-patterns.md) |
| AIOps alert correlation, automated triage | [references/aiops-patterns.md](references/aiops-patterns.md) |
| Kalman canary, cost autoscaler, CI capacity stabiliser | [references/control-theory-applied.md](references/control-theory-applied.md) |
| capacity planning, saturation SLO, pipeline bottleneck hunt | [references/queueing-theory-applied.md](references/queueing-theory-applied.md) |
| CI/CD throughput recovery, constraint surfacing, spend reallocation | [references/theory-of-constraints-applied.md](references/theory-of-constraints-applied.md) |
| platform-team charter, algedonic escalation, PRR audit | [references/cybernetics-vsm-applied.md](references/cybernetics-vsm-applied.md) |
| MTBF/MTTR, availability budgets, FMEA | [references/reliability-theory-applied.md](references/reliability-theory-applied.md) |
| CAP/PACELC, consensus, idempotency, quorums | [references/distributed-systems-applied.md](references/distributed-systems-applied.md) |
| source URLs and release trackers | [data/sources.json](data/sources.json) |

### Templates

**AWS / GCP / Azure**
- [assets/aws/template-aws-ops.md](assets/aws/template-aws-ops.md) — AWS day-2 ops checklist
- [assets/aws/template-aws-terraform.md](assets/aws/template-aws-terraform.md) — AWS Terraform module skeleton
- [assets/aws/template-cost-optimization.md](assets/aws/template-cost-optimization.md) — AWS cost right-sizing and reservation review
- [assets/gcp/template-gcp-ops.md](assets/gcp/template-gcp-ops.md) — GCP day-2 ops checklist
- [assets/gcp/template-gcp-terraform.md](assets/gcp/template-gcp-terraform.md) — GCP Terraform module skeleton
- [assets/azure/template-azure-ops.md](assets/azure/template-azure-ops.md) — Azure day-2 ops checklist

**Kubernetes**
- [assets/kubernetes/template-kubernetes-ops.md](assets/kubernetes/template-kubernetes-ops.md) — cluster day-2 ops
- [assets/kubernetes/template-ha-dr.md](assets/kubernetes/template-ha-dr.md) — HA and disaster-recovery topology
- [assets/kubernetes/template-platform-api.md](assets/kubernetes/template-platform-api.md) — platform API contract for self-service
- [assets/kubernetes/template-k8s-deploy.yaml](assets/kubernetes/template-k8s-deploy.yaml) — base Deployment manifest

**Docker / Kafka**
- [assets/docker/template-docker-ops.md](assets/docker/template-docker-ops.md) — image build and runtime hardening
- [assets/kafka/template-kafka-ops.md](assets/kafka/template-kafka-ops.md) — Kafka cluster operations

**Terraform / IaC**
- [assets/terraform-iac/template-iac-terraform.md](assets/terraform-iac/template-iac-terraform.md) — root module structure
- [assets/terraform-iac/template-module.md](assets/terraform-iac/template-module.md) — reusable child module
- [assets/terraform-iac/template-env-promotion.md](assets/terraform-iac/template-env-promotion.md) — environment promotion workflow

**CI/CD and GitOps**
- [assets/cicd-pipelines/template-ci-cd.md](assets/cicd-pipelines/template-ci-cd.md) — generic CI/CD pipeline design
- [assets/cicd-pipelines/template-github-actions.md](assets/cicd-pipelines/template-github-actions.md) — GitHub Actions workflow with OIDC
- [assets/cicd-pipelines/template-gitops.md](assets/cicd-pipelines/template-gitops.md) — GitOps promotion pipeline
- [assets/cicd-pipelines/template-release-safety.md](assets/cicd-pipelines/template-release-safety.md) — release gates and rollback

**Monitoring / Observability**
- [assets/monitoring-observability/template-slo.md](assets/monitoring-observability/template-slo.md) — SLO definition sheet
- [assets/monitoring-observability/template-alert-rules.md](assets/monitoring-observability/template-alert-rules.md) — burn-rate alert rules
- [assets/monitoring-observability/template-observability-slo.md](assets/monitoring-observability/template-observability-slo.md) — full observability + SLO stack
- [assets/monitoring-observability/template-loadtest-perf.md](assets/monitoring-observability/template-loadtest-perf.md) — load-test and performance baseline

**Incident response**
- [assets/incident-response/template-postmortem.md](assets/incident-response/template-postmortem.md) — blameless postmortem
- [assets/incident-response/template-runbook-starter.md](assets/incident-response/template-runbook-starter.md) — runbook starter
- [assets/incident-response/template-incident-comm.md](assets/incident-response/template-incident-comm.md) — stakeholder communications
- [assets/incident-response/template-incident-response.md](assets/incident-response/template-incident-response.md) — full IR playbook

**Security / Cost**
- [assets/security/template-security-hardening.md](assets/security/template-security-hardening.md) — hardening checklist
- [assets/cost-governance/template-cost-governance.md](assets/cost-governance/template-cost-governance.md) — FinOps tagging and budget controls

### Shared utilities

- [../software-clean-code-standard/references/config-validation.md](../software-clean-code-standard/references/config-validation.md)
- [../software-clean-code-standard/references/resilience-utilities.md](../software-clean-code-standard/references/resilience-utilities.md)
- [../software-clean-code-standard/references/logging-utilities.md](../software-clean-code-standard/references/logging-utilities.md)
- [../software-clean-code-standard/references/observability-utilities.md](../software-clean-code-standard/references/observability-utilities.md)

## Related Skills

- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md)
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md)
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md)
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md)
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md)
- [../software-backend/SKILL.md](../software-backend/SKILL.md)
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md)
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md)
- [../dev-git-workflow/SKILL.md](../dev-git-workflow/SKILL.md)
- [../ai-mlops/SKILL.md](../ai-mlops/SKILL.md)

## Trend Awareness Protocol

When users ask for current tool recommendations, verify:

- current supported Kubernetes and ecosystem versions
- active IaC and GitOps tool state
- current observability and policy-engine capabilities
- current CI/CD and platform-tool support windows

Prefer official docs and release notes over blogs or rankings.

## Fact-Checking

- Verify current versions, deprecations, support windows, pricing, and cloud limits before final answers.
- Prefer official docs and release notes for named tools and platforms.
- If web access is unavailable, mark version-sensitive guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

