# Data Access Patterns

## Persistence selector
| Need | Prefer | Why |
| --- | --- | --- |
| Query-heavy SQL reads with tight control over SQL text | Dapper | Lowest overhead and precise SQL ownership |
| Relational aggregate writes with evolving domain model | EF Core | Strong mapping/modeling support and transaction boundaries |
| Document-centric aggregate with flexible schema | Mongo | Natural aggregate storage and projection-friendly reads |
| Mixed workload by module | Polyglot | Choose per module/use case, not globally |

## Query/write separation
- Keep read models optimized for query shape; do not force domain aggregates into every query.
- Keep write models focused on invariants and consistency.
- Define repository/query handlers around use cases, not tables/collections alone.

## Dapper SQL patterns
- Select only required columns.
- Use keyset pagination for large ordered datasets; use offset pagination only for small/admin screens.
- Batch related reads to avoid N+1 (joins, IN queries, preloaded maps).
- Keep transaction scopes short and explicit; avoid long business logic inside a transaction.

## EF Core patterns
- Use `AsNoTracking()` for read-only flows and keep tracking enabled only where changes are committed.
- Use projection (`Select`) early to prevent over-fetching entities.
- Use explicit `Include` paths intentionally; avoid accidental lazy-loading behavior.
- Keep `DbContext` scoped per request/unit of work; do not share across concurrent operations.
- Use DbContext pooling only after measuring startup/throughput gain.
- Prefer `ExecuteUpdate`/`ExecuteDelete` for bulk updates when full aggregate loading is unnecessary.
- For advanced relational scenarios and EF Core 10 capabilities, load `references/efcore-persistence-patterns.md`.

## Mongo patterns
- Model documents around aggregate boundaries and read/write access patterns.
- Index by exact filter/sort patterns used in production queries.
- Use projection queries for list endpoints.
- Use optimistic concurrency/version checks when concurrent edits are possible.

## Idempotency and consistency
- Require idempotency keys for externally triggered writes that can be retried.
- Persist idempotency outcome with deterministic replay behavior.
- Use outbox pattern for transactionally consistent event publication.
- Document exactly-once assumptions; default to at-least-once handling.

## Pagination and performance
- Return stable sort keys and continuation token for cursor paging.
- Enforce sensible max page size.
- Measure query latency and rows/documents scanned in telemetry.

## Data-access checklist
- Is the chosen persistence mode aligned to this use case (Dapper/EF Core/Mongo)?
- Is N+1 impossible by design for this path?
- Are indexes aligned to filters and sorts?
- Is write behavior safe under retries and duplicate delivery?
