# agents-hooks — Learnings

## Patterns That Work

## Mistakes to Avoid

- [2026-07-11] Settings precedence was wrong: real order is managed > CLI flags > settings.local.json > settings.json > user settings.json — local beats project/user, not last (code.claude.com/docs/en/settings).
## Domain Knowledge

- [2026-07-11] Hooks can live in plugin hooks/hooks.json and in skill/agent frontmatter (once:true = run-then-remove); tool-event hooks also accept an 'if' permission-rule field to scope beyond matcher.
- [2026-06-18] Codex CLI now has lifecycle hooks (hooks.json / [hooks] in config.toml), ~10 events mirroring Claude, command-handlers only, same stdin schema. No longer notify-only — but verify-first (firing bugs codex#21639/#17532, no Windows).
- [2026-06-18] Hook event count reached 30 (verified 2026-06-18); the 30th is InstructionsLoaded — observability-only (cannot block), fires when CLAUDE.md/includes/glob-matched instructions load. Re-verify count each audit; validators do not catch drift.
- [2026-07-11] Correction to the 2026-06-18 entry above: Codex hooks.json now supports Windows via a `commandWindows` override — the "no Windows" caveat is stale. The firing-reliability bugs (codex#21639, codex#17532) are still open, so verify-first still stands; only the Windows part changed. Model/pricing tables in reference docs (budget-and-loop-hooks.md) also drift fast — Claude Opus 4.8 and Sonnet 5 superseded Opus 4.7/Sonnet 4.6 as current-gen pricing anchors, and OpenAI retired GPT-5/GPT-5 Mini for GPT-5.4/5.5 — re-check any hardcoded model price table against official pricing pages every audit, not just event/API surface claims.
- [2026-07-11] Claude Code runs all hooks matching an event in parallel (not sequentially), dedupes identical command/URL hooks, and does not document a tie-break rule for conflicting allow/deny outputs — treat "deny wins" as a design assumption to build in, not a guaranteed runtime behavior. Also: `allowManagedHooksOnly` can silently suppress user/project/plugin hooks in managed environments, which looks identical to a broken hook script — check settings precedence before debugging the script itself.

## Open Questions

## Consolidated Principles

