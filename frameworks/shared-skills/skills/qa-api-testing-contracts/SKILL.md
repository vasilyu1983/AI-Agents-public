---
name: qa-api-testing-contracts
description: "API contract testing across REST, GraphQL, gRPC, AsyncAPI, webhooks, and workflow contracts. Use when you need schema validation, breaking-change detection, and CI quality gates."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA API Testing and Contracts

Use this skill to turn API artifacts into enforceable checks: linting, breaking-change detection, executable contracts, negative/security coverage, and release gates that stop unsafe changes from shipping.

## Quick Reference

| Need | Go to |
|------|-------|
| Run the contract-testing workflow | `## Workflow` |
| Gather the right API inputs first | `## Inputs to Gather` |
| Check release-gate quality | `## Quality Checks` |
| Load templates and references | `## Navigation` |

## Inputs to Gather

- Contract surface and canonical artifact for each surface:
  - REST: OpenAPI 3.1 or 3.2
  - GraphQL: SDL plus schema registry if used
  - gRPC: `.proto` plus `buf.yaml`
  - Async/event flows: AsyncAPI
  - Multi-step workflows: Arazzo
  - Webhooks/callbacks: OpenAPI webhooks or AsyncAPI channels
- Where each artifact lives in-repo and whether generated artifacts exist in CI.
- Environments, auth methods, webhook signing model, and stable test identities/keys.
- Critical operations, messages, and workflows ranked by business risk.
- Data constraints: idempotency, ordering, pagination/cursors, retries, eventual consistency, rate limits, state convergence after backend changes, and DLQ/replay behavior.
- Versioning/deprecation policy, consumer inventory, and any operation registry or broker/registry already in use.
- Current tooling and CI policy: what blocks PR merge, release promotion, and production deploy.

## Outputs (What to Produce)

- A minimal gate set for PR and release: lint + breaking diff + contract checks + promotion gate.
- A coverage map derived from the canonical artifacts, with critical operations and workflows first.
- A negative/security baseline aligned to OWASP API risks plus webhook/event-specific failure modes.
- An explicit quota and degraded-mode matrix for critical endpoints (for example `429`/`Retry-After`, fallback body shape, and state-transition convergence checks).

## Quick Start

1. Identify the source-of-truth artifacts and remove drift between fragments, generated files, and runtime behavior.
2. Lint every artifact before writing tests.
3. Add breaking-change checks against the base branch on every PR.
4. Choose an enforcement mix:
   - CDC: Pact / PactFlow
   - Schema-driven: Specmatic / Microcks
   - Property-based hardening for HTTP APIs: Schemathesis
5. Add minimum negative/security cases for auth, validation, error contracts, rate limits, webhooks, and async replay behavior.
6. Make release gates explicit:
   - Pact `can-i-deploy`
   - GraphQL schema plus operations checks
   - `buf breaking`
   - Executable async/workflow contract checks

## Workflow

### 1) Establish Canonical Contract Artifacts

- REST: keep a single checked-in or compiled OpenAPI artifact. Treat OpenAPI 3.2 as current, but keep 3.1 as the safe default when tool support is unclear.
- GraphQL: keep checked-in SDL and, if available, schema registry plus collected operations.
- gRPC: keep checked-in `.proto` files with stable module layout and `buf.yaml`.
- Async/event APIs: keep checked-in AsyncAPI and message examples that reflect real payloads.
- Workflows: keep Arazzo documents for multi-step API outcomes where individual endpoint checks are insufficient.
- Webhooks/callbacks: treat provider payload schemas, signatures, retry rules, and replay semantics as part of the contract.

### 2) Validate the Artifacts

- OpenAPI / AsyncAPI / Arazzo: use Spectral with a small explicit ruleset.
- GraphQL: use GraphQL Inspector for local diff/lint and GraphOS or Hive when registry-based checks are available.
- gRPC: use `buf lint`.
- Keep rules small and intentional: naming, descriptions, auth annotations, examples, and a consistent error model.

