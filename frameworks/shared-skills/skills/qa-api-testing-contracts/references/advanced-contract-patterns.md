# Advanced Contract Patterns

Use this reference for bi-directional contract testing (BDCT) and Arazzo-based workflow contract testing — two techniques that extend the core CDC and schema-driven models.

## Table of Contents

- [Bi-Directional Contract Testing (BDCT)](#bi-directional-contract-testing-bdct)
- [When BDCT Beats Classic Consumer-Driven Pact](#when-bdct-beats-classic-consumer-driven-pact)
- [BDCT Tradeoffs and Limits](#bdct-tradeoffs-and-limits)
- [PactFlow 2025-2026 Developments](#pactflow-2025-2026-developments)
- [Arazzo Workflow Contracts](#arazzo-workflow-contracts)
- [Arazzo Conformance Runners](#arazzo-conformance-runners)
- [The Shift: From Single-Call to Workflow Contracts](#the-shift-from-single-call-to-workflow-contracts)
- [Anti-Patterns](#anti-patterns)

---

## Bi-Directional Contract Testing (BDCT)

BDCT is a PactFlow-exclusive feature (not available in the open-source Pact Broker) that lets both sides of an integration publish their own contract artifact independently, then delegates compatibility verification to PactFlow.

**How it works:**

- The **consumer** publishes a consumer contract (a Pact file or equivalent mock-tool artifact) that records what it expects from the provider.
- The **provider** publishes a provider contract — typically an OpenAPI specification validated against real provider behavior using an existing test tool (Schemathesis, Postman, Swagger Validator, RestAssured, etc.). Note: Dredd (apiaryio) was archived in November 2024 and should not be used for new integrations.
- PactFlow performs **cross-contract verification**: it compares the consumer contract against the provider's OpenAPI spec server-side. Neither team runs the other's test suite. The `can-i-deploy` gate then checks this cross-verified result before deployment.

This is the key structural difference from classic Pact: in classic CDC the provider must run the consumer's pact file against its own implementation; in BDCT the provider only needs to prove its OpenAPI spec matches its implementation, and PactFlow handles the cross-check.

---

## When BDCT Beats Classic Consumer-Driven Pact

| Scenario | Why BDCT fits |
| --- | --- |
| Provider already publishes a maintained OpenAPI spec | The spec becomes the provider contract with no extra test work; no need to run consumer pact suites against the provider |
| Retrofitting contract testing onto existing systems | Lower barrier than wiring Pact into legacy codebases from scratch |
| High consumer count or third-party / public API consumers | Consumers do not require code-level access to the provider; fewer coordination points |
| API-first teams where providers publish specs before consumers exist | Provider-driven flow is natural; BDCT supports it without forcing a consumer-first model |
| Broader team participation needed (QA, SDET, non-developer roles) | Consumer contracts can be captured with mocking tools (Wiremock, Cypress, Postman, MSW) rather than code-level Pact tests |

Classic consumer-driven Pact remains preferred when:

- Building green-field services where no OpenAPI spec exists yet
- Consumer and provider teams co-develop and want code-level, white-box integration tests
- Fine-grained matching semantics (specific matchers, request body assertions) are critical and the OpenAPI spec alone is too coarse

---

## BDCT Tradeoffs and Limits

**Lower coupling, lower granularity.** BDCT delegates matching to a schema comparison. Classic Pact supports fine-grained matchers (type matchers, regex, date formats) inside individual pact interactions. A provider's OpenAPI spec may be valid but still allow responses the consumer cannot handle — BDCT is less likely to catch that.

**PactFlow-only.** BDCT is exclusive to PactFlow (commercial/hosted). Teams using the open-source Pact Broker cannot use BDCT.

**Provider spec quality matters.** The cross-contract check is only as precise as the OpenAPI spec. An incomplete or overly permissive spec weakens the gate.

**Still needs provider spec verification.** The provider must prove its OpenAPI spec reflects real behavior using a separate tool run. Skipping that step means the spec is unverified and the gate is hollow.

**Tooling surface for consumer contracts.** Consumer contracts captured via mocking tools (not native Pact) may be less expressive. Confirm supported consumer contract types in current PactFlow docs before committing to a stack.

---

## PactFlow 2025-2026 Developments

PactFlow (owned by SmartBear since April 2022) shipped several notable additions in 2025-2026:

**AI features:**
- AI Code Review (beta, August 5 2025): automatically reviews existing Pact suites for quality issues and suggests improvements. Confirmed general availability for JavaScript/TypeScript and Java on all cloud plans; other languages (Kotlin, .NET, Go, PHP, Swift) were mentioned in early material — verify current language coverage in PactFlow docs before relying on it.
- PactFlow MCP Server (October 2025): the original IDE integration for generating/maintaining Pact tests via the Model Context Protocol. As of mid-2026 this has been superseded/expanded into **PactFlow Agent Skills** (docs.pact.io/ai_tools/installation, last updated May 2026), which bundle the renamed **SmartBear MCP Server** (docs.pact.io/ai_tools/smartbear-mcp) alongside assistant-specific skill files. Supported assistants now include Claude Code, GitHub Copilot, Cursor, Windsurf, OpenCode, Codex, Kiro, and Antigravity. Prefer the current "PactFlow Agent Skills" docs page over the October 2025 blog post when configuring this.

**Drift (confirmed live as of mid-2026):** spec-driven API testing that runs deterministic, automated checks (plus AI-generated test scaffolding from the OpenAPI parser) to confirm a provider implementation actually conforms to its OpenAPI spec. Positioned as a complement to CDC rather than a replacement — Drift answers "does the provider spec reflect reality?" while BDCT/classic Pact answers "are consumers compatible?". Docs: pactflow.github.io/drift-docs.

These are all hosted/commercial features. The open-source Pact libraries and Pact Broker remain unaffected. Verify current feature availability and pricing before adopting any of these in a delivery pipeline.

---

## Arazzo Workflow Contracts

The **Arazzo Specification** (OpenAPI Initiative; spec.openapis.org/arazzo/latest.html) defines a standard, language-agnostic format for expressing sequences of API calls and the dependencies between them. An Arazzo document references one or more source descriptions and defines one or more workflows: ordered steps, parameter mappings between steps, and success/failure criteria.

**Arazzo 1.1.0 (released May 18, 2026) is the current stable release**, superseding 1.0.1 (January 2025). It is backward-compatible: existing 1.0.x documents remain valid with no structural changes to the core workflow model. Key 1.1.0 additions:

- **AsyncAPI support**: `sourceDescriptions` can now reference AsyncAPI documents in addition to OpenAPI and Arazzo documents, so a single workflow can coordinate synchronous HTTP steps alongside asynchronous send/receive operations against event-driven APIs.
- JSONPath and XPath support where only JSONPointer was previously supported.
- `$self` for identity-based referencing.

This closes the gap the previous version of this reference flagged as "in progress" — AsyncAPI-spanning workflow contracts are now a first-class, specified capability, not just a roadmap item. Confirm tool support (linters, runners) has caught up to 1.1.0 before relying on the new AsyncAPI step type in CI, since tooling typically lags a spec release by one to two quarters.

**What Arazzo adds that OpenAPI alone cannot express:**

- The sequence of calls needed to achieve a business outcome (for example: authenticate → create resource → poll for status → confirm)
- Explicit data flow between steps (output of step A as input to step B)
- Per-step and per-workflow success/failure criteria
- Conditional branching and error paths across the workflow

**CI usage pattern:**

1. Keep Arazzo documents in the repo alongside the OpenAPI specs they reference.
2. Lint Arazzo documents with Spectral (which has Arazzo ruleset support).
3. Detect structural breaking changes via diff tooling on each PR.
4. Execute workflows against a real environment with an Arazzo runner to verify cross-step behavior.
5. Use workflow test evidence as part of the pre-release gate alongside schema-level checks.

---

## Arazzo Conformance Runners

Tooling for executing and conformance-testing Arazzo workflows is emerging. The ecosystem is active but evolving; verify current status and maturity before adopting in production CI.

| Tool | Role | Notes |
| --- | --- | --- |
| `arazzo-cli` | Standalone Arazzo workflow executor with runtime engine, debugger, and MCP server | Verify current maintenance status, stability, and 1.1.0/AsyncAPI-step support at the project's repository |
| Arazzo Runner | Workflow execution engine processing Arazzo + OpenAPI documents | Verify current status |
| Specmatic | Arazzo-based workflow testing as part of its mixed-protocol contract suite | Documented in Specmatic OSS; verify current Arazzo feature surface in their docs |
| Spectral | Linting for Arazzo documents | Arazzo ruleset support; verify current ruleset coverage |

Because this tooling space is evolving rapidly, treat tool maturity ratings as provisional and check primary sources before selecting.

---

## The Shift: From Single-Call to Workflow Contracts

Contract testing has historically focused on individual API calls: does the consumer's expected request/response pair match what the provider can produce? This is necessary but insufficient for many business-critical flows.

The emerging pattern treats a **multi-step workflow outcome** as the contract surface:

- A login-then-fetch-then-update sequence that must complete atomically
- An order flow that must reach a confirmed state after N steps
- An event-driven workflow that spans HTTP calls and async messages

Arazzo formalizes these as machine-readable workflow descriptions. Executable Arazzo runners turn them into conformance tests. This shifts the contract boundary from "did this endpoint respond correctly?" to "did this business operation complete correctly across its required steps?"

Single-call schema checks remain necessary as a fast feedback layer. Workflow contracts sit above them and catch breakage that no individual endpoint test would detect: a change to step 2's response shape that silently breaks step 3's parameter mapping, or a removed intermediate endpoint that collapses a multi-step flow.

**Recommended layering:**

1. Lint and breaking-change diff on every PR (fast, artifact-level).
2. Single-call contract tests for critical endpoints (CDC or schema-driven).
3. Arazzo workflow contracts for critical multi-step business outcomes (slower; run pre-release or on a separate branch).

---

## Anti-Patterns

- Treating BDCT as a drop-in replacement for classic Pact without verifying that the provider's OpenAPI spec is accurate and kept up to date
- Using BDCT with an unverified or stale OpenAPI spec — the cross-contract check becomes meaningless
- Writing Arazzo documents only as documentation artifacts and never executing them
- Running Arazzo workflow tests only in production-like environments where failures are expensive — run them in a stable staging or ephemeral environment on every release candidate
- Pinning a specific `arazzo-cli` or runner version without confirming it targets your documents' declared Arazzo version (1.0.x vs 1.1.0) — a 1.1.0 document using AsyncAPI-referencing steps will not run correctly against a runner that only understands 1.0.x
