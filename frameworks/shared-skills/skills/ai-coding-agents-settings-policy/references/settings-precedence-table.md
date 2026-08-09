# Settings Precedence Table

Concrete reference for the merge order of settings sources in a coding-agent runtime. The order below is highest-to-lowest precedence: a source higher in the table wins over any source below it.

## Table of Contents

- [Precedence Order (Highest → Lowest)](#precedence-order-highest--lowest)
- [Override Examples](#override-examples)
- [Rules](#rules)
- [Debugging effective settings](#debugging-effective-settings)
- [Cache invalidation per layer](#cache-invalidation-per-layer)
- [Related](#related)

## Precedence Order (Highest → Lowest)

| Layer | Source | Editable? | Override rule | Example |
|-------|--------|-----------|---------------|---------|
| **1. distro_policy** | Binary-baked manifest (Custom Distro) | No — immutable without new binary | Wins over everything; cannot be narrowed at runtime | Enterprise distro pins `provider = "anthropic"` and locks `allow_network_tools = false` |
| **2. managed_policy** | Drop-in `.json` files in a managed directory | No — operator-written | Wins over all user-controlled sources; multiple drop-ins merge by filename sort order | IT policy drops `disallow_bash = true`; user cannot re-enable it |
| **3. CLI flags** | `--flag value` on invocation | Per-invocation | Wins over file-based sources for the current process lifetime only | `--model <model-id>` overrides user's configured default |
| **4. local** | `<repo>/.agent/settings.local.json` (gitignored) | Yes — machine-local | Wins over project and user; highest-precedence editable file | Developer overrides `lsp_path` for their machine |
| **5. project** | `<repo>/.agent/settings.json` (checked in) | Yes — shared with team | Wins over user; shared across all contributors | Project pins `max_tokens = 8192` for CI consistency |
| **6. user** | `~/.config/agent/settings.json` (global user file) | Yes — user-owned | Lowest user-editable layer | User sets `theme = "dark"` globally |
| **7. defaults** | Compiled-in defaults | No — code-defined | Applied when no other source specifies a value | Default `timeout_ms = 30000` |

Verified reference point: Claude Code's own precedence is `managed > CLI flags > .claude/settings.local.json > .claude/settings.json (project) > ~/.claude/settings.json (user)` (`code.claude.com/docs/en/settings`, checked 2026-07-11). Local is the most specific file a contributor controls, so it should beat both project and user — the inverse ordering (user or project beating local) is the single most common precedence mistake in this domain; verify against current docs before trusting memory on this point.

## Override Examples

### Managed policy overrides user

```json
// managed_policy/company.json (operator-written)
{ "allow_network_tools": false }

// user settings.json (user-written)
{ "allow_network_tools": true }  ← LOSES — managed_policy wins
```

### CLI flag overrides project

```bash
# project settings.json: { "model": "<project-default-model-id>" }
claude --model <requested-model-id>   # CLI flag wins for this invocation
```

### Local overrides project for shared keys

```json
// project settings.json
{ "max_tokens": 8192 }

// local settings.local.json
{ "max_tokens": 4096 }  ← WINS — local layer wins for this key
```

Note: project only wins for keys that local does not specify. Precedence applies per-key, not per-file — if local is silent on a key, project's value (or user's, if project is also silent) takes effect.

### Distro policy cannot be widened by managed policy

```
distro_policy: { allow_plugins: false }
managed_policy: { allow_plugins: true }  ← LOSES — distro is immutable ceiling
```

### Multiple managed drop-ins merge by sort order, last wins within policy layer

```
managed_policy/00_base.json:    { "timeout_ms": 10000 }
managed_policy/10_security.json: { "timeout_ms": 5000 }   ← wins (sorts later)
managed_policy/20_team.json:    { "allow_bash": false }    ← additive
```

Effective: `{ "timeout_ms": 5000, "allow_bash": false }`

## Rules

- Precedence is **per-key**: for each setting key, find the highest layer that specifies it and use that value.
- CLI flags are **transient**: they apply for the current process only and are not written back to any file.
- Managed policy is **source-aware**: the merge engine must track which layer set each key so the effective-settings debug view can explain "why can't I change this."
- Distro policy is a **ceiling**, not a floor: managed policy can only narrow within the distro envelope.
- **Plugin-only restrictions** are an additional axis: see [`plugin-only-restriction-recipes.md`](plugin-only-restriction-recipes.md).
- **ToolSearch gating** is a policy-layer concern: see [`deferred-tool-policy-layer.md`](deferred-tool-policy-layer.md).

## Debugging effective settings

A well-built effective-settings view must show:

```
Key:          allow_bash
Effective:    false
Won by:       managed_policy/10_security.json
Overrode:     user (true), project (unset), local (unset)
```

Without source attribution, operators cannot explain constraint sources to users. "It's locked by policy" with no file path is not acceptable in production runtimes.

## Cache invalidation per layer

| Layer changed | What to invalidate |
|---------------|--------------------|
| distro_policy | Full settings cache (restart required in most runtimes) |
| managed_policy drop-in added/removed | managed-policy cache + merged cache |
| CLI flag change | Merged cache only (flags are not persisted) |
| user file | user-layer cache + merged cache |
| project file | project-layer cache + merged cache |
| local file | local-layer cache + merged cache |

Never invalidate all caches for a single-file change. Targeted invalidation is required for correct reload sequencing.

## Related

- [`settings-source-precedence-and-managed-policy.md`](settings-source-precedence-and-managed-policy.md) — Source model and managed policy architecture
- [`plugin-only-restriction-recipes.md`](plugin-only-restriction-recipes.md) — Which sources can enable plugin surfaces
- [`deferred-tool-policy-layer.md`](deferred-tool-policy-layer.md) — How ToolSearch trigger is settings-gated
- [`settings-validation-and-safe-runtime-application.md`](settings-validation-and-safe-runtime-application.md) — Validation and runtime application
