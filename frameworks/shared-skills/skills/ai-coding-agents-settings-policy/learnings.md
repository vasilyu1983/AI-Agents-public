# ai-coding-agents-settings-policy — Learnings

## Patterns That Work

- [2026-07-11] When one repo's `.claude/settings.local.json` has a defect, sweep every repo: `find ~/Projects -maxdepth 4 -path '*/.claude/settings*.json' -not -path '*/node_modules/*'` then batch-check with `jq`. A copied "maximum autonomy" template had spread the same invalid `mcp__*` rule and `bypassPermissions` mode to 7 of 17 repos.
- [2026-07-11] Global `~/.claude/settings.json` hygiene: with bare tool allows (`Read`, `Bash`) present, path- and prefix-scoped variants of the same tool are dead weight — prune to either the bare rule or the specific ones, never both, so the file shows what is actually granted.

## Mistakes to Avoid

- [2026-07-11] Settings templates copied between repos carry defects with them; fixing only the repo where the warning surfaced leaves the same issue live everywhere else the template landed. Treat any settings bug as a fleet-wide search, not a single-file fix.
- [2026-07-11] Legacy duplicate keys accumulate silently: `voiceEnabled: true` alongside `voice: {enabled: true}` — the flat boolean is the deprecated form; keep the structured object.

## Domain Knowledge

- [2026-07-11] Settings precedence: user → project (`.claude/settings.json`) → local (`.claude/settings.local.json`), later overrides earlier — so a project-local `defaultMode` beats the global one, and cleaning the global file changes nothing in repos with local overrides.
- [2026-07-11] Invalid permission rules in settings files do not fail loading; they are skipped with a per-session startup warning, so a broken rule can sit unnoticed for months while appearing to grant access.
- [2026-07-11] `skipDangerousModePermissionPrompt` and `skipAutoPermissionPrompt` suppress the one-time bypass/auto opt-in dialogs machine-wide — combined with project-level `bypassPermissions` this removes every reminder that a repo runs unguarded.

- [2026-07-11] Web-verify audit of this skill (`code.claude.com/docs/en/settings`, `code.claude.com/docs/en/hooks`, `learn.chatgpt.com/docs/config-file/config-reference`, all checked 2026-07-11): (1) `settings-precedence-table.md` and the SKILL.md Quick Reference had local/project/user inverted — corrected to the verified order `managed > CLI flags > local > project > user`; (2) three Claude Code managed-policy keys (`strictPluginOnlyCustomization`, `policyHelper`, `parentSettingsBehavior`) could not be verified in current docs and were removed rather than kept as unsourced claims; (3) `disableAutoMode`/`disableAgentView`/`disableBundledSkills`/`autoUpdatesChannel` were mislabeled as managed-only — they exist in all settings scopes, policy just makes them non-negotiable; `autoUpdatesChannel` valid values are `"latest"`/`"stable"`, not `"stable"`/`"preview"`/`"disabled"`; (4) Codex `approval_policy` value was `"unless-trusted"` in this skill but current docs use `"untrusted"`; (5) Codex named profiles are separate `$CODEX_HOME/<name>.config.toml` files, not `[profiles.NAME]` tables inside `config.toml` as previously shown. `cleanupPeriodDays` default of 30 (min 1) was confirmed accurate and added as an explicit fact to guard against the same error propagating here.

## Open Questions

## Consolidated Principles
