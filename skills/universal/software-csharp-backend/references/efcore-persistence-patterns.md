# EF Core Persistence Patterns

## When EF Core fits
- Prefer EF Core for relational modules with rich aggregates, transactional writes, and evolving domain models.
- Prefer Dapper for read-heavy SQL paths where query text ownership and low overhead are primary.
- Use EF Core selectively per module in polyglot systems.

## Setup defaults
- Configure `DbContext` with explicit command timeout and connection resiliency settings.
- Keep `DbContext` lifetime scoped to request/unit-of-work.
- Add DbContext pooling only after measuring benefit; validate no shared mutable state in context services.
- Keep provider-specific behaviors explicit (for example, Npgsql retry and timeout settings).

## Modeling and configuration
- Keep entity configuration in `IEntityTypeConfiguration<T>` classes.
- Define key, length, nullability, precision, and index constraints explicitly.
- Use query filters intentionally for soft-delete and tenant isolation.
- Keep aggregate invariants in domain/application logic, not only in EF configuration.

## Query and performance patterns
- Use `AsNoTracking()` for read paths and projections for API payload shaping.
- Avoid unbounded `Include` chains; design query handlers per endpoint use case.
- Two or more collection navigations loaded in one query (via `Include` or a projection) become one JOIN whose row count is the product of the collection sizes (cartesian explosion). Project only the fields the endpoint needs, or use `AsSplitQuery()` (per query, or globally via `UseQuerySplittingBehavior`). Measure returned row counts before and after. Split queries cost one extra round trip per collection and, outside a suitably isolated transaction, can read data that changed between the queries.
- Use compiled queries only for proven hot paths.
- Prevent N+1 via explicit includes, joins, or batched secondary queries.
- Use bulk operations (`ExecuteUpdate`/`ExecuteDelete`) when full entity materialization is unnecessary.

## Consistency and transactions
- Keep transactions short and centered around state transitions.
- Combine idempotency and transaction boundaries for externally retried writes.
- With a retrying execution strategy (`EnableRetryOnFailure`), run a user-initiated transaction inside `Database.CreateExecutionStrategy().ExecuteAsync(...)` so the whole unit retries; a bare `BeginTransaction` under that strategy throws. Do not add an app-level retry around it as well.
- Avoid cross-service distributed transaction assumptions; prefer outbox/eventual consistency.

## Migrations and rollout safety
- Keep migrations small, deterministic, and reversible where possible.
- Generate idempotent SQL for controlled production rollout when required by operations.
- Coordinate schema/application rollout for backward compatibility across deploy windows.

## EF Core 10 feature notes
- Named query filters improve selective filter disable behavior; use clear filter names.
- `LeftJoin`/`RightJoin` reduce verbose join composition for readability.
- Simplified `ExecuteUpdate` flow improves conditional bulk update readability.
- Complex types can now map directly to JSON columns (SQL Server's native `json` type on compatibility level 170+/Azure SQL, and PostgreSQL `jsonb`) — use this for genuinely semi-structured value objects instead of hand-rolled JSON string columns, but keep query-critical fields relational so they stay indexable without JSON path expressions.
- Treat new features as optional upgrades; prioritize compatibility with active repository standards.
- EF Core NativeAOT and precompiled queries are documented by Microsoft as "highly experimental" and not recommended for production. If the host targets Native AOT, use raw ADO.NET or Dapper.AOT for that data path (see `references/aspnet-core-api-patterns.md`). Outside AOT, `dotnet ef dbcontext optimize --precompile-queries` is a startup optimization. Treat it as experimental until the docs say otherwise.
- EF10 requires the .NET 10 runtime, so an EF upgrade is coupled to the host runtime upgrade.
- EF10 translates parameterized collections (`ids.Contains(x.Id)`) to one padded scalar parameter per value by default, replacing the EF8/9 `OPENJSON` array parameter. This changes query plans. Control it globally with `UseParameterizedCollectionMode(...)` or per query with `EF.Constant(...)`.
- On SQL Server compatibility level 170+ or Azure SQL, the first EF10 migration changes existing `nvarchar` JSON columns to the native `json` type. To opt out, pin `nvarchar(max)` or keep a lower compatibility level.
- EF10 redacts inlined constants in SQL logs by default and ships an analyzer that warns on string concatenation inside `FromSqlRaw`. Do not suppress that warning casually.

## Pitfalls to avoid
- Sharing one `DbContext` across threads. For concurrent work, create a scope per operation or use `IDbContextFactory<T>`.
- Long-lived transactions with outbound network calls inside them.
- Blindly enabling lazy loading in latency-sensitive paths.
- Treating migrations as a deployment afterthought.
