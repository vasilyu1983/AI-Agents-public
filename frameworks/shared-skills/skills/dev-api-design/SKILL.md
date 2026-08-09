---
name: dev-api-design
description: Designs durable API contracts across REST, GraphQL, gRPC, tRPC, and AsyncAPI. Use when specifying interfaces, auth, versioning, errors, rate limits, or agent APIs.
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# API Design

Use this skill for contract-first API design across REST, GraphQL, gRPC, tRPC, AsyncAPI, and agent-facing interfaces. It owns contract choice, auth boundaries, versioning, errors, pagination, rate limits, idempotency, and validation; it does not replace backend implementation or security review.

## Style Decision Table

| API style | Choose when | Avoid when | Canonical artifact |
|-----------|-------------|------------|--------------------|
| REST + OpenAPI | Public APIs, broad tooling compatibility, cacheable resources | Sub-10ms internal calls, streaming-first | OpenAPI 3.2.0 |
| GraphQL | Complex client-driven query shapes, multi-team schema ownership | Simple CRUD, caching is critical, single-team | GraphQL SDL |
| gRPC | Internal services, bidirectional streaming, type-critical boundaries | Public internet consumers, browser-native clients | protobuf |
| tRPC | TypeScript monorepos with shared server+client | Non-TS stacks, public third-party consumers | TypeScript types |
| AsyncAPI + webhooks | Event-driven contracts, pub/sub, push notifications | Synchronous request-reply | AsyncAPI 3.x |
| MCP tool layer | Agent or LLM is the primary consumer | Human-only clients | MCP tool schema |

## Quick Reference

| API style | Load |
|-----------|------|
| REST + OpenAPI | [references/restful-design-patterns.md](references/restful-design-patterns.md), [references/openapi-guide.md](references/openapi-guide.md) |
| GraphQL | [references/graphql-patterns.md](references/graphql-patterns.md) |
| gRPC | [references/grpc-patterns.md](references/grpc-patterns.md) |
| tRPC | [references/trpc-patterns.md](references/trpc-patterns.md) |
| AsyncAPI and webhooks | [references/asyncapi-patterns.md](references/asyncapi-patterns.md), [references/webhook-patterns.md](references/webhook-patterns.md) |
| Core cross-cutting | [references/error-handling-patterns.md](references/error-handling-patterns.md), [references/authentication-patterns.md](references/authentication-patterns.md), [references/pagination-filtering.md](references/pagination-filtering.md), [references/rate-limiting-patterns.md](references/rate-limiting-patterns.md), [references/api-testing-patterns.md](references/api-testing-patterns.md) |

## Contract Review Checklist

Run on every API contract before handoff:

- [ ] Canonical spec artifact exists (OpenAPI, AsyncAPI, protobuf, GraphQL SDL, or MCP schema)
- [ ] Versioning model named: URL path (`/v1/`), header, or content-type negotiation
- [ ] Deprecation timeline written into the spec or linked doc
- [ ] Error model: RFC 9457 Problem Details with stable `type` URI and `code` field
- [ ] Auth boundary: which endpoints require which scopes; token type (JWT, opaque); revocation path
- [ ] Pagination: cursor-based for high-cardinality; offset only for small, stable sets
- [ ] Rate limits: `RateLimit` + `RateLimit-Policy` headers (current IETF httpapi draft, still not an RFC as of July 2026) or documented legacy `X-RateLimit-*` triad; 429 includes `Retry-After`
- [ ] Idempotency: POST/PATCH operations document idempotency key or mark non-idempotent explicitly
- [ ] Long-running jobs: 202 + `Location` poll URL; `state` enum with terminal states named
- [ ] Webhooks: HMAC signature; replay protection; `trace_id` on payload
- [ ] Breaking-change detection: oasdiff or equivalent configured in CI
- [ ] Contract tests: Schemathesis (property-based) or Pact (consumer-driven) wired up

## Workflow

1. Choose the API style using the decision table above.
2. Define the canonical contract artifact.
3. Run the contract review checklist.
4. Add contract validation, breaking-change detection, and documentation.
5. Hand off spec, examples, and rollout notes.

## Route Elsewhere

- Backend implementation: [software-backend](../software-backend/SKILL.md)
- AppSec review and auth hardening: [software-security-appsec](../software-security-appsec/SKILL.md)
- System-wide architecture: [software-architecture-design](../software-architecture-design/SKILL.md)
- Rollout and migration sequencing: [dev-workflow-planning](../dev-workflow-planning/SKILL.md)

## Defaults

