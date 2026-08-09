# GitHub Copilot CLI Plugin Manifest And Marketplace

Source: `docs.github.com/en/copilot/concepts/agents/copilot-cli/about-cli-plugins`, `docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference`, and `docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-finding-installing` (verified 2026-07-11). Copilot CLI reached general availability 2026-02-27; enterprise-managed plugins entered public preview 2026-05-06.

## Table of Contents

- [Design Goal](#design-goal)
- [Manifest Shape](#manifest-shape)
- [Component Path Fields](#component-path-fields)
- [Marketplace Manifest](#marketplace-manifest)
- [Install Sources](#install-sources)
- [Cross-Runtime Convergence](#cross-runtime-convergence)
- [Traps](#traps)

## Design Goal

Copilot CLI plugins package the same capability shape as other terminal coding agents: agents, skills, hooks, MCP servers, and LSP servers, discovered from a manifest rather than by executing plugin code.

## Manifest Shape

A plugin is a directory containing a `plugin.json` manifest at its root. The loader checks these locations in order and uses the first one found:

1. `.plugin/plugin.json`
2. `plugin.json`
3. `.github/plugin/plugin.json`
4. `.claude-plugin/plugin.json`

**Required field**: `name` — kebab-case, letters/numbers/hyphens only, max 64 characters.

**Metadata fields**: `description` (max 1024 chars), `version` (semver), `author` (`{name, email, url}`, name required), `homepage`, `repository`, `license`, `keywords`, `category`, `tags`.

## Component Path Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `agents` | string\|array | `agents/` | `*.agent.md` files |
| `skills` | string\|array | `skills/` | directories containing `SKILL.md` |
| `commands` | string\|array | — | command directories |
| `hooks` | string\|object | — | `hooks.json` path or inline config |
| `extensions` | string\|array\|object | — | supports `{ paths: [...], exclusive: true }` |
| `mcpServers` | string\|object | — | `.mcp.json`/`mcp.json` path or inline |
| `lspServers` | string\|object | — | `lsp.json` path or inline |

LSP server entries require at least one of `command`, `bash`, or `powershell` (platform-specific launch scripts) plus a required `fileExtensions` map. Optional: `cwd` (supports `${PLUGIN_ROOT}`), `args`, `env`, `rootUri`, `initializationOptions`.

## Marketplace Manifest

A marketplace is a `marketplace.json` file (checked at the same four candidate locations, mirroring the plugin manifest search order) with required top-level `name` (kebab-case, max 64 chars), required `owner` (`{name, email?}`), and a required `plugins` array. Each plugin entry carries its own metadata plus a required `source` (relative path, GitHub reference, or URL) and an optional `strict` flag (default `true`) controlling validation strictness for that entry.

Copilot CLI registers two marketplaces by default: `copilot-plugins` and `awesome-copilot`.

## Install Sources

`copilot plugin install` (or the `/plugin install` slash command) accepts:

| Form | Example | Resolution |
|------|---------|------------|
| Marketplace | `plugin@marketplace` | registered marketplace catalog |
| GitHub repo | `OWNER/REPO` | repository root |
| GitHub subdirectory | `OWNER/REPO:PATH/TO/PLUGIN` | specific directory in repo |
| Git URL | `https://github.com/o/r.git` | any Git-compatible host |
| Local path | `./my-plugin` | filesystem directory |

Declarative installs are also supported: list plugins under `enabledPlugins` in configuration rather than issuing an imperative install command. Enterprise-managed plugins (public preview since 2026-05-06) let an organization push required plugins to Copilot CLI users the same way, without user opt-in.

## Cross-Runtime Convergence

Copilot CLI's manifest loader explicitly falls back to `.claude-plugin/plugin.json` if none of its own three preferred locations exist. That is a deliberate interoperability decision, not an accident: a plugin authored for Claude Code (manifest at `.claude-plugin/plugin.json`, with `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`) loads as-is under Copilot CLI. The two schemas share nearly identical field names (`name`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`, `skills`, `agents`, `hooks`, `mcpServers`, `lspServers`) and both tolerate unrecognized fields rather than rejecting the manifest.

**Design implication for a new coding-agent runtime**: treat `.claude-plugin/plugin.json` and `plugin.json` component conventions (`skills/<name>/SKILL.md`, `agents/*.md`, `.mcp.json`) as the de facto cross-vendor baseline as of mid-2026. A new host that wants day-one access to the existing plugin ecosystem should check for that manifest shape rather than inventing a parallel one — Copilot CLI's own maintainers made that call. This does not mean the schemas are identical forever; re-verify field-for-field compatibility before promising authors "write once, run on both hosts," since capability-specific fields (Copilot's `extensions` block with `exclusive`, Claude Code's `experimental.themes`/`experimental.monitors`, `channels`) do not have a counterpart on the other host and will be silently dropped or ignored there.

## Traps

- Assuming a Claude Code plugin "just works" on Copilot CLI because the manifest loads — capability-specific fields with no counterpart on the other host are silently ignored, not migrated or warned about.
- Treating the marketplace's registered short name as identical to the source repository name. As with Claude Code (see the Claude Code reference in this skill), a marketplace's install-time name and its GitHub source can differ; always confirm the name shown by the host's own marketplace-list command before writing install instructions into docs.
- Relying on `strict: true` (the default) in a marketplace entry to catch author mistakes at marketplace-build time, then forgetting that per-plugin manifests still load leniently at install/runtime — the strict/lenient split lives at different layers, same as in Claude Code.
