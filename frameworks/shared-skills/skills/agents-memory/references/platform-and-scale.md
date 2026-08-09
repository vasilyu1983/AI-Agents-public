# Platform and Scale

## Table of Contents

- [Path-Scoped Rules](#path-scoped-rules)
- [Cross-Platform Strategy](#cross-platform-strategy)
- [Large Repo Guidance](#large-repo-guidance)
- [Memory Progression](#memory-progression)

## Path-Scoped Rules

Claude Code supports YAML frontmatter in `.claude/rules/*.md` to scope rules to specific file patterns using the `paths` field. Use this for rules that only apply to parts of the codebase:

```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/routes/**/*.ts"
---
# API Layer Rules

- All endpoints must validate input with Zod schemas
- Return RFC 7807 Problem Details for errors
- Use dependency injection via the container
```

Rules without a `paths` field load unconditionally at launch. Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use. Glob patterns support brace expansion (`*.{ts,tsx}`).

This keeps global memory clean and loads rules only when the agent touches matching files. Codex does not use this mechanism; for Codex, use nested `AGENTS.md` files in the relevant directories instead.

## Cross-Platform Strategy

- Recommended portable baseline: keep `AGENTS.md` as the shared source of truth.
- Claude Code can bridge to it in two ways:
  - **Symlink** (simplest on macOS/Linux): `ln -sf AGENTS.md CLAUDE.md`
  - **Import** (supports Claude-specific additions): create `CLAUDE.md` with `@AGENTS.md` on the first line, then add Claude-only instructions below the import
- On Windows, prefer an explicit copy or sync step unless your environment handles symlinks reliably.
- Do not make Codex depend on `.claude/rules/` or Claude-only `@imports`; keep essential shared instructions in `AGENTS.md`.
- After any model upgrade (e.g. Opus 4.6 → 4.7), regression-test your top prompts before editing `AGENTS.md`; the memory often doesn't need changes, but you'll learn which lines are now dead weight.

## Large Repo Guidance

- Root memory should stay navigation-focused.
- Use nested per-directory `AGENTS.md` files for packages or services with real local conventions.
- Keep Claude modular rules small and topic-focused.
- Push long tutorials, inventories, and architecture deep-dives into docs or skill references.
- If a repo needs large, on-demand operating procedures, build or reuse a skill instead of stuffing more into project memory.
- If guidance starts reading like a README summary, delete or relocate it.

## Memory Progression

Flat `AGENTS.md` / `CLAUDE.md` is the default and handles most repos. It stops being enough in two specific situations:

1. **Corpus grows past ~1,000 durable facts** — keyword search across markdown starts missing synonyms and paraphrases.
2. **Queries cross entities** — "was Alice's project affected by Tuesday's outage?" needs a bridge fact that keyword or vector search alone will not find.

When either happens, the next rung is a structured memory store (graph + vector + relational), not a bigger `AGENTS.md`. For the ladder (in-memory → flat files → vector → graph-vector hybrid), the compiled-truth + timeline file schema, tiered entity enrichment, the thin-harness/fat-skills split, and the memory taxonomy (episodic / semantic / procedural), see [memory-architecture-ceilings.md](memory-architecture-ceilings.md).

Do not preemptively climb the ladder. Each rung adds infra, cost, and a frontier-model reliance. Climb only when a real user query fails in a way the current layer cannot fix.
