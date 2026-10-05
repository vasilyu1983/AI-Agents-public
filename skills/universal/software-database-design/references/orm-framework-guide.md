# ORM Framework Guide

Use this file when the question is about how strongly to lean on an ORM versus SQL.

## Selection Heuristic

| Need | Default |
|---|---|
| Fast CRUD app with strong conventions | EF Core, Prisma |
| SQL-first control with typed queries | Drizzle, sqlc, SQLAlchemy Core |
| Complex Python domain model | SQLAlchemy ORM |
| Mixed raw SQL and ORM convenience | EF Core or SQLAlchemy with explicit raw SQL escape hatches |

## Guardrails

- Keep schema ownership explicit; do not let migration generation run unreviewed.
- Watch for N+1 queries, hidden lazy loads, and accidental cartesian joins.
- Prefer explicit transactions around multi-step writes.
- Use raw SQL for performance-critical paths or advanced database features.

## ORM Patterns

| Pattern | When | Example |
|---------|------|---------|
| Repository pattern | Isolate data access from business logic | `UserRepository.findByEmail()` |
| Unit of Work | Batch multiple changes into one transaction | EF Core `SaveChanges()`, SQLAlchemy `session.commit()` |
| Lazy loading | Relationships rarely accessed | Default in most ORMs |
| Eager loading | N+1 query prevention | `.Include()` (EF), `.joinedload()` (SA), `.populate()` (Mongoose) |
| Raw SQL escape hatch | Complex queries ORMs model poorly | Window functions, recursive CTEs |

## ORM Anti-Patterns

| Avoid | Problem | Do Instead |
|-------|---------|------------|
| N+1 queries | Loading related entities in a loop | Use eager loading or batch queries |
| Fat models with business logic | Couples domain logic to persistence | Separate domain and data layers |
| Ignoring generated SQL | ORM produces inefficient queries | Log and review SQL in development |
| Using ORM for bulk operations | Row-by-row processing is slow | Use bulk insert/update or raw SQL |
| Mapping every table to an entity | Over-abstraction | Use raw queries for reports and analytics |
