---
name: qa-testing-strategy
description: "Designs risk-based test strategy for software delivery. Use when defining coverage, setting CI gates, managing flaky tests, choosing test layers, or establishing release criteria."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.5"
last_validated: 2026-09-27
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
3. Map each critical risk to a claim, oracle, layer, environment, build identity, evidence artifact, owner, and expiry. Label it `configured`, `executed`, `behavior-verified`, or `release-observed`; static analysis, discovery, coverage, and a green build stop before executed behavior.
4. Choose the smallest effective layer first: unit, component, contract, schema fuzzing, integration, then E2E.
5. Make failures diagnosable: logs, traces, screenshots, videos, build links, request IDs, trace IDs, and owners.
6. Operationalize the suite: explicit smoke vs targeted-batch vs deploy-gate scopes, quarantine with expiry, suite budgets, retries with evidence retention, and dashboards. List uncovered critical risks and the next gate instead of treating a targeted pass as universal release proof.

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

## Risk-Based Prioritisation

Coverage is allocated by risk, not by shape. Score each journey or module before choosing tests, and put the score in the strategy one-pager:

- **Impact** (1–3): revenue, data loss, security or compliance exposure, and whether a failure is reversible without customer contact.
- **Likelihood** (1–3): change frequency over the last quarter, escaped-defect history, number of integration boundaries crossed, and share of AI-authored or new-contributor code.
- Risk = impact × likelihood. Score ≥ 6 gets executed behaviour evidence at more than one layer plus a deploy-gate check; 3–5 gets the smallest single layer that proves the claim; ≤ 2 gets static checks and opportunistic unit tests only, and the strategy states that gap explicitly.
- Re-score after each incident and each quarter; a module whose score drops loses tests from the PR gate before it gains them elsewhere.

## Contract vs E2E

- Contract tests prove that two parties agree on shape and semantics at one boundary; E2E proves that a journey works across many boundaries in a deployed build. They are not substitutes.
- Default: every service boundary with a separate deploy cadence gets a contract check pre-merge; every revenue or data-loss journey gets one thin E2E at the deploy gate. Nothing else gets E2E by default.
- Replace an E2E with contract plus integration tests when the failure it caught last quarter was a boundary-shape mismatch or a persistence bug; keep it when the failure was cross-service sequencing, auth-session flow, or a UI state the lower layers cannot see.
- A contract test with no consumer-side verification (provider publishes a schema, nobody checks a consumer against it) is documentation, not evidence.

## Coverage Metrics

