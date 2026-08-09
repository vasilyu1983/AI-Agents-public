# Wrangler Storage And Data

## Table of Contents

- [Choosing a Storage Primitive](#choosing-a-storage-primitive)
- [KV (Key-Value Store)](#kv-key-value-store)
- [R2 (Object Storage)](#r2-object-storage)
- [D1 (SQL Database)](#d1-sql-database)

## Choosing a Storage Primitive

Pick by consistency model and access shape, not familiarity — this is the most common source of an over- or under-engineered Cloudflare architecture. Durable Objects bindings/CLI live in `references/configuration.md`; this table exists so the choice is made before reaching for any one product's commands below.

| Need | Reach for | Why |
|------|-----------|-----|
| Read-heavy, eventually-consistent, small values (config, flags, cached fragments) | KV | Cheap global reads, ~seconds-to-a-minute propagation; do not use it where you need read-your-writes consistency |
| Relational data that partitions per-tenant/per-user and fits one shard | D1 | SQL, per-database size cap (verify current cap at `developers.cloudflare.com/d1/platform/limits/`) — design for many small databases, not one large one |
| Strongly consistent single-writer state (WebSocket room, lock, counter, in-memory aggregation before flush) | Durable Objects | Single-threaded per-id execution gives you real consistency without external locking |
| Large binary objects, uploads, media | R2 | No egress fee, S3-compatible API |

**D1 vs external Postgres/MySQL (via Hyperdrive)**: use D1 when data naturally shards per-tenant/per-user and stays within the per-database size cap with moderate write volume. Reach for Hyperdrive + an external Postgres/MySQL instance when the workload needs cross-tenant joins, heavy analytical queries, an existing relational estate, or write throughput that would force artificial sharding of D1 just to stay under its cap.

**Durable Objects pitfall**: a single global DO id fronting all traffic for a feature is a deliberate serialization point, not free concurrency — every request to that id executes one at a time. Shard DO ids by user/tenant/document/room unless the feature genuinely requires one global total order.

## KV (Key-Value Store)

### Manage Namespaces

```bash
# Create namespace
wrangler kv namespace create MY_KV

# List namespaces
wrangler kv namespace list

# Delete namespace
wrangler kv namespace delete --namespace-id <ID>
```

### Manage Keys

```bash
# Put value
wrangler kv key put --namespace-id <ID> "key" "value"

# Put with expiration (seconds)
wrangler kv key put --namespace-id <ID> "key" "value" --expiration-ttl 3600

# Get value
wrangler kv key get --namespace-id <ID> "key"

# List keys
wrangler kv key list --namespace-id <ID>

# Delete key
wrangler kv key delete --namespace-id <ID> "key"

# Bulk put from JSON
wrangler kv bulk put --namespace-id <ID> data.json
```

### Config Binding

```jsonc
{
  "kv_namespaces": [
    { "binding": "CACHE", "id": "<NAMESPACE_ID>" }
  ]
}
```

**Limits note**: KV enforces a per-key write rate limit (one write to the same key per second, on every plan) and a maximum value size — this is why KV suits config/flags, not high-frequency counters or large payloads. Verify the current max value size and free/paid read-write allowances at `developers.cloudflare.com/kv/platform/limits/` and `.../pricing/`.

---


## R2 (Object Storage)

### Manage Buckets

```bash
# Create bucket
wrangler r2 bucket create my-bucket

# Create with location hint
wrangler r2 bucket create my-bucket --location wnam

# List buckets
wrangler r2 bucket list

# Get bucket info
wrangler r2 bucket info my-bucket

# Delete bucket
wrangler r2 bucket delete my-bucket
```

### Manage Objects

```bash
# Upload object
wrangler r2 object put my-bucket/path/file.txt --file ./local-file.txt

# Download object
wrangler r2 object get my-bucket/path/file.txt

# Delete object
wrangler r2 object delete my-bucket/path/file.txt
```

### Config Binding

```jsonc
{
  "r2_buckets": [
    { "binding": "ASSETS", "bucket_name": "my-bucket" }
  ]
}
```

**Pricing note**: R2's headline differentiator is $0 egress (including via the Workers binding, S3 API, and public `r2.dev` domains) — you pay for storage and a modest per-operation fee only. R2 also supports event notifications (object-create/delete) that can trigger a Queue consumer or Worker. Current per-GB/per-operation rates and free-tier storage move independently of this skill — verify at `developers.cloudflare.com/r2/pricing/` before quoting a number.

---


## D1 (SQL Database)

### Manage Databases

```bash
# Create database
wrangler d1 create my-database

# Create with location
wrangler d1 create my-database --location wnam

# List databases
wrangler d1 list

# Get database info
wrangler d1 info my-database

# Delete database
wrangler d1 delete my-database
```

### Execute SQL

```bash
# Execute SQL command (remote)
wrangler d1 execute my-database --remote --command "SELECT * FROM users"

# Execute SQL file (remote)
wrangler d1 execute my-database --remote --file ./schema.sql

# Execute locally
wrangler d1 execute my-database --local --command "SELECT * FROM users"
```

### Migrations

```bash
# Create migration
wrangler d1 migrations create my-database create_users_table

# List pending migrations
wrangler d1 migrations list my-database --local

# Apply migrations locally
wrangler d1 migrations apply my-database --local

# Apply migrations to remote
wrangler d1 migrations apply my-database --remote
```

### Export/Backup

```bash
# Export schema and data
wrangler d1 export my-database --remote --output backup.sql

# Export schema only
wrangler d1 export my-database --remote --output schema.sql --no-data
```

### Config Binding

```jsonc
{
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "my-database",
      "database_id": "<DATABASE_ID>",
      "migrations_dir": "./migrations"
    }
  ]
}
```

**Limits/pricing note**: each D1 database has a fixed per-database size cap by design — Cloudflare's stated model is horizontal scale-out across many small (per-tenant/per-user) databases rather than one large one, and the cap is not raisable. Billing is consumption-based on rows read, rows written, and storage, with no charge for idle compute or data-transfer/bandwidth. Verify the current cap and rates at `developers.cloudflare.com/d1/platform/limits/` and `.../pricing/` — both have moved before and will move again.

---
