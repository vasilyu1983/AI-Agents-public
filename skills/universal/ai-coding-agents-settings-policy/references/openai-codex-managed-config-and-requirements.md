# OpenAI Codex Managed Config And Requirements

Source kind: the vendor config reference, the managed-configuration page, and the Codex config loader (`codex-rs/config`, `docs/config.md`) read at the release tag you target. Look them up before copying a key, value, or layer order.

Web sources:

- OpenAI, "Running Codex safely at OpenAI", May 8, 2026: https://openai.com/index/running-codex-safely/
- Codex configuration docs entrypoint: https://developers.openai.com/codex

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

Some clients expose a configurable budget for the available-skills catalog (`skills.max_context_tokens` in Codex). Look up its current default and cap in the [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) before choosing a value. Advice that this budget cannot be configured is outdated for clients supporting this setting.

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

   The value is an example; keep it within the documented cap. This is a chosen larger catalog allocation, not a universal default or a guarantee that everything fits. It does not change the model context window, compaction, permissions, plugin enablement, or invocation policy.

4. Parse the result with a TOML parser and compare parsed before/after settings: only this value should differ. A temporary session comparison can use `codex -c 'skills.max_context_tokens=10000'`; it does not persist the setting. Inspect the selected client's diagnostic help before using any version-specific prompt-render command.
5. Verify the persistent value without the CLI override. Compare loader errors and discovered/enabled counts separately from rendered catalog count, description retention, and warnings. Test both standalone and desktop-bundled clients when both are in use; a successful CLI parser check alone is insufficient.
6. Open a fresh desktop session without interrupting active sessions. Confirm whether the original warning remains with that session's complete plugin catalog. Report “configuration saved,” “local rendering checked,” and “fresh desktop warning checked” separately. If the warning persists, inspect catalog contributors and targeted host controls before considering a smaller installation; do not blanket-disable skills or plugins.

### Rollback

Restore the previous value, or remove only `skills.max_context_tokens` if it was absent. Remove an added `[skills]` table only if it is now empty. Preserve any settings changed after the backup; use the backup as comparison evidence rather than overwriting newer edits. Parse again and start a fresh session to confirm the effective default or previous value.

## Notes And Searchable Context History

The [OpenAI configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) documents an experimental notes-and-searchable-history mode (`features.context_management.experimental_mode`) for preserving accumulated details. Look up its current key and account-plan requirements before enabling it.

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
