# Managed Backend Platform Comparison

Use this table when the user is choosing a platform, not when they already know the platform and need implementation details.

| Platform | Data model | Strongest fit | Watch-outs |
|----------|------------|---------------|------------|
| Supabase | PostgreSQL + RLS | SQL-first products, browser-safe multi-tenant apps, teams that want one platform for auth/storage/realtime/functions | You still need strong schema and RLS discipline; weak policies become the real risk |
| Convex | Function-centric reactive backend | TypeScript-heavy products with live subscriptions, server-owned workflows, and durable scheduled actions | Not SQL-first; migration expectations and data-access patterns differ from Postgres stacks |
| Firebase / Firestore | Document database with strong client sync | Mobile/web apps where offline-first sync and mature SDKs dominate | Data modeling and query patterns require discipline early; SQL portability is low. Firebase's relational option (formerly Data Connect, managed Postgres via Cloud SQL) has since been renamed — verify current product name and GA status in the Firebase docs before recommending it as the SQL escape hatch |
| Appwrite | Full backend bundle with auth, DB, functions, storage, realtime | Self-hosted teams that want an integrated product backend surface | Operational ownership is higher than fully managed platforms; permission design still matters. Appwrite Cloud has historically run in public beta alongside a fully-featured, free self-hosted path — verify current cloud maturity and self-host parity before committing either way |
| PocketBase | Embedded SQLite backend in a single binary | Internal tools, prototypes, and small deployments where simplicity wins | Still pre-1.0 as of mid-2026: full backward compatibility across releases is not guaranteed. Not the default for high-criticality systems or large-team platform ownership. Verify the current version and changelog before an upgrade |
| Neon | Serverless PostgreSQL (branching, scale-to-zero, instant provisioning) — no bundled auth/storage/realtime | Teams that want Postgres-as-a-service without a full BaaS bundle, or that need fast ephemeral database branches (including per-agent databases for AI workloads) | Not a Supabase substitute — bring your own auth, storage, and realtime layer. Acquired by Databricks (deal closed 2025); still operates as an independent Postgres product, but roadmap and pricing direction now sit inside a data/AI-platform strategy — verify current ownership posture and pricing |
| PlanetScale (Postgres) | Managed PostgreSQL with branching and a very low-cost single-node entry tier | Teams that want cheap, branchable Postgres without a bundled BaaS layer, including solo/side-project use | Same "bring your own auth/storage/realtime" caveat as Neon; historically a MySQL/Vitess shop before adding a Postgres product — verify which engine and feature set a given plan actually offers |

## Quick Selection Rules

- Pick **Supabase** if the team already thinks in tables, SQL, and Postgres extensions, and wants RLS, auth, storage, and realtime bundled with the database.
- Pick **Convex** if the team already thinks in TypeScript functions, subscriptions, and live product state.
- Pick **Firebase** if the dominant constraint is cross-device sync and mobile-first client behavior.
- Pick **Appwrite** if the dominant constraint is self-hosting a full app backend rather than only a database.
- Pick **PocketBase** if the dominant constraint is operational simplicity and tiny deployment footprint.
- Pick **Neon or PlanetScale Postgres** if the team wants portable, branchable Postgres but plans to own auth, storage, and realtime itself (or already does, via a custom backend) — this is a database-hosting decision, not a BaaS-bundle decision, so it pairs with [../software-database-design/SKILL.md](../../software-database-design/SKILL.md) rather than replacing this comparison.

## Supabase Operational Gotchas

Production patterns that are easy to miss and cause silent failures at scale.

### PostgREST-style `.in()` filters and URL-length ceilings

Supabase client queries go through PostgREST-style HTTP filters, which encode IDs into the URL. In real deployments, large `.in()` filters can hit proxy, CDN, or server URL-length limits before the application notices.

**The dangerous part**: the failure mode is often "empty result" or ambiguous query failure rather than a crisp compile-time or application-level error. Code that falls back on empty results (authorization checks, reporting, personalization, reconciliation) can degrade silently.

**Fix**: Batch `.in()` queries conservatively, log and inspect errors on each batch, and verify the effective URL-length ceiling in the deployed stack instead of assuming one universal threshold.

```typescript
const BATCH_SIZE = 500;
const allResults = [];
for (let i = 0; i < ids.length; i += BATCH_SIZE) {
  const batch = ids.slice(i, i + BATCH_SIZE);
  const { data, error } = await supabase
    .from('table')
    .select('*')
    .in('id', batch);
  if (error) console.error('Batch query failed:', error);
  if (data) allResults.push(...data);
}
```

**When to worry**: Any cron job, bulk operation, or reporting query that touches hundreds or thousands of rows by ID. User-facing single-row queries are usually unaffected.

### Admin list pagination

Admin list APIs are paginated. Treat page size, cursors, and maximum results as current-provider facts that must be verified in official docs before relying on them in exports, audits, or backfills. For targeted lookups, fetch the specific record directly; for enumerations, paginate explicitly and prove total coverage.

## Cost Traps Beyond The Sticker Price

Managed-Postgres and BaaS pricing pages change frequently; treat any specific dollar figure as stale the moment it is quoted and re-verify at the official pricing page before using it in a decision.

- **Egress/bandwidth**: Supabase, Neon, and PlanetScale all meter database and storage egress separately from compute, with a free allowance that resets monthly and an overage rate per GB. Media-heavy apps, high-fanout realtime reads, and reporting jobs that pull large result sets are the usual budget-busters. Model expected monthly egress before committing to a tier, not after the first overage bill.
- **Compute/branch sprawl**: Branching workflows (Supabase preview branches, Neon/PlanetScale database branches) are cheap individually but easy to leave running; an unmanaged branch-per-PR habit can quietly multiply compute spend. Verify current branch pricing and set an expiry/cleanup policy.
- **Seat- and org-based tiers**: Some platforms (e.g., Appwrite) price paid tiers per organization member rather than per project — a growing team can trigger a tier jump that has nothing to do with usage. Check whether pricing scales with team size, data volume, or both.

## Default Escalation

Move to custom backend services when one of these becomes true:

- security rules are too hard to reason about
- business logic no longer fits the platform's natural model
- one service needs independent scale, ownership, or failure isolation
- audits and controls require stronger separation than the platform offers