### 3) Detect Breaking Changes

- REST: diff OpenAPI against the base branch and block removals, incompatible type changes, requiredness tightening, auth changes, and error-envelope changes.
- GraphQL: block unsafe schema diffs and, when possible, run operations checks against real collected traffic.
- gRPC: run `buf breaking`; never reuse field numbers.
- AsyncAPI / webhooks / workflows: use structural diff where available, but back it with executable contract tests because runtime workflow breakage is often behavioral.

### 4) Execute Contracts

Pick one or combine:

- CDC (Pact / PactFlow): best when many independent consumers exist and provider behavior matters beyond schema shape.
- Schema-driven (Specmatic / Microcks): best when the schema or workflow artifact is the contract and you want broad executable coverage quickly.
- Property-based (Schemathesis): best for systematic edge-case discovery and response validation on HTTP APIs.

### 5) Add Negative + Security Cases

- AuthN/AuthZ: missing, expired, malformed, or under-scoped credentials; tenant isolation; privileged actions.
- Validation: missing required fields, invalid types, boundaries, malformed enums, oversized payloads.
- Error handling: stable RFC 9457 `application/problem+json` shape for REST where adopted; safe messages; correlation/trace IDs.
- Abuse and limits: rate limits, `Retry-After`, pagination/cursor misuse, idempotency replay, retry safety, duplicate event delivery, and list/count/search endpoints under quota pressure.
- Webhooks: signature verification, timestamp skew, replay protection, duplicate deliveries, and retry behavior.
- Async/event flows: poison messages, schema evolution, ordering assumptions, DLQ handling, and timeout/retry expectations.

### 6) Define CI Quality Gates

- Pre-merge: lint + breaking diff + build/composition checks where relevant.
- Pre-release: executable contract suite for critical flows, plus smoke coverage.
- Pre-deploy/promotion:
  - Pact `can-i-deploy`
  - GraphOS/Hive operations checks when collected operations exist
  - `buf breaking`
  - Async/workflow contract verification
- Publish artifacts in CI: diff report, verification results, failing cases, and workflow evidence.

## Quality Checks

- Fail fast on schema violations and unsafe diffs.
- Prefer deterministic fixtures, isolated test data, and frozen time where relevant.
- Separate flake mitigation from contract logic; retry only known-transient infrastructure failures.
- Rate-limited and degraded responses are contract surface, not incidental noise; assert them intentionally.
- Keep contracts aligned with deprecation policy, consumer inventory, and release cadence.
- Keep resilience/load testing separate unless the user explicitly wants it combined.

## Judgment Calls

- **When contract testing is overkill:** a single consumer and single provider owned by the same team, deployed together, with an end-to-end smoke test already gating every release. Prototype, throwaway, or single-repo internal integrations rarely justify broker infrastructure — a linted, diffed schema artifact is enough.
- **When it is essential:** 3+ independent consumer teams, any third-party/public consumer, async/event contracts where producer and consumer deploy independently, or any surface where a breaking change can reach production before a human notices (slow-updating mobile clients, partner integrations, webhook receivers you do not control).
- **Contract tests that verify nothing:** the most common CDC failure is a consumer expectation written against the mock's own canned fixture rather than the provider's real behavior (for example, asserting a hardcoded ID the stub always returns). Provider verification then passes trivially because it replays the same fixture, not real business logic. Counter this by seeding provider states with realistic, varied data and reviewing new pact matchers for being tight enough to catch shape regressions but not so tight they only pass against the fixture that generated them.
- **Provider-state drift:** state-setup handlers accumulate across many consumer pacts and quietly stop reflecting real preconditions after schema or business-logic changes (a "user has a pending order" state that no longer creates a real pending order). Verification then passes against stale state while the deployed provider fails in production. Treat state-handler code as production code: review it on every provider-side schema change, and periodically run a canary consumer test against a fresh environment.
- **Broker-versioning strategy:** prefer branches + environments + deployments/releases over the legacy tag-based model. `can-i-deploy` only answers "has every pairing currently deployed to this environment verified compatibility with this version?" — it is only as trustworthy as the deployment record, so `record-deployment`/`record-release` must run inside the real deploy pipeline, not as an optional side step.
- **Rolling out a breaking change across teams:** publish the new contract alongside the old one (additive/dual-write period), use the consumer inventory or operations-check data (Pact Broker matrix, GraphOS/Hive operations) to confirm who still depends on the old shape, gate removal on zero live usage rather than a fixed calendar, and only then remove.

