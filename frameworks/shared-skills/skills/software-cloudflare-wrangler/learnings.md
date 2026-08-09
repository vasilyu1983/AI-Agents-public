# software-cloudflare-wrangler — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-06-05] A complete `wrangler deploy` prints `Uploaded <name> (Ns)` then `Deployed <name> triggers` then `Current Version ID:`; a lone `Deployed triggers` (no `Uploaded`) = partial deploy: script never shipped, routes 404 on stale version. Re-run.
- [2026-06-05] Cloudflare Pages bindings added in the dashboard snapshot per-deployment and do NOT attach to the live one — after adding a D1/KV binding you must redeploy for env.<BINDING> to be defined; set it on the Production tab, name matched exactly.
- [2026-05-31] Top-level `vars` in wrangler.toml are NOT inherited by `env.<name>.vars`: a var declared only at top level goes missing under `--env staging/production` and wrangler warns at deploy — redeclare each var inside every env block.
## Domain Knowledge

- [2026-06-05] `wrangler d1 list` num_tables is cached metadata that lags writes minutes (reads 0 right after a good `migrations apply --remote`); authoritative check is a `d1 execute --remote` SELECT on sqlite_master — trust sqlite_master over d1 list.
- [2026-07-11] SQLite-backed storage is now the default for new Durable Object classes, but a binding alone does not create the class — every new DO class still needs an explicit `migrations` entry (`new_sqlite_classes`) in `wrangler.jsonc`, or the binding fails at deploy/runtime with no code-level error to point at it.
## Open Questions

## Consolidated Principles

