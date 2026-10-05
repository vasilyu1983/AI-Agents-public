---
paths:
  - "**/*.sql"
  - "**/migrations/**"
description: Destructive-statement and migration-safety rules for SQL and migration files.
owner: skills/universal/software-database-design/SKILL.md
---
Extends common/security.md.
- Give every `UPDATE` and `DELETE` a `WHERE` clause; run the predicate as a `SELECT` first, inside a transaction.
- On PostgreSQL, run each DDL statement with `SET lock_timeout` and `SET statement_timeout`, plus a retry loop.
- Check for long-running transactions on the target table before you run DDL.
- Never edit a migration that has already run; add a new one.
- Run a data backfill as a separate step, not inside the schema migration.
- Enforce these in the project's CI with a SQL or migration linter, such as sqlfluff or squawk.
Why and procedure: skills/universal/software-database-design/SKILL.md#migration-safety-checklist
