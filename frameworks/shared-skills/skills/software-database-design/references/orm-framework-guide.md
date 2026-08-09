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
