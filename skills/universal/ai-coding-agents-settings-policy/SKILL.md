---
name: ai-coding-agents-settings-policy
description: "Designs coding-agent settings and fleet CLI version control. Use when diagnosing precedence, managed policy, version pins, update kill switch, catalog budgets, or searchable notes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-09-11
---

# AI Coding Agents Settings Policy

Use this skill to design or review the settings and policy layer of a coding-agent runtime: settings sources, precedence, managed policy, validation, safe environment handling, runtime application of settings changes, and the fleet controls that decide which CLI version runs (release channel, version range, update kill switches, staged rollout).

This skill owns configuration and policy architecture for coding-agent runtimes. For project memory in `AGENTS.md` or `CLAUDE.md`, use [`../agents-memory/SKILL.md`](../agents-memory/SKILL.md).

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should settings sources and policy precedence work? | [references/settings-source-precedence-and-managed-policy.md](references/settings-source-precedence-and-managed-policy.md) | Source model, merge order, managed policy, plugin-only restrictions |
| How should settings be validated and applied safely? | [references/settings-validation-and-safe-runtime-application.md](references/settings-validation-and-safe-runtime-application.md) | Schema validation, invalid-rule handling, safe env controls, runtime re-application |
| What are the exact override examples for each settings layer? | [references/settings-precedence-table.md](references/settings-precedence-table.md) | Full precedence table: managed > CLI flags > local > project > user, with concrete examples and cache invalidation |
| Which sources can enable plugin surfaces? | [references/plugin-only-restriction-recipes.md](references/plugin-only-restriction-recipes.md) | Trust-class recipes for locking, scoping, and logging plugin-surface activations |
| How do I handle Codex “Exceeded skills context budget”? | [references/openai-codex-managed-config-and-requirements.md#skill-catalog-context-budget](references/openai-codex-managed-config-and-requirements.md#skill-catalog-context-budget) | Supported budget override, safe config merge, rollback, and fresh-session verification |
| How do I enable Codex notes and searchable earlier context, including tool calls? | [references/openai-codex-managed-config-and-requirements.md#notes-and-searchable-context-history](references/openai-codex-managed-config-and-requirements.md#notes-and-searchable-context-history) | Experimental setting (look it up), memory distinction, and restart/validation steps |
| How do I pin the CLI version across a fleet, stop self-updates, or stage a CLI rollout? | [references/managed-delivery-and-fleet-controls.md](references/managed-delivery-and-fleet-controls.md) | Channel vs background check vs all-path block, hard range vs soft floor, fail-open or fail-closed per key class, install provenance, staged rollout |
| How does OpenAI Codex separate config layers from managed requirements? | [references/openai-codex-managed-config-and-requirements.md](references/openai-codex-managed-config-and-requirements.md) | Layer stack, requirements constraints, managed-hooks-only mode, debug surfaces |

## When To Use

- Design a settings system for a coding-agent CLI or runtime
- Separate user, project, local, flag, and managed policy sources
- Review how managed settings should override user configuration
- Define which environment variables or customization surfaces are safe to accept
- Apply runtime settings changes without restarting the whole process
- Diagnose Codex skill catalog omissions or stripped descriptions and verify the effective budget
- Pin or freeze the CLI version across a managed fleet, choose release channels, or block self-updates on image-managed machines
- Plan the operator side of a staged CLI rollout: canary, floor bump, halt criteria, rollback lever

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |
| Tool approval and permission modes | [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md) |
| Plugin package architecture, plugin cache, and plugin compatibility across CLI upgrades | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Scheduled or background-run triggers and session state | [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) |
| Packaging, signing, and install scripts for a CLI you ship (this skill covers only which version a fleet runs) | [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md) |
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
10. **Make fleet version control explicit.** Name each release channel and who receives it, then choose the release channel, background-check suppression, all-path update block, and hard version range as separate managed decisions (see [Fleet Version and Update Controls](#fleet-version-and-update-controls)).
11. **Prove the effective value.** For each load-bearing setting, record the winning source, parsed value, ignored or invalid contenders, and active runtime value. A key being accepted by a parser or present in a file does not prove that the selected model and runtime support or applied the behavior.

## Host Rules

- Keep source precedence explicit and stable.
- Always include managed-policy and CLI-flag sources even when users restrict editable sources.
- Distinguish editable sources from read-only policy and flag overlays.
- Prefer schema validation plus targeted filtering over all-or-nothing rejection when individual rules are bad.
- Keep dangerous environment settings and shell-like helper values behind explicit trust gates.
- Apply settings changes by recomputing derived runtime state, not by mutating scattered subsystems in place.
- Treat plugin-only customization policy as source-aware. Not every settings source is equally trusted to enable plugin surfaces.
- Sanitize persisted permission rules after reload before they become active state.
- Choose the managed-delivery failure mode explicitly. When the managed source cannot be fetched, a regulated fleet fails closed (blocks startup); otherwise the runtime runs on last-known-good policy with a visible banner. Never run silently with no policy, and record the policy version or fingerprint in the audit record.

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
- Precedence applies per value type: scalars take the highest source, lists merge across sources, and deny or block lists from any source always apply (see [references/settings-precedence-table.md](references/settings-precedence-table.md#rules)).
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

## Fleet Version and Update Controls

Which CLI version a managed fleet runs is a settings-policy decision. Detail, a worked golden-image decision, and the lookup steps are in [references/managed-delivery-and-fleet-controls.md](references/managed-delivery-and-fleet-controls.md).

- **Three update controls, not one.** Release-channel selection, suppression of the background update check, and a block on every update path (including manual update and install commands) are separate controls. A channel choice is not a kill switch, and suppressing the background check still leaves manual updates working. A fleet whose version is owned by a golden image or another release process needs the all-path block, set from managed policy.
- **Hard range vs soft floor.** A hard minimum or maximum blocks startup outside the range (a security floor, a compliance freeze); a soft floor only stops the updater from moving below it and does not stop an older build from starting. Set hard gates only from managed policy.
- **Fail open or fail closed per key class.** A malformed version gate fails open with an alert, so a bad policy push cannot lock out the fleet. A malformed or newer-schema restriction (deny rules, sandbox, allowed sources) fails closed, because losing it widens capability. Preferences load defaults and warn.
- **Managed distribution is its own channel.** An enterprise-pinned build has its own cadence, plugin allowlist, and rollback path; it is not the self-serve build with different flags.
- **Updater provenance.** The self-updater confirms the install came from the channel it will update through (package manager vs standalone) before replacing it, and warns with remediation when it cannot prove the target.
- **Staged CLI rollout.** Name halt metrics, thresholds, and the halt owner before exposure; canary on a pinned cohort before raising the managed minimum; keep the previous approved version installable until the rollback window closes.
- **Look up key names.** Channel values, kill-switch keys, and version-gate keys change between releases. Find them in the host's settings or managed-settings reference; never generate them from memory. An invalid channel value is not "off".

## Reference Runtime: Claude Code Precedence, Locks, and Cleanup

Source kind: the vendor settings and hooks docs (`code.claude.com/docs/en/settings`, `code.claude.com/docs/en/hooks`); look them up before relying on a key, scope, or default. The Claude Code precedence order is the reference implementation for the `settings-precedence-table.md` model in this skill:

```
managed (highest, cannot be overridden)
  > CLI flags (session-only)
    > .claude/settings.local.json (gitignored; allow rules apply without a trust dialog)
      > .claude/settings.json (project, checked in; requires the trust dialog)
        > ~/.claude/settings.json (user, lowest)
```

The most common audit mistake is inverting the last three: local is the **most** specific and highest-precedence editable file, not the least. A clean `~/.claude/settings.json` changes nothing in a repo that carries a conflicting `.claude/settings.local.json`.

Session-file retention is a settings key too. When auditing a fleet for stale-session accumulation or unexpected data loss, look up the retention key, its default, and its minimum before assuming a bug: a value of `0` may be a validation error rather than "disable cleanup", and a value below the shipped default is a deliberate override, not drift.

### Lock classes

A "locked" setting belongs to one of four classes. Name the class before advising where to set a key; "just set X in your project settings" is wrong for classes 1, 2, and 4.

1. **Managed-only keys.** Honored only from managed policy; the same key in user or project settings is silently ignored. Examples of the class: restricting permission rules, hooks, or MCP servers to the managed set; organization-managed instructions; rejecting sideload flags at startup (a marketplace restriction without a sideload block has a per-run bypass); forcing a fresh managed-settings fetch before startup (see the delivery failure-mode rule in Host Rules).
2. **Any-scope keys enforced only from managed.** A user or project file may contain the key, but only the managed value is enforced (a login-method restriction is the usual example). Treat a non-managed value as decorative.
3. **Any-scope keys where managed simply wins.** Normal precedence; policy only makes the choice non-negotiable for that user or repo (for example disabling the classifier permission mode, background agents, or bundled skills).
4. **A repo cannot grant itself.** Project scope ignores security-sensitive keys even though user and managed scope accept them, so a compromised or careless repo cannot loosen its own sandbox, approvals, or credential handling.

Lists keep their merge rule inside every class: a deny or block list merges from all sources and wins over an allowlist, even a managed one, and a blocklist must be enforced on every install, update, and refresh, not only when a source is added.

Look up each key's Scope line in the vendor settings reference before placing it in a class; vendors move keys between classes.

Update controls (channel, background check, all-path block, version range) are portable rules; see [Fleet Version and Update Controls](#fleet-version-and-update-controls).

### Hook events relevant to settings and policy

| Event | Trigger | Use Case |
|-------|---------|----------|
| `ConfigChange` | Fires when a configuration file changes during a session, covering user, project, local, and managed settings | Audit trail, policy-compliance checks, external notification on settings drift |
| `MessageDisplay` | Fires while assistant message text is displayed | Display-only — no blocking or decision control; can replace displayed text via `hookSpecificOutput.displayContent` but never changes the transcript or what the model sees. Do not use it for enforcement; use `PreToolUse`/`PermissionRequest` for that. |

Both events follow the standard hook lifecycle alongside `PreToolUse`, `PostToolUse`, `SessionStart`, and `SessionEnd`, and are available in user, project, and managed-policy hook sources.

## Reference Runtime: OpenAI Codex Config Home, Layering, and Two Stacks

Source kind: the vendor config reference and config-file docs; look up key names, values, and file locations there before writing config.

### CODEX_HOME and Config File Location

`$CODEX_HOME` is the base directory for all Codex user state, defaulting to `~/.codex/` (`%USERPROFILE%\.codex\` on Windows). The primary user config file is `$CODEX_HOME/config.toml`.

Operators can relocate all user state by setting `$CODEX_HOME` — no config file edits required. Managed/enterprise configuration and CLI flags sit above this in precedence and are not affected by `$CODEX_HOME`.

### Config Layering (named profiles)

Named profiles are separate files next to `config.toml`, selected at launch with `--profile <profile-name>`, not a table inside one `config.toml`. Confirm the current file naming in the config docs before templating one.

```toml
# $CODEX_HOME/ci.config.toml
approval_policy = "never"

[sandbox_workspace_write]
network_access = false
```

One Codex install can then serve interactive dev, CI, and enterprise review without one file trying to hold every mode.

### Approval policy

Sandbox mode and approval policy are separate axes; approval values and their semantics are owned by [`../ai-coding-agents-safety-envelope/SKILL.md#approval-policy-vs-sandbox`](../ai-coding-agents-safety-envelope/SKILL.md#approval-policy-vs-sandbox). Look up the current values in the vendor config reference before writing config; a retired value can prevent startup.

### Two stacks: preferences and requirements

Codex keeps two separate stacks. The config stack (managed defaults, CLI flags, project `.codex/config.toml`, profile, user config) chooses preferences. The requirements stack (managed requirements; look up the current delivery channels) constrains what any layer of the config stack may choose, including approval and sandbox values; a config value outside the permitted set fails the constraint and is surfaced before tools run instead of being merged. See [references/openai-codex-managed-config-and-requirements.md](references/openai-codex-managed-config-and-requirements.md#requirements-are-constraints). Model an equivalent for another CLI the same way: preferences merge, requirements constrain.

Project-scoped config ignores a fixed set of security-critical keys so a repo cannot loosen its own trust boundary. Look up the current project-ignored key list in the config reference; do not assume which keys it covers. Treat "which keys project config may touch" as a threat-modeling question when designing an equivalent for another CLI.

## Cross-Platform Patterns (Goose)

Goose introduces two settings-layer patterns beyond the standard user/project/flag/managed-policy stack: **custom distros as policy-delivery mechanism**, and **`.goosehints`-style narrative project hints** as a distinct source class.

### Custom distros as a read-only policy source

Goose's Custom Distributions bake an allowlist, provider pinning, and branding into the binary itself. From the settings layer's perspective, this is a *new source class*: read-only, above CLI flags in precedence, immutable at runtime.

- **Pattern:** add `distro_policy` to the source-precedence table as the highest immutable layer (above `managed_policy`, which can be updated without a binary change). Effective-settings UI must attribute wins to the distro layer explicitly so operators can explain "why can't I change this."
- **Anti-pattern:** encoding enterprise restrictions through managed-policy files shipped alongside the open-source binary. Users can rename, move, or delete those files; distro policy cannot be bypassed without swapping the binary.
- **Recipe:** add a distro source class with a frozen manifest, rendered in `--version` output and visible in the effective-settings debug view. Managed-policy layers can still narrow further but cannot broaden beyond the distro envelope.
- **Distro as a release channel:** give each distro an ID, a pinned upstream revision, its extension manifest, and its own update policy. Show the distro ID in `--version` output and telemetry so users and support know they are not on the main stable build, and track distro identity in the compatibility matrix, because a distro's plugin set is frozen at build time. Shipping a partner or enterprise build as "stable channel plus a config file" leaks its providers into the upstream matrix and makes breakage attribution impossible.

### `.goosehints` — narrative project-hint layer

Goose loads `.goosehints` as a per-project narrative file (similar to `AGENTS.md` / `CLAUDE.md`). This is *not* structured settings — it is unstructured guidance for the agent about the project. But it is a source layer in the sense that the agent consumes it deterministically at session start.

- **Pattern:** model project-narrative hints as a distinct source class, separate from typed settings. It has its own trust model (user-editable), its own precedence (always loaded, low priority), and its own invalidation (file-watch triggers re-read).
- **Anti-pattern:** treating narrative hints as "just settings" and applying schema validation to prose. Or treating them as entirely separate and duplicating source-precedence logic for them.
- **Recipe:** the settings layer acknowledges project-narrative as a source with explicit lifecycle hooks (read, invalidate, merge into agent context). Concrete formats — `AGENTS.md`, `CLAUDE.md`, `.goosehints`, `.cursorrules` — are implementations of that source class. The `agents-memory` skill owns the content side; the settings-policy layer owns the source-loader plumbing.

## Navigation

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and implementation references for settings and policy guidance. Reference files are listed in the Quick Reference table.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