- Define the contract before implementation or code generation.
- Use RFC 9457 Problem Details with stable machine-readable error codes.
- Make versioning, deprecation, idempotency, pagination, and rate limits explicit in the spec.
- Prefer OpenAPI 3.2.0 or AsyncAPI as the canonical source for HTTP or event-driven interfaces.
- Treat agent APIs as domain contracts with clear side effects, not thin wrappers around random endpoints.
- MCP is the standard tool-exposure layer for agent consumers; OAuth 2.1 (servers as formal OAuth 2.1 resource servers, RFC 9728 Protected Resource Metadata, RFC 8707 Resource Indicators) is the direction locked into the 2026-07-28 MCP spec — final publication date, still forthcoming as of this writing; verify current status before depending on it.

## Versioning Strategy Table

| Approach | When to use | Breaking-change gate |
|----------|-------------|----------------------|
| URL path versioning (`/v2/`) | Public APIs, broad client install base | oasdiff `--fail-on ERR` in CI |
| Header versioning (`API-Version: 2`) | Internal APIs, frequent iteration | oasdiff on each PR |
| Content-type negotiation | Hypermedia or media-type-driven APIs | Manual review + tests |
| Evolutionary (GraphQL, gRPC) | Teams own schema, introspection tools run | GraphQL Inspector / protobuf compatibility |

## Expert Judgment

**Versioning strategy — pick based on who controls the client, not team preference.**
- If you do not control every client (public API, third-party integrators, mobile apps you cannot force-update), version explicitly (URL path or dated header à la Stripe) and support N-1 for a published window — undo cost after ship is high because you cannot silently migrate callers.
- If you control every client (internal service mesh, monorepo with generated clients), prefer evolutionary compatibility (additive fields, deprecate-then-remove) over versioning — a new version number is a coordination tax you don't need to pay.
- Dated versions (`2026-07-11` style, not `v3`) beat integer majors once you have more than a handful of releases: they let you pin per-account instead of forcing a global cutover, and the date itself communicates recency without a changelog lookup.
- Never let "evolutionary" become an excuse to skip a compatibility gate — GraphQL and gRPC still need CI-enforced schema diffing (GraphQL Inspector, `buf breaking`); "no versioning" is not "no discipline."

**Breaking-change detection instincts — what schema-diff tools structurally cannot catch:**

The instances below are all applications of Hyrum's Law: with enough consumers of an API, every observable behavior — not just the documented schema — becomes a de facto contract, whether or not you ever promised it. (Same law, applied to schema deploy-sequencing rather than API surface, in [software-database-design/references/migration-strategies.md](../software-database-design/references/migration-strategies.md#hyrums-law-and-the-adds-vs-drops-rule).) That is why a clean schema diff is not proof of compatibility:
- Semantic changes with no shape change: tightening an existing enum's allowed values, narrowing a previously-permissive validation rule, or changing what a field *means* while keeping its type — `oasdiff`/`buf breaking` will report zero diff.
- Behavioral defaults: changing a default sort order, default page size, or default timeout is a breaking change for callers who rely on the default, even though the schema is untouched.
- Cross-field coupling: a field that used to be optional-but-ignored becoming optional-but-enforced (e.g., a previously-cosmetic `region` field now affecting routing).
- Rate-limit and quota tightening: not a contract break in the schema sense, but it breaks production traffic identically to a removed field — treat quota changes with the same deprecation-notice discipline as field removal.
- Error-code reclassification: moving a case from `404` to `410`, or from a generic `code` to a more specific one, breaks clients that pattern-match on the old code even though the Problem Details shape is unchanged.
- Treat automated diffing (oasdiff, GraphQL Inspector, `buf breaking`, Pact) as a floor, not a ceiling — pair it with a changelog review by someone who understands what callers actually depend on.

Hyrum's Law framing adapted from addyosmani/agent-skills (MIT), commit `7676817`, 2026-08-09.

**When GraphQL, gRPC, or event-driven contracts are the wrong choice:**
- GraphQL is wrong for simple CRUD with one client shape, for teams that need HTTP-cache semantics (GraphQL responses are POST-only and cache-hostile by default), and for single-team ownership where the query-flexibility payoff is never realized — you inherit N+1 risk, query-complexity DoS surface, and federation tooling cost for no client benefit.
- gRPC is wrong for anything a browser calls directly, for public third-party integrators (protobuf tooling and HTTP/2 trailers are still a barrier outside internal or mobile-native ecosystems), and for APIs whose primary value is discoverability/self-documentation over raw performance — reach for Connect-RPC or REST+OpenAPI instead.
- AsyncAPI/event contracts are wrong when the caller needs an immediate, correlated answer to a specific request — forcing request/response workflows through pub/sub adds correlation-ID bookkeeping and timeout ambiguity that plain synchronous HTTP avoids.
- The tell that a style choice was fashion, not fit: nobody on the team can name the specific latency budget, client platform constraint, or multi-team ownership problem the chosen style solves.

## Known Traps

