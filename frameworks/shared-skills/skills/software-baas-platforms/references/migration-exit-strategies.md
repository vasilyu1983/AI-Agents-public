# Migration And Exit Strategies

Every platform choice should include an exit story before the first production dependency becomes sticky.

## Exit Signals

- The platform's natural data model now fights the product.
- Security rules or policies are hard to audit.
- One workflow needs bespoke scaling or operational SLOs.
- Scheduled jobs, file handling, or privileged writes have outgrown the platform boundary.
- The team needs portability across multiple services or vendors.

## Practical Exit Paths

| Starting point | Common exit path |
|----------------|------------------|
| Supabase | Keep Postgres, move auth- or workflow-heavy paths into custom backend services first. The database itself is the most portable layer — `pg_dump`/`pg_restore` to a plain Postgres host (RDS, Neon, PlanetScale Postgres, self-hosted) is the well-trodden path; auth, storage, and RLS policies do not move automatically and need their own migration plan |
| Convex | Keep product surface stable, move the heaviest workflow or integration boundaries into external services incrementally |
| Firebase / Firestore | Move the highest-value bounded context into a custom API plus a new operational datastore before rewriting the entire app |
| Appwrite | Peel off critical services one domain at a time while keeping Appwrite for less-sensitive product surfaces |
| PocketBase | Promote hot paths into a dedicated backend early rather than stretching the single-binary model too far |

## Default Rule

Do not migrate the whole platform at once unless the product is still very early. Migrate the tightest pain point first: auth boundary, write path, scheduled workflow, or reporting domain.
