# Supabase Cost Guide

Operational reference for controlling Supabase spend. Covers plan tiers, billing mechanics, cost drivers ranked by impact, and a concrete optimization checklist.

## Table of Contents

- [Plan Tiers](#plan-tiers)
- [Billing Model](#billing-model)
- [Cost Drivers](#cost-drivers)
  - [Database Compute](#database-compute)
  - [Storage](#storage)
  - [Bandwidth (Egress)](#bandwidth-egress)
  - [Auth MAUs](#auth-maus)
  - [Edge Functions](#edge-functions)
  - [Realtime](#realtime)
- [Database Optimization for Cost](#database-optimization-for-cost)
- [Project Management](#project-management)
- [Common Optimization Checklist](#common-optimization-checklist)
- [Monitoring](#monitoring)
- [When to Consider Alternatives](#when-to-consider-alternatives)

---

## Plan Tiers

| Feature | Free | Pro ($25/mo) | Team ($599/mo) |
|---|---|---|---|
| Projects | 2 active | Unlimited | Unlimited |
| Database | 500 MB | 8 GB | 8 GB + higher limits |
| Storage | 1 GB | 100 GB | 100 GB + higher limits |
| Bandwidth | 2 GB | 250 GB | 250 GB + higher limits |
| Auth MAUs | 50K | 100K | 100K + higher limits |
| Edge Function invocations | 500K | 2M | 2M + higher limits |
| Backups | None | Daily | Daily + PITR |
| Support | Community | Email | Priority |
| Compliance | -- | -- | SOC2 |

### Decision framework

- **Stay on Free** when the project is a prototype, internal tool with light traffic, or a dev/staging environment that fits within the 500 MB database and 2 GB bandwidth caps.
- **Move to Pro** when any single Free-tier limit is regularly hit, when daily backups are needed, or when the $25/month cost is less than the engineering time spent working around Free-tier constraints (pausing projects, manual backups, etc.).
- **Move to Team** when the organization requires SOC2 compliance, priority support SLAs, or needs compute and bandwidth headroom beyond what Pro overage pricing makes economical.

---

## Billing Model

- **Base subscription** is the flat monthly fee for the chosen tier (Free, Pro, Team).
- **Compute add-ons** are billed separately from the base plan. Each project can have its own compute tier (Micro, Small, Medium, Large, etc.) with per-hour pricing.
- **Usage overage** applies to bandwidth and storage beyond plan-included allowances. Overage is billed per GB at published rates.
- **Pausing inactive projects** stops compute charges for that project. On the Free tier, projects that are inactive for 7+ days may be auto-paused. On paid tiers, pausing is manual and removes the compute cost while the project remains accessible for reactivation.
- Billing is per-organization. All projects under one org roll up into a single invoice.

---

## Cost Drivers

Ranked by typical impact on the monthly bill, highest first.

### Database Compute

**What it is:** Postgres CPU and RAM allocation for each project. This is the single largest cost lever on most Supabase bills.

**Compute tiers:**

| Tier | Approx. hourly rate | Typical use |
|---|---|---|
| Micro | $0 (included in Pro) | Dev, staging, low-traffic production |
| Small | ~$0.0206/hr | Light production workloads |
| Medium | ~$0.0822/hr | Moderate traffic, heavier queries |
| Large | ~$0.1644/hr | High-concurrency production |
| XL and above | Higher | Large-scale or compute-intensive apps |

**Common waste:**
- Running Small or Medium compute on projects that never exceed Micro-level CPU usage.
- Keeping dev/staging projects on paid compute tiers around the clock.

**Optimization:**
- Use connection pooling (Supavisor / pgbouncer) on every project. Pooling reduces connection overhead and lets smaller compute tiers handle more concurrent clients.
- Optimize expensive queries (see [Database Optimization for Cost](#database-optimization-for-cost)).
- Use read replicas only when query volume actually saturates the primary; each replica is a separate compute charge.
- Run dev and staging projects on Micro or on Free-tier projects.

### Storage

**What it is:** Object storage for user uploads, media, and application files. Billed per GB stored plus per-operation charges for uploads, downloads, and transformations.

**Common waste:**
- Orphaned uploads (user deletes account but files remain).
- No lifecycle or cleanup policy.
- Storing large uncompressed images or videos when compressed versions would suffice.

**Optimization:**
- Implement cleanup policies: delete orphaned objects on a schedule or via database triggers.
- Compress and resize images before upload (client-side or via an edge function on ingest).
- Use signed URLs with short expiration for private assets to prevent indefinite caching and unmetered access.
- Audit storage buckets periodically for stale or duplicate files.

### Bandwidth (Egress)

**What it is:** Combined egress from database queries, storage downloads, and Edge Function responses.

**Common waste:**
- Fetching entire tables client-side without pagination or column selection.
- Serving large media files directly from Supabase storage without a CDN.
- Edge Functions returning large payloads on every invocation.

**Optimization:**
- Paginate all list queries. Use `.range()` or cursor-based pagination.
- Select only needed columns (`.select('id, name')` instead of `.select('*')`).
- Use RPC functions (database functions called via `.rpc()`) to aggregate or filter data server-side, reducing the payload sent to the client.
- Implement client-side caching (SWR, React Query, or HTTP cache headers).
- Serve public assets through a CDN (Cloudflare, Vercel, etc.) rather than directly from Supabase storage.

### Auth MAUs

**What it is:** Monthly Active Users who authenticate at least once in a billing period. Free includes 50K, Pro includes 100K.

**What counts as an MAU:** Any unique user who signs in, signs up, refreshes a token, or triggers an auth event within the calendar month.

**Optimization:**
- Review whether anonymous auth is enabled unintentionally. Anonymous sign-ins count toward MAU totals and can inflate numbers significantly on public-facing apps.
- Clean up inactive accounts that will never return (with appropriate data retention compliance).
- If MAU count is the primary cost driver pushing you to the next tier, evaluate whether the auth volume is genuine or inflated by bots.

### Edge Functions

**What it is:** Serverless Deno functions deployed at the edge. Billed by invocations and execution time.

**Common waste:**
- Using Edge Functions for logic that could run as a Postgres function (plpgsql), avoiding the network round-trip and invocation cost entirely.
- No response caching, so identical requests trigger full re-execution.

**Optimization:**
- Move server-side logic that reads or writes the database into database functions (plpgsql or SQL functions) invoked via `.rpc()`. This eliminates Edge Function invocation costs and reduces latency.
- Cache Edge Function responses where the data is not user-specific (e.g., using CDN cache headers or a short-lived cache layer).
- Batch operations: design Edge Functions to handle arrays of items per call rather than one item per call.

### Realtime

**What it is:** WebSocket-based pub/sub for live database changes, broadcast, and presence. Billed by concurrent connections.

**Common waste:**
- Opening Realtime channels on every page, including pages that do not display live data.
- Presence channels left open after the user navigates away or the tab goes idle.

**Optimization:**
- Subscribe to Realtime channels only on screens that genuinely need live updates.
- Unsubscribe and clean up presence when the component unmounts or the tab becomes inactive.
- Use polling (with a reasonable interval) instead of Realtime for data that changes infrequently.

---

## Database Optimization for Cost

These practices reduce compute charges by lowering CPU and memory pressure on the Postgres instance.

- **Query optimization:** Use `EXPLAIN ANALYZE` to find sequential scans and high-cost nodes. Rewrite queries to avoid unnecessary joins, subqueries, and full-table scans.
- **Indexing:** Add indexes on columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses. Remove unused indexes (they cost write performance and storage).
- **RLS policy performance:** Poorly written Row Level Security policies can cause per-row function calls that multiply CPU usage. Test RLS-heavy queries with `EXPLAIN ANALYZE` and look for high row estimates. Prefer simple, index-backed policies (e.g., `auth.uid() = user_id`) over correlated subqueries.
- **Connection pooling:** Always use Supavisor (or pgbouncer) in production. Direct connections consume more memory per client. Pooled mode (transaction or session) reduces idle connection overhead.
- **Vacuum and maintenance:** Postgres auto-vacuum prevents table bloat. If auto-vacuum is falling behind (visible as increased dead tuples in `pg_stat_user_tables`), tune `autovacuum_vacuum_scale_factor` and `autovacuum_analyze_scale_factor` for high-churn tables. Uncontrolled bloat increases storage costs and slows queries.

---

## Project Management

- **Pausing unused projects:** On the Free tier, only 2 projects can be active. Pause projects that are not in use to free a slot. On paid tiers, pausing stops compute charges.
- **Branching and preview environments:** Each branch is a separate, temporary database. Branches incur compute cost for the duration they are active. Merge or delete branches promptly after review.
- **Dev/staging environments:** Use Free-tier projects for development and staging when possible. There is no requirement that dev environments match the production plan tier. If the Free-tier 500 MB database limit is too small for realistic staging data, use Pro with Micro compute.

---

## Common Optimization Checklist

1. Enable connection pooling (Supavisor) on all projects.
2. Audit RLS policies for performance -- run `EXPLAIN ANALYZE` on queries hitting RLS-protected tables.
3. Add indexes for frequently queried and filtered columns.
4. Implement pagination on all list queries (no unbounded `SELECT *`).
5. Set up storage cleanup policies for orphaned and expired uploads.
6. Use database functions (plpgsql) instead of Edge Functions where possible.
7. Pause inactive projects to stop compute charges.
8. Review compute tier -- downsize if average CPU usage is consistently below 20%.
9. Check if any paid project can run on the Free tier instead.
10. Serve public storage assets through a CDN rather than direct Supabase URLs.

---

## Monitoring

**Supabase Dashboard metrics:**
- Database size and growth rate (Settings > Database).
- Bandwidth consumption by category (database, storage, Edge Functions).
- Compute usage: CPU and memory utilization over time.
- Auth MAU count for the current billing period.
- Edge Function invocation count and execution time.

**Setting up usage alerts:**
- Supabase supports usage notifications. Configure alerts for bandwidth and database size thresholds to catch runaway growth before the bill arrives.
- For more granular alerting, query `pg_stat_statements` and `pg_stat_user_tables` on a schedule via a cron extension (pg_cron) or external monitor.

**Key metrics to track:**
- Database size growth rate (GB/week). Sudden jumps indicate bloat or unexpected data volume.
- Peak concurrent connections. If consistently near the compute tier limit, upgrade or optimize pooling.
- Bandwidth per project per week. Identifies which project is the cost driver.
- Edge Function error rate. Failed invocations still count toward billing.

---

## When to Consider Alternatives

| Scenario | Alternative to evaluate |
|---|---|
| Read-heavy workload with simple auth needs | PlanetScale or Neon (serverless Postgres). Both offer generous free tiers and scale-to-zero compute. |
| Offline-first mobile app | Local-first database with sync (PowerSync, ElectricSQL, or CRDT-based stores). Reduces bandwidth and Realtime costs. |
| Very high bandwidth / media-heavy | Self-hosted Postgres + dedicated CDN (Cloudflare R2 for storage). Eliminates Supabase egress charges. |
| Need for multi-region writes | CockroachDB or PlanetScale. Supabase read replicas are single-region write. |

Switching cost is non-trivial. Evaluate alternatives only when Supabase-specific costs are the dominant line item and optimization has already been applied.
