---
name: software-cloudflare-wrangler
description: "Guides Cloudflare Wrangler CLI usage for Workers, bindings, deploys, local dev, and config. Use when running or reviewing wrangler commands."
version: "1.1"
last_validated: 2026-07-11
---

# Wrangler CLI

Your knowledge of Wrangler CLI flags, config fields, and subcommands may be outdated. **Prefer retrieval over pre-training** for any Wrangler task.

## Quick Reference

| Task | Read or Run | Outcome |
|------|-------------|---------|
| Check install/version and core commands | `references/getting-started.md` | Current Wrangler source, install, and command basics |
| Edit config or bindings | `references/configuration.md` | `wrangler.jsonc` shape and generated types |
| Run locally or deploy safely | `references/local-development-and-deployment.md` | Dev modes, remote bindings, dry runs, secrets, rollbacks |
| Manage storage/data resources | `references/storage-and-data.md` | KV, R2, and D1 commands/config |
| Manage Cloudflare platform services | `references/platform-services.md` | Vectorize, Hyperdrive, Workers AI, Queues, Containers, Workflows, Pipelines, Secrets Store |
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
| Install/version check, retrieval sources, core commands | `references/getting-started.md` |
| `wrangler.jsonc`, bindings, environments, generated types | `references/configuration.md` |
| Local dev, remote bindings, deploys, secrets, rollbacks | `references/local-development-and-deployment.md` |
| KV, R2, and D1 commands/config | `references/storage-and-data.md` |
| Vectorize, Hyperdrive, Workers AI, Queues, Containers, Workflows, Pipelines, Secrets Store | `references/platform-services.md` |
| Pages, logs, tests, troubleshooting, best practices | `references/pages-observability-testing.md` |

## Fact-Checking

- Treat Cloudflare docs and the local Wrangler schema as authoritative.
- Re-check flags, binding shapes, compatibility dates, and newly released products before quoting exact syntax.
- Mark any command unverified if docs or schema cannot be retrieved.
- Treat every specific number in this skill (CPU-ms, MB, GB, $/unit, row counts) as a snapshot that can move between Cloudflare pricing revisions — re-verify at the cited `developers.cloudflare.com/<product>/platform/limits/` or `.../pricing/` page before it drives a customer-facing estimate or a hard architectural commitment.
- Wrangler itself ships weekly-ish minor/patch releases (v4.x line, e.g. v4.110 as of 2026-07); re-run `wrangler --version` and `npm view wrangler version` rather than assuming a specific patch is current. There is no wrangler v5 as of this writing — verify at `developers.cloudflare.com/workers/wrangler/`.

## Expert Judgment

Apply this judgment before reaching for a command — a syntactically correct `wrangler` invocation on the wrong primitive is still the wrong answer.

**When *not* to reach for Workers at all**
- Jobs that run longer than the CPU-time ceiling (10ms/request on Free; up to 5 minutes/request on Paid, configurable via `limits.cpu_ms` — verify at `developers.cloudflare.com/workers/platform/limits/`) belong in Containers, Queues consumers with checkpointing, or an external batch system — don't fight the limit with busy-loops or artificial chunking that fragments one logical job across many invocations.
- Payloads or working sets that approach or exceed the 128MB isolate memory ceiling (same on Free and Paid) need Containers, R2 streaming, or an external compute tier — Workers isolates are not a general-purpose memory-heavy runtime.
- Anything that needs a persistent local filesystem, native binaries, GPUs, or a full Linux process model is a Containers workload, not a Worker — Containers reached GA in 2026 with active-CPU pricing (billed for cycles actually consumed, not wall-clock) but they are a genuinely different compute model with real cold starts, unlike Worker isolates. Verify current GA scope and pricing at `developers.cloudflare.com/containers/`.

**Cold-start reality, not folklore**
- V8 isolates (Workers) start in low single-digit milliseconds and are effectively "no cold start" for request-serving traffic — that is the architectural reason to prefer a Worker over a container when the workload fits.
- Containers/Sandboxes are real VMs/processes underneath; they have measurable cold-start and warm-pool considerations even at GA. Don't sell Containers with the same latency story as Workers.

**Durable Objects: single point of serialization**
- Every DO id maps to exactly one instance with single-threaded, serialized execution — it is a strongly-consistent bottleneck by design, not an accident. A single "global" DO id fronting all traffic for a feature will cap that feature's throughput; shard by user/tenant/room/document id instead, and only route to one global DO for state that genuinely must be totally ordered (e.g., a single counter or lock).
- SQLite-backed storage is the default for new DO classes and is the one to reach for; verify at `developers.cloudflare.com/durable-objects/what-are-durable-objects/` before assuming legacy key-value-only storage. New classes still need an explicit migration entry (e.g., `new_sqlite_classes`) in config — DOs do not exist until a migration creates the class.
- DO compute is billed on wall-clock GB-seconds while an instance is active or idle-but-non-hibernating, plus per-request charges; SQLite storage billing (rows read/written, GB stored) mirrors D1's pricing. Verify current thresholds at `developers.cloudflare.com/durable-objects/platform/pricing/` — these numbers have moved at least once (SQLite storage billing itself only started being enforced in Jan 2026) and will move again.

**KV vs D1 vs Durable Objects — pick by consistency and access shape, not by familiarity**
| Need | Reach for |
|------|-----------|
| Read-heavy, eventually-consistent, small values (config, feature flags, cached HTML) | KV — cheap reads, ~60s global propagation, weak consistency is a feature here |
| Relational data, per-tenant/per-user SQL, joins within one ~10GB shard | D1 — verify the current per-database size cap at `developers.cloudflare.com/d1/platform/limits/`; D1 is designed for horizontal fan-out across many small databases, not one large one |
| Strongly consistent, low-latency coordination or per-entity state (WebSocket room, single-writer document, rate limiter, in-memory-then-flush aggregation) | Durable Objects |
| Large binary objects, user uploads, static/media assets | R2 — no egress fee, S3-compatible API |

**D1 vs external Postgres/MySQL** — pick D1 when the data naturally partitions per-tenant/per-user and stays under the current per-database size cap with modest write volume. Reach for Hyperdrive-fronted Postgres/MySQL when you need cross-tenant joins, complex analytical queries, existing relational infrastructure, or write volume/size that would require sharding D1 artificially just to fit the cap.

**Pages vs Workers** — for new projects, Cloudflare has converged the two: a Worker with static assets is the current recommended starting point (single deployment for frontend + backend, full feature parity with Pages for static assets/SSR/custom domains as of 2026). Existing Pages projects remain fully supported with no forced migration deadline — migrate opportunistically when adding substantial backend logic or hitting a Pages-only limitation. Verify current guidance at `developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/`.

## Operating Rules

- Use `wrangler.jsonc` unless the project already standardizes on another supported config format.
- Run `wrangler types` after config or binding changes when the project uses TypeScript.
- Use `wrangler deploy --dry-run` or the safest available validation before production deploys.
- Prefer Wrangler commands over manually constructed Cloudflare API requests when Wrangler supports the operation.
- Never echo secrets; use `wrangler secret put` or equivalent secure project flow.

## Deployment Checklist

Before deploying to production:

- [ ] `wrangler deploy --dry-run` passes without errors
- [ ] `wrangler types` run and generated types committed (TypeScript projects)
- [ ] All binding names in `wrangler.jsonc` match the names used in Worker code
- [ ] Secrets set via `wrangler secret put` — not embedded in config or code
- [ ] Compatibility date set explicitly; no unintended compatibility flag changes
- [ ] Environment-specific config (`[env.production]`) verified separately from staging

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