- Picking GraphQL, gRPC, or AsyncAPI for architectural fashion instead of actual client, latency, or interoperability constraints.
- Designing happy-path resources without an explicit idempotency and retry story for duplicated or partial-failure requests.
- Letting auth stay implicit until implementation, producing inconsistent enforcement across endpoints.
- Reusing pagination models that leak internal storage semantics into the public contract.
- Treating webhook or event delivery as reliable push without signature validation, replay protection, or consumer backpressure.
- Generating a spec from code after implementation and calling it contract-first.
- Wrapping arbitrary internal endpoints as agent APIs without stable side-effect, auth, and validation rules.

## Navigation

**Core patterns:**
- [references/restful-design-patterns.md](references/restful-design-patterns.md) — HTTP method semantics, URL structure, idempotency
- [references/pagination-filtering.md](references/pagination-filtering.md) — cursor vs offset, filtering contracts
- [references/error-handling-patterns.md](references/error-handling-patterns.md) — RFC 9457, error taxonomy
- [references/authentication-patterns.md](references/authentication-patterns.md) — OAuth 2.1, JWT, API keys, mTLS
- [references/rate-limiting-patterns.md](references/rate-limiting-patterns.md) — headers, 429 handling, burst strategies

**Style-specific:**
- [references/api-design-best-practices.md](references/api-design-best-practices.md) — cross-style DX and governance
- [references/versioning-strategies.md](references/versioning-strategies.md) — breaking change detection, deprecation
- [references/api-security-checklist.md](references/api-security-checklist.md) — OWASP API Top 10 checklist
- [references/graphql-patterns.md](references/graphql-patterns.md) — schema design, federation v2, Cosmo Router
- [references/grpc-patterns.md](references/grpc-patterns.md) — protobuf design, streaming, deadlines
- [references/trpc-patterns.md](references/trpc-patterns.md) — TypeScript end-to-end type sharing
- [references/openapi-guide.md](references/openapi-guide.md) — OpenAPI 3.2.0, Spectral, Redocly
- [references/openapi-32-arazzo-101.md](references/openapi-32-arazzo-101.md) — OpenAPI 3.2 new features (streaming types, QUERY method, OAuth flows) and Arazzo 1.1.0 multi-step workflow chains; load when specifying multi-call API sequences or adopting 3.2 features
- [references/asyncapi-patterns.md](references/asyncapi-patterns.md) — event-driven contracts, pub/sub
- [references/webhook-patterns.md](references/webhook-patterns.md) — HMAC signing, replay protection, delivery guarantees
- [references/real-time-api-patterns.md](references/real-time-api-patterns.md) — SSE, WebSocket, long-polling tradeoffs
- [references/api-testing-patterns.md](references/api-testing-patterns.md) — contract tests, property-based testing, Schemathesis
- [references/llm-agent-api-contracts.md](references/llm-agent-api-contracts.md) — MCP integration, AX design, agent-first patterns

**Assets and templates:**
- [assets/openapi-template.yaml](assets/openapi-template.yaml)
- [assets/fastapi/fastapi-complete-api.md](assets/fastapi/fastapi-complete-api.md)
- [assets/express-nodejs/express-complete-api.md](assets/express-nodejs/express-complete-api.md)
- [assets/django-rest/django-rest-complete-api.md](assets/django-rest/django-rest-complete-api.md)
- [assets/spring-boot/spring-boot-complete-api.md](assets/spring-boot/spring-boot-complete-api.md)
- [assets/cross-platform/api-patterns-universal.md](assets/cross-platform/api-patterns-universal.md)
- [assets/cross-platform/template-api-governance.md](assets/cross-platform/template-api-governance.md)
- [assets/cross-platform/template-api-design-review-checklist.md](assets/cross-platform/template-api-design-review-checklist.md)
- [assets/cross-platform/template-api-error-model.md](assets/cross-platform/template-api-error-model.md)
- [data/sources.json](data/sources.json)

**Related skills:**
- [software-backend](../software-backend/SKILL.md), [software-security-appsec](../software-security-appsec/SKILL.md), [data-sql-optimization](../data-sql-optimization/SKILL.md), [qa-testing-strategy](../qa-testing-strategy/SKILL.md), [qa-observability](../qa-observability/SKILL.md), [docs-codebase](../docs-codebase/SKILL.md), [docs-ai-prd](../docs-ai-prd/SKILL.md), [dev-workflow-planning](../dev-workflow-planning/SKILL.md), [software-architecture-design](../software-architecture-design/SKILL.md)

## Fact-Checking

- Verify current standards, library behavior, and tooling claims against primary sources before presenting them as fact.
- Prefer primary specs, official docs, and official tool documentation over summaries.
- If live verification is unavailable, mark version-sensitive claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
