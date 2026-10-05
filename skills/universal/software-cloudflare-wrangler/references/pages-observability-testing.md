# Wrangler Pages Observability Testing

## Table of Contents

- [Pages (Frontend Deployment)](#pages-frontend-deployment)
- [Observability](#observability)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Pages (Frontend Deployment)

**Before reaching for Pages commands**: for new projects, Cloudflare's current default recommendation is a Worker with static assets, not Pages — it unifies frontend and backend in one deployment and covers static assets and SSR. Parity is not complete: custom domains outside Cloudflare zones are Pages-only, custom branch aliases are still in progress on Workers, and Early Hints needs a workaround — check the migration matrix for the feature you depend on. Secrets Store, Workflows, Containers, and Durable Objects remain Workers-only, so a Pages project that grows backend needs will eventually hit a wall Workers doesn't have. Existing Pages projects remain fully supported with no forced migration deadline — only migrate when adding substantial backend logic, consolidating a split frontend/backend deployment, or hitting a Pages-specific limitation. Verify current guidance at `developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/` before defaulting a new project to Pages.

```bash
# Create Pages project
wrangler pages project create my-site

# Deploy directory to Pages
wrangler pages deploy ./dist

# Deploy with specific branch
wrangler pages deploy ./dist --branch main

# List deployments
wrangler pages deployment list --project-name my-site
```

---


## Observability

### Tail Logs

```bash
# Stream live logs
wrangler tail

# Tail specific Worker
wrangler tail my-worker

# Filter by status
wrangler tail --status error

# Filter by search term
wrangler tail --search "error"

# JSON output
wrangler tail --format json
```

### Config Logging

```jsonc
{
  "observability": {
    "enabled": true,
    "head_sampling_rate": 1
  }
}
```

---


## Testing

### Local Testing with Vitest

Use `@cloudflare/vitest-plugin` and its `cloudflareTest` setup; it replaces the older `@cloudflare/vitest-pool-workers` package and its `defineWorkersConfig` config. Copy the current config snippet from `developers.cloudflare.com/workers/testing/vitest-integration/` (which also has the migration guide) rather than from older examples, and point it at the project's `wrangler.jsonc`.

### Test Scheduled Events

```bash
# Enable in dev
wrangler dev --test-scheduled

# Trigger via HTTP
curl http://localhost:8787/__scheduled
```

---


## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `command not found: wrangler` | Install: `npm install -D wrangler` |
| Auth errors | Run `wrangler login` |
| Startup time limit exceeded | Run `wrangler check startup` to profile startup and generate CPU profiles |
| Type errors after config change | Run `wrangler types` |
| Local storage not persisting | Check `.wrangler/state` directory |
| Binding undefined in Worker | Verify binding name matches config exactly |

### Debug Commands

```bash
# Check auth status
wrangler whoami

# Profile Worker startup time
wrangler check startup

# View config schema
wrangler docs configuration
```

---


## Best Practices

The deploy, secrets, types, and environment rules live in `SKILL.md` (Operating Rules, Deployment Checklist). Local secrets and resource provisioning need these additional checks:

- Use `.dev.vars` for local secrets and keep it out of version control.

### Automatic Resource Provisioning

Read the [supported products and binding fields](https://developers.cloudflare.com/workers/wrangler/configuration/#automatic-provisioning) before adding an unprovisioned binding. KV, R2 and D1 support this flow; the product list extends to services such as Queues, so check it for the selected resource rather than assuming all bindings support provisioning.

- Omit a resource ID (or R2 bucket name) to request creation. `wrangler dev` creates persistent local resources; `wrangler deploy` can create real resources prefixed by the Worker name.
- CLI deploy writes created IDs into the local config. Review that diff and preserve the resolved identity for the next deployment. Dashboard/Git-connected deployment does not write IDs back to the repository; retrieve them from the dashboard instead.
- In shared or production accounts, pre-create and explicitly bind the intended resources, and disable provisioning with `--no-x-provision` after checking the installed command's help. The [provisioning changelog](https://developers.cloudflare.com/changelog/post/2025-10-24-automatic-resource-provisioning/) documents that opt-out; verify it before treating CI as unable to create resources.

---
