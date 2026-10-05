---
description: In-directory entry point and frontmatter conventions for the agents-subagents reference library.
last_verified: 2026-09-02
status: stable
---

# References

In-directory entry point. For the curated, task-shaped TOC, see [navigation-index.md](navigation-index.md).

## Conventions

Every file in this directory carries YAML frontmatter for auditability:

```yaml
---
description: <one-line summary>
last_verified: <YYYY-MM-DD>
status: stable | community-reported | dated-snapshot | pointer
---
```

- `stable` — content cross-checked against current Anthropic / Claude Code / Codex documentation.
- `community-reported` — load-bearing claims rest on practitioner reports or open issues; verify before relying operationally.
- `dated-snapshot` — a point-in-time measurement whose evidence window has closed. Historical only; re-run the method before acting on it.
- `pointer` — a stub that redirects to the canonical file. Kept so existing inbound links keep resolving.

`last_verified` is the date the file was last cross-checked, not the date it was edited. This
directory carries **one** freshness convention: the frontmatter key. Do not add a prose
`_Last verified: ..._` line — `validate_catalog_integrity.py` reads the frontmatter, and a
second stamp is a second thing to forget.

A `last_verified` older than the file's own last commit date means the file was edited
after it was last checked. `validate_catalog_integrity.py` lists those as `STALE STAMP`
(advisory), and fails on them under `--strict-freshness`.

## Where to start

- **Picking a pattern or trap** → [navigation-index.md](navigation-index.md)
- **Game-theoretic team mechanisms** → [game-theory-agent-teams.md](game-theory-agent-teams.md) (agent-team applied recipes) — canonical 22-mechanism playbooks in [`foundations-game-theory`](../../foundations-game-theory/SKILL.md)
- **Runtime-specific behavior (Claude Code vs Codex)** → [runtime-surfaces.md](runtime-surfaces.md)
- **Workflow and team launch contracts** → [workflow-contracts.md](workflow-contracts.md)
- **Tool, permission, MCP, isolation** → [agent-tools.md](agent-tools.md)
- **Traps and anti-patterns** → [traps-and-antipatterns.md](traps-and-antipatterns.md)

If a file is missing from `navigation-index.md`, treat that as an index gap, not a missing file — open the directory and read directly.
