# AGENTS.md (per source-repo template)

> Drop a short `AGENTS.md` like this into each **source repo** so any tool
> (Claude Code, Codex, Copilot) routes back to this hub instead of
> re-deriving cross-repo context. Keep it tiny — it is a pointer.

```markdown
# AGENTS.md — <repo>

This repo belongs to the **<domain>** domain.
Cross-repo context lives in the requirements hub, not here.

- Hub: <relative-or-URL path to requirements-hub>
- This repo's catalog page: <hub>/<domain>/as-is/<repo>.md
- Domain overview: <hub>/<domain>/README.md
- Binding rules: <hub>/rules/

## Local conventions (non-inferable only)
- <commands / boundaries an agent cannot infer from the code>

Do not paste cross-repo inventories here. Update the hub catalog page.
```

Replace placeholders. The hub is the system of record for anything that
spans repos; the per-repo `AGENTS.md` only carries what is local and
non-inferable.
