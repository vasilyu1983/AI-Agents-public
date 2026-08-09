# DevOps Best Practices

*Purpose: Operational guidance for safe, efficient, and auditable infrastructure automation, deployment, and reliability engineering in cloud-native environments.*

*Use when:* You already know the task is a production change, deployment, rollback, or ops safety review and need concrete operating patterns rather than tool selection guidance.

## Table of Contents
- Core Patterns
- Decision Matrices
- Common Anti-Patterns
- Quick Reference
- DORA 2025 Research Findings

---

## Core Patterns

### Pattern 1: Safe Infrastructure Changes

**Use when:** Managing production changes with Infrastructure as Code (Terraform, CloudFormation, etc.)

**Structure:**
```

1. Write and test changes in a feature branch.
2. Run automated `terraform plan`/`cloudformation validate` in CI.
3. Require pull request review from a peer or SRE.
4. Apply changes via CI/CD runner with restricted credentials.
5. Record all changes (logs, plan/apply diffs) in version control or audit logs.

```

**Checklist:**
- [ ] Infrastructure code in version control
- [ ] Peer review required before merge
- [ ] Automated validation in pipeline
- [ ] Change is tracked and auditable
- [ ] Sensitive credentials managed via secrets backend

---

### Pattern 2: Blue-Green & Canary Deployments

**Use when:** Deploying applications/services with minimal user impact

**Structure:**
```

1. Deploy new version (green) alongside current (blue).
2. Run health checks on green.
3. Shift small % of traffic to green (canary phase).
4. Monitor SLOs, logs, errors for N minutes.
5. If healthy, route all traffic to green; otherwise, rollback.

```

**Checklist:**
- [ ] Parallel environments provisioned
- [ ] Automated health and readiness checks
- [ ] Metrics/alerts active during rollout
- [ ] Rollback plan in place and tested

---

### Pattern 3: Incident Response Escalation

**Use when:** Responding to production alerts, outages, or service degradation

**Structure:**
```

1. On-call receives and acknowledges alert (5 min SLA)
2. Assess impact (severity, affected users, systems)
3. Page escalation (SRE, Dev, Management as needed)
4. Initiate incident comms (status page, stakeholders)
5. Follow incident runbook for triage and resolution
6. Begin postmortem process if SEV-1/SEV-2

```

**Checklist:**
- [ ] On-call rotation documented and tested
- [ ] Escalation contacts up-to-date
- [ ] Incident comms template ready
- [ ] Postmortem template in use
- [ ] Blameless review process

---

### Pattern 4: Documentation Co-Delivery

**Use when:** Shipping behavioral changes to platform libraries, infrastructure services, or shared contracts where stale docs would mislead future engineers or agents.

**Structure:**
1. Identify all docs, ADRs, and runbooks that describe the changed behavior.
2. Update each document in the same delivery cycle as the runtime change.
3. If the change introduces a new mode or opt-in flag, add a section explaining the new behavior and migration path.
4. Review updated docs alongside code in the same PR or merge request.

**Checklist:**
- [ ] ADR reflects current decision and rationale
- [ ] Runbooks updated for new operational paths
- [ ] README/onboarding docs match current behavior
- [ ] No stale guidance that could cause reintroduction of old assumptions
- [ ] Doc updates included in same PR as behavior change

**Why:** For platform libraries, stale docs are not cosmetic — they change how future engineers and agents modify the code. Docs that move with behavior prevent silent regression from outdated guidance.

---

## Decision Matrices

| Situation                | Approach                   | Validation                |
|--------------------------|----------------------------|---------------------------|
| Major change (prod)      | Peer review, CI plan, canary| Plan reviewed, logs checked|
| Minor change (dev/stage) | Auto-apply in pipeline      | Automated tests pass       |
| Alert: non-critical      | Wait for next standup       | Ack'd in incident tracker  |
| Alert: critical/SEV-1    | Page on-call, escalate      | Response time < SLA, issue tracked |

---

## Common Anti-Patterns

- AVOID: Direct change to production (no review)  
  - Risk of accidental outage, no audit trail.  
  - BEST: All production changes via code, review, and CI/CD.

- AVOID: Overprivileged CI/CD runners  
  - Attack surface for credentials or data exfiltration.  
  - BEST: Least-privilege roles, rotate tokens, no human secrets in code.

- AVOID: No automated rollbacks  
  - Manual errors and slow recovery.  
  - BEST: Scripts and runbooks for automated rollback tested regularly.

- AVOID: No post-incident analysis  
  - Repeat failures, lack of learning.  
  - BEST: Schedule blameless postmortems after every major incident.

---

## Quick Reference

### Pre-Deployment Checklist

- [ ] All infra/app code in version control
- [ ] Changes reviewed and approved
- [ ] Automated test suite passes
- [ ] Rollback script/runbook ready
- [ ] Health checks defined and monitored
- [ ] Stakeholders notified if high-risk

### CI/CD Best Practices

- Use immutable build artifacts
- Store pipeline configs as code (e.g., `.github/workflows/`, `.gitlab-ci.yml`)
- Tag and version every release
- Enforce secrets scanning on push
- Auto-expire old build credentials

---

## Edge Cases & Fallbacks

- If CI/CD pipeline fails: Block deploy, alert owner, require manual approval for override.
- If blue-green rollout fails: Roll traffic fully back to stable ("blue") env, auto-notify team.
- If incident detection tools down: Enable fallback monitoring (infra, external uptime checker), escalate to SRE lead.

---

## DORA Research Findings (current as of July 2026)

