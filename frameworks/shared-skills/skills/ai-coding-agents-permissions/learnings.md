# ai-coding-agents-permissions — Learnings

## Patterns That Work

- [2026-07-11] Audit fix for over-permissive local setups: switch `defaultMode: "bypassPermissions"` → `"auto"` and delete blanket `Bash(*)`/bare-tool allows; keep specific prefix rules (`Bash(npm run build:*)`) so routine commands stay frictionless while the classifier gates the rest. Applied across 7 repos with no day-to-day workflow change.
- [2026-07-11] When auditing settings for embedded secrets, grep permission files for token shapes (`eyJ` JWT, `Bearer [A-Za-z0-9._-]{30,}`, `sk-`, `ghp_`, `AIza`, `xox[bap]-`) — "always allow" clicks persist full command strings, including auth headers, into `.claude/settings.local.json`.

## Mistakes to Avoid

- [2026-07-11] A bare `Bash` (or `Bash(*)`) allow rule silently disables the auto-mode classifier for all shell commands — allow rules bypass classification unless `autoMode.classifyAllShell: true`. Blanket Bash allow + auto mode gives bypass-level exposure while looking safe.
- [2026-07-11] Approving a raw `curl` with an `Authorization: Bearer <token>` header via "always allow" wrote the live token into `settings.local.json`, where it sat in plaintext (and in transcripts) for months. Secrets belong in `.env.local`; never persist an allow rule containing a credential — and rotate any token found this way.
- [2026-07-11] With `defaultMode: "bypassPermissions"`, the entire allow/ask/deny structure is decorative — carefully curated `ask` lists for `rm -rf`/`git push --force`/`DROP` enforce nothing. Verify the mode before trusting any rule list during an audit.

## Domain Knowledge

- [2026-07-11] Settings precedence is managed > CLI > local project > shared project > user, but a deny rule from any scope blocks regardless of that precedence order — deny beats allow at every scope.
- [2026-07-11] Claude Code v2.1.186+ has background subagents escalate denied-by-default tool calls to the parent session (labeled with subagent name) instead of silently auto-denying them.
- [2026-07-11] Codex AskForApproval drifted since a May-2026 pinned source: UnlessTrusted now serializes "untrusted" (not "unless-trusted"); standalone OnFailure is gone, "on-failure" is now just a serde alias for OnRequest.
- [2026-07-11] Claude Code allow rules reject wildcard tool names: `mcp__*` is invalid and skipped with a startup warning. An MCP allow rule must name a literal server (`mcp__<server>` or `mcp__<server>__toolglob*`); wildcards anywhere are only legal in deny and ask rules.
- [2026-07-11] Permission precedence is deny > ask > allow, so `ask` entries still gate commands matched by broader allow rules (in modes that consult rules at all).
- [2026-07-11] Absolute paths in Read/Edit rules use a double-slash prefix (`Read(//Users/x/**)`); a single leading slash is resolved relative to the settings file's directory, so `Read(/Users/x/**)` in user settings does not match what it appears to.

## Open Questions

## Consolidated Principles
