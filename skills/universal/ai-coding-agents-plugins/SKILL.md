---
name: ai-coding-agents-plugins
description: "Designs coding-agent plugin systems. Use when adding plugin manifests, extension points, or reloadable integrations, or keeping plugin cache compatible across CLI upgrades."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Plugins

Use this skill to design or review plugin systems for coding-agent runtimes, especially terminal-first CLIs that load skills, hooks, MCP servers, commands, agents, or output styles from installable extensions.

This skill owns plugin architecture for coding agents. For the broader coding-agent creation workflow, start with [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md).

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should a coding-agent plugin be structured? | [references/plugin-manifest-and-capability-model.md](references/plugin-manifest-and-capability-model.md) | Package layout, manifest fields, capability families |
| How should plugins load, reload, and register? | [references/plugin-loading-and-runtime-lifecycle.md](references/plugin-loading-and-runtime-lifecycle.md) | Discovery order, activation flow, cache and reload rules |
| Where should trust boundaries live? | [references/plugin-trust-boundaries-and-safety.md](references/plugin-trust-boundaries-and-safety.md) | Install-time safety, runtime restrictions, policy controls |
| What must stay compatible when the CLI upgrades? | [references/plugin-loading-and-runtime-lifecycle.md#compatibility-and-upgrades](references/plugin-loading-and-runtime-lifecycle.md#compatibility-and-upgrades) | Separate contracts, cache identity, partial-upgrade contract, startup gates, upgrade tests |
| How does OpenAI Codex structure plugin manifests and marketplace lifecycle? | [references/openai-codex-plugin-manifest-and-marketplace.md](references/openai-codex-plugin-manifest-and-marketplace.md) | Skills/MCP/apps/hooks paths, interface metadata, path rules, marketplace add/remove/upgrade |
| How does GitHub Copilot CLI structure plugin manifests and marketplaces? | [references/github-copilot-cli-plugin-manifest-and-marketplace.md](references/github-copilot-cli-plugin-manifest-and-marketplace.md) | Manifest search order, component paths, marketplace.json shape, install sources, cross-host fallback |

## When To Use

- Design a plugin system for a coding-agent CLI or terminal runtime
- Add installable extensions that provide commands, skills, hooks, agents, or MCP servers
- Separate built-in capabilities from marketplace or repo-local plugins
- Define plugin manifests, capability registration, namespacing, or reload behavior
- Review whether a plugin architecture has safe trust boundaries and host-owned precedence
- Keep plugins and plugin caches working across CLI upgrades, downgrades, rollbacks, and cache migrations

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| End-to-end coding agent or coding team design | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |
| MCP server design and connectivity | [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md) |
| Hook authoring and lifecycle automation | [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md) |
| Subagent definitions and delegation contracts | [`../agents-subagents/SKILL.md`](../agents-subagents/SKILL.md) |
| Generic CLI and SDK design, or packaging, signing, and install scripts for a CLI you ship | [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md) |
| Scheduled or background-run triggers that load plugins | [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) |
| Fleet CLI version pinning, release channels, or update kill switches | [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md#fleet-version-and-update-controls) |
| Skill packaging and shared-skills validation | [`../agents-skills/SKILL.md`](../agents-skills/SKILL.md) |

## Default Workflow

1. **Classify the extension surface.** Decide whether the user actually needs a plugin, or just a local skill, hook, MCP server, or built-in command.
2. **Define capability families first.** Model commands, skills, hooks, agents, output styles, and MCP servers as typed host-owned extension points.
3. **Choose the trust boundary.** Decide what is allowed at install time, what is allowed at runtime, and which fields third-party plugin content is forbidden to control.
4. **Write the manifest contract.** Keep identity, metadata, dependencies, and capability declarations in the manifest instead of relying on implicit folder discovery alone.
5. **Namespace plugin-provided components.** Avoid collisions by having the host prefix commands, agents, and output styles with the plugin name or source.
6. **Define deterministic load order.** Core runtime first, then built-ins, then installed plugins, then session-local overlays or inline plugins.
7. **Split plugin state into layers.** Keep install intent, materialized on-disk plugin contents, and active in-memory components as separate layers.
8. **Design reload semantics explicitly.** Separate cache clearing, component re-registration, and transport reconnection. Do not assume hot reload is safe for every capability type.
9. **Preserve partial success.** A failing plugin should not take down the whole runtime if unaffected capability families can still be swapped safely.
10. **Validate with hostile cases.** Test duplicate names, invalid manifests, blocked plugins, stale caches, plugin disable, and partial reload failures.
11. **Measure activation cost.** Capture schema/instruction tokens, startup latency, spawned processes, and network connections before and after enablement. Package size or capability count is not a proxy for context cost, and installed does not mean active.

## Host Rules

Use these defaults unless the runtime has a better documented model:

- Treat the host as the only authority on precedence, activation, and capability registration.
- Keep plugin manifests declarative. Avoid executing plugin code just to discover metadata.
- Make built-ins look like plugins to the UI and registry, but keep their trust and enablement rules host-controlled.
- Keep plugin-provided component names namespaced by plugin ID or plugin name.
- Allow third-party plugins to contribute capabilities, but do not let nested files silently escalate permissions beyond what the user approved at install time.
- Prefer reloadable registries for commands, agents, hooks, output styles, and MCP connections, but allow restart-required behavior when side effects cannot be safely swapped.
- Version plugin caches by compatibility boundary, not only by plugin display version.
- Treat git-subdir and path-based installs as distinct cache identities so different mounts cannot collide.

## Build Order

1. Define capability families and host-owned extension points.
2. Write the manifest contract and validation path.
3. Define plugin trust boundaries and install-time restrictions.
4. Implement deterministic discovery and activation order.
5. Split plugin state into intent, materialization, and active runtime components.
6. Add reload semantics, cache invalidation, and partial-failure handling.
7. Add managed-policy and built-in-plugin interaction rules.

## Core Invariants

- The host owns precedence, trust, and activation.
- Plugin manifests must be declarative and inspectable without executing plugin code.
- Built-ins may look like plugins in UI, but they are not trusted the same way.
- Capability names must be namespaced or collision-safe.
- Reloading one capability family must not silently corrupt another.
- Cache identity must include compatibility-relevant install context, not only plugin name.

## Failure Modes

- Executing plugin code during metadata discovery.
- Name collisions between built-ins and third-party capabilities.
- Stale caches keeping removed or disabled plugins active.
- Partial reload leaving command registries and MCP state inconsistent.
- Different plugin installs colliding in cache because path or subdir identity was ignored.
- Plugin-provided settings or nested files broadening trust beyond approved scope.

## Minimal Viable Version

- One declarative manifest format.
- One validation path before activation.
- One deterministic discovery and precedence order.
- One namespacing rule for plugin-provided capabilities.
- One explicit boundary between install intent, materialized plugin files, and active runtime registration.
- One restart-required fallback when hot reload is unsafe.

## What Strong Implementations Add

- Versioned cache directories and compatibility probing.
- Layered refresh that loads plugins first, then rebuilds dependent registries, then reconnects transports.
- Built-in plugins with host-controlled enablement semantics.
- Managed-policy interaction for plugin-only capabilities.
- Typed plugin errors and partial-failure recovery.
- Orphaned plugin-version cleanup and compatibility-aware cache keys.
- Reloadable registries for commands, hooks, agents, output styles, and MCP connections.

## Known Traps

- Treating plugin discovery as filesystem scanning alone and ending up with activation behavior that changes by path layout rather than manifest contract.
- Loading untrusted marketplace plugins with the same precedence and capability surface as built-ins or managed extensions.
- Rebuilding active registries in place during reload and leaving commands, hooks, or MCP connections in a half-updated state.
- Ignoring compatibility boundaries between core version, plugin API version, cache schema, and persisted state.
- Assuming every capability family can hot reload safely even when it holds long-lived connections or runtime-owned policy hooks.

## Common Anti-Patterns

- Using folder scanning as the manifest contract.
- Letting third-party plugins decide precedence or trust at runtime.
- Assuming hot reload is safe for every capability family.
- Treating installed files and active runtime state as one undifferentiated layer.
- Treating built-ins and marketplace plugins as identical trust classes.
- Ignoring cache schema and compatibility when plugin APIs evolve.

## Compatibility, Cache Identity, and Upgrades

A CLI upgrade is where plugin systems break quietly. Detail, the startup gates, and the upgrade test set are in [references/plugin-loading-and-runtime-lifecycle.md](references/plugin-loading-and-runtime-lifecycle.md#compatibility-and-upgrades); fill in [assets/templates/compatibility-matrix.md](assets/templates/compatibility-matrix.md) for each release.

- **Separate contracts.** Runtime version, plugin API range, settings schema, cache schema, and session-store schema are different contracts with different break surfaces. The binary's version number alone is not a compatibility signal, and "plugin installed successfully" does not mean "plugin is semantically compatible".
- **Cache identity.** A plugin cache entry is identified by content digest plus source kind, canonical source location and subdirectory, runtime ABI, and cache-schema version. Display version alone cannot tell apart path installs, git-subdir installs, or repackaged sources, and two installs sharing one identity corrupt each other across upgrades. A cache written by a different release channel is not trusted blindly.
- **Pin shared installs by digest.** Project-scope plugin intent records source plus content digest, like a lockfile, so teammates resolve identical bytes; a version range alone lets two machines run different code under one name.
- **Partial-upgrade contract.** A partially upgraded host either keeps the previous readable state side by side or stops before a destructive migration. It never mixes a new runtime with unverified old plugin or cache state. Define downgrade behavior before rollout, retain the prior artifact until the rollback window closes, and remove orphaned plugin versions and cache layouts only after no active session or rollback target references them.
- **Check at startup, not mid-task.** Detect plugin or cache incompatibility before a session starts, and tell the user when an upgrade resets or invalidates meaningful local state. Do not hide plugin breakage behind a successful core update.
- **Migrate conservatively.** Prefer additive migrations; keep startup checks fast and deterministic; make destructive cache resets explicit; detect downgrades as well as upgrades; separate "must migrate now" from best-effort cleanup. The runtime should be able to say in one sentence why each local artifact is reused, migrated, or discarded.
- **Test upgrade paths, not only fresh installs.** Exercise in-place upgrade, startup on an old cache, plugin version mismatch, downgrade, and rollback. Fresh-install coverage proves nothing about operators with old caches, old plugins, and customized settings.

## Reference Runtimes: Durable Lessons

Claude Code, GitHub Copilot CLI, and OpenAI Codex each document a plugin manifest, component paths, marketplaces, install scopes, and policy keys. Those tables change between releases, so look them up in each host's plugin reference before writing a manifest, install instructions, or policy. These lessons from the reference runtimes hold across releases:

- **An explicit version that goes stale blocks updates.** When update resolution prefers the manifest's version field, a version the author forgets to bump silently stops users from receiving new commits. Pin an explicit version only with a release step that bumps it; otherwise let the host fall back to the source revision.
- **Tolerate unknown fields at load; be strict in CI.** Hosts ignore unrecognized top-level manifest keys (a type mismatch on a recognized field still fails), so one file can double as another tool's manifest. Run the host's own strict plugin validator in CI to turn unknown-field and near-miss-name warnings into errors before publishing.
- **Trust follows scope, not intent.** A plugin the user placed in a personal directory and a plugin checked into a repository are different trust classes. Repo-sourced plugin content loads only after workspace trust, and its long-lived capabilities (MCP servers, LSP servers, background monitors) are restricted further or not loaded.
- **Marketplace name ≠ repository name.** A marketplace's registered install-time name can differ from its source repository name, so `<plugin>@<repo-name>` fails. Confirm the name with the host's marketplace-list command before writing install instructions into docs or onboarding scripts.
- **Plugin agents cannot escalate.** Plugin-shipped agent definitions must not set their own hooks, MCP servers, or permission mode; the host ignores those fields. Copy this restriction into any new host.
- **Host-specific fields are silently dropped across hosts.** A capability field with no counterpart on another host is ignored there, not migrated and not warned about.
- **A plugin's default settings honor only a host-defined subset of keys.** Check which keys the host applies from a plugin before shipping defaults, and ship instructions as a skill, not as a plugin-root instructions file the host may not load.
- **Reloading plugins that add or remove MCP servers invalidates the prompt cache.** Warn before applying such a reload mid-session.
- **Managed policy can narrow plugin sources.** Hosts let an administrator allowlist or block marketplaces and restrict customization to plugins plus managed settings. Look up the key names in the host's managed-settings reference.

### Portability across hosts

Design a portable core manifest plus per-host overlays. The portable core carries identity (name, version, author, license) and the shared component conventions (skills, agents, hooks, MCP servers). Each host overlay carries only that host's capability fields. Check which portable manifest format each target host reads, and in what loader search order, before promising authors "write once, run anywhere": hosts have shipped both cross-host fallbacks to another vendor's manifest location and separate portable plugin formats. See [references/github-copilot-cli-plugin-manifest-and-marketplace.md](references/github-copilot-cli-plugin-manifest-and-marketplace.md) for one host's loader search order.

## Cross-Platform Patterns (Goose)

Goose unifies the "plugin" and "MCP extension" concepts into a single typed extension model, and shows what manifest-in-recipe delivery looks like when tasks ship with their own extension declarations.

### Unified extension kind with `type:` discriminator

Goose recipes declare extensions inline:

```yaml
extensions:
  - type: builtin
    name: developer
  - type: mcp
    name: github
```

Both are `extension` entries; the `type` discriminator selects transport and trust. This collapses the dual-track "built-ins vs MCP" mental model into one ontology with two transports.

- **Pattern:** model the extension registry with a single type whose `origin` or `transport` field carries `builtin | mcp | ...`. Manifest, precedence, namespacing, and cache identity apply uniformly.
- **Anti-pattern:** maintaining parallel "plugin registry" and "MCP registry" APIs with subtly different lifecycle, reload, and trust semantics. Future transports (ACP-delegated extensions, WASM plugins) then each need their own track.
- **Recipe:** one `Extension` trait / interface, one activation path, one cache-identity rule. The `transport` field is free to evolve — `builtin`, `mcp-stdio`, `mcp-sse`, `acp-client` — without new mental models.

### Manifest-in-recipe (task-level extension declaration)

In Goose, the unit of work (recipe) declares its extension dependencies inline. This differs from classic plugin systems where plugins are enabled globally at runtime-config level.

- **Pattern:** allow plugin/extension declaration at multiple layers: host config, project/repo config, *and* task artifact. Task-layer declarations are subsets of what the project/host allows and define the active envelope for that task only.
- **Anti-pattern:** forcing all plugin activation to happen at CLI startup. Coding agents that support shareable task blueprints need blueprint-local extension sets — a recipe shared between teammates should carry its dependencies, not assume the receiver pre-enabled them.
- **Recipe:** the plugin resolver is called with a scope: `(host_config, project_config, task_manifest)`. The resolver intersects them — task can narrow but not broaden. A task's declared extensions must be subsets of the project's allowlist; violations are install-time errors, not runtime surprises.

### Host-shipped plugins (hypothesis)

A runtime vendor may publish first-party plugins through its own marketplace. They look like marketplace plugins in the registry, but their publisher and update channel differ, so treat them as a possibly distinct trust class.

- **Pattern:** carry an `origin: official | builtin | marketplace | local` tag on every plugin record so trust, cache identity, and update policy can differ per origin.
- **Check before assuming:** look up how the host versions and updates its first-party plugins. Do not assume they update in lockstep with the runtime or that their compatibility key is the runtime version; a first-party plugin can carry its own version like any other.

### Schema validation as a first-class gate

Goose's `recipe-scanner/` validates YAML recipes (and therefore their declared extensions) at build/ship time. This generalizes: plugin manifests and task manifests should face static validation before activation, not just at runtime load.

- **Pattern:** manifests are structured data; run the host's own strict plugin validator in CI, and validate again at install and at activation. Treat an invalid manifest as a shipping defect, not a runtime edge case.

## Navigation

### References

- [references/plugin-manifest-and-capability-model.md](references/plugin-manifest-and-capability-model.md) — Package layout, manifest structure, and capability typing
- [references/plugin-loading-and-runtime-lifecycle.md](references/plugin-loading-and-runtime-lifecycle.md) — Discovery, caching, reload, activation flow, and compatibility across CLI upgrades
- [references/plugin-trust-boundaries-and-safety.md](references/plugin-trust-boundaries-and-safety.md) — Trust model, validation, and policy guardrails
- [references/openai-codex-plugin-manifest-and-marketplace.md](references/openai-codex-plugin-manifest-and-marketplace.md) — OpenAI Codex plugin manifest fields, interface metadata, path validation, and marketplace lifecycle
- [references/github-copilot-cli-plugin-manifest-and-marketplace.md](references/github-copilot-cli-plugin-manifest-and-marketplace.md) — GitHub Copilot CLI manifest search order, component paths, marketplace.json shape, and cross-host fallback

### Templates

- [assets/templates/compatibility-matrix.md](assets/templates/compatibility-matrix.md) — Per-release compatibility matrix and upgrade gate rules

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and source references for plugin-runtime guidance

### Related Skills

- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) — Broader coding-agent architecture and creation workflow
- [`../agents-hooks/SKILL.md`](../agents-hooks/SKILL.md) — Hook lifecycle design
- [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md) — MCP server integration
- [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md) — Fleet version controls and managed plugin-source policy
- [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) — Session-store compatibility and resume across upgrades

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
