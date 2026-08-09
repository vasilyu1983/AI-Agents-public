# Cross-Tool Context Template

Purpose: keep one canonical project context layer while routing tool-specific behavior to the correct files.

## Core Rule

Do not assume one file is universally loaded by every coding assistant.

Use this pattern instead:
1. Put shared project context in `AGENTS.md` when the toolchain supports it.
2. Put tool-specific instructions in tool-specific files.
3. Link to deeper docs instead of copying the same rules into multiple places.

## Recommended Surfaces (Verified March 2026)

| Tool | Primary surface | Tool-specific extensions |
|------|-----------------|--------------------------|
| Claude Code | `CLAUDE.md` | `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md`, `AGENTS.md`, `.github/agents/`, `.github/skills/` |
| Cursor | `.cursor/rules/` or root `AGENTS.md` | root `CLAUDE.md`, scoped rules, CLI approvals |
| Portable baseline | `AGENTS.md` | link to tool-specific files for overrides |

## Layering Pattern

### Shared layer: `AGENTS.md`

Keep only durable repo facts:
- repo purpose
- architecture summary
- repo map
- commands that actually run
- coding conventions
- constraints and gotchas

Use [minimal-agents.md](minimal-agents.md) when you need a starter.

### Claude-specific layer: `CLAUDE.md`

Put Claude Code behavior here:
- preferred workflows
- approval expectations
- subagent or hook guidance
- project-specific memory imports

Use [minimal-claudemd.md](minimal-claudemd.md) when you need a starter.

### Copilot-specific layer

Use:
- `.github/copilot-instructions.md` for repository-wide guidance
- `.github/instructions/*.instructions.md` for path- or task-specific rules
- `.github/agents/` for custom agents
- `.github/skills/` for reusable agent skills

### Cursor-specific layer

Use:
- `.cursor/rules/` for scoped rules
- root `AGENTS.md` as the shared baseline when appropriate
- root `CLAUDE.md` only if the workflow explicitly relies on it

## Suggested File Layout

```text
repo/
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── .cursor/
│   └── rules/
│       └── project.mdc
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/
│   │   └── backend.instructions.md
│   ├── agents/
│   │   └── reviewer.md
│   └── skills/
│       └── docs-ai-prd/
└── docs/
    ├── architecture.md
    └── feature-x-prd.md
```

## Copy-Ready Shared Context Skeleton

````markdown
# [Project Name]

[One sentence on the product and the repo's purpose]

## Outcomes

- Primary outcome: [what to optimize for]
- Non-goals: [what should not be changed casually]

## Repo Map

- `src/` - main implementation
- `tests/` - automated tests
- `docs/` - canonical specs and runbooks
- `scripts/` - repo tooling

## Commands

```bash
npm test
npm run build
npm run lint
```

## Conventions

- Follow surrounding patterns before introducing new ones
- Add or update tests when behavior changes
- Keep external facts source-backed and date-stamped when volatile

## Key Constraints

- [latency, compliance, compatibility, platform constraints]

## Gotchas

- [non-obvious behavior]
- [migration or legacy constraints]
````

## Copy-Ready Claude Overlay

````markdown
# Claude Code Project Notes

See `AGENTS.md` for shared repo context.

## Claude-Specific Rules

- Use planning mode for high-ambiguity or multi-file changes
- Prefer reading linked docs instead of pasting long context blocks
- Ask before destructive commands or non-obvious migrations
- Keep handoff notes focused on changed behavior, validation, and open risks
````

## Copy-Ready Copilot Overlay

````markdown
# Copilot Instructions

See `AGENTS.md` for shared repo context.

## Repository Guidance

- Match existing abstractions and file layout
- Use path-specific instruction files for area-specific rules
- Treat generated code as draft until tests and review pass
- Do not introduce dependencies without a stated reason
````

## Copy-Ready Cursor Rule

````markdown
---
description: Project-wide Cursor rules
alwaysApply: true
---

See `AGENTS.md` for shared repo context.

- Keep edits scoped and reviewable
- Prefer existing utilities over duplicate helpers
- Call out missing validation or unclear requirements instead of guessing
````

## Sync Checklist

- [ ] Shared facts live in one canonical place
- [ ] Tool-specific files only contain tool-specific behavior
- [ ] Commands and paths were verified against the repo
- [ ] No secrets, credentials, or customer data are present
- [ ] Volatile vendor details are linked to primary sources, not copied as facts

## Security Notes

Do not store:
- secrets, tokens, or credentials
- private internal URLs unless explicitly safe to share
- customer data or incident details

Safe to store:
- repo structure
- commands
- conventions
- high-level architecture
- non-sensitive operational guidance

## Verification

Use `data/sources.json` and `scripts/validate_sources.py` to keep vendor docs current.
