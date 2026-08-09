# &lt;company&gt; Requirements Hub

A single, navigable knowledge hub for a portfolio of repositories. This is a
**blank scaffold**: copy it next to your repos, then let the
`dev-context-*` skills populate it from your actual code.

```
cp -r hub-scaffold ~/repos/requirements-hub
```

## What this is

A coordination repo that holds **compiled, agent-maintained knowledge** about
many source repos — without containing their source. It separates:

- **hot layer** — `AGENTS.md` + `rules/`: short, always-on execution policy.
- **compiled layer** — `context/` and the domain folders: profiles, catalog
  pages, graphs, and reviewed markdown the LLM maintains.
- **raw layer** — optional `raw/` capture areas (add when you ingest
  non-repo evidence such as exported docs or screenshots).

The hub is the system of record for *cross-repo* knowledge. Each source repo
keeps its own single-repo context.

## Reading order

1. `AGENTS.md` — how agents should operate against this hub.
2. `context/docs/architecture-overview.md` — the platform in one page.
3. `context/docs/domain-map.md` — domains and which repos belong to each.
4. `context/docs/repo-index.md` — every repo, one line, with a catalog link.
5. The relevant `&lt;domain&gt;/README.md` for the area you are working in.

## Quick links

| You want… | Go to |
|-----------|-------|
| The platform in one page | `context/docs/architecture-overview.md` |
| Which repo owns what | `context/docs/domain-map.md`, `context/docs/repo-index.md` |
| A specific domain's current state | `&lt;domain&gt;/as-is/` |
| Gaps and proposed changes | `&lt;domain&gt;/assessment/`, `&lt;domain&gt;/initiatives/` |
| Cross-repo graph queries | `context/graphs/`, see `context/scripts/README.md` |
| Generated reports | `context/reports/` |
| Compliance / data / AI rules | `rules/` |

## How it gets populated

This scaffold ships empty on purpose. Use the three pipeline skills:

- **`dev-context-code-graph`** — per-repo symbol/import graph
  (`graphs/code-graph.json`) for one repo at a time.
- **`dev-context-multi-repo`** — discover repos, scan them into profiles,
  build the cross-repo knowledge graph, and compile catalog pages here.
- **`dev-context-engineering`** — single-repo context layers + the
  `context-graph.json` build/validate for this hub itself.

See `context/scripts/README.md` for the exact command sequence.

## Domain folders

Each domain (e.g. `payments/`, `identity/`) follows the same shape:

```
<domain>/
├── README.md           # what this domain is, repos in it, key flows
├── as-is/              # current-state docs, diagrams, dependencies
├── assessment/         # gap analysis, migration roadmap, proposals
└── initiatives/        # RFC lifecycle: see example-domain/README.md
```

`example-domain/` is a working template — copy it per real domain and rename.

> Replace every `&lt;company&gt;` / `&lt;domain&gt;` placeholder. Nothing here is
> specific to any organization.
