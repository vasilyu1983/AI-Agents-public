# Managed Delivery And Fleet Version Controls

How a fleet operator controls which coding-agent CLI version runs on managed machines: release channels, hard version ranges, soft floors, update kill switches, install provenance, and staged rollout of a new CLI version. Plugin and cache compatibility across upgrades belongs to [`../../ai-coding-agents-plugins/SKILL.md`](../../ai-coding-agents-plugins/SKILL.md#compatibility-cache-identity-and-upgrades).

## Table Of Contents

- [Separate Controls](#separate-controls)
- [Channel Design](#channel-design)
- [Version Gates](#version-gates)
- [Fail Open Or Fail Closed Per Key Class](#fail-open-or-fail-closed-per-key-class)
- [Install Provenance And Update Targets](#install-provenance-and-update-targets)
- [Staged Rollout Of A New CLI Version](#staged-rollout-of-a-new-cli-version)
- [Worked Decision](#worked-decision)
- [Lookup Steps](#lookup-steps)

## Separate Controls

Each row is its own control. Hosts expose them as separate keys, and conflating two of them leaves a gap.

| Control | What it does | What it does not do | Set it from |
|---|---|---|---|
| Release channel | Chooses which release stream the updater follows | Does not stop updates; an invalid channel name is not "off" | Any scope; managed makes it non-negotiable |
| Background-check suppression | Stops the periodic automatic update check | Leaves manual update and install commands working | Managed or the image's environment |
| All-path update block | Blocks every update path, including manual update and install commands | Does not choose a version; the image or release process must | Managed |
| Hard version range (minimum and maximum) | Blocks startup outside the range and tells the user to install an approved version | Does not end sessions that are already running | Managed only |
| Soft floor | Stops the updater from moving below the floor | Does not stop a user already on an older build from starting | Look up its scope line |

A fleet whose version is owned by a golden image, a package pipeline, or an offline install needs the all-path block. Background-check suppression alone lets any user run the manual update command and drift off the image.

## Channel Design

Make every channel explicit: stable, pre-release, and enterprise-pinned or managed. For each channel, write down:

- who receives it
- how fast it rolls out
- whether automatic update is allowed
- what rollback path exists
- its migration posture: stable stays conservative on compatibility; pre-release may migrate earlier but must say so; a fast channel may invalidate caches aggressively only if users were told to expect it

Managed enterprise distribution is a different channel, not the self-serve build with different flags. Its update cadence, plugin allowlist, and bundled capabilities can intentionally lag the public release, and breakage attribution needs to know which channel a machine is on.

A custom distribution with baked-in policy is a channel class of its own. See the SKILL.md section "Custom distros as a read-only policy source".

## Version Gates

- Use a hard minimum for a security-patch floor.
- Use a hard maximum to freeze a release for a compliance or validation period.
- Use a channel choice when a team wants fewer regressions rather than a hard freeze.
- Use a soft floor only when a user on an older build may keep working until they next update.
- Set hard gates only from managed policy. A user or project file that carries the key is decorative at best (lock classes 1 and 2 in SKILL.md).
- Validate a gate value when it is set, not only when the runtime reads it.

## Fail Open Or Fail Closed Per Key Class

Decide per key class what the runtime does with a malformed value or with a value from a newer settings schema than it understands:

- **Gates whose enforcement could brick the fleet** (a version range): fail open with an alert. The runtime ignores and logs the bad gate. It never refuses to start because a policy push was malformed.
- **Restrictions whose loss widens capability** (deny rules, sandbox settings, allowed plugin or marketplace sources, managed-only locks): fail closed. Losing the restriction silently is worse than blocking startup.
- **Preferences** (model, theme, output style): load defaults and warn. Never overwrite the user's file.

State the class for every managed key you ship. Pair this with the managed-delivery failure mode in SKILL.md Host Rules: when the managed source cannot be fetched at all, regulated fleets fail closed and others run on last-known-good policy with a visible banner.

## Install Provenance And Update Targets

A fleet with several install paths (package manager, standalone installer, archive, image) can update one install while the shell keeps running another.

- Record install provenance at launch: which channel and which package root launched this binary.
- Before replacing anything, the updater confirms that the install came from the channel it will update through. A package-manager install is updated through the package manager; a standalone install through its own updater.
- When the update target cannot be proven, warn and include remediation, not just a failed status.
- Keep "where the CLI is installed" separate from "where it keeps state". A state-root override can move config, auth, logs, and transcripts independently of the install path, and a diagnostic needs both.
- Every install channel should be diagnosable by a support command that emits a redacted, machine-readable report.

## Staged Rollout Of A New CLI Version

The operator side of rolling a new CLI version to a fleet:

1. Before exposure, name the halt metrics (plugin-load failures, session-resume failures, crash rate), their thresholds, and who owns the halt decision.
2. Canary the new version on a small cohort, pinned with a managed range, before raising the managed minimum for everyone.
3. Raise the floor only after the canary shows no halt signal and plugin and cache compatibility has been checked on real upgraded machines, not fresh installs.
4. Keep the previous approved version installable until the rollback window closes. Lowering the managed maximum is the rollback lever, so it must not strand migrated state (see the plugins skill's partial-upgrade contract).
5. Announce version bumps as release communication: record the approved range, the channel, and the date it changed in the fleet's change log.

## Worked Decision

Task: pin the agent CLI for a large fleet built from a golden image, and stop self-updates.

- The image owns the version, so set the all-path update block from managed policy. Suppressing only the background check leaves the manual update command working.
- Set a hard minimum at the image's version to stop anyone starting an older, unpatched build from another install path.
- Set a hard maximum only if the compliance process requires a freeze; otherwise the all-path block already holds the version.
- Classify the range keys as fail-open-with-alert and every restriction key as fail-closed.
- Re-image to upgrade, following the staged rollout above.

## Lookup Steps

Key names, allowed values, defaults, and which scopes honor each key change between releases. Before writing config:

- Find the host's channel key and its allowed values, the background-check and all-path update controls, and the hard-range and soft-floor keys in the host's managed-settings or settings reference. For Claude Code that is the settings and setup docs; for Codex the config reference and managed requirements docs.
- Check each key's scope line to place it in a lock class.
- Check the host's documented behavior for an invalid gate value before assuming fail-open.
- Never generate a key name or value from memory or from another skill's copy. A plausible key that does not exist silently does nothing.