- Line and branch coverage measure execution, not assertion. Use them only for a no-decrease delta gate on PRs and to find untested files; never as a release criterion.
- Any coverage number above the diff-level delta gate is a target that gets gamed (tests that execute without asserting). Where a number matters (auth, payments, migrations, domain rules), gate on mutation score of the changed files instead; the policy is in [references/quality-metrics-dashboard.md](references/quality-metrics-dashboard.md#operationalising-mutation-coverage).
- Coverage collected under test-impact analysis or a partial suite is not comparable to a full-suite baseline; compare like with like or the delta gate fires on noise.
- For every checked component, at least one check runs the shipped default (config, bundled data, entry point) with no overrides or patched copies; a test that builds or patches its own fixture proves only that fixture. A check that passes suspiciously easily is a reason to inspect the observation method before trusting the result.

## Flaky-Test Policy

- Classify by the [taxonomy](references/test-automation-patterns.md#flaky-test-taxonomy-and-detection) before touching the test; environment-class failures are fixed in the environment, never quarantined.
- Quarantine only with owner, ticket, expiry and the smallest scope (one test, not a file); a quarantined test keeps running and reporting. Expired quarantines fail the build.
- Rerun-pass is recorded as flake debt on the test; security, auth and payment tests are never retried to green.
- Time-to-fix follows the severity tiers in [MTTR-Flake SLO](references/production-testing-and-shift-right.md#mttr-flake-slo); the merge-queue cost model in the [operational playbook](references/operational-playbook.md#pattern-ci-test-gates) decides whether a given test justifies same-day quarantine.

## Test Data

- Every test creates its own data through factories with unique identifiers; shared fixtures and seed rows that tests mutate are the top source of order-dependent flakes.
- Real customer data stays out of CI, preview and staging. When production-shaped data is required, use irreversibly masked subsets with referential integrity preserved and an owner for the masking rules; see [references/synthetic-test-data.md](references/synthetic-test-data.md).
- Seed generators with a fixed seed per test run and print it on failure so a case can be replayed.

## Principles

- Prefer the smallest layer that can prove the behavior.
- Keep pre-merge gates fast: contracts, static checks, unit tests, selective component/integration smoke.
- Prefer targeted batch reruns locally; reserve full E2E for deploy gates or scheduled regression.
- Use full E2E only for critical journeys or risks that cannot be proven lower in the stack.
- Favor web-first assertions and stable locators over custom waits or brittle selectors.
- Treat accessibility automation as partial coverage. Pair it with manual checks and inclusive design review.
- Use telemetry as evidence. Production traces, incidents, and support signals should drive new tests.
- Use AI for brainstorming and triage only when evidence stays attached. Do not weaken assertions to “heal” tests.
- Treat AI-authored test oracle quality as a first-class risk, peer to flake debt. AI-generated tests routinely hit high line coverage while passing trivially (hardcoded returns, shallow assertions). Before accepting a test, ask the cheap manual pre-check: would it still pass if every function under test returned nothing? Reject mock-only or absence-only checks, self-referential expectations, pinned constants, and fixtures that assert themselves. Then gate on mutation score, not coverage, as the operational check: a test that cannot fail when the business logic is reverted is not a test.
- When the same model writes and reviews a change, its review shares the writer's blind spots. Run the tests and the build before any AI review and report their failures first. Then add regression tests where AI changes most often regress: a field added on one code path but not its twin (sandbox or mock mode, a flag branch, a cached or batch path); a response field missing from the query projection or mapper; error handling that sets an error but leaves stale data on screen; an optimistic update with no rollback when the call fails. Each fixed bug gets a test that fails on the pre-fix revision.

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
- [references/playwright-webapp-testing.md](references/playwright-webapp-testing.md): redirect stub — see [qa-testing-playwright](../qa-testing-playwright/SKILL.md)
- [references/schema-aware-api-fuzzing.md](references/schema-aware-api-fuzzing.md): schema-driven API fuzzing with OpenAPI
- [qa-api-testing-contracts](../qa-api-testing-contracts/SKILL.md): owner of contract testing (Pact, Specmatic, `can-i-deploy`, breaking-change gates)
- [references/observability-driven-testing.md](references/observability-driven-testing.md): OpenTelemetry-first debugging and trace-based validation
- [references/quality-metrics-dashboard.md](references/quality-metrics-dashboard.md): metrics, dashboards, hard-gate release readiness, and a mutation-coverage gate policy
- [references/production-testing-and-shift-right.md](references/production-testing-and-shift-right.md): synthetic monitoring, dark launches, feature flag rollouts, MTTR-flake SLO, production replay, observability-driven gates
- [references/test-impact-analysis.md](references/test-impact-analysis.md): TIA concept, CloudBees Smart Tests (formerly Launchable), Datadog Test Optimization, BuildPulse flake trending, jest --findRelatedTests
- [references/shift-left-testing.md](references/shift-left-testing.md): shift-left practices, test doubles, and coverage targets that move quality checks earlier
- [references/test-automation-patterns.md](references/test-automation-patterns.md): Page Object Model, data factories, fixtures, test doubles, AAA, and isolation patterns
- [references/test-environment-management.md](references/test-environment-management.md): environment-as-code, seeding, service virtualization, isolation, and shared-vs-dedicated tradeoffs
- [references/synthetic-test-data.md](references/synthetic-test-data.md): test-data management rules — per-test factories, masked production subsets, seeding, and when synthetic data misleads
- [references/chaos-resilience-testing.md](references/chaos-resilience-testing.md): redirect stub to [qa-resilience](../qa-resilience/SKILL.md)
- [references/compliance-testing.md](references/compliance-testing.md): compliance-as-code, audit-evidence automation, access control, data residency, and encryption validation (HIPAA pen-testing rule is a proposed rule, not final)
- [references/feature-matrix-vs-test-matrix-gate.md](references/feature-matrix-vs-test-matrix-gate.md): pre-release gate mapping implemented features to auditable test evidence
- [references/property-based-testing.md](references/property-based-testing.md): choose valid domains and oracles, then run property and metamorphic checks with fast-check, Hypothesis, jqwik (maintenance-mode caveat), or the portable contract runner
- [references/comprehensive-testing-guide.md](references/comprehensive-testing-guide.md): retired redirect map pointing each test layer to its dedicated sibling skill
- [references/reliability-theory-applied.md](references/reliability-theory-applied.md): reliability primitives (MTBF/MTTR, error budgets, escape probability, minimal cut sets) applied to QA testing strategy
- [scripts/release_readiness.py](scripts/release_readiness.py): release-readiness gate — hard gates (security, critical E2E, open P0) evaluated before any weighted score; see `scripts/test_release_readiness.py`

## Templates

- [assets/test-strategy-template.md](assets/test-strategy-template.md): strategy one-pager
- [assets/automation-pipeline-template.md](assets/automation-pipeline-template.md): CI/CD pipeline blueprint
- [assets/component/template-vitest-browser.md](assets/component/template-vitest-browser.md): browser-mode component tests
- [assets/e2e/template-playwright.md](assets/e2e/template-playwright.md): redirect stub — see [qa-testing-playwright](../qa-testing-playwright/SKILL.md) for live Playwright templates
- [assets/bdd/template-cucumber-gherkin.md](assets/bdd/template-cucumber-gherkin.md): use when a critical journey is specified as Gherkin/BDD scenarios (see [references/operational-playbook.md](references/operational-playbook.md))
- [assets/unit/template-jest-vitest.md](assets/unit/template-jest-vitest.md): use when the smallest effective layer is a Jest/Vitest unit test (see [references/operational-playbook.md](references/operational-playbook.md))
- [assets/integration/template-api-integration.md](assets/integration/template-api-integration.md): API + DB integration tests
- [assets/performance/template-k6-load-testing.md](assets/performance/template-k6-load-testing.md): redirect stub — see [qa-testing-performance](../qa-testing-performance/SKILL.md) for live k6 templates
- [assets/visual-regression/template-visual-testing.md](assets/visual-regression/template-visual-testing.md): redirect stub — see [qa-testing-playwright](../qa-testing-playwright/SKILL.md) for visual regression; keeps the stable-pages-only strategy rule
- [assets/runbooks/template-flaky-test-triage-deflake-runbook.md](assets/runbooks/template-flaky-test-triage-deflake-runbook.md): deflake runbook
- [assets/runbooks/template-release-coverage-audit.md](assets/runbooks/template-release-coverage-audit.md): use when running the feature-matrix-vs-test-matrix release gate from [references/feature-matrix-vs-test-matrix-gate.md](references/feature-matrix-vs-test-matrix-gate.md)
- [assets/template-test-case-design.md](assets/template-test-case-design.md): Given/When/Then and oracles

## Property and Metamorphic Contract Tools

- [scripts/property_contract_runner.py](scripts/property_contract_runner.py): dependency-free adapter runner with deterministic seed and case-index replay
- [assets/property_contract_example.py](assets/property_contract_example.py): known-correct calculator, config-parser, and JSON round-trip adapter with deliberate negative-control mutations
- [scripts/test_property_contract_runner.py](scripts/test_property_contract_runner.py): verifies correct behavior, mutation detection, exit codes, and replay

From this skill directory, run `python3 scripts/property_contract_runner.py --contract assets/property_contract_example.py --seed 20260908 --cases 120 --json`; equivalent absolute paths work from any directory. Review the adapter first because the runner imports and executes the Python file and does not sandbox it. It defensively copies case and result values, but adapter global state remains the adapter author's responsibility. Exit `0` passes the sampled contract, exit `1` reports a replayable property failure, and exit `2` reports an invalid adapter or command.

## Navigation

- `## Default Workflow`, `## Decision Rules`, `## Risk-Based Prioritisation`, and `## Principles` for the baseline strategy sequence
- `## Resources` and `## Templates` for deeper materials
- `## Related Skills` for tool-specific execution handoffs

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-refactoring](../qa-refactoring/SKILL.md) | Safe refactoring with behavior preservation |
| [software-code-review](../software-code-review/SKILL.md) | Code review process and checklists |
| [software-architecture-design](../software-architecture-design/SKILL.md) | System design and architecture decisions |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
