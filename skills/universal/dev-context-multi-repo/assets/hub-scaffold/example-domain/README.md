# example-domain

> **This is the per-domain template.** Copy this whole folder once per real
> domain (`cp -r example-domain payments`), rename it, and fill in
> `README.md` from `../context/templates/domain-readme.md`.

## Purpose

&lt;What this domain owns, in two sentences.&gt; — replace.

## Repos in this domain

| Repo | Kind | Catalog |
|------|------|---------|
| &lt;repo&gt; | service\|library\|app | `as-is/&lt;repo&gt;.md` |

## Folder map

```
example-domain/
├── README.md       this file
├── as-is/          current state: catalog pages, diagrams, deps
├── assessment/     gap analysis, migration roadmap, proposals
└── initiatives/    change RFCs (lifecycle below)
```

- **`as-is/`** — compiled current-state truth. Per-repo catalog pages
  (from `../context/templates/`), `diagrams.md`,
  `cross-repo-dependencies.md`. Generated from profiles; human-reviewed.
- **`assessment/`** — `gap-analysis.md`, `migration-roadmap.md`,
  `architecture-proposal.md`. Point-in-time; carry a lifecycle state.
- **`initiatives/`** — one folder per change RFC, numbered:
  `001-<slug>/`, `002-<slug>/`.

## Initiative lifecycle

Each initiative folder carries a `status:` in its own README and moves
through:

```
draft → proposed → accepted → in-progress → done → graduated
```

- **draft** — being written, not yet circulated.
- **proposed** — circulated for review/approval.
- **accepted** — approved, not yet started.
- **in-progress** — being implemented in the source repos.
- **done** — shipped; `as-is/` updated to reflect new reality.
- **graduated** — fully absorbed into `as-is/`; the initiative folder
  moves to `initiatives/_graduated/` for history.

Create `initiatives/_graduated/` when the first initiative graduates.
`.gitkeep` files keep `as-is/`, `assessment/`, and `initiatives/` under
version control while empty.
