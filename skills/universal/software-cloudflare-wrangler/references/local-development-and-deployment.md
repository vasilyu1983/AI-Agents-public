# Wrangler Local Development And Deployment

## Table of Contents

- [Local Development](#local-development)
- [Deployment](#deployment)

## Local Development

### Start Dev Server

```bash
# Local mode (default) - uses local storage simulation
wrangler dev

# With specific environment
wrangler dev --env staging

# Force local-only (disable remote bindings)
wrangler dev --local

# Remote mode - runs on Cloudflare edge (legacy; local dev with per-binding `remote: true` is the current default pattern)
wrangler dev --remote

# Custom port
wrangler dev --port 8787

# Live reload for HTML changes
wrangler dev --live-reload

# Test scheduled/cron handlers
wrangler dev --test-scheduled
# Then visit: http://localhost:8787/__scheduled
```

### Remote Bindings for Local Dev

Use `remote: true` in binding config to connect to real resources while running locally:

```jsonc
{
  "r2_buckets": [
    { "binding": "BUCKET", "bucket_name": "my-bucket", "remote": true }
  ],
  "ai": { "binding": "AI", "remote": true },
  "vectorize": [
    { "binding": "INDEX", "index_name": "my-index", "remote": true }
  ]
}
```

Workers AI runs remotely. For Vectorize, Browser Run (formerly Browser Rendering), mTLS and Images, check the [development-mode binding matrix](https://developers.cloudflare.com/workers/development-testing/bindings-per-env/) before setting `remote: true`. Browser Run uses a real browser through a remote binding; see its [Wrangler guide](https://developers.cloudflare.com/browser-run/reference/wrangler/).

### Local Secrets

Create `.dev.vars` for local development secrets:

```
API_KEY=local-dev-key
DATABASE_URL=postgres://localhost:5432/dev
```

---


## Deployment

### Deploy Worker

```bash
# Deploy to production
wrangler deploy

# Deploy specific environment
wrangler deploy --env staging

# Dry run (validate without deploying)
wrangler deploy --dry-run

# Keep dashboard-set variables
wrangler deploy --keep-vars

# Minify code
wrangler deploy --minify
```

### Branch Previews and CI

[Worker Previews](https://developers.cloudflare.com/workers/previews/) requires a project Wrangler dependency of at least 4.135.0; check the installed project's version and current support before changing CI. A newer global installation does not satisfy the project dependency.

1. Define branch variables, secrets and bindings under `previews` using the [setup guide](https://developers.cloudflare.com/workers/previews/get-started/).
2. Run `npx wrangler preview` locally or in CI. It creates or updates a Preview named from the current Git branch; use `--name <PREVIEW_NAME>` when CI needs an explicit name.
3. Test the returned Preview URL and retain the unique deployment URL with the tested commit. Use `wrangler deploy` for the production deployment.
4. Inspect [resource isolation](https://developers.cloudflare.com/workers/previews/resources/) before tests write data: explicitly bound D1/KV/R2 resources can be shared, and a Preview service binding can still call another Worker's production service. A branch URL alone does not prove data isolation.

### Manage Secrets

> **Security**: Never pass secret values as command arguments or pipe them via `echo`.
> Use the interactive prompt (preferred), pipe from a file, or use `secret bulk`.
> Never output, log, or hardcode secret values in commands.

```bash
# Set secret — interactive prompt (preferred, wrangler will ask for the value securely)
wrangler secret put API_KEY

# Set secret from a file (useful for PEM keys, CI environments)
wrangler secret put PRIVATE_KEY < path/to/private-key.pem

# List secrets
wrangler secret list

# Delete secret
wrangler secret delete API_KEY

# Bulk secrets from JSON file (do not commit this file to version control)
wrangler secret bulk secrets.json
```

### Versions and Rollback

```bash
# List recent versions
wrangler versions list

# View specific version
wrangler versions view <VERSION_ID>

# Rollback to previous version
wrangler rollback

# Rollback to specific version
wrangler rollback <VERSION_ID>
```

---
