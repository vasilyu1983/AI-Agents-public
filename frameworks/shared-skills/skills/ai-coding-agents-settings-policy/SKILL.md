---
name: ai-coding-agents-settings-policy
description: "Designs settings and policy layers for coding-agent runtimes. Use when modeling source precedence, managed policy, env controls, or runtime settings validation."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Settings Policy

Use this skill to design or review the settings and policy layer of a coding-agent runtime: settings sources, precedence, managed policy, validation, safe environment handling, and runtime application of settings changes.

This skill owns configuration and policy architecture for coding-agent runtimes. For project memory in `AGENTS.md` or `CLAUDE.md`, use [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md).

## ASCII Flow

```text
settings sources
  defaults + managed policy + user + project + local + flags + env
       |
       v
precedence merge
  deterministic order + source provenance + plugin-only restrictions
       |
       v
validation
  schema + forbidden keys + unsafe env + unknown options
       |
       v
runtime application
  provider policy + tools + permissions + plugins + UI + cache invalidation
       |
       v
audit record
  effective settings without secrets
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should settings sources and policy precedence work? | [`references/settings-source-precedence-and-managed-policy.md`](references/settings-source-precedence-and-managed-policy.md) | Source model, merge order, managed policy, plugin-only restrictions |
| How should settings be validated and applied safely? | [`references/settings-validation-and-safe-runtime-application.md`](references/settings-validation-and-safe-runtime-application.md) | Schema validation, invalid-rule handling, safe env controls, runtime re-application |
| What are the exact override examples for each settings layer? | [`references/settings-precedence-table.md`](references/settings-precedence-table.md) | Full precedence table: managed > CLI flags > local > project > user, with concrete examples and cache invalidation |
| Which sources can enable plugin surfaces? | [`references/plugin-only-restriction-recipes.md`](references/plugin-only-restriction-recipes.md) | Trust-class recipes for locking, scoping, and logging plugin-surface activations |
| How is ToolSearch gated by settings policy? | [`references/deferred-tool-policy-layer.md`](references/deferred-tool-policy-layer.md) | Settings keys, policy decision flow, and interaction with tool-pool assembly |
| How does OpenAI Codex separate config layers from managed requirements? | [`references/openai-codex-managed-config-and-requirements.md`](references/openai-codex-managed-config-and-requirements.md) | Layer stack, requirements constraints, managed-hooks-only mode, debug surfaces |

## When To Use

- Design a settings system for a coding-agent CLI or runtime
- Separate user, project, local, flag, and managed policy sources
- Review how managed settings should override user configuration
- Define which environment variables or customization surfaces are safe to accept
- Apply runtime settings changes without restarting the whole process

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |
| Tool approval and permission modes | [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md) |
| Plugin package architecture | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| AGENTS.md or CLAUDE.md repo memory | [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md) |
| Generic config or schema design outside agent runtimes | [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md) |

## Default Workflow

1. **Define source layers.** Separate user, shared project, local gitignored, CLI-flag, and managed-policy sources.
2. **Freeze precedence.** Document one merge order and keep it consistent across disk reads, UI display, and runtime application.
3. **Make managed policy authoritative.** Policy layers should override user-controlled settings and bypass local customization where required.
4. **Validate at the boundary.** Parse, coerce, and validate settings before they mutate runtime state.
5. **Fail soft on invalid fragments.** Preserve the file on disk, but ignore invalid pieces when safe to do so.
6. **Protect dangerous env and customization surfaces.** Whitelist what can be applied automatically; strip or gate anything that could redirect providers or execute shell code.
7. **Separate cache tiers.** Keep merged settings, per-source reads, and parsed-file caches distinct so invalidation is targeted and explainable.
8. **Apply changes through one runtime path.** Re-read settings, snapshot hooks or dependent callbacks, reload dependent subsystems, and update app state through a single function.
9. **Test hostile cases.** Cover malformed JSON, invalid permission rules, drop-in conflicts, managed overrides, and live settings-change notifications.

## Host Rules

- Keep source precedence explicit and stable.
- Always include managed-policy and CLI-flag sources even when users restrict editable sources.
- Distinguish editable sources from read-only policy and flag overlays.
- Prefer schema validation plus targeted filtering over all-or-nothing rejection when individual rules are bad.
- Keep dangerous environment settings and shell-like helper values behind explicit trust gates.
- Apply settings changes by recomputing derived runtime state, not by mutating scattered subsystems in place.
- Treat plugin-only customization policy as source-aware. Not every settings source is equally trusted to enable plugin surfaces.
- Sanitize persisted permission rules after reload before they become active state.

## Build Order

1. Define settings sources and immutable precedence.
2. Define the canonical merged schema and validation path.
3. Add managed-policy and CLI-flag overlays.
4. Add dangerous-surface filtering for env and helper values.
5. Split merged, per-source, and parsed-file caches.
6. Implement one runtime re-application path.
7. Add reload sequencing for caches, hook snapshots, plugins, and UI state.

## Core Invariants

- Precedence must be identical in disk reads, UI views, and runtime application.
- Managed policy overrides user settings even when users can edit local files.
- Invalid fragments should not corrupt valid configuration.
- Dangerous customization surfaces require explicit trust rules.
- Runtime state should be recomputed from merged settings, not patched piecemeal.
- Cache invalidation must respect which layer changed: parsed file, source layer, or merged result.

## Failure Modes

- Different parts of the runtime seeing different precedence orders.
- Managed drop-ins loading after user config but before flags in one code path and not another.
- Invalid permission rules poisoning the whole settings load.
- Reload side effects applying out of order across cache resets, hooks, and app state.
- Plugin-only restrictions differing by source because trust class was lost during merge.
- Safe-looking env overrides redirecting providers or shell helpers unexpectedly.

## Minimal Viable Version

- One source-precedence table.
- One merged schema and validation pass.
- One managed-policy overlay.
- One filter for dangerous env or helper surfaces.
- One source-aware trust rule for plugin-only or privileged customization.
- One central function that reapplies derived runtime state after settings change.

## What Strong Implementations Add

- Read-only versus editable source distinctions in UI and runtime.
- Plugin-only customization restrictions.
- Fine-grained invalid-fragment filtering instead of all-or-nothing rejection.
- Distinct caches for parsed files, per-source layers, and merged effective settings.
- Explicit sequencing for hook snapshots, cache resets, and state reapplication.
- Auditability explaining which source won for any effective value.

## Known Traps

- Letting different subsystems invent their own precedence rules and ending up with settings that disagree between runtime, UI, and policy enforcement.
- Treating environment overrides as harmless configuration even when they bypass managed policy or expand the trust boundary.
- Reapplying one changed field in place instead of rebuilding the derived state that depends on source layering, hooks, and permissions.
- Using one shared cache for parse results, merged settings, and source-specific state, which makes invalidation unreliable.
- Hiding policy wins from the effective-settings view and making debugging impossible for operators.

## Common Anti-Patterns

- Letting every subsystem define its own precedence order.
- Treating flags, policy, and user files as one merge layer.
- Reapplying only the changed field instead of rebuilding derived state.
- Using one undifferentiated settings cache for parse results, source layers, and merged output.
- Accepting arbitrary env overrides because they are “just config.”
- Hiding managed-policy wins from the effective settings view.

## Claude Code: Precedence, Managed Policy, and Cleanup (2026, web-verified)

Verified against `code.claude.com/docs/en/settings` and `code.claude.com/docs/en/hooks` on 2026-07-11. The Claude Code precedence order is the reference implementation for the `settings-precedence-table.md` model in this skill:

```
managed (highest, cannot be overridden)
  > CLI flags (session-only)
    > .claude/settings.local.json (gitignored; allow rules apply without a trust dialog)
      > .claude/settings.json (project, checked in; requires the trust dialog)
        > ~/.claude/settings.json (user, lowest)
