# gRPC & Protobuf Design Patterns

> Operational reference for contract-first gRPC APIs. Focuses on protobuf evolution, deadlines, status codes, retries, and browser/public compatibility decisions.

**Freshness anchor:** March 2026 — grounded in current `grpc.io` and `protobuf.dev` guidance.

## When to Use gRPC

- Internal service-to-service calls with strict latency budgets
- Streaming APIs (server, client, or bidirectional)
- Typed contracts shared across multiple languages
- Environments where HTTP/2 and protobuf tooling are already standard

Use REST or GraphQL instead when browser compatibility, cacheability, or third-party ecosystem support matter more than transport efficiency.

## Protobuf Evolution Rules

- Never reuse field numbers.
- Reserve removed field numbers and names.
- Prefer additive schema changes over field renames or type changes.
- Treat enum expansion as potentially breaking for consumers that do not handle unknown values safely.
- Document default values explicitly; do not rely on zero values to imply business meaning.

```proto
message User {
  string id = 1;
  string email = 2;
  string display_name = 3;

  reserved 4, 5;
  reserved "full_name";
}
```

## API Design Checklist

- Define request and response messages explicitly; avoid `google.protobuf.Struct` as a default escape hatch.
- Make deadlines and cancellation part of the contract, not an afterthought.
- Return canonical gRPC status codes and map them to stable application error codes.
- Keep long-running operations explicit with operation resources or async task semantics.
- Document idempotency for mutating RPCs, especially retried unary calls.

## Deadlines, Retries, and Cancellation

- Clients should always send deadlines.
- Servers should propagate cancellation downstream.
- Retry only idempotent or explicitly retry-safe RPCs.
- Publish retry guidance per method rather than relying on blanket client defaults.

```text
Unary reads: safe to retry on UNAVAILABLE or DEADLINE_EXCEEDED when idempotent
Mutations: retry only with idempotency keys or server-side dedupe
Streams: reconnect with explicit resume semantics if continuity matters
```

## Streaming Patterns

- Server streaming: live feeds, export jobs, incremental progress
- Client streaming: batched ingest, telemetry upload
- Bidirectional streaming: collaborative or conversational systems

For each stream, document:

- message ordering guarantees
- heartbeat / keepalive expectations
- backpressure behavior
- reconnect or resume behavior

## Error Model

- Use canonical gRPC status codes (`INVALID_ARGUMENT`, `NOT_FOUND`, `FAILED_PRECONDITION`, `UNAUTHENTICATED`, `PERMISSION_DENIED`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`)
- Add stable domain error codes in metadata or structured details
- Correlate every failure with trace IDs and request IDs

## Browser and Public Compatibility

gRPC alone is often a poor fit for browser-first or public APIs.

Prefer one of these when you need broader compatibility:

- REST + OpenAPI for public developer ecosystems
- GraphQL for client-driven reads
- Connect or gRPC-Gateway style HTTP bridges when you want protobuf contracts with browser-friendly transport

### Connect-RPC and gRPC-Web

**Choose Connect** when you need browser clients or simpler HTTP-native tooling. Connect (canonical implementation: [buf.build/connect](https://buf.build/connect)) speaks plain HTTP/1.1 and HTTP/2, requires no proxy shim, and generates idiomatic TypeScript/Go/Kotlin clients from the same `.proto` files. It is wire-compatible with gRPC and gRPC-Web, so backend services need no changes.

**Stay on vanilla gRPC** for internal service meshes where all callers are server-side and you want the full gRPC ecosystem (interceptors, health protocol, reflection).

**Migration story**: add a Connect handler alongside an existing gRPC handler on the same port (buf's `connect-go` supports this natively). Migrate browser clients first, then decommission gRPC-Web proxies. No protobuf schema changes required.

Avoid gRPC-Web for greenfield work; Connect is the actively maintained successor and requires no Envoy sidecar.

## Cross-References

- `dev-api-design/references/openapi-guide.md` — public HTTP contract documentation
- `dev-api-design/references/error-handling-patterns.md` — stable error design
- `software-backend/SKILL.md` — framework-specific service implementation
