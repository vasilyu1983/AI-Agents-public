---
name: software-cloudflare-wrangler
description: "Guides Cloudflare Wrangler CLI usage for Workers, bindings, deploys, local dev, and config. Use when running or reviewing wrangler commands."
version: "1.1"
last_validated: 2026-07-11
---

# Wrangler CLI

Scope: CLI usage, config, and deploy safety. Workers code review belongs to `workers-best-practices` when installed; platform choice (Cloudflare vs other hosts) belongs to `../software-paas-hosting/SKILL.md`. References keep judgment and gates; full command syntax comes from `wrangler <cmd> --help` and the Cloudflare docs.

## Quick Reference

| Task | Read or Run | Outcome |
|------|-------------|---------|
| Check install/version and core commands | `references/getting-started.md` | Current Wrangler source, install, and command basics |
| Edit config or bindings | `references/configuration.md` | `wrangler.jsonc` shape and generated types |
| Run locally or deploy safely | `references/local-development-and-deployment.md` | Dev modes, remote bindings, dry runs, secrets, rollbacks |
| Manage storage/data resources | `references/storage-and-data.md` | KV, R2, and D1 command groups, remote/local safety, limits notes |
| Manage Cloudflare platform services | `references/platform-services.md` | Command groups plus judgment for Hyperdrive, Workers AI, Containers, Workflows, Pipelines, Secrets Store |
| Debug, observe, test, or deploy Pages | `references/pages-observability-testing.md` | Pages, logs, tests, troubleshooting, best practices |

## Workflow

1. Check the installed Wrangler version or project dependency before writing commands.
2. Retrieve current Cloudflare docs or the local `node_modules/wrangler/config-schema.json` for flags, config fields, and binding shapes.
3. Choose the smallest relevant reference below and verify syntax against docs/schema before running commands.
4. Prefer `wrangler.jsonc`, generate types after binding/config edits, and validate with local dev, dry-run deploy, or the safest available project check.
5. Surface any command that can mutate production resources before running it.

## Navigation

| Need | Read |
|------|------|
| Install/version check, retrieval sources, core commands | [references/getting-started.md](references/getting-started.md) |
| `wrangler.jsonc`, bindings, environments, generated types | [references/configuration.md](references/configuration.md) |
| Local dev, remote bindings, deploys, secrets, rollbacks | [references/local-development-and-deployment.md](references/local-development-and-deployment.md) |
| KV, R2, and D1 command groups and safety | [references/storage-and-data.md](references/storage-and-data.md) |
| Vectorize, Hyperdrive, Workers AI, Queues, Containers, Workflows, Pipelines, Secrets Store | [references/platform-services.md](references/platform-services.md) |
| Pages, logs, tests, troubleshooting, best practices | [references/pages-observability-testing.md](references/pages-observability-testing.md) |

## Expert Judgment

Apply this judgment before reaching for a command — a syntactically correct `wrangler` invocation on the wrong primitive is still the wrong answer.

