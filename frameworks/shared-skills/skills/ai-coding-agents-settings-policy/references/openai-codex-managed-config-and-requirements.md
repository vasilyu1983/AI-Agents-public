# OpenAI Codex Managed Config And Requirements

Source snapshot: OpenAI Codex commit `9f42c89c0112771dc29100a6f3fc904049b2655f` (2026-05-24), especially `codex-rs/config/src/state.rs`, `codex-rs/config/src/loader`, and `docs/config.md`.

Web sources checked 2026-05-25:

- OpenAI, "Running Codex safely at OpenAI", May 8, 2026: https://openai.com/index/running-codex-safely/
- Codex configuration docs entrypoint: https://developers.openai.com/codex

Re-verified 2026-07-11 against `learn.chatgpt.com/docs/config-file/config-reference`. Two details from the May snapshot had drifted and are corrected inline below: `approval_policy` uses `"untrusted"` (not `"unless-trusted"`), and named profiles are separate `$CODEX_HOME/<name>.config.toml` files, not `[profiles.NAME]` tables inside `config.toml`. `allow_managed_hooks_only` in `requirements.toml` (see "Managed Hooks Only" below) was independently re-confirmed as current.

## Table Of Contents

- [Design Goal](#design-goal)
- [Layer Stack](#layer-stack)
- [Requirements Are Constraints](#requirements-are-constraints)
- [Managed Hooks Only](#managed-hooks-only)
- [Debuggability](#debuggability)
- [Known Traps](#known-traps)

## Design Goal

Separate user preferences from organization requirements. Codex's config loader keeps a stack of config layers, records source metadata, and carries requirements that constrain the derived runtime config.

## Layer Stack

Codex models config as entries with:

- source name
- parsed TOML
- raw TOML when available
- version/fingerprint
- disabled reason
- associated `.codex/` folder for project-level config
- hook config folder override for linked worktrees

The layer stack is ordered from lowest to highest precedence. Keep this explicit so debug output can explain why a setting won.

## Requirements Are Constraints

Codex distinguishes config layers from requirements. A managed requirement is not just a higher-precedence preference; it is a constraint that later config derivation must obey.

Use this distinction in new runtimes:

- config says "what this user/project wants"
- requirements say "what this environment permits"
- policy failures should be surfaced before tools execute

## Managed Hooks Only

The current Codex docs note `allow_managed_hooks_only = true` in `requirements.toml`: user, project, and session hooks are ignored while managed hooks remain allowed. This setting is requirements-only; placing it in normal user config must not activate it.

This is a good pattern for high-risk surfaces:

- allow organization-managed automation
- suppress user/project-provided hooks in locked environments
- make the lock visible in config debug output

## Debuggability

A production settings system needs a debug surface that can show:

- loaded layers
- disabled layers and reasons
- raw source path or managed source class
- active profile
- requirements source
- startup warnings
- hook folder used for each layer

Without this, policy support turns into guesswork.

## Known Traps

- Treating managed config as just "another config file" instead of a constraint source.
- Letting a user config key enable a requirements-only security mode.
- Hiding disabled layers, which makes operators think a setting was ignored randomly.
- Resolving hooks from the wrong worktree when project config is linked.
- Applying config reloads without re-sanitizing permissions, hooks, and plugin surfaces.
