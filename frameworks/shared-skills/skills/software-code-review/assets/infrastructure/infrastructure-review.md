# Infrastructure as Code Review Checklist

Use this template when reviewing Terraform/Kubernetes/Docker/CI/CD/cloud infrastructure changes.

## Core

### Standards

- Clean code standard (cite `CC-*` IDs when applicable): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Shared secure code review checklist (baseline): [../../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md](../../../software-clean-code-standard/assets/checklists/secure-code-review-checklist.md)

### Intent & Scope

- [ ] PR description states what/why/scope; blast radius and rollback plan are present.
- [ ] Diff matches intent; unrelated refactors are split or explicitly justified.

### Change Safety

- [ ] Apply order, rollout strategy, and rollback are clear (especially for breaking or stateful changes).
- [ ] State/data migrations are safe (forward-only vs reversible is explicit).
- [ ] Drift and reconciliation behavior is understood (controllers, desired vs actual state).

### Security & Identity

- [ ] Least privilege applied to IAM/RBAC; privileged access is explicit and audited.
- [ ] No hardcoded credentials/secrets; secrets are stored and rotated safely (cite `CC-SEC-03`).
- [ ] Dependencies are pinned/locked (providers, modules, actions, images) and vetted (cite `CC-SEC-05`).
- [ ] Network exposure is minimal; public access is explicit, justified, and monitored.

### Terraform / IaC

- [ ] Terraform and provider versions are locked; inputs/outputs are typed and documented.
- [ ] Remote state uses locking and encryption; secrets are not stored in state.
- [ ] Resource naming/tagging/labels support ownership, cost, and operations.

### Kubernetes

- [ ] Resource requests/limits, liveness/readiness probes, and disruption budgets are set for production workloads.
- [ ] Security context is safe by default (non-root, read-only FS where feasible); network policies restrict traffic.
- [ ] Secrets/config are managed correctly (Secrets for sensitive values; ConfigMaps for non-sensitive).
- [ ] Images are pinned and come from trusted registries; upgrade strategy is clear.

### Containers

- [ ] Base images are pinned and minimal; container runs as non-root; no secrets in layers.
- [ ] Health checks exist where the platform supports them; resource usage is bounded.

### CI/CD

- [ ] Branch protection and required checks exist for deploy paths (https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [ ] CI permissions are least-privilege; secrets are masked and never printed.
- [ ] Artifact integrity is addressed for production releases (signing/provenance expectations) [Inference].

### Observability

- [ ] Critical systems are observable (logs/metrics/traces appropriate to risk) (cite `CC-OBS-03`).
- [ ] Alerts have runbooks; alert fatigue is considered (signal > noise).

## Optional: AI / Automation

- [ ] IaC validation and policy checks run (fmt/validate, linters, IaC security scanning).
- [ ] Container and dependency scanning is enabled (image vuln scan, secret scan, SBOM as applicable).
- [ ] Automation findings are mapped to `CC-*` IDs where possible to reduce review noise.
