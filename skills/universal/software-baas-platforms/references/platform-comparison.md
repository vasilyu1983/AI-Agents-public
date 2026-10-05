# Managed Backend Platform Comparison

Use this table when the user is choosing a platform, not when they already know the platform and need implementation details.

| Platform | Data model | Strongest fit | Watch-outs |
|----------|------------|---------------|------------|
| Supabase | PostgreSQL + RLS | SQL-first products, browser-safe multi-tenant apps, teams that want one platform for auth/storage/realtime/functions | You still need strong schema and RLS discipline; weak policies become the real risk |
| Convex | Function-centric reactive backend | TypeScript-heavy products with live subscriptions, server-owned workflows, and durable scheduled actions | Not SQL-first; migration expectations and data-access patterns differ from Postgres stacks. The backend is self-hostable under FSL-Apache-2.0: fair source, with a competing-service restriction and later Apache conversion. Check cloud-plan billing units before comparing team costs |
| Firebase / Firestore | Document database with strong client sync | Mobile/web apps where offline-first sync and mature SDKs dominate | Data modeling and query patterns require discipline early; SQL portability is low. [Firebase SQL Connect](https://firebase.google.com/docs/sql-connect) (formerly Data Connect) provides managed Cloud SQL for PostgreSQL. For richer document queries, evaluate Firestore Enterprise modes below before exiting Firebase |
| Appwrite | Full backend bundle with auth, DB, functions, storage, realtime | Self-hosted teams that want an integrated product backend surface | Operational ownership is higher than fully managed platforms; permission design still matters. Appwrite Cloud graduated from beta with the 2025-09-01 pricing change. Check the current pricing page for project-based charges and compare cloud/self-host feature parity |
| PocketBase | Embedded SQLite backend in a single binary | Internal tools, prototypes, and small deployments where simplicity wins | Still pre-1.0 — verify release status: full backward compatibility across releases is not guaranteed. Not the default for high-criticality systems or large-team platform ownership. Verify the current version and changelog before an upgrade |
| Neon | Lakebase Postgres with branching and scale-to-zero; optional Object Storage, Functions, Managed Better Auth, and AI Gateway | Branchable Postgres alone, or a composed backend using its additional primitives | Decide database-only versus bundled services explicitly; inventory auth/storage/function coupling rather than assuming Neon has no app-backend services |
| PlanetScale (Postgres) | Managed PostgreSQL with branching and single-node or HA deployment | Teams that want branchable Postgres while owning app auth/storage/realtime separately | Bring your own app auth/storage/realtime; historically a MySQL/Vitess shop before adding a Postgres product — verify which engine and feature set a given plan actually offers |

## Vendor Status (verify before starting a new project)

| Vendor | Status | Source to re-check |
|--------|--------|--------------------|
| InstantDB | New signups closed; all cloud apps shut down on 2027-08-31, backups available until 2028-08-31; code stays open source with a self-host guide. Do not start new projects on the hosted service | instantdb.com/essays/instant_team_joins_openai |
| Supabase keys | Legacy `anon`/`service_role` keys deprecated by the end of 2026; use publishable/secret keys | supabase.com/docs/guides/api/api-keys |
| Appwrite Cloud | GA since 2025-09-01, per-project pricing | appwrite.io/blog/post/appwrite-pricing-update |
| Convex | Self-hostable fair-source backend (FSL-Apache-2.0); review the competing-service restriction | [Self-hosting](https://docs.convex.dev/self-hosting) |
| Neon | Markets the database as Lakebase Postgres; its [backend announcement](https://neon.com/blog/neon-backend-is-ga) includes Object Storage, Functions, Managed Better Auth, and AI Gateway | Recheck the selected primitives and regional availability in [Neon docs](https://neon.com/docs) |
| Firebase Dynamic Links | Shutdown date was 2025-08-25; do not use it for new deep links or auth-link dependencies | [Deprecation FAQ](https://firebase.google.com/support/dynamic-links-faq) |

## Quick Selection Rules

- Pick **Supabase** if the team already thinks in tables, SQL, and Postgres extensions, and wants RLS, auth, storage, and realtime bundled with the database.
- Pick **Convex** if the team already thinks in TypeScript functions, subscriptions, and live product state.
- Pick **Firebase** if the dominant constraint is cross-device sync and mobile-first client behavior.
- Pick **Appwrite** if the dominant constraint is self-hosting a full app backend rather than only a database.
- Pick **PocketBase** if the dominant constraint is operational simplicity and tiny deployment footprint.
- Pick **PlanetScale Postgres or Neon database-only** when the team wants branchable Postgres with separately owned app services. If adopting Neon backend primitives, compare that bundle and its exit path explicitly. Use [software-database-design](../../software-database-design/SKILL.md) for schema decisions.

## Staying on Firebase

Before a Firestore exit, check [Enterprise edition modes](https://firebase.google.com/docs/firestore/enterprise/overview-enterprise-edition-modes): Native mode combines Core operations (including listeners/offline persistence) with Pipeline operations for advanced queries; MongoDB compatibility is a separate mode using MQL/BSON and MongoDB drivers. Do not assume identical client SDK, offline, or security behavior across the modes. Choose SQL Connect when the actual requirement is PostgreSQL rather than richer document queries.

## Supabase Operational Gotchas

Production patterns that are easy to miss and cause silent failures at scale.

### PostgREST-style `.in()` filters and URL-length ceilings

Supabase client queries go through PostgREST-style HTTP filters, which encode IDs into the URL. In real deployments, large `.in()` filters can hit proxy, CDN, or server URL-length limits before the application notices.

**The dangerous part**: the failure mode is often "empty result" or ambiguous query failure rather than a crisp compile-time or application-level error. Code that falls back on empty results (authorization checks, reporting, personalization, reconciliation) can degrade silently.

**Fix**: Batch `.in()` queries conservatively, log and inspect errors on each batch, and verify the effective URL-length ceiling in the deployed stack instead of assuming one universal threshold.

```typescript
const BATCH_SIZE = 500; // Illustrative; size from deployed URL/proxy limits.
const allResults = [];
for (let i = 0; i < ids.length; i += BATCH_SIZE) {
  const batch = ids.slice(i, i + BATCH_SIZE);
  const { data, error } = await supabase
    .from('table')
    .select('*')
    .in('id', batch);
  if (error) throw new Error('Batch query failed', { cause: error });
  if (!data) throw new Error('Batch query returned no data');
  allResults.push(...data);
}
```

**When to worry**: Any cron job, bulk operation, or reporting query that touches hundreds or thousands of rows by ID. User-facing single-row queries are usually unaffected.

### Admin list pagination

Admin list APIs are paginated. Treat page size, cursors, and maximum results as current-provider facts that must be verified in official docs before relying on them in exports, audits, or backfills. For targeted lookups, fetch the specific record directly; for enumerations, paginate explicitly and prove total coverage.

## Billing and Availability Lookup

Read these provider pages when comparing plans. Record the retrieved date, engine/region, and chosen plan in the decision artifact; this skill stores no price snapshot.

| Provider | Lookup | Decision inputs to capture |
|----------|--------|----------------------------|
| Supabase | [Pricing](https://supabase.com/pricing) | Free-project inactivity pausing and restoration; project/compute charges, auth MAU, storage, cached versus uncached egress, branch costs, and spend-cap scope |
| Neon | [Pricing](https://neon.com/pricing) and [scale-to-zero](https://neon.com/docs/introduction/scale-to-zero) | Free eligibility; autosuspend configuration and wake latency; active compute, storage/history, branches, transfer, and selected backend-primitive charges. Idle compute does not imply zero storage cost |
| PlanetScale | [Pricing](https://planetscale.com/pricing) | Free-plan availability (do not assume one); Postgres versus Vitess/Neki, single-node versus HA, region/architecture, replicas, storage/transfer, and development-branch costs. A cheap single-node tier has no HA replicas |
| Convex | [Pricing](https://www.convex.dev/pricing) | Developer/seat basis, project/deployment scope, function and storage usage, bandwidth, and overage handling |
| Firebase | [Pricing](https://firebase.google.com/pricing) | Reads/writes/query execution, storage/transfer, functions, auth, and the separate Cloud SQL bill for SQL Connect; distinguish Enterprise modes |
| Appwrite | [Pricing](https://appwrite.io/pricing) | Project billing, inactivity policy, bandwidth/storage/function quotas, and cloud versus self-host operating cost |

Estimate production plus preview branches, backup retention, idle periods, and a high-egress case. Do not assume every provider meters database and object-storage egress identically. Set branch expiry and cleanup ownership before enabling branch-per-PR workflows.

## Default Escalation

Move to custom backend services when one of these becomes true:

- security rules are too hard to reason about
- business logic no longer fits the platform's natural model
- one service needs independent scale, ownership, or failure isolation
- audits and controls require stronger separation than the platform offers
