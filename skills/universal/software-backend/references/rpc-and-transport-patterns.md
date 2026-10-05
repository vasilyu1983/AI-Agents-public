# RPC And Transport Patterns

Use this reference when choosing between REST, GraphQL, tRPC, and Connect/gRPC for a backend API.

## Table of Contents

- [Quick Comparison](#quick-comparison)
- [Default Choices](#default-choices)
- [Selection Rules](#selection-rules)
- [REST](#rest)
- [GraphQL](#graphql)
- [tRPC](#trpc)
- [Connect And gRPC](#connect-and-grpc)
- [Anti-Patterns](#anti-patterns)
- [Primary Sources](#primary-sources)

## Quick Comparison

| Transport | Default Use | Strengths | Watch-outs |
|-----------|-------------|-----------|------------|
| REST | Public APIs, simple integrations | Ubiquitous tooling, cache-friendly, easy debugging | Over/under-fetching on complex UIs |
| GraphQL | Client-driven product surfaces | Flexible reads, strong schema, one endpoint | Needs complexity limits, auth, and N+1 controls |
| tRPC | TypeScript monorepos | End-to-end TS inference, low ceremony | Tight TypeScript coupling, weaker polyglot story |
| Connect/gRPC | Service-to-service RPC, browser + backend protobuf APIs | One contract across gRPC, gRPC-Web, and Connect; strong streaming story | More infra and schema discipline than REST |

## Default Choices

- Use REST for third-party-facing APIs, webhook providers, admin APIs, and most CRUD-heavy products.
- Use GraphQL when clients genuinely need shape control across many related entities.
- Use tRPC for TypeScript-only teams shipping a monorepo or tightly-coupled internal app.
- Use Connect when you want protobuf contracts and browser compatibility without maintaining separate gRPC and gRPC-Web stacks.

## Selection Rules

```text
What is the strongest constraint?
  ├─ Public API consumed by many languages/tools -> REST
  ├─ TypeScript monorepo, same team owns client + server -> tRPC
  ├─ Client needs flexible aggregate reads -> GraphQL
  ├─ Internal platform RPC or streaming with protobuf contracts -> Connect/gRPC
  └─ Unsure -> start with REST and add specialized transport only when the pain is real
```

## REST

Prefer REST when:

- The API will be called by partners, scripts, CLIs, or automation tools.
- You need straightforward auth, pagination, rate limiting, and HTTP cache semantics.
- The team wants operational simplicity over transport sophistication.

Checklist:

- Use resource-oriented URLs and correct HTTP methods.
- Return RFC 9457 Problem Details for machine-readable errors.
- Use cursor pagination by default on mutable lists.
- Support idempotency keys for mutating endpoints that may be retried.

## GraphQL

Prefer GraphQL when:

- The frontend needs multiple entity shapes from the same domain graph.
- Over-fetching and request fan-out are a measurable problem.
- The team is willing to invest in schema governance and resolver discipline.

Checklist:

- Persist queries in production.
- Add query depth and complexity limits.
- Use DataLoader or equivalent batching.
- Treat federation as the default distributed-graph approach.
- Do not default to schema stitching for new multi-team graphs; keep it for legacy composition only.

## tRPC

Prefer tRPC when:

- The client and server are both TypeScript.
- Runtime validation and compile-time inference should come from the same schema.
- You want RPC ergonomics without protobuf tooling.

Checklist:

- Keep procedures close to domain boundaries; avoid turning tRPC routers into a dumping ground.
- Use Zod or a similarly explicit validation layer for every input/output boundary.
- Use REST or Connect for external integrations and webhook surfaces.

## Connect And gRPC

Prefer Connect/gRPC when:

- Multiple services need a stable contract and generated clients.
- You need bidirectional or server streaming.
- You want browser support without a separate gRPC-Web implementation path.

Why Connect is the pragmatic default:

- It keeps protobuf contracts.
- It supports gRPC, gRPC-Web, and Connect protocols.
- It works cleanly with browsers and service-to-service traffic.

Checklist:

- Define protobuf packages and versioning rules early.
- Treat protobuf schemas as public contracts with review gates.
- Keep unary RPCs idempotent where retries are possible.
- Model deadlines, auth metadata, and status handling explicitly.

## Anti-Patterns

- Do not pick GraphQL to avoid writing endpoint design.
- Do not expose tRPC as your external public API by default.
- Do not introduce gRPC just because it is "faster" if your bottleneck is the database or downstream services.
- Do not run multiple transports for the same use case unless you can explain the operational gain.

## Primary Sources

- Connect: https://connectrpc.com/
- GraphQL: https://graphql.org/learn/
- tRPC: https://trpc.io/docs
- RFC 9457: https://www.rfc-editor.org/rfc/rfc9457
