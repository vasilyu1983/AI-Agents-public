# Architecture Overview

> Template stub. One page that lets a new agent or engineer understand the
> whole platform before drilling into a domain. Generated/maintained from
> profiles and the knowledge graph — do not hand-write what the compiler
> can produce.

## Platform in one paragraph

&lt;What the platform does, who it serves, the 3–5 load-bearing systems.&gt;

## Domains

&lt;Table of domains → one-line purpose. Keep in sync with
`domain-map.md`.&gt;

| Domain | Purpose | Entry doc |
|--------|---------|-----------|
| &lt;domain&gt; | &lt;one line&gt; | `&lt;domain&gt;/README.md` |

## Cross-cutting flows

&lt;The 2–4 flows that cross domains (e.g. onboarding, settlement). Link
the generated diagrams in `context/overview/`.&gt;

## Tech baseline

&lt;Languages, runtimes, datastores, messaging — derived from repo
profiles, not prose.&gt;

## How this page is built

Regenerate from `context/graphs/knowledge-graph.json` + repo profiles.
See `context/scripts/README.md`.
