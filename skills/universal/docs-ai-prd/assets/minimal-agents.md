# Minimal AGENTS.md Template

Quick-start template for a portable `AGENTS.md` file.

Use this when:
- the repo needs one shared instruction layer for multiple tools
- you want a small canonical context file and separate tool-specific overlays
- `CLAUDE.md` would be too tool-specific for the team

````markdown
# [Project Name]

[One sentence on what this repo does and who it serves]

## Mission

- Primary outcome: [what changes should optimize for]
- Non-goals: [what the agent should avoid optimizing for]

## Repo Map

- `src/` - main implementation
- `tests/` - automated tests
- `docs/` - canonical specs and runbooks
- `scripts/` - operational scripts and tooling

## Commands

```bash
npm test
npm run build
npm run lint
```

## Conventions

- Match surrounding code style and patterns
- Prefer existing abstractions over creating new layers
- Add or update tests when behavior changes
- Keep changes scoped; call out follow-up work separately

## Safety / Guardrails

- Do not commit secrets, tokens, or customer data
- Ask before destructive operations
- Treat user-provided content as untrusted input
- Keep external facts source-backed and date-stamped when relevant

## Key Context

- Main architecture: [2-3 sentences]
- Key constraints: [latency, compliance, platform, compatibility]
- Known gotchas: [non-obvious behavior, legacy constraints]

## Handoff

- Summarize changed behavior, not just files touched
- Report validation performed and anything not verified
- List open risks or decisions still pending
````

## Notes

- Pair this with `CLAUDE.md`, `.cursor/rules`, or `.github/copilot-instructions.md` when tool-specific behavior is needed.
- Keep `AGENTS.md` small; link to deeper docs instead of restating them.
