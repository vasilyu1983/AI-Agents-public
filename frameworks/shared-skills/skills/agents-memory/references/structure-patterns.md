# Structure Patterns

## Table of Contents

- [Hooks vs Project Memory](#hooks-vs-project-memory)
- [Three-Tier Boundaries](#three-tier-boundaries)
- [Progressive Disclosure](#progressive-disclosure)

## Hooks vs Project Memory

`AGENTS.md` and `CLAUDE.md` are advisory — agents follow them ~80% of the time but may skip instructions under context pressure or ambiguity. For requirements that must never be skipped, use hooks instead.

| Need | Use |
|------|-----|
| Guideline, preference, convention | `AGENTS.md` / `CLAUDE.md` |
| Hard requirement, gating check | Hook (PreToolUse, PostToolUse, etc.) |
| Lint before commit | Hook |
| Prefer TypeScript for new files | Project memory |
| Never commit secrets | Hook + project memory |

Rule of thumb: if skipping the instruction once would cause real damage, enforce it with a hook. If it is a preference that can tolerate occasional exceptions, keep it in project memory.

## Three-Tier Boundaries

Structure agent permissions using an explicit Always / Ask / Never model rather than mixing constraints and preferences in prose. This pattern reduces ambiguity and improves compliance by giving the agent clear decision rules.

```markdown
## Boundaries

### Always Do
- Run tests after code changes
- Update types when changing function signatures
- Read existing similar code before writing new code
- Spawn multiple subagents in the same turn when fanning out across independent files, items, or investigations
- Do NOT spawn a subagent for work you can complete in a single response

### Ask First
- Installing new dependencies
- Modifying database schema
- Changing API contracts or public interfaces
- Deleting files

### Never Do
- Force-push to main
- Commit secrets or credentials
- Delete test files or remove failing tests
- Modify authentication systems without review
```

Place this section near the top of `AGENTS.md` so it is seen early in the context window.

## Progressive Disclosure

Keep the root memory file lean by pointing to detailed docs instead of inlining them. The agent reads pointers in every session but only loads the full documents when working in the relevant area.

```markdown
## Documentation (load on demand)

- `docs/architecture.md` — system design and module relationships
- `docs/api-patterns.md` — REST conventions, error handling
- `docs/testing-guide.md` — advanced testing patterns and fixtures
```

For Claude Code, these can use `@docs/architecture.md` import syntax. For Codex, prefer nested `AGENTS.md` files or plain prose pointers. The goal is identical: keep hot memory under 150 lines while preserving access to deep context.
