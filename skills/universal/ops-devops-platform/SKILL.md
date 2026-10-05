---
name: ops-devops-platform
description: "Designs DevOps and platform engineering systems. Use when planning Kubernetes, Terraform, GitOps, CI/CD, observability, incident response, or cloud-native operations."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# DevOps and Platform Engineering

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
4. use [source and release links](data/sources.json) to check the target runtime's supported APIs, tool compatibility, and deprecations; for provenance, load [supply-chain-security](references/supply-chain-security.md) and assess the actual builder against the selected SLSA track
5. separate evidence stages: static lint/plan, target-environment reconciliation, runtime health plus a representative service path, and rollback or roll-forward readiness
6. finish with concrete operational outputs: plan, controls, owners, artifact or commit identity, environment, observation window, and untested failure modes

## Decision Rules

| Situation | Rule |
|-----------|------|
| infrastructure change | IaC by default; reconcile an emergency manual change back into code before the next promotion |
| steady-state production reconciliation | GitOps (Argo CD / Flux) over push-based deploys |
| CI credentials | workload identity (OIDC) over long-lived secrets |
| alerting | page on actionable SLO burn rates or imminent capacity exhaustion; send diagnostic host metrics to dashboards |
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
- running a live incident, on-call, or postmortems -> [ops-incident-response](../ops-incident-response/SKILL.md)
- cloud, SaaS, or AI API spend -> [ops-cost-optimization](../ops-cost-optimization/SKILL.md)
- .NET builds on NUKE -> [ops-nuke-cicd](../ops-nuke-cicd/SKILL.md)

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
| golden paths, internal developer portal, platform maturity, when NOT to build an IDP, platform-vs-product boundary, measuring team cognitive load (Weis four-cluster model, Teamperature, leadership load), CI/IaC/GitOps adoption sequencing | [references/platform-engineering-patterns.md](references/platform-engineering-patterns.md) |
| GitOps multi-env promotion, Argo CD / Flux patterns, automation lag and why continuous apply beats apply-on-change | [references/gitops-workflows.md](references/gitops-workflows.md) |
| Terraform state isolation, why `terraform workspace` is wrong for environments, stage/prod/mgmt/global layout, secrets-in-state and backend choice | [references/terraform-state-architecture.md](references/terraform-state-architecture.md) |
| stack sizing (monolithic → application-group → service → micro), blast radius, "is my stack a monolith?" | [references/stack-sizing-patterns.md](references/stack-sizing-patterns.md) |
| IaC testing rungs and their blind spots, infrastructure test diamond vs pyramid, Swiss-cheese layering | [references/infrastructure-testing-strategy.md](references/infrastructure-testing-strategy.md) |
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

When changing the source inventory, run `python3 scripts/validate_sources.py --skip-network` from this skill directory for schema and coverage only. Run the [offline CLI regressions](scripts/test_validate_sources.py) with `python3 -m pytest scripts/test_validate_sources.py`. URL reachability and source content require separate checks; a schema pass does not refresh evidence dates.

### Templates

**AWS / GCP / Azure**
- [assets/aws/template-aws-ops.md](assets/aws/template-aws-ops.md) — AWS day-2 ops checklist
- [assets/aws/template-aws-terraform.md](assets/aws/template-aws-terraform.md) — AWS Terraform module skeleton
- [assets/aws/template-cost-optimization.md](assets/aws/template-cost-optimization.md) — AWS cost right-sizing and reservation review
- [assets/gcp/template-gcp-ops.md](assets/gcp/template-gcp-ops.md) — GCP day-2 ops checklist
- [assets/gcp/template-gcp-terraform.md](assets/gcp/template-gcp-terraform.md) — GCP Terraform module skeleton
- [assets/azure/template-azure-ops.md](assets/azure/template-azure-ops.md) — Azure day-2 ops checklist

**Kubernetes**
- [assets/kubernetes/template-kubernetes-ops.md](assets/kubernetes/template-kubernetes-ops.md) — cluster day-2 ops, probe and rolling-update rules, HPA checklist
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

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
