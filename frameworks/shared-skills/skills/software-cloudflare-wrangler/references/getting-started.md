# Wrangler Getting Started

## Table of Contents

- [Retrieval Sources](#retrieval-sources)
- [FIRST: Check if Wrangler is installed, and if not, install it](#first-check-if-wrangler-is-installed-and-if-not-install-it)
- [Key Guidelines](#key-guidelines)
- [Quick Start: New Worker](#quick-start-new-worker)
- [Quick Reference: Core Commands](#quick-reference-core-commands)

## Retrieval Sources

Fetch the **latest** information before writing or reviewing Wrangler commands and config. Do not rely on baked-in knowledge for CLI flags, config fields, or binding shapes.

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Wrangler docs | `https://developers.cloudflare.com/workers/wrangler/` | CLI commands, flags, config reference |
| Wrangler config schema | `node_modules/wrangler/config-schema.json` | Config fields, binding shapes, allowed values |
| Cloudflare docs | Search tool or `https://developers.cloudflare.com/workers/` | API reference, compatibility dates/flags |


## FIRST: Check if Wrangler is installed, and if not, install it

Check if Wrangler is installed by running:

```bash
wrangler --version  # v4.x is current (e.g. 4.110 as of 2026-07); v3 and earlier are unsupported/legacy
```

If Wrangler is not installed, you should install it by running:

```bash
npm install -D wrangler@latest
```

Wherever possible, you should use Wrangler instead of manually constructing API requests.

Wrangler v4 changed several defaults from v3 — expect these if a project or its docs predate the migration:
- KV/R2/D1 commands default to **local** mode; add `--remote` explicitly to read/write the live resource (a bare `wrangler kv key get` after a v3→v4 upgrade silently reads local simulated storage, not production).
- Node.js 16 and legacy Node.js compat modes are unsupported; `getBindingsProxy()` and the `usage_model` config field are removed.
- Re-verify against `developers.cloudflare.com/workers/wrangler/migration/update-v3-to-v4/` before assuming any v3-era flag still works.

## Workers Platform Limits (verify before quoting)

These move with Cloudflare pricing/limits revisions — treat every number below as provisional and re-check `developers.cloudflare.com/workers/platform/limits/` and `.../pricing/` before it drives a capacity or cost decision.

| Limit | Free | Paid |
|-------|------|------|
| CPU time per request | 10ms | 30s default, configurable up to 5 min (`limits.cpu_ms`) |
| Memory per isolate | 128MB | 128MB |
| Subrequests per invocation | 50 external (+1,000 to Cloudflare services) | 10,000 default, configurable up to 10M |
| Bundle size (compressed) | 3MB | 10MB |
| Startup time (global scope) | 1s | 1s |

Waiting on network I/O (fetch, KV/D1/DO calls) does not consume CPU time — only active computation does. A Worker that looks like it's hitting the CPU ceiling is usually doing real synchronous work (parsing, crypto, large JSON), not blocked on I/O.


## Key Guidelines

- **Use `wrangler.jsonc`**: Prefer JSON config over TOML. Newer features are JSON-only.
- **Set `compatibility_date`**: Use a recent date (within 30 days). Check https://developers.cloudflare.com/workers/configuration/compatibility-dates/
- **Generate types after config changes**: Run `wrangler types` to update TypeScript bindings.
- **Local dev defaults to local storage**: Bindings use local simulation unless `remote: true`.
- **Profile Worker startup**: Run `wrangler check startup` to measure startup time and detect scripts that exceed the startup time limit.
- **Use environments for staging/prod**: Define `env.staging` and `env.production` in config.


## Quick Start: New Worker

```bash
# Initialize new project
npx wrangler init my-worker

# Or with a framework
npx create-cloudflare@latest my-app
```


## Quick Reference: Core Commands

| Task | Command |
|------|---------|
| Start local dev server | `wrangler dev` |
| Deploy to Cloudflare | `wrangler deploy` |
| Deploy dry run | `wrangler deploy --dry-run` |
| Generate TypeScript types | `wrangler types` |
| Profile Worker startup time | `wrangler check startup` |
| View live logs | `wrangler tail` |
| Delete Worker | `wrangler delete` |
| Auth status | `wrangler whoami` |

---
