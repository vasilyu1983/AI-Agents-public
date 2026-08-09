# Wrangler Configuration

## Table of Contents

- [Configuration (wrangler.jsonc)](#configuration-wranglerjsonc)

## Configuration (wrangler.jsonc)

### Minimal Config

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-01-01"
}
```

### Full Config with Bindings

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2026-01-01",
  "compatibility_flags": ["nodejs_compat"],

  // Environment variables
  "vars": {
    "ENVIRONMENT": "production"
  },

  // KV Namespace
  "kv_namespaces": [
    { "binding": "KV", "id": "<KV_NAMESPACE_ID>" }
  ],

  // R2 Bucket
  "r2_buckets": [
    { "binding": "BUCKET", "bucket_name": "my-bucket" }
  ],

  // D1 Database
  "d1_databases": [
    { "binding": "DB", "database_name": "my-db", "database_id": "<DB_ID>" }
  ],

  // Workers AI (always remote)
  "ai": { "binding": "AI" },

  // Vectorize
  "vectorize": [
    { "binding": "VECTOR_INDEX", "index_name": "my-index" }
  ],

  // Hyperdrive
  "hyperdrive": [
    { "binding": "HYPERDRIVE", "id": "<HYPERDRIVE_ID>" }
  ],

  // Durable Objects — SQLite-backed storage is the current default for new classes.
  // A binding alone is not enough: every new DO class needs a matching migration entry
  // (below) or the class does not exist and the binding fails at deploy/runtime.
  "durable_objects": {
    "bindings": [
      { "name": "COUNTER", "class_name": "Counter" }
    ]
  },
  "migrations": [
    { "tag": "v1", "new_sqlite_classes": ["Counter"] }
  ],

  // Cron triggers
  "triggers": {
    "crons": ["0 * * * *"]
  },

  // Environments — top-level `vars` are NOT inherited by `env.<name>.vars`.
  // Redeclare every var your Worker needs inside each env block, or it will be
  // undefined at runtime under `--env staging`/`--env production` (Wrangler warns
  // at deploy time, but the var is still missing).
  "env": {
    "staging": {
      "name": "my-worker-staging",
      "vars": { "ENVIRONMENT": "staging" }
    }
  }
}
```

### `nodejs_compat` Is a Special Compatibility Flag

Unlike most compatibility flags, `nodejs_compat` is not scheduled to become a default-on behavior tied to a future `compatibility_date` — it must be set explicitly in every project that needs Node.js API polyfills/natives (`fs`, `path`, `crypto`, streams, etc.), regardless of how recent the compatibility date is. Sub-features gated under it (specific modules like `node:dgram` or `node:timers`) do auto-enable once `nodejs_compat` is on and the compatibility date crosses their own threshold. Re-verify current sub-flag behavior at `developers.cloudflare.com/workers/configuration/compatibility-flags/` before assuming a given Node.js module works without it.

### Generate Types from Config

```bash
# Generate worker-configuration.d.ts
wrangler types

# Custom output path
wrangler types ./src/env.d.ts

# Check types are up to date (CI)
wrangler types --check
```

---
