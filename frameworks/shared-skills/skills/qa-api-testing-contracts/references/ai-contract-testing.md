# AI-Assisted Contract Testing

Use AI to accelerate contract coverage, not to replace deterministic gates.

## Guardrails

- Keep lint, breaking diffs, executable contracts, and release gates as the source of truth.
- Treat generated tests as drafts. Tighten matchers and expected behavior before promoting them into CI.
- Sanitize payloads, examples, secrets, and webhook signatures before sharing data with third-party tools.
- Confirm pricing, feature flags, hosted-only features, and CLI syntax in vendor docs before final recommendations.

## Tool Roles

| Tool | Best fit | Keep in mind |
| --- | --- | --- |
| PactFlow AI Code Review | Review and improve existing Pact suites (beta Aug 2025) | Confirmed GA for JavaScript/TypeScript and Java on all cloud plans; useful only if Pact is already part of the delivery model |
| PactFlow Agent Skills (formerly "PactFlow MCP Server") | Generate, review, and maintain Pact/Drift tests from inside the IDE, plus live workspace queries via the bundled SmartBear MCP server | Supports Claude Code, GitHub Copilot, Cursor, Windsurf, OpenCode, Codex, Kiro, Antigravity; PactFlow Cloud, on-premises, and Pact Broker users; see docs.pact.io/ai_tools/installation for current capabilities |
| Keploy | Bootstrap regression tests from captured traffic | Great for legacy HTTP APIs; captured traffic still needs curation |
| Postman AI (Agent Mode, formerly "Postbot") | Generate assertions, edge-case ideas, and — as of the March 2026 platform relaunch — act across collections/tests/mocks and generate contract/load/unit/e2e tests | Treat as a functional-testing assistant, not the contract authority; verify current agentic scope before granting write access to collections |
| Specmatic | Generate executable contracts from schema/workflow artifacts | Strong for mixed protocol (OpenAPI, gRPC, GraphQL, AsyncAPI, Arazzo, Avro, MCP) |
| Microcks | Mock and test across REST, GraphQL, gRPC, and AsyncAPI | CNCF Incubating as of May 2026; broad protocol surface |
| Schemathesis | Generate edge-case HTTP requests from OpenAPI or GraphQL | v4 (June 2025): use `--max-examples` not `--hypothesis-max-examples`; best for hardening |

## Recommended Workflow

1. Establish deterministic gates first: schema lint, breaking diff, executable contracts, release promotion rules.
2. Use AI to suggest missing cases, improve matchers, and convert exploratory traffic into reusable tests.
3. Review generated tests for:
   - Overspecified exact-value assertions
   - Missing auth or tenant boundaries
   - Missing negative and retry cases
   - Hidden coupling to timestamps, ordering, or random IDs
4. Promote only the stable subset into CI.

## What AI Is Good At

- Drafting happy-path and negative cases from OpenAPI, GraphQL SDL, AsyncAPI, or Arazzo artifacts
- Suggesting boundary values and malformed payloads
- Finding weak matchers in Pact or request-level assertions
- Translating captured traffic into a first-pass regression suite
- Highlighting missing webhook and async replay scenarios

## What AI Is Bad At

- Knowing whether a provider state is truly production-safe
- Preserving exact compatibility rules across all consumers without a broker/registry
- Distinguishing flaky infrastructure failures from genuine contract failures
- Making release/promotion decisions without deterministic evidence

## Practical Guidance By Tool

### Pact / PactFlow

- Use AI review only after the consumer and provider verification flow already works.
- Keep `can-i-deploy` and verification results as the real release gate.
- Prefer environments, deployments, and releases over legacy tag-based flows.

### Keploy

- Use for traffic capture and fast bootstrap when existing coverage is poor.
- Do not keep raw captured payloads unchanged if they contain PII, secrets, unstable IDs, or timestamps.
- Review generated cases for false confidence: replay success does not prove compatibility for all consumers.

### Postman / Postbot (now Postman AI / Agent Mode)

- Good for interactive exploration and quick assertion drafts; as of the March 2026 relaunch it can also act on collections/tests/mocks and generate contract, load, unit, integration, and e2e tests directly.
- Keep Postman in the "functional and governance adjunct" role unless the team already standardizes on it.
- Avoid claiming collection tests alone are full contract testing.
- Because Agent Mode can now edit collections and tests autonomously, review its changes with the same scrutiny as any other AI-generated code before merging.

### Specmatic / Microcks

- Prefer them when the team wants executable contracts from OpenAPI, GraphQL, AsyncAPI, or workflow artifacts without a large amount of handwritten test code.
- Re-check product capabilities before prescribing exact commands because OSS and commercial tracks evolve quickly.

### Schemathesis

- Use to discover invalid assumptions, 5xx responses, and schema-validation bugs early.
- Treat it as a hardening tool layered on top of contract testing, not a replacement for consumer/provider compatibility checks.
- v4.0.0 released June 2025: `--hypothesis-max-examples` is now `--max-examples`; `--base-url` is now `--url`. Re-check the migration guide before quoting CLI flags or updating existing CI scripts.

## Minimum Review Checklist For AI-Generated Tests

- [ ] Every generated test maps to a real operation, message, or workflow in the canonical artifact.
- [ ] Matchers are permissive enough for stable fields and strict enough for business invariants.
- [ ] Negative/security cases cover auth, authorization, validation, replay, and rate limits.
- [ ] Captured traffic was sanitized and de-flaked.
- [ ] Promotion gates still rely on deterministic verification, not AI confidence.

## Primary Sources To Re-check

- `data/sources.json`
- Pact / PactFlow docs for broker workflows and deploy gates
- Schemathesis docs for CLI syntax and reports
- Specmatic / Microcks docs for current supported protocol surfaces
- Postman docs for current Postman AI / Agent Mode and governance capabilities
