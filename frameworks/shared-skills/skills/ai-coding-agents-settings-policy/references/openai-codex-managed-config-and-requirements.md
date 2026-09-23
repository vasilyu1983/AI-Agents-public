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
- [Skill Catalog Context Budget](#skill-catalog-context-budget)
- [Notes And Searchable Context History](#notes-and-searchable-context-history)
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

## Skill Catalog Context Budget

Verified 2026-09-11 against the [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference): `skills.max_context_tokens` accepts a positive integer for the available-skills catalog. The default is 2% of the model context window; explicit overrides are capped at 10,000 tokens. Advice that this budget cannot be configured is outdated for clients supporting this setting.

“Exceeded skills context budget” concerns the initial catalog of names, descriptions, and paths. Separate three observations: a skill discovered and enabled by the loader, its entry retained in model-visible context, and its full instructions loaded on selection. Loader success does not prove catalog inclusion. A compact routing graph provides navigation but does not filter native discovery; shortening full skill bodies does not directly fix this catalog limit. See [agents-skills](../../agents-skills/SKILL.md) for portable content and host-specific discovery controls.

### Apply and verify

1. Identify the actual client and config home (`$CODEX_HOME`, default `~/.codex`). Record existing `skills.max_context_tokens` and any CLI, profile, project, or managed overrides. Do not print the whole config because it can contain secrets.
2. Back up the existing file beside it with a unique timestamp and preserve its permissions, for example:

   ```bash
   skill_config_path="${CODEX_HOME:-$HOME/.codex}/config.toml"
   cp -p "$skill_config_path" "$skill_config_path.skills-budget.$(date +%Y%m%dT%H%M%S).bak"
   ```

3. Merge the following into the existing table. Do not append a duplicate `[skills]`, replace the whole file, or disturb `[[skills.config]]` entries. If the file does not exist, create it with user-only permissions and record that there was no original file.

   ```toml
   [skills]
   max_context_tokens = 10000
   ```

   This is a chosen larger catalog allocation, not a universal default or a guarantee that everything fits. It does not change the model context window, compaction, permissions, plugin enablement, or invocation policy.

4. Parse the result with a TOML parser and compare parsed before/after settings: only this value should differ. A temporary session comparison can use `codex -c 'skills.max_context_tokens=10000'`; it does not persist the setting. Inspect the selected client's diagnostic help before using any version-specific prompt-render command.
5. Verify the persistent value without the CLI override. Compare loader errors and discovered/enabled counts separately from rendered catalog count, description retention, and warnings. Test both standalone and desktop-bundled clients when both are in use; a successful CLI parser check alone is insufficient.
6. Open a fresh desktop session without interrupting active sessions. Confirm whether the original warning remains with that session's complete plugin catalog. Report “configuration saved,” “local rendering checked,” and “fresh desktop warning checked” separately. If the warning persists, inspect catalog contributors and targeted host controls before considering a smaller installation; do not blanket-disable skills or plugins.

### Rollback

Restore the previous value, or remove only `skills.max_context_tokens` if it was absent. Remove an added `[skills]` table only if it is now empty. Preserve any settings changed after the backup; use the backup as comparison evidence rather than overwriting newer edits. Parse again and start a fresh session to confirm the effective default or previous value.

### Historical local evidence and limits

On 2026-09-11, standalone CLI `0.154.0` and desktop-bundled `0.153.4` accepted the temporary override. The local prompt-render comparison retained 230 entries while the skill section increased from 22,218 to 40,454 characters; descriptions were still shortened. These are diagnostic character counts, not token measurements or a supported capacity promise. The diagnostic renderer did not reproduce the desktop session's complete plugin catalog, so it did not prove elimination of the reported 186 omitted entries. These versions identify the tested binaries, not current-version recommendations.

## Notes And Searchable Context History

Verified 2026-09-05 against the [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) and an installed Codex CLI. The documentation names `features.context_management.experimental_mode` and describes notes plus searchable history for preserving accumulated details. It requires ChatGPT sign-in on Plus, Pro, or Pro Lite.

For requests such as “save notes across context windows,” “search earlier messages and tool calls,” or “make Codex less forgetful,” merge this into the existing user configuration at `$CODEX_HOME/config.toml` (default `~/.codex/config.toml`):

```toml
[features]
memories = true
context_management = { experimental_mode = true }
```

Do not create a duplicate `[features]` table or overwrite unrelated settings. Back up the file first. Keep the selected model and its context/compaction limits unchanged unless the user separately requests a supported change.

- `context_management.experimental_mode` enables the experimental notes and searchable-history mechanism across context windows. Local CLI inspection found history operations for listing windows, filtering items by role/tool, reading items, and searching literal content, plus note read/write/append operations. This supports recovering message and tool-call detail; it does not establish that every past conversation is automatically indexed.
- `memories` is the separate persistent-memory feature. Enabling it alone does not establish that cross-window history tools are available. The reference also exposes `memories.generate_memories` and `memories.use_memories`, both defaulting to `true`; inspect explicit overrides before claiming memory generation or use is enabled.
- This improves recoverability without increasing the model's physical context window. Do not inflate `model_context_window` or suppress compaction to simulate more capacity.

Validate with:

```bash
codex --version
codex login status
codex features list | rg 'context_management|memories'
```

The installed CLI accepted the documented inline-table form and reported both features enabled. It also accepted the older `context_management = true` form via `codex features enable context_management`; prefer the documented `experimental_mode` form. CLI acceptance is configuration evidence, not proof of successful recovery after a context transition.

Restart Codex and use a fresh session to test runtime availability. Check that the relevant note/history tools are exposed and that a harmless checkpoint can be recovered after a context transition. Runtime, account, or managed-policy differences may affect availability; the inspected binary contained an explicit code-mode history-tool limitation, so do not promise support solely from a true feature flag. Report separately whether configuration was saved, the feature is enabled, and recovery was actually tested. Keep the experimental status visible.

## User-Selected Runtime Baseline (2026-09-07)

For this workspace, the selected runtime baseline uses Astra low for the main agent and heavy roles, Luna max for subagents without explicit model/effort fields, and a cap of 12 spawned agents. Explicit mechanical roles retain Luna low. The executable tier policy is owned by `agents-subagents/data/model-policy.json`; its [configuration example](../../agents-subagents/references/cost-control.md) shows the complete configuration.

The user explicitly selected `model_auto_compact_token_limit = 282000` with scope `total`. This is a custom threshold, not a documented standard or a guarantee of lower token usage. Keep this top-level setting separate from `[features]`, where `context_management = { experimental_mode = true }` belongs. Neither setting grants a larger context window. Confirm the selected client's supported window before interpreting the threshold as reachable; do not add a 1M override just to match an API model specification.

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