**When *not* to reach for Workers at all**
- Jobs that exceed the request CPU budget (look up the plan ceiling and `limits.cpu_ms` at [Workers limits](https://developers.cloudflare.com/workers/platform/limits/)) belong in Containers, Queues consumers with checkpointing, or an external batch system — don't fight the limit with busy-loops or artificial chunking that fragments one logical job across many invocations.
- Payloads or working sets that approach the isolate memory ceiling (look up [Workers limits](https://developers.cloudflare.com/workers/platform/limits/)) need Containers, R2 streaming, or an external compute tier — Workers isolates are not a general-purpose memory-heavy runtime.
- Anything that needs a persistent local filesystem, native binaries, or a full Linux process model is a Containers workload, not a Worker. For Containers plan eligibility, release status, GPU support and billing units, check [Containers docs](https://developers.cloudflare.com/containers/) before committing to a design; startup and provisioned memory/disk affect its cost.

**Cold-start reality, not folklore**
- V8 isolates avoid provisioning a separate process for each request. Measure startup and first-request latency for the actual bundle; do not promise a fixed cold-start time.
- Containers/Sandboxes have process startup and warm-pool considerations. Don't sell Containers with the same latency story as Workers.

**Durable Objects: single point of serialization**
- Each DO id addresses one active instance with single-threaded JavaScript and strongly consistent storage. Requests can interleave across non-storage `await`s; do not treat an entire async handler as serialized. See [Durable Object concurrency rules](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/). A single "global" DO id fronting all traffic for a feature will cap that feature's throughput; shard by user/tenant/room/document id instead, and only route to one global DO for state that genuinely must be totally ordered (e.g., a single counter or lock).
- SQLite-backed storage is the default for new DO classes and is the one to reach for; verify at `developers.cloudflare.com/durable-objects/what-are-durable-objects/` before assuming legacy key-value-only storage. New classes still need an explicit migration entry (e.g., `new_sqlite_classes`) in config — DOs do not exist until a migration creates the class.
- For DO cost, separate request/duration charges from SQLite rows and stored data; hibernation changes duration usage. Look up billed units, allowances and storage charges at [Durable Objects pricing](https://developers.cloudflare.com/durable-objects/platform/pricing/) before estimating cost; do not reuse D1 rates.

**KV vs D1 vs Durable Objects — pick by consistency and access shape, not by familiarity**
| Need | Reach for |
|------|-----------|
| Read-heavy, eventually-consistent, small values (config, feature flags, cached HTML) | KV — eventually consistent; look up [propagation and cache behavior](https://developers.cloudflare.com/kv/concepts/how-kv-works/) before choosing it for a correctness-sensitive read |
| Relational data, per-tenant/per-user SQL, joins within one bounded database | D1 — verify the current per-database size cap at `developers.cloudflare.com/d1/platform/limits/`; D1 is designed for horizontal fan-out across many small databases, not one large one |
| Tenant-local SQL plus coordination or WebSocket state, with no cross-tenant joins | SQLite-backed DO per tenant — derive the object id from the authenticated tenant; use `new_sqlite_classes` for its class migration and check [DO storage limits](https://developers.cloudflare.com/durable-objects/platform/limits/) |
| Strongly consistent, low-latency coordination or per-entity state (WebSocket room, single-writer document, rate limiter, in-memory-then-flush aggregation) | Durable Objects |
| Large binary objects, user uploads, static/media assets | R2 — S3-compatible API; read [storage, operation and transfer pricing](https://developers.cloudflare.com/r2/pricing/) before estimating cost |

**D1 vs external Postgres/MySQL** — pick D1 when the data naturally partitions per-tenant/per-user and stays under the per-database size cap (see the D1 row above for the verify link) with modest write volume. Reach for Hyperdrive-fronted Postgres/MySQL when you need cross-tenant joins, complex analytical queries, existing relational infrastructure, or write volume/size that would require sharding D1 artificially just to fit the cap.

**Pages vs Workers** — for new projects, Cloudflare has converged the two: a Worker with static assets is the recommended starting point (single deployment for frontend + backend, covering static assets and SSR). Parity is not complete — e.g. custom domains outside Cloudflare zones are Pages-only and Early Hints needs a workaround — so check the migration guide's compatibility list before moving a project. Existing Pages projects remain fully supported with no forced migration deadline — migrate opportunistically when adding substantial backend logic or hitting a Pages-only limitation. Verify current guidance at `developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/`.

## Operating Rules

**Environment identity gate.**

Before any remote mutation, resolve the effective config and state the account, Worker or Pages project, environment, database or namespace binding, and route being targeted. After deploy, verify the returned version or deployment identifier and exercise the bound resource through that deployed environment. A successful CLI exit proves the command completed; it does not prove the intended environment received the intended artifact — a complete `wrangler deploy` prints `Uploaded <name>`, `Deployed <name> triggers`, and `Current Version ID`; `Deployed triggers` without `Uploaded` means the script never shipped. For staged rollouts use `wrangler versions upload` then `wrangler versions deploy`.

- Use `wrangler.jsonc` unless the project already standardizes on another supported config format.
- Run `wrangler types` after config or binding changes when the project uses TypeScript.
- Use `wrangler deploy --dry-run` or the safest available validation before production deploys.
- Prefer Wrangler commands over manually constructed Cloudflare API requests when Wrangler supports the operation.
- Never echo secrets; use `wrangler secret put` or equivalent secure project flow.

- Treat Cloudflare docs and the local Wrangler schema as authoritative.
- Re-check flags, binding shapes, compatibility dates, and newly released products before quoting exact syntax.
- Wrangler ships frequent minor/patch releases; check the current major and patch with `npm view wrangler version` rather than assuming one. Check the Wrangler changelog before relying on a newly announced command or flag.

## Deployment Checklist

Before deploying to production:

- [ ] `wrangler deploy --dry-run` passes without errors
- [ ] `wrangler types` run and generated types committed (TypeScript projects)
- [ ] All binding names in `wrangler.jsonc` match the names used in Worker code
- [ ] Secrets set via `wrangler secret put` — not embedded in config or code
- [ ] Compatibility date set explicitly and bumped only deliberately (recent dates turn `nodejs_compat` on by default — check the threshold on the compatibility-flags page; see `references/configuration.md`)
- [ ] Environment-specific config (`[env.production]`) verified separately from staging

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
