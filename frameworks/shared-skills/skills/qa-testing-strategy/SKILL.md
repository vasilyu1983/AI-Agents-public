---
name: qa-testing-strategy
description: "Risk-based test strategy for software delivery. Use when defining coverage, setting CI gates, managing flaky tests, choosing test layers, or establishing release criteria."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Testing Strategy

Risk-based quality engineering guidance for modern software delivery. Use this skill to decide what to test, at which layer, with which gates, and how to keep the signal trustworthy.

Start with [references/operational-playbook.md](references/operational-playbook.md) for the navigation hub. Use current official sources from [data/sources.json](data/sources.json) when you need vendor or standards guidance.

## Scope

- Create or update a risk-based test strategy
- Choose a test shape (pyramid, trophy, honeycomb) based on architecture and defect origin
- Define merge gates, deploy gates, and release evidence — including merge queue interaction
- Choose the smallest effective layer: unit, component, contract, schema fuzzing, integration, E2E, property-based
- Make failures diagnosable with artifacts, correlation IDs, traces, and ownership
- Operationalize suite health: flake SLO, quarantine policy, execution budgets, dashboards

## Use Instead

| Need | Skill |
|------|-------|
| Implement or debug Playwright suites | [qa-testing-playwright](../qa-testing-playwright/SKILL.md) |
| Design API contract suites in depth | [qa-api-testing-contracts](../qa-api-testing-contracts/SKILL.md) |
| Debug failing tests or incidents | [qa-debugging](../qa-debugging/SKILL.md) |
| Add observability, telemetry, or tracing | [qa-observability](../qa-observability/SKILL.md) |
| Test LLM agents or evaluations | [qa-agent-testing](../qa-agent-testing/SKILL.md) |
| Mobile-specific strategy or automation | [qa-testing-mobile](../qa-testing-mobile/SKILL.md) |
| Security audit or threat-model depth | [software-security-appsec](../software-security-appsec/SKILL.md) |
| CI/CD pipeline design and infra | [ops-devops-platform](../ops-devops-platform/SKILL.md) |

## Quick Reference

| Layer | Goal | Typical Use |
|------|------|-------------|
| Unit | Prove logic and invariants fast | Pure functions, domain rules, validators |
| Component | Validate UI behavior in a real browser with narrow scope | UI components, state transitions, accessibility smoke |
| Contract | Prevent breaking changes across service boundaries | OpenAPI, AsyncAPI, JSON Schema, Protobuf |
| Schema fuzzing | Stress the API contract with generated valid and invalid inputs | Request/response edge cases, parser and validation drift |
| Property-based | Verify universal invariants across generated input spaces | Serialization round-trips, numeric contracts, state-machine invariants, AI-code edge cases |
| Integration | Validate real boundaries and dependencies | API + DB, queues, adapters, auth flows |
| E2E | Validate thin critical journeys | Sign-up, checkout, publish, payment, admin recovery |
| Performance | Enforce budgets and capacity | Load, stress, soak, latency regression |
| Visual | Catch intentional vs accidental UI changes | Stable pages, design-system components |
| Accessibility | Check for common WCAG 2.2 failures early | axe smoke + manual audit plan |
| Security | Catch common web/API vulnerabilities early | SAST, DAST smoke, auth and dependency checks |

## E2E Gate Topology (Default)

Use three distinct E2E scopes instead of one monolithic suite:

- Smoke: PR gate and fastest feedback on the highest-risk journeys.
- Targeted batch/spec: local triage and deflake work for one journey, subsystem, or dependency chain.
- Deploy-gate replay: dependency-chain or critical-journey replay used only when proving release readiness.

Rules:

- Do not use full local E2E as the first response to a single failing journey.
- Treat rerun-pass as unresolved flake debt.
- Promote scope only after the smaller scope is green.

## Default Workflow

1. Clarify scope and risk: critical journeys, failure modes, compliance constraints, and non-functional risks.
2. Define quality signals: SLOs, budgets, contract checks, accessibility target, and what blocks merge vs deploy.
3. Choose the smallest effective layer first: unit, component, contract, schema fuzzing, integration, then E2E.
4. Make failures diagnosable: logs, traces, screenshots, videos, build links, request IDs, trace IDs, and owners.
5. Operationalize the suite: explicit smoke vs targeted-batch vs deploy-gate scopes, quarantine with expiry, suite budgets, retries with evidence retention, and dashboards.

## Decision Rules

```text
Need to test: [Change or Risk]
    │
    ├─ Pure business rule or invariant?
    │   └─ Unit test
    │
    ├─ UI behavior or component state in isolation?
    │   └─ Component test in a real browser
    │
    ├─ API compatibility between teams/services?
    │   └─ Contract test
    │
    ├─ API parser/validation edge cases against the schema?
    │   └─ Schema-aware fuzzing + core integration smoke
    │
    ├─ Real dependency boundary or persistence behavior?
    │   └─ Integration test with real DB/queue/service doubles only at external edges
    │
    ├─ User-critical cross-page workflow?
    │   └─ Thin E2E test
    │
    ├─ Universal invariant or property that should hold for all valid inputs?
    │   └─ Property-based test (fast-check / Hypothesis / jqwik)
    │
    └─ Capacity, resilience, or reliability regression?
        └─ Performance, resilience, or synthetic monitoring tests
```

## Principles