## Scripts

Runnable CI bash scripts in `scripts/`. Copy into your pipeline or call from a CI job step.

| Script | Purpose |
|--------|---------|
| `scripts/pact_can_i_deploy.sh` | Gate deployment via Pact Broker `can-i-deploy`; exits non-zero if verifications are missing or failed |
| `scripts/schemathesis_baseline.sh` | Run Schemathesis `--checks all` property-based checks against an OpenAPI spec |
| `scripts/buf_breaking_check.sh` | Detect breaking `.proto` changes with `buf breaking`; fails build on any breaking change |
| `scripts/spectral_lint.sh` | Lint an OpenAPI/AsyncAPI/Arazzo file with Spectral; fails on violations at or above `--fail-severity` |

See `scripts/README.md` for env vars, exit codes, and GitHub Actions / GitLab CI snippets.

## Templates

- Coverage and rollout plan: `assets/api-test-plan.md`
- Release review: `assets/contract-change-checklist.md`
- Tooling map: `assets/schema-validation-matrix.md`

## AI Assistance (Use Carefully)

- Use AI to draft candidate tests, missing edge cases, and matcher improvements.
- Keep deterministic gates as the source of truth; AI output must still pass them.
- Treat vendor AI features as optional and volatile; confirm current behavior and pricing before recommending them.
- Sanitize payloads, examples, logs, and webhook secrets before sending anything to third-party tools.
- For current tooling tradeoffs and cautions, read `references/ai-contract-testing.md`.

## Resources

- Change safety and deploy-gate patterns: `references/contract-testing-patterns.md`
- AI-assisted tooling and volatile vendor features: `references/ai-contract-testing.md`
- Versioning, deprecation, and compatibility policy: `references/api-versioning-strategies.md`
- Schema-driven, property-based, and executable contract workflows: `references/schema-driven-testing.md`
- Security coverage for APIs, webhooks, and async flows: `references/api-security-testing.md`
- Bi-directional contract testing (BDCT) and Arazzo workflow contracts: `references/advanced-contract-patterns.md`
- Curated authoritative links: `data/sources.json`

## ASCII Flow

```text
API contract task
  -> Identify canonical artifacts: OpenAPI, SDL, proto, AsyncAPI, Arazzo
  -> Lint artifacts and remove generated/source drift
  -> Diff against base branch for breaking changes
  -> Execute contracts with CDC, schema-driven, or property-based tests
  -> Add negative/security cases for auth, validation, limits, and replay
  -> Publish CI evidence and block unsafe merge, release, or deploy
```

## Navigation

- `## Workflow` and `## Quality Checks` for the main sequence and acceptance criteria
- `## Templates`, `## AI Assistance (Use Carefully)`, and `## Resources` for deeper materials
- `## Related Skills` for design, resilience, and AppSec handoffs

## Related Skills

| Skill | Purpose |
|-------|---------|
| [dev-api-design](../dev-api-design/SKILL.md) | API design decisions |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Overall testing strategy |
| [qa-resilience](../qa-resilience/SKILL.md) | Chaos and reliability testing |
| [software-security-appsec](../software-security-appsec/SKILL.md) | API security review |

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources and cite exact links for volatile tooling guidance.
- If web access is unavailable, state the limitation and mark vendor/tool details as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

