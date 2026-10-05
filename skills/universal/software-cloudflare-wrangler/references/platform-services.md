# Wrangler Platform Services

Command syntax for these services changes often and is documented upstream. Get it from `wrangler <group> --help` and the linked docs rather than from this file. This file keeps the judgment calls, limits and safety notes that the command reference leaves out.

## Table of Contents

- [Command Groups](#command-groups)
- [Hyperdrive](#hyperdrive)
- [Workers AI](#workers-ai)
- [Containers](#containers)
- [Workflows](#workflows)
- [Pipelines](#pipelines)
- [Secrets Store](#secrets-store)

## Command Groups

| Service | Command group | Binding key in `wrangler.jsonc` | Docs |
|---------|---------------|--------------------------------|------|
| Vectorize | `wrangler vectorize --help` | `vectorize` | `developers.cloudflare.com/vectorize/` |
| Hyperdrive | `wrangler hyperdrive --help` | `hyperdrive` | `developers.cloudflare.com/hyperdrive/` |
| Workers AI | `wrangler ai --help` | `ai` | `developers.cloudflare.com/workers-ai/` |
| Queues | `wrangler queues --help` | `queues.producers` / `queues.consumers` | `developers.cloudflare.com/queues/` |
| Containers | `wrangler containers --help` | `containers` + Durable Object class | `developers.cloudflare.com/containers/` |
| Workflows | `wrangler workflows --help` | `workflows` | `developers.cloudflare.com/workflows/` |
| Pipelines | `wrangler pipelines --help` | `pipelines` | `developers.cloudflare.com/pipelines/` |
| Secrets Store | `wrangler secrets-store --help` | `secrets_store_secrets` | `developers.cloudflare.com/secrets-store/` |

For binding field names, trust `node_modules/wrangler/config-schema.json` over any example you remember. After you add a binding, run `wrangler types`.

For Vectorize presets, look up the current preset names with `wrangler vectorize create --help`. Do not hardcode an embedding-model version.

## Hyperdrive

Hyperdrive is a connector, not a database. Use it when a Worker has to reach an existing Postgres or MySQL instance: it adds connection pooling and query caching on the hot path. If you do not yet have an external database and the data shards naturally per tenant, look at D1 first; see the storage table in `references/storage-and-data.md`.

**Credential exposure warning:** `--origin-password "$DB_PASSWORD"` and `--connection-string "$URL"` look safe because the value lives in an environment variable. It is not safe: the shell expands the variable into the process arguments, where process listings can see it, and CI logs record it if shell tracing (`set -x`) is on. Run these commands from a trusted machine or a masked CI step with tracing off, and rotate the database password if it leaks. Check the current `wrangler hyperdrive create --help` output to see whether it can prompt for the password instead.

Hyperdrive configs that use database drivers normally need `nodejs_compat`. Recent compatibility dates turn it on by default; check the threshold as described in `references/configuration.md`.

## Workers AI

Workers AI always runs remotely. It incurs usage charges even in local dev; see `references/local-development-and-deployment.md`.

Pick models by capability tier from the current catalogue (`wrangler ai models`). Do not pin a model-version string in guidance, because the lineup changes faster than this skill is reviewed. Route calls through AI Gateway when you need caching, rate limiting, retries or cost analytics. Verify current Gateway capabilities at `developers.cloudflare.com/ai-gateway/`.

## Containers

Look up Containers release status and plan eligibility in the docs before selecting it.

**Billing:**
- CPU is billed on active usage only.
- Memory and disk are billed on the resources you provision, whether or not you use them.

Do not describe Containers as "billed only for cycles consumed".

**When to use them:**
- Long-running or CPU-bound jobs that exceed the Workers CPU ceiling.
- Workloads that need a full Linux filesystem or process model.
- Arbitrary native binaries or CLI tools.

GPU availability is not stated on the pricing page. Treat it as unverified until the current docs say otherwise.

Containers are real sandboxed VMs or processes, and cold starts are measurable. Do not promise Workers-style near-zero cold starts for a Containers-based feature.

Never put registry credentials directly in a command. Pass them through masked environment variables, and apply the same argv caution as for Hyperdrive.

Verify current regions, instance types and pricing at `developers.cloudflare.com/containers/`.

## Workflows

**Billing and limits:** Workflows pricing includes compute, invocations, steps and stored state; check which charges are currently enforced. Workflows caps steps per instance, `step.sleep` duration, and event-payload and step-result size. Look up current allowances, rates and caps at `developers.cloudflare.com/workflows/reference/pricing/` and `.../reference/limits/` before sizing a design.

**Design notes:**
- Keep large data in R2 and pass references between steps.
- Make each step idempotent, because steps retry.

For cross-platform durable-execution choices, see `../software-workflow-automation/SKILL.md`.

## Pipelines

Check Pipelines' current release status in the docs before committing production data to it. It has three parts:

- **Streams** ingest events.
- **Pipelines** transform them with SQL.
- **Sinks** write the results to R2 or R2 Data Catalog (Iceberg). Verify the current sink types before relying on them.

Start with the guided `npx wrangler pipelines setup`. The older single-command `wrangler pipelines create <name> --r2 <bucket>` flow belongs to the legacy model, so do not copy it from older examples. Check the current subcommands with `wrangler pipelines --help` and `developers.cloudflare.com/pipelines/`.

## Secrets Store

The Secrets Store holds secrets at account level and shares them across Workers. Per-Worker `wrangler secret put` stays the default for secrets that one Worker owns.

Use `wrangler secrets-store secret create <STORE-ID> --name <NAME> --scopes workers` and the interactive value prompt. Add `--remote` only after resolving the production store; without it the command targets local development. Do not use the `--value` flag for real secrets because it exposes the value in argv/history. Verify flags in [Secrets Store commands](https://developers.cloudflare.com/workers/wrangler/commands/secrets-store/).