```

The most common audit mistake is inverting the last three: local is the **most** specific and highest-precedence editable file, not the least. A clean `~/.claude/settings.json` changes nothing in a repo that carries a conflicting `.claude/settings.local.json`.

`cleanupPeriodDays` (any editable scope; default `30`, minimum `1`) controls how many days of session files and other application data Claude Code deletes at startup. Setting it to `0` is a validation error, not "disable cleanup." When auditing a fleet for stale-session accumulation or unexpected data loss, check this key before assuming a bug — 30 days is the shipped default and a lower value elsewhere is a deliberate override, not drift.

### Managed-settings-only keys

These keys are honored **only** when set in managed/enterprise policy; the same key in user or project settings is silently ignored. This is the strongest lockdown class — verify this distinction before telling an operator "just set X in your project settings," because for this table that advice is wrong.

| Key | Type | Effect |
|-----|------|--------|
| `allowManagedPermissionRulesOnly` | boolean | User/project permission rules (`allow`/`ask`/`deny`) are ignored; only managed-settings rules apply |
| `allowManagedHooksOnly` | boolean | Only managed hooks, SDK hooks, and plugin hooks force-enabled via managed `enabledPlugins` load; user/project/other-plugin hooks are blocked |
| `allowManagedMcpServersOnly` | boolean | Only the managed `allowedMcpServers` allowlist is respected; `deniedMcpServers` still merges from all sources on top of it |
| `claudeMd` | string | Organization-managed CLAUDE.md-style instructions injected as memory; ignored if set anywhere other than managed/policy settings |
| `disableSideloadFlags` | boolean | Rejects `--plugin-dir`, `--plugin-url`, `--agents`, and `--mcp-config` CLI flags at startup — closes the loophole where a user could otherwise sideload past `strictKnownMarketplaces` for a single run |
| `forceRemoteSettingsRefresh` | boolean | Blocks CLI startup until remote managed settings are freshly fetched; the CLI exits on fetch failure rather than falling back to a cached or absent policy |
| `blockedMarketplaces` | array | Blocklist enforced on marketplace add and on every plugin install/update/refresh/auto-update, so a marketplace added before the policy existed still loses access |
| `forceLoginMethod` | `"claudeai"` \| `"console"` \| `"gateway"` | Restricts login to one account class |
| `forceLoginOrgUUID` | string or array of UUIDs | Requires login to a specific Anthropic organization (or any of a listed set) |
| `allowAllClaudeAiMcps` | boolean | Loads claude.ai connectors alongside a deployed `managed-mcp.json`, which otherwise takes exclusive control and suppresses them |
| `allowedChannelPlugins` / `deniedMcpServers` | array | Allow/deny lists for channel plugins and MCP servers respectively; the deny list always wins over the allow list, even against managed servers |

### Keys that exist in all scopes but are commonly set via managed policy

Do not describe these as "managed-only" — a user or project file can set them too; policy is simply the layer that makes the choice non-negotiable for that user or repo.

| Key | Type | Effect |
|-----|------|--------|
| `disableAutoMode` | `"disable"` | Prevents auto permission mode from being activated; removed from the Shift+Tab cycle and rejects `--permission-mode auto` at startup |
| `disableAgentView` | boolean | Turns off background agents and agent view (`claude agents`, `--bg`, `/background`) |
| `disableBundledSkills` | boolean | Removes bundled skills/workflows entirely; `/init`-style built-in commands stay typable but hidden from the model |
| `autoUpdatesChannel` | `"latest"` (default) \| `"stable"` | Release channel; `"stable"` trails by about a week and skips versions with major regressions. There is no `"disabled"` channel value — to stop auto-updates entirely, set the `DISABLE_AUTOUPDATER` env var instead |

A prior version of this skill listed `strictPluginOnlyCustomization`, `policyHelper`, and `parentSettingsBehavior` as managed-policy keys. None of the three could be verified against current docs on re-check (2026-07-11) — they have been removed rather than carried forward as unverified claims. If a runtime you are auditing needs "all customization must come through plugins" or "policy context injected into the system prompt" behavior, treat it as a custom control you are designing, not an existing Claude Code key, until you find it in current docs yourself.

### Hook events relevant to settings and policy

| Event | Trigger | Use Case |
|-------|---------|----------|
| `ConfigChange` | Fires when a configuration file changes during a session, covering user, project, local, and managed settings | Audit trail, policy-compliance checks, external notification on settings drift |
| `MessageDisplay` | Fires while assistant message text is displayed | Display-only — no blocking or decision control; can replace displayed text via `hookSpecificOutput.displayContent` but never changes the transcript or what the model sees. Do not use it for enforcement; use `PreToolUse`/`PermissionRequest` for that. |

Both events follow the standard hook lifecycle alongside `PreToolUse`, `PostToolUse`, `SessionStart`, and `SessionEnd`, and are available in user, project, and managed-policy hook sources.

## OpenAI Codex: Config Home, File Layering, and Approval-Mode TOML Key

Re-verified against `learn.chatgpt.com/docs/config-file/config-reference` on 2026-07-11. This supersedes an earlier version of this section that was pinned to a May 2026 source snapshot and had drifted on two points — see corrections below.

### CODEX_HOME and Config File Location

`$CODEX_HOME` is the base directory for all Codex user state, defaulting to `~/.codex/` (`%USERPROFILE%\.codex\` on Windows). The primary user config file is `$CODEX_HOME/config.toml`.

Operators can relocate all user state by setting `$CODEX_HOME` — no config file edits required. Managed/enterprise configuration and CLI flags sit above this in precedence and are not affected by `$CODEX_HOME`.

### Config Layering (named profiles) — corrected

Named profiles are **separate files next to `config.toml`**, not a `[profiles.NAME]` table inside it: `$CODEX_HOME/<profile-name>.config.toml`, selected at launch with `--profile <profile-name>`. A prior version of this skill showed `[profiles.strict]` / `[profiles.ci]` tables inside one `config.toml` — that syntax is not current and should not be used as a template.

```toml
# $CODEX_HOME/ci.config.toml
approval_policy = "never"

