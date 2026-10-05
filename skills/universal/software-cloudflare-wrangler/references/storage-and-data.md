# Wrangler Storage And Data

Before you touch any product's commands, choose the storage primitive. The KV vs D1 vs Durable Objects vs R2 decision table, and the D1 vs Hyperdrive rule, are in `SKILL.md` under Expert Judgment.

Command syntax is maintained upstream. Get it from `wrangler <group> --help` and the product docs instead of copying it from memory.

## Table of Contents

- [Command Groups](#command-groups)
- [Remote vs Local Safety](#remote-vs-local-safety)
- [Product Notes](#product-notes)

## Command Groups

| Product | Command group | Binding key | Docs |
|---------|---------------|-------------|------|
| KV | `wrangler kv --help` (namespace, key, bulk) | `kv_namespaces` | `developers.cloudflare.com/kv/` |
| R2 | `wrangler r2 --help` (bucket, object) | `r2_buckets` | `developers.cloudflare.com/r2/` |
| D1 | `wrangler d1 --help` (create, execute, migrations, export) | `d1_databases` | `developers.cloudflare.com/d1/` |

## Remote vs Local Safety

In Wrangler v4, KV, R2 and D1 data commands act on **local** simulated storage unless you pass `--remote`. A bare read that looks correct may be reading local data, and a write you believed was local may be remote if you added `--remote` out of habit.

Before you run any `--remote` write, apply the environment identity gate in `SKILL.md`.

For D1, apply migrations locally first (`wrangler d1 migrations apply <db> --local`). Then take a backup with `wrangler d1 export <db> --remote` before you apply the same migrations with `--remote`.

## Product Notes

### KV

- Per-key write-rate and value-size limits constrain hot keys; read the current limits before estimating throughput.

This is why KV suits config and feature flags, not high-frequency counters or large payloads. Verify the current value size and plan allowances at `developers.cloudflare.com/kv/platform/limits/`.

### R2

- There are no egress fees, whether you read through the Workers binding, the S3 API or public `r2.dev` domains.
- You pay for storage plus a per-operation fee.
- Event notifications for object create and delete can trigger a Queue consumer.

Verify the current rates at `developers.cloudflare.com/r2/pricing/`.

### D1

Each database has a fixed size cap by design. The cap cannot be raised: the intended model is many small databases, for example one per tenant.

Billing covers:
- rows read
- rows written
- storage

There is no charge for idle compute or for bandwidth. Verify the current cap and rates at `developers.cloudflare.com/d1/platform/limits/` and `.../pricing/`.