- Prefer the smallest layer that can prove the behavior.
- Keep pre-merge gates fast: contracts, static checks, unit tests, selective component/integration smoke.
- Prefer targeted batch reruns locally; reserve full E2E for deploy gates or scheduled regression.
- Use full E2E only for critical journeys or risks that cannot be proven lower in the stack.
- Treat flaky tests as reliability defects, not harmless noise.
- Favor web-first assertions and stable locators over custom waits or brittle selectors.
- Treat accessibility automation as partial coverage. Pair it with manual checks and inclusive design review.
- Use telemetry as evidence. Production traces, incidents, and support signals should drive new tests.
- Use AI for brainstorming and triage only when evidence stays attached. Do not weaken assertions to “heal” tests.
- Treat AI-authored test oracle quality as a first-class risk, peer to flake debt. AI-generated tests routinely hit high line coverage while passing trivially (hardcoded returns, shallow assertions). Gate them on mutation score, not coverage: a test that cannot fail when the business logic is reverted is not a test.

## Core Targets

| Signal | Default Target |
|--------|----------------|
| PR gate | p50 <= 10 min, p95 <= 20 min |
| Mainline health | >= 99% green builds/day |
| Suite flake rate | <= 1% weekly |
| Quarantine policy | owner + ticket + expiry, never indefinite |
| AI-authored test oracle quality | mutation score gate on changed files (line coverage is not a gate); calibrate threshold to the suite, never accept AI tests on coverage alone |

## Resources

- [references/operational-playbook.md](references/operational-playbook.md): start here
- [references/component-testing-browser-mode.md](references/component-testing-browser-mode.md): real-browser component strategy with Vitest Browser Mode
- [references/playwright-webapp-testing.md](references/playwright-webapp-testing.md): current Playwright guidance
- [references/schema-aware-api-fuzzing.md](references/schema-aware-api-fuzzing.md): schema-driven API fuzzing with OpenAPI
- [references/contract-testing.md](references/contract-testing.md): Pact, Specmatic, and contract decisions
- [references/observability-driven-testing.md](references/observability-driven-testing.md): OpenTelemetry-first debugging and trace-based validation
- [references/quality-metrics-dashboard.md](references/quality-metrics-dashboard.md): metrics, dashboards, mutation coverage, and anti-patterns
- [references/production-testing-and-shift-right.md](references/production-testing-and-shift-right.md): synthetic monitoring, dark launches, feature flag rollouts, MTTR-flake SLO, production replay, observability-driven gates
- [references/test-impact-analysis.md](references/test-impact-analysis.md): TIA concept, Launchable, Datadog Test Visibility, BuildPulse flake trending, jest --findRelatedTests, NCrunch
- [references/shift-left-testing.md](references/shift-left-testing.md): shift-left practices, test doubles, and coverage targets that move quality checks earlier
- [references/test-automation-patterns.md](references/test-automation-patterns.md): Page Object Model, data factories, fixtures, test doubles, AAA, and isolation patterns
- [references/test-environment-management.md](references/test-environment-management.md): environment-as-code, seeding, service virtualization, isolation, and shared-vs-dedicated tradeoffs
- [references/synthetic-test-data.md](references/synthetic-test-data.md): ephemeral, privacy-safe test data to avoid real customer data in CI and staging
- [references/chaos-resilience-testing.md](references/chaos-resilience-testing.md): chaos experiments, fault injection, CI/CD integration, and DORA/SOC 2 resilience evidence
- [references/compliance-testing.md](references/compliance-testing.md): compliance-as-code, audit-evidence automation, access control, data residency, and encryption validation
- [references/feature-matrix-vs-test-matrix-gate.md](references/feature-matrix-vs-test-matrix-gate.md): pre-release gate mapping implemented features to auditable test evidence
- [references/property-based-testing.md](references/property-based-testing.md): property-based testing with fast-check, Hypothesis, and jqwik — universal invariants, edge-case discovery, and AI-code blind-spot detection
- [references/comprehensive-testing-guide.md](references/comprehensive-testing-guide.md): retired redirect map pointing each test layer to its dedicated sibling skill

## Templates

- [assets/test-strategy-template.md](assets/test-strategy-template.md): strategy one-pager
- [assets/automation-pipeline-template.md](assets/automation-pipeline-template.md): CI/CD pipeline blueprint
- [assets/component/template-vitest-browser.md](assets/component/template-vitest-browser.md): browser-mode component tests
- [assets/e2e/template-playwright.md](assets/e2e/template-playwright.md): Playwright E2E with traces and accessibility smoke
- [assets/integration/template-api-integration.md](assets/integration/template-api-integration.md): API + DB integration tests
- [assets/performance/template-k6-load-testing.md](assets/performance/template-k6-load-testing.md): performance budgets and scenarios
- [assets/runbooks/template-flaky-test-triage-deflake-runbook.md](assets/runbooks/template-flaky-test-triage-deflake-runbook.md): deflake runbook
- [assets/template-test-case-design.md](assets/template-test-case-design.md): Given/When/Then and oracles

## ASCII Flow

```text
Test strategy request
  -> Clarify risks, critical journeys, constraints, and release criteria
  -> Pick smallest proving layer: unit, component, contract, integration, E2E
  -> Define merge gates, deploy gates, evidence artifacts, and owners
  -> Add diagnostics: logs, traces, screenshots, request IDs, and dashboards
  -> Set suite health policy: flake SLO, quarantine expiry, runtime budgets
  -> Review production signals and incidents to evolve coverage
```

## Navigation

- `## Default Workflow`, `## Decision Rules`, and `## Principles` for the baseline strategy sequence
- `## Resources` and `## Templates` for deeper materials
- `## Related Skills` for tool-specific execution handoffs
- [references/reliability-theory-applied.md](references/reliability-theory-applied.md) — Reliability primitives (MTBF/MTTR, availability, FMEA, error budgets) applied to QA testing strategy.

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-refactoring](../qa-refactoring/SKILL.md) | Safe refactoring with behavior preservation |
| [software-code-review](../software-code-review/SKILL.md) | Code review process and checklists |
| [software-architecture-design](../software-architecture-design/SKILL.md) | System design and architecture decisions |

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

