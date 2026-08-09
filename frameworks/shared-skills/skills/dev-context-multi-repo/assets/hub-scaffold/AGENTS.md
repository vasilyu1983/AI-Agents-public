# AGENTS.md — &lt;company&gt; Requirements Hub

This file is the portable, always-on instruction layer for any AI agent
operating against this hub. Keep it short. It is a **map, not an
encyclopedia** — it routes to the compiled layer, it does not duplicate it.

## What this repo is

A cross-repo knowledge hub. It contains compiled markdown, profiles, and
graphs about many source repos. It does **not** contain their source code.
Treat the compiled layer as the system of record for cross-repo facts.

## Operating rules

1. **Read before answering.** For any cross-repo question, start from
   `context/docs/repo-index.md` and the relevant `&lt;domain&gt;/README.md`.
   Do not infer architecture from repo names.
2. **Ground every claim.** A statement about a repo must trace to a profile
   (`context/graphs/` / `&lt;domain&gt;/as-is/`) or a cited source. Mark
   unverified claims as `inferred` or `unverified`.
3. **Right tool for the question.** Direct file read or lexical search for
   simple lookups; the knowledge graph (`context/scripts/README.md`) only
   when relationship structure changes the answer.
4. **File durable answers back.** A reusable analysis becomes a catalog
   page, concept note, or `context/reports/` entry — not a chat-only reply.
   Run the placement test in `context/docs/documentation-governance.md`
   first.
5. **Do not paste inventories here.** Repo lists, dependency dumps, and
   long tables belong in the compiled layer, never in this file.
6. **Respect the rule layer.** `rules/` constraints (compliance, data
   handling, AI governance, secrets, resilience) are binding. If a task
   conflicts with a rule, stop and surface the conflict.

## Layout

```
AGENTS.md            this file (hot layer)
rules/               binding policy stubs
context/docs/        canonical platform docs
context/templates/   page templates the compiler uses
context/scripts/     thin runners + pointers to the pipeline skills
context/graphs/      repos.json, knowledge-graph.json, context-graph.json
context/overview/    generated cross-cutting maps and catalogs
context/reports/     dated, lifecycle-tagged analyses
<domain>/            one folder per domain (as-is / assessment / initiatives)
```

## Runtime layers

`AGENTS.md` is the portable baseline read by Claude Code, Codex, and
Copilot. Add `.claude/`, `.codex/`, or `.github/` layers only when a tool
needs behavior it cannot get from this file.

> Replace `&lt;company&gt;` / `&lt;domain&gt;` placeholders before use.