Source: https://dora.dev/insights/dora-2025-year-in-review/ | https://dora.dev/research/publications/ | https://dora.dev/ai/roi/report/ | https://www.infoq.com/news/2026/03/ai-dora-report/ | https://cd.foundation/blog/2025/10/16/dora-5-metrics/

DORA's publication cadence accelerated through 2025–2026: the core "State of AI-Assisted Software Development" report (2025), a companion "DORA AI Capabilities Model" report (2025), and a follow-on "ROI of AI-assisted Software Development" report (published ~April 2026) are all live on dora.dev as of this writing. Treat the 2025 core report as the source for metrics/archetypes and the 2026 ROI report as the source for ROI/instability guidance — do not cite either as "the 2026 DORA report" as if it replaces the 2025 one; they are companion publications.

### Five core metrics (the four-metric era ended in 2025)

The 2025 report added a fifth metric — **rework rate** — and reorganized all five into two categories. Do not describe DORA as "four metrics" for 2026 guidance; that description is stale.

| Category | Metric | What it measures |
|----------|--------|-----------------|
| Throughput | Deployment frequency | How often an organization deploys to production |
| Throughput | Lead time for changes | Time from commit to production |
| Throughput | Failed-deployment recovery time | Time to restore service after a failed deployment |
| Instability | Change failure rate | Percentage of deployments causing a production failure |
| Instability | Rework rate | Percentage of deployments that are unplanned fixes for user-facing defects, not new work |

Rework rate closes a real blind spot: a team can have a low change-failure rate while still burning most of its capacity on unplanned fixes that never show up as a "failed" deployment. Track it explicitly rather than inferring it from change failure rate alone.

### 2025 change: seven team archetypes replace four performance tiers

The 2025 DORA report **retired the Elite / High / Medium / Low four-tier cluster classification**. The new model identifies **seven team archetypes** that blend delivery performance with human factors — burnout, friction, and perceived value — rather than ranking teams on throughput alone.

Representative archetypes (approximate respondent share, corroborated across multiple secondary sources — treat exact percentages as approximate, not load-bearing for a specific team's benchmarking):

- **Harmonious High Achievers** (~20%) — strong delivery performance, low burnout, high perceived value. Reporting indicates this archetype plus "Pragmatic Performers" together account for roughly 40% of respondents, evidence against a hard speed-vs-stability tradeoff.
- **Legacy Bottleneck** (~11%) — AI makes individual engineers faster, but weak deployment pipelines and legacy-system drag absorb the gain; architecture modernization is the actual constraint, not more AI seats.

The archetypes are not a ranking ladder. Two teams in different archetypes may have similar deployment frequency but differ sharply on burnout or organizational friction. Use archetype framing to diagnose the full picture, not just throughput.

### Central AI finding (2025 report)

The report's primary AI conclusion (paraphrase varies slightly across DORA's own summaries and secondary coverage — treat the exact wording below as a close paraphrase, not a verified verbatim quote):

> "AI's primary role is as an amplifier, magnifying an organization's existing strengths and weaknesses."

Teams with strong engineering culture and low-friction change processes see AI accelerate delivery. Teams with high friction, poor testing discipline, or high burnout see AI amplify those problems. AI tooling is not a shortcut around organizational dysfunction.

### 2026 follow-on: the "instability tax" and the AI-adoption J-curve

The newer ROI report (dora.dev/ai/roi/report/, ~April 2026) extends the amplifier finding with two operational concepts:

- **Instability tax** — AI adoption is associated with higher individual effectiveness and code quality, but also with a rise in software-delivery instability: more code moving faster overwhelms pipelines and manual review gates that were sized for the pre-AI throughput. This is presented as a reason to invest in automated testing, CI, and small-batch delivery — not a reason to delay adoption.
- **J-curve value realization** — teams should expect an initial productivity dip after rollout before ROI turns positive; the report frames this as a budgeting/expectation-setting tool for defending AI investment through the dip, not a sign the initiative is failing.

Operational read: if a team is already unstable (poor CI, weak tests, no golden path), AI adoption will surface that instability faster and harder than it would in a mature platform. Sequence platform hardening (CI reliability, deployment pipeline health) before broad AI-coding-tool rollout, not after.

### Operational implications

- Do not use Elite/High/Medium/Low tier labels in 2026 assessments — the classification is retired.
- Do not describe DORA as tracking "four metrics" — it is five, with rework rate as the newest.
- When benchmarking a team, measure all five core metrics *and* human-factor indicators (burnout, perceived value, friction). Throughput alone gives an incomplete picture.
- AI coding tools adoption should follow platform maturity, not precede it. Introduce AI tooling after deployment friction, change failure rate, and rework rate are under control — the 2026 ROI report's "instability tax" finding is the concrete mechanism for why this ordering matters, not just a platform-team preference.

---

## Shared Utilities (Implementation Patterns)

For cross-cutting implementation concerns in DevOps automation, reference these centralized utilities:

- [config-validation.md](../../software-clean-code-standard/references/config-validation.md) — Zod 3.24+, secrets management (1Password, Doppler, Vault)
- [resilience-utilities.md](../../software-clean-code-standard/references/resilience-utilities.md) — p-retry v6, circuit breaker, OTel spans for service health
- [logging-utilities.md](../../software-clean-code-standard/references/logging-utilities.md) — pino v9 + OpenTelemetry integration for structured logging
- [observability-utilities.md](../../software-clean-code-standard/references/observability-utilities.md) — OpenTelemetry SDK, tracing, metrics for infrastructure monitoring
- [testing-utilities.md](../../software-clean-code-standard/references/testing-utilities.md) — Test factories, fixtures for infrastructure tests

---

*This guide focuses on safe, auditable, and high-velocity DevOps operations. All practices are actionable and ready for direct use in cloud-native teams.*
