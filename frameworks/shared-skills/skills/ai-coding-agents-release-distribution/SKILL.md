---
name: ai-coding-agents-release-distribution
description: "Designs release and distribution systems for coding-agent CLIs. Use when modeling packaging, auto-update channels, plugin compatibility, cache migrations, or install footprints."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Release And Distribution

Use this skill to design or review how a coding-agent CLI ships and evolves: packaging, install channels, auto-update policy, plugin compatibility, cache versioning, migration strategy, and local footprint management.

This skill covers the productization layer that matters once the runtime itself already exists.

## ASCII Flow

```text
runtime build
  |
  v
package artifact
  binary/app bundle/npm/pip/homebrew + bundled assets + plugin ABI
  |
  v
release channel
  dev | canary | stable | enterprise-managed
  |
  v
install or update
  compatibility checks + cache migrations + rollback hooks
  |
  v
post-update verification
  version, plugin compatibility, migrated state, telemetry, rollback signal
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should packaging, updates, and compatibility work? | [`references/packaging-updates-and-compatible-plugins.md`](references/packaging-updates-and-compatible-plugins.md) | Install channels, version policy, plugin compatibility, and release discipline |
| How should caches, migrations, and local state evolve safely? | [`references/cache-migrations-and-install-channels.md`](references/cache-migrations-and-install-channels.md) | Cache keys, migration boundaries, rollback posture, and footprint control |
| How does OpenAI Codex handle install channels, update targets, app-server packages, and doctor? | [`references/openai-codex-install-update-and-doctor.md`](references/openai-codex-install-update-and-doctor.md) | Install provenance, update target checks, package variants, redacted support diagnostics |

## When To Use

- Design packaging and distribution for a coding-agent CLI
- Add auto-update channels or controlled rollout strategy
- Review plugin compatibility and extension version policy
- Model local caches, migration safety, or install footprint changes
- Decide how release engineering should handle breaking runtime changes

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Plugin manifest and extension architecture | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Settings and policy migration concerns | [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md) |
| Session-state compatibility and resume boundaries | [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md) |
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |

## Default Workflow

1. **Define the artifact strategy.** Decide what ships as the CLI, what is embedded, and what is loaded dynamically.
2. **Design install channels.** Stable, beta, nightly, enterprise-pinned, or managed-distribution channels should be explicit.
3. **Version compatibility intentionally.** Core runtime, plugin API, cache schema, and settings schema may need separate compatibility promises.
4. **Treat caches as versioned state.** Cache invalidation should be tied to schema and compatibility boundaries, not only app version.
5. **Plan safe migrations.** Upgrade, downgrade, rollback, and partial-update behavior should be defined before shipping breaking changes.
6. **Constrain local footprint.** Logs, caches, session state, tool registries, and downloaded integrations need bounded retention policy.
7. **Clean up orphaned state.** Old plugin versions and abandoned cache layouts need retention and garbage-collection rules.
8. **Protect user trust during rollout.** Make plugin breakage, cache resets, or session migration visible when they materially affect behavior.
9. **Test upgrade paths.** New installs, in-place upgrades, old-cache startup, plugin version mismatch, and rollback should all be exercised.

## Host Rules

- Keep runtime versioning distinct from plugin or extension compatibility.
- Prefer additive migrations, with explicit breaking boundaries when unavoidable.
- Version caches and local state independently from binary packaging.
- Make rollback behavior a first-class release concern.
- Bound local cache and log growth so the CLI does not silently accumulate unowned disk usage.
- Treat managed enterprise distribution as a different channel, not just a different flag.
- Cache keys should include compatibility-relevant install context when plugins can come from paths, subdirs, or repackaged sources.

## Scratch-Rebuild Coverage

- Coverage strength:
  strong for release channels, compatibility boundaries, versioned state, rollback framing, local-footprint discipline, and the requirement that plugin and cache identity be treated as separate compatibility surfaces
- Missing for faithful reproduction:
  cross-version plugin API contracts, staged rollout telemetry, orphaned-version cleanup, cache-schema migration choreography, and downgrade behavior across partially updated hosts need more operational detail
- Required additions:
  document compatibility matrices for core versus plugins versus caches, cache-key rules for path or subdir installs, rollout and rollback observability requirements, and spell out how partial upgrades fail safely

## Build Order

1. Define the shipping artifact and install surfaces.
2. Define release channels and rollout policy.
3. Separate compatibility promises for runtime, plugins, caches, and settings.
4. Add versioned migrations and rollback rules.
5. Define cache identity and orphan-cleanup policy.
6. Add footprint controls for logs, caches, and downloaded integrations.
7. Add staged rollout telemetry and downgrade tests.

## Core Invariants

- Binary version, plugin API version, and cache schema version are different contracts.
- Rollback is part of release design, not a later repair.
- Users must be told when upgrades reset or invalidate meaningful local state.
- Enterprise-managed distribution is a first-class operating mode.
- Install footprint growth must be bounded and owned.
- Obsolete plugin versions and caches must have explicit retention and cleanup rules.

## Failure Modes

- New binaries booting against incompatible old caches with silent corruption.
- Plugin breakage hidden behind a “successful” core update.
- Rollbacks that leave migrated state unreadable to the previous version.
- Partial updates where helpers, plugins, and core disagree on protocol.
- Long-term disk growth from logs, caches, or downloaded runtimes with no retention policy.
- Different plugin installs sharing one cache identity and corrupting each other across upgrades.

## Minimal Viable Version

- One shipping artifact and one documented install path.
- One stable channel and one pre-release channel.
- One versioned cache schema.
- One explicit rollback posture.
- One retention rule for orphaned plugin versions or cache directories.
- One visible warning path for incompatible plugin or cache state.

## What Strong Implementations Add

- Multi-channel rollout with staged exposure and telemetry.
- Compatibility matrices across core, plugins, settings, and caches.
- Automatic migration with safe fallback or quarantine on failure.
- Orphaned-version cleanup and cache identities that incorporate install context.
- Bounded retention for session logs, caches, and downloaded assets.
- Enterprise-pinned or managed-distribution release streams.
- **Custom Distributions** as a distinct channel class, with pinned upstream commit, manifest, and distro ID visible in `--version`.
- **OSS install scripts** (`*.sh` + `*.ps1`) committed to the repo with checksum verification and unattended-install modes.
- **Foundation-level governance** (OSS license, maintainers, security disclosure, supply-chain gates like `deny.toml`).
- **Recipe/manifest static scanners** so YAML artifacts face the same gating as compiled code.

## Known Traps

- Treating a binary version number as the only compatibility signal while plugin APIs, cache schema, and managed policy have their own break surfaces.
- Shipping state or cache migrations without downgrade planning and then stranding users who roll back or switch channels.
- Assuming fresh-install test coverage proves upgrade safety for existing operators with old caches, old plugins, and customized settings.
- Reusing one cache namespace across different install sources, channels, or packaging layouts and creating subtle runtime corruption.
- Calling enterprise distribution “the same build with different flags” when policy, update cadence, or bundled capabilities differ materially.
- Fabricating or copy-pasting update-channel/version-gate key names and allowed values instead of checking current vendor docs — e.g. inventing an `autoUpdatesChannel: "disabled"` value that doesn't exist (the real values are `latest`/`stable`; updates are stopped via `DISABLE_AUTOUPDATER`, a separate control). Any config key, env var, or CLI flag you generate for a real host product must be verified against that product's current docs, not inferred from a plausible-sounding pattern.

## Common Anti-Patterns

- Treating semantic version of the binary as the only compatibility signal.
- Shipping cache migrations without downgrade planning.
- Assuming plugin authors will discover breakage without host-level checks.
- Reusing one cache namespace for plugin installs that came from materially different paths or subdirs.
- Calling enterprise distribution “the same build with different flags.”
- Ignoring install footprint because each file seems small in isolation.

## Cross-Platform Patterns (Goose)

Goose's distribution model is more explicit than the Claude Code lineage on three fronts: white-label custom distributions, OSS-style install scripts, and foundation-level governance.

### Custom Distributions — white-label as a first-class channel

Goose supports `CUSTOM_DISTROS.md`: preconfigured builds with specific providers, extensions, branding, and bundled recipes. This is not a flag on the same binary — it is a distinct shipping artifact with a narrowed capability envelope and baked-in policy.

- **Pattern:** treat custom distros as a separate channel class, parallel to stable/beta/nightly. Compatibility matrices must track distro identity because a custom distro's plugin set is frozen at build time.
- **Anti-pattern:** representing enterprise or partner builds as "stable channel with a config file." That leaks partner-specific providers into the upstream compatibility matrix and makes breakage attribution impossible.
- **Recipe:** give each custom distro a distro ID, a pinned upstream commit, a recipe/extension manifest, and its own update policy. Users must see (in `--version` output and in telemetry) that they are on a distro build, not the main stable.

### Install-script duality and OSS install surface

Goose ships `download_cli.sh` and `download_cli.ps1` as canonical OSS install paths, alongside platform package managers. The scripts are the contract — they pin channel resolution, signature verification, and binary placement.

- **Pattern:** commit install scripts into the repo root with public, stable URLs. They serve as the source-of-truth install path when package managers are unavailable (CI, air-gapped, bleeding-edge).
- **Anti-pattern:** depending on one package manager (Homebrew-only, npm-only) as the install path for a coding agent that needs to reach varied developer environments.
- **Recipe:** one script per platform family (`sh` + `ps1`), each with explicit channel flag, checksum verification, and a documented unattended-install mode for enterprise automation.

### Governance and foundation-level trust

Goose operates under the **Agentic AI Foundation (AAIF)** within the Linux Foundation (founding contributors Block, Anthropic, OpenAI; transferred April 7, 2026; 170+ member organizations including AWS, Google, Microsoft et al.; Apache-2.0 license; documented `GOVERNANCE.md`, `MAINTAINERS.md`, `SECURITY.md`). For OSS coding agents, foundation-level governance is a trust signal for enterprise distribution.

- **Pattern:** separate release engineering (binary + update channels) from governance (who can accept a maintainer PR, who signs releases, who has CVE coordination authority). Both belong in the distribution surface.
- **Anti-pattern:** treating "open source" as a single checkbox. Enterprises buying custom distros need to know the upstream governance, release signing, and vulnerability-disclosure paths.
- **Recipe:** alongside release channels, publish `GOVERNANCE.md`, `MAINTAINERS.md`, `SECURITY.md`, and `deny.toml` (supply-chain gates). The `recipe-scanner` pattern generalizes as "static analysis for shipped artifacts" — validate not only code but also the YAML recipes and plugin manifests that your distro ships.

### Update channels, disabling auto-update, and enterprise version-pinning (Claude Code, verified 2026-07-11)

Claude Code's real update-channel surface is smaller than "stable/beta/nightly" naming would suggest, and the exact keys matter because a wrong one silently no-ops.

- **`autoUpdatesChannel`** (user settings, `~/.claude/settings.json`) takes exactly two values: `"latest"` (default — most recent release) or `"stable"` (roughly a week behind, skips releases with known major regressions). There is no `"disabled"`, `"none"`, or `"off"` value — a config with one of those strings does not turn updates off, it is simply an invalid channel name. **Known trap:** at least one sibling skill in this cluster previously fabricated a `"disabled"` channel value; treat any coding-agent doc or generated config that sets `autoUpdatesChannel` to something other than `latest`/`stable` as suspect until re-verified against `code.claude.com/docs/en/settings`.
- **To actually stop auto-updates**, set the `DISABLE_AUTOUPDATER` environment variable (e.g. `"env": {"DISABLE_AUTOUPDATER": "1"}` in settings.json, or export it in the shell/container). Channel selection and the update kill-switch are two different controls — don't conflate "pick a channel" with "turn updates off."
- **`requiredMinimumVersion`** and **`requiredMaximumVersion`** are managed-settings-only fields (MDM or a system `managed-settings.json`, never user/project settings) that block startup entirely outside the declared range — the CLI exits with an instruction to install an approved version. Contrast with the older **`minimumVersion`**, a soft floor that blocks downgrades via `claude update`/auto-update but does not stop a user already on an older build from starting Claude Code.
- **Fail-open nuance (the part non-experts miss):** an invalid or malformed `requiredMinimumVersion`/`requiredMaximumVersion` value is stripped rather than enforced — a bad policy push cannot brick the fleet by accidentally locking everyone out. Design your own hard version gates the same way: validate the gate value at the point it is *set*, and make the runtime's response to a malformed gate "ignore and log," never "refuse to start."

- **Pattern:** use `requiredMinimumVersion` to enforce a security patch floor and `requiredMaximumVersion` to freeze a release for a compliance period; use `autoUpdatesChannel: "stable"` for teams that want fewer regressions rather than a hard version freeze; use `DISABLE_AUTOUPDATER` only when a separate release process (image baking, golden AMI, offline install) already owns the version.
- **Anti-pattern:** using `minimumVersion` when you need a hard block, or assuming a channel setting also disables updates. A soft floor does not stop a user on an older build from starting Claude Code, and a channel choice is not a kill-switch.
- **Recipe:** document the current pinned range and channel choice in your enterprise settings file alongside the last-verified date. Track version bumps as a first-class release-communication concern, and re-verify exact key names against current docs before generating configs for users — do not rely on memory or a prior skill's copy.

### Desktop-runtime upgrade: Electron to Tauri (Goose 2.0, April 2026)

Goose 2.0 is migrating the desktop app from Electron to Tauri. Both old (Electron) and new (Tauri) desktop clients communicate with the shared ACP daemon rather than bundling separate runtimes. The migration is a case study for custom distribution operators: the distribution artifact changes (app bundle, binary size, OS trust signing), but the protocol contract (ACP) is stable. Users on old desktop builds can still interact with the new daemon; the surface change is UI, not protocol.

- **Pattern:** when migrating desktop runtimes, stabilize the daemon protocol first. Distribution channels then ship the new UI as a separate upgrade path from the daemon, and rollback is the previous UI version, not a full revert.
- **Anti-pattern:** coupling the desktop runtime to the daemon version with a hard parity check. That forces simultaneous upgrades for all distribution tiers and eliminates the rollback option for the UI.

### Build-time supply-chain gates (deny.toml + recipe-scanner)

Goose uses `deny.toml` (cargo-deny) for license/advisory/source gating at build, and `recipe-scanner/` to statically validate the recipes that will ship with the binary.

- **Pattern:** every shipping artifact — binary, plugin, recipe, extension manifest — has a build-time static gate. Nothing reaches a release channel without passing.
- **Anti-pattern:** scanning only code. Recipes and plugin manifests are executable-ish too; ship them through static validation as well.

## Navigation

### References

- [`references/packaging-updates-and-compatible-plugins.md`](references/packaging-updates-and-compatible-plugins.md) — Packaging, update policy, release channels, and plugin compatibility
- [`references/cache-migrations-and-install-channels.md`](references/cache-migrations-and-install-channels.md) — Cache versioning, state migrations, rollback, and local footprint control
- [`references/openai-codex-install-update-and-doctor.md`](references/openai-codex-install-update-and-doctor.md) — OpenAI Codex install channels, update target checks, app-server package variants, and doctor diagnostics

### Data

- [`data/sources.json`](data/sources.json) — Primary docs and implementation references for coding-agent release and distribution design

### Related Skills

- [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md)
- [`../ai-coding-agents-settings-policy/SKILL.md`](../ai-coding-agents-settings-policy/SKILL.md)
- [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Packaging and update mechanics depend heavily on the target OS, installer strategy, and enterprise controls. Preserve the release architecture, but verify the actual platform constraints before implementation.
- Cache and migration behavior must be tested on real upgraded installs, not only fresh environments.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
