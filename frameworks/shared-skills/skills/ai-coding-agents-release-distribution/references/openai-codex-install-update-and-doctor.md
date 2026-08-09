# OpenAI Codex Install Update And Doctor

Source snapshot: OpenAI Codex commit `9f42c89c0112771dc29100a6f3fc904049b2655f` (2026-05-24), especially `README.md`, `codex-rs/cli/src/main.rs`, `codex-rs/cli/src/doctor`, `.github/scripts/build-codex-package-archive.sh`, and `codex-rs/app-server-daemon/README.md`.

Web sources checked 2026-05-25:

- Codex product page: https://openai.com/codex/
- OpenAI, "Running Codex safely at OpenAI", May 8, 2026: https://openai.com/index/running-codex-safely/
- OpenAI, "Building a safe, effective sandbox to enable Codex on Windows", May 13, 2026: https://openai.com/index/building-codex-windows-sandbox/

Re-verified 2026-07-11 against `github.com/openai/codex` (install methods, npm/Homebrew commands) and `developers.openai.com/codex/environment-variables` (`CODEX_HOME` semantics). Install-channel commands and `CODEX_HOME` behavior below confirmed current as of this date.

## Table Of Contents

- [Design Goal](#design-goal)
- [Install Channels](#install-channels)
- [Update Target Checks](#update-target-checks)
- [Package Variants](#package-variants)
- [Doctor As Release Support](#doctor-as-release-support)
- [Known Traps](#known-traps)

## Design Goal

Release design for a coding-agent CLI must cover more than publishing a binary. Codex has multiple install paths, managed package roots, app-server variants, update checks, sandbox helpers, plugin bundles, and diagnostics that explain whether an update will hit the running install.

## Install Channels

Codex supports (verified 2026-07-11 against `github.com/openai/codex` and `developers.openai.com/codex`):

- hosted install script (`curl -fsSL https://chatgpt.com/codex/install.sh | sh`; PowerShell equivalent for Windows)
- npm package: `npm install -g @openai/codex` (the unscoped `codex` package on npm is an unrelated project — the scope is load-bearing)
- Homebrew cask: `brew install --cask codex`
- GitHub release archives (platform-specific binaries, e.g. `codex-aarch64-apple-darwin.tar.gz`, `codex-x86_64-unknown-linux-musl.tar.gz`)

`CODEX_HOME` is not itself an install channel — it is an environment variable that overrides the root directory (`~/.codex` by default) for all persistent state: `config.toml`, `auth.json`, logs, session transcripts, and installed-plugin metadata. Any of the four channels above can point at a relocated `CODEX_HOME` (e.g. a project-scoped automation identity: `CODEX_HOME=$(pwd)/.codex codex exec ...`). Do not conflate "where Codex is installed" with "where Codex keeps its state" — they vary independently, and a doctor/diagnostic check needs both.

For your own runtime, document which channel is authoritative for each environment and what update command owns it.

## Update Target Checks

Codex doctor checks whether an npm update would target the package root that launched the current binary. This prevents a common failure: `npm install -g` updates one installation while the shell keeps running another.

Copy the pattern:

- record install provenance at launch
- compare update target with running package root
- warn when the update command cannot be proven
- include remediation, not just a failed status

## Package Variants

Codex release scripts distinguish primary and app-server package bundles. The app-server entrypoint is a separate release concern because remote clients may depend on it independently of the interactive CLI.

Design implication:

- treat CLI, app-server, shell completions, sandbox helpers, and plugin bundle archives as release artifacts with compatibility contracts
- version their schemas and protocol boundaries
- test partial upgrade and downgrade behavior

## Doctor As Release Support

Codex's `doctor` command is part of release distribution. It checks installation, updates, config, auth, MCP, sandbox helpers, terminal environment, app-server state, and more. It can emit redacted JSON for support tooling.

Release checklist:

- every install channel should be diagnosable
- every helper binary should have a readiness check
- every update path should have a target check
- remote/app-server background state should be inspectable without mutating it

## Known Traps

- Publishing several install channels without proving which one `update` affects.
- Treating app-server as an internal detail when remote clients depend on it.
- Shipping sandbox helpers without doctor checks for missing or unsupported helpers.
- Making support ask users for screenshots instead of a redacted JSON report.
- Updating daemon and app-server processes in the wrong order.