[sandbox_workspace_write]
network_access = false
```

The active profile is selected via `--profile ci`, letting one Codex install serve multiple use-case contexts (interactive dev, CI, enterprise review) without one file trying to hold every mode.

### Approval-Mode TOML Key — corrected value

```toml
# ~/.codex/config.toml
approval_policy = "on-request"  # default; see AskForApproval enum in ai-coding-agents-permissions
```

Verified valid values (2026-07-11): `"untrusted"`, `"on-request"`, `"never"`, or a granular object (sub-keys for `sandbox_approval`, `rules`, `mcp_elicitations`, `request_permissions`, `skill_approval`). `"on-failure"` still appears but is deprecated. **`"unless-trusted"` is not a valid value** — a prior version of this skill used that spelling; if you find it in an older Codex install or a stale example elsewhere, treat it as the pre-rename form of `"untrusted"` and do not propagate the old spelling into new configs.

### Precedence, including project scope

Current documented order (highest first): managed/enterprise configuration > CLI flags > project-scoped `.codex/config.toml` > profile file (via `--profile`) > user-level `$CODEX_HOME/config.toml`. A fixed set of security-critical keys — provider selection, authentication, notification routing, telemetry routing, and the approval/sandbox trio (`approval_policy`, `sandbox_mode`, `sandbox_workspace_write`) — are deliberately ignored if set in project-scoped config, so a compromised or careless repo cannot loosen its own sandbox. Treat "which keys project config is allowed to touch" as a threat-modeling question, not an oversight, when designing an equivalent for another CLI.

## Cross-Platform Patterns (Goose)

Goose introduces two settings-layer patterns beyond the standard user/project/flag/managed-policy stack: **custom distros as policy-delivery mechanism**, and **`.goosehints`-style narrative project hints** as a distinct source class.

### Custom distros as a read-only policy source

Goose's Custom Distributions (see `ai-coding-agents-release-distribution`) bake an allowlist, provider pinning, and branding into the binary itself. From the settings layer's perspective, this is a *new source class*: read-only, above CLI flags in precedence, immutable at runtime.

- **Pattern:** add `distro_policy` to the source-precedence table as the highest immutable layer (above `managed_policy`, which can be updated without a binary change). Effective-settings UI must attribute wins to the distro layer explicitly so operators can explain "why can't I change this."
- **Anti-pattern:** encoding enterprise restrictions through managed-policy files shipped alongside the open-source binary. Users can rename, move, or delete those files; distro policy cannot be bypassed without swapping the binary.
- **Recipe:** add a distro source class with a frozen manifest, rendered in `--version` output and visible in the effective-settings debug view. Managed-policy layers can still narrow further but cannot broaden beyond the distro envelope.

### `.goosehints` — narrative project-hint layer

Goose loads `.goosehints` as a per-project narrative file (similar to `AGENTS.md` / `CLAUDE.md`). This is *not* structured settings — it is unstructured guidance for the agent about the project. But it is a source layer in the sense that the agent consumes it deterministically at session start.

- **Pattern:** model project-narrative hints as a distinct source class, separate from typed settings. It has its own trust model (user-editable), its own precedence (always loaded, low priority), and its own invalidation (file-watch triggers re-read).
- **Anti-pattern:** treating narrative hints as "just settings" and applying schema validation to prose. Or treating them as entirely separate and duplicating source-precedence logic for them.
- **Recipe:** the settings layer acknowledges project-narrative as a source with explicit lifecycle hooks (read, invalidate, merge into agent context). Concrete formats — `AGENTS.md`, `CLAUDE.md`, `.goosehints`, `.cursorrules` — are implementations of that source class. The `agents-memory` skill owns the content side; the settings-policy layer owns the source-loader plumbing.

## Navigation

### References

- [`references/settings-source-precedence-and-managed-policy.md`](references/settings-source-precedence-and-managed-policy.md) — Source layering, managed policy, and customization restrictions
- [`references/settings-validation-and-safe-runtime-application.md`](references/settings-validation-and-safe-runtime-application.md) — Validation, safe env handling, and runtime application
- [`references/settings-precedence-table.md`](references/settings-precedence-table.md) — Concrete precedence table with override examples (managed > CLI flags > local > project > user)
- [`references/plugin-only-restriction-recipes.md`](references/plugin-only-restriction-recipes.md) — Trust-class enforcement for plugin-surface activations
- [`references/deferred-tool-policy-layer.md`](references/deferred-tool-policy-layer.md) — How ToolSearch trigger is settings-gated
- [`references/openai-codex-managed-config-and-requirements.md`](references/openai-codex-managed-config-and-requirements.md) — OpenAI Codex config layer stack, managed requirements, requirements-only settings, and policy debug surfaces

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and implementation references for settings and policy guidance

### Related Skills

- [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md) — Permission modes and rule handling
- [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) — Plugin-only customization and extension policy
- [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md) — Project instruction files rather than runtime settings

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- These patterns are grounded in a local April 2026 `claude_code` source snapshot. Re-check upstream code or docs before relying on volatile runtime details.
- Managed policy, safe-env rules, and live settings application are implementation-specific. Preserve the control model, but verify the exact field names and trust semantics in the target runtime.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
