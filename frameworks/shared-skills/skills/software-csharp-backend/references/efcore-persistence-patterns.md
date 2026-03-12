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
- Use compiled queries only for proven hot paths.
- Prevent N+1 via explicit includes, joins, or batched secondary queries.
- Use bulk operations (`ExecuteUpdate`/`ExecuteDelete`) when full entity materialization is unnecessary.

## Consistency and transactions
- Keep transactions short and centered around state transitions.
- Combine idempotency and transaction boundaries for externally retried writes.
- Avoid cross-service distributed transaction assumptions; prefer outbox/eventual consistency.

## Migrations and rollout safety
- Keep migrations small, deterministic, and reversible where possible.
- Generate idempotent SQL for controlled production rollout when required by operations.
- Coordinate schema/application rollout for backward compatibility across deploy windows.

## EF Core 10 feature notes
- Named query filters improve selective filter disable behavior; use clear filter names.
- `LeftJoin`/`RightJoin` reduce verbose join composition for readability.
- Simplified `ExecuteUpdate` flow improves conditional bulk update readability.
- Treat new features as optional upgrades; prioritize compatibility with active repository standards.

## Pitfalls to avoid
- Sharing one `DbContext` across threads.
- Long-lived transactions with outbound network calls inside them.
- Blindly enabling lazy loading in latency-sensitive paths.
- Treating migrations as a deployment afterthought.
