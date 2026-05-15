# &lt;domain&gt;

> Template for a domain folder's `README.md`. Copy `example-domain/` per
> real domain, rename, and fill this in.

## Purpose

&lt;What this domain is responsible for, in two sentences.&gt;

## Repos in this domain

| Repo | Kind | Catalog |
|------|------|---------|
| &lt;repo&gt; | service\|library\|app | `as-is/&lt;repo&gt;.md` |

## Key flows

&lt;The 1–3 flows this domain owns end-to-end. Link diagrams in
`as-is/diagrams.md`.&gt;

## Boundaries

- **Owns (system of record):** &lt;data/flows&gt;
- **Depends on:** &lt;upstream domains&gt;
- **Consumed by:** &lt;downstream domains&gt;

## Folder map

- `as-is/` — current state: per-repo catalog pages, diagrams,
  cross-repo dependencies.
- `assessment/` — gap analysis, migration roadmap, proposals.
- `initiatives/` — change RFCs (see `../example-domain/README.md` for the
  lifecycle).
