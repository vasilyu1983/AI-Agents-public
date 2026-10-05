# Inspection And Review Surfaces

## Table of Contents

- [Why this layer is mandatory for user-visible KBs](#why-this-layer-is-mandatory-for-user-visible-kbs)
- [Surface inventory](#surface-inventory)
- [Minimum viable vs. full review surface](#minimum-viable-vs-full-review-surface)
- [Binding requirements](#binding-requirements)
- [Known gaps across current frameworks](#known-gaps-across-current-frameworks)
- [When review UI is mandatory — the checklist](#when-review-ui-is-mandatory--the-checklist)
- [Check](#check)

**Purpose.** Define the human-facing layer that sits on top of the context layer:
graph view, page view, contradiction queue, source trace, confidence view, and
editorial approval workflow. This is the missing half of the architecture model —
most frameworks ship pieces of it; check whether any ships all of it
end-to-end before building your own. Pair with `patterns-catalog.md` (P9) and
`knowledge-compilation-and-wiki-pattern.md` (P7).

## Why this layer is mandatory for user-visible KBs

When the knowledge layer is visible to end users, operators, or customers,
everything in the rest of the skill — provenance, bi-temporal facts, lifecycle
verbs, confidence — only earns its cost if a human can *inspect and act on* it.
Without the review surface, those properties are load-bearing for nothing.

Mandatory when:

- the product exposes the KB to non-engineer users or customers (the case in a practitioner request for a reviewable knowledge base);
- the domain is regulated (finance, health, legal, compliance);
- the tenant model is multi-customer and trust matters;
- the KB is the product, not an implementation detail;
- reviewers must approve facts before they reach end users.

Optional when:

- the KB is consumed by an LLM only and never read by a human;
- the system is single-user and offline;
- the blast radius of a wrong fact is contained within a single session.

## Surface inventory

The full review layer is composed of six surfaces, each bound to a contract.

### 1. Graph view

- **What**: nodes are entities and pages; edges are wikilinks, relations, or typed
  KG edges. Users pan, zoom, filter by type, and click through to page view.
- **Binding**: reads the typed ontology from P4/P5; each node exposes
  `source_episode_id`, last-updated timestamp, and confidence.
- **Example implementations (verify current state before relying on them)**: Cognee graph UI, llm-wiki-agent `graph.html`
  (wikilink graph with community detection), Graphiti temporal explorer, Neo4j
  Bloom when the backend is Neo4j.
- **Minimum viable**: static HTML with nodes and edges rendered once per ingest.

### 2. Page view

- **What**: single entity or concept page with extracted facts, inferred synthesis,
  and a footer listing source pages.
- **Binding**: each claim tagged `extracted | inferred | ambiguous` with a
  clickable source pointer; page header shows confidence summary and contradiction
  flags; page footer links to the log of mutations.
- **Minimum viable**: plain markdown with wikilinks and source footnotes.

### 3. Contradiction queue

- **What**: a work queue of unresolved contradictions grouped by category.
- **Binding**: each item carries the MemPalace category (attribution / temporal /
  stale), both sides of the contradiction, and the actions available (approve A,
  approve B, supersede, defer).
- **Example implementations (verify current state before relying on them)**: none known end-to-end. Frameworks typically surface
  a flag on the page rather than a dedicated review queue. **This is the
  headline gap in the ecosystem.**

### 4. Source trace view

- **What**: given a claim, walk backwards through the chain: claim → extracted
  fact → episode → raw source location.
- **Binding**: uses `source_episode_id` as the index; the episode store holds the
  raw input verbatim so the chain always terminates in something a human can
  read.
- **Example implementations (verify current state before relying on them)**: Graphiti's episode provenance API (programmatic),
  Zep dashboard (partial), llm-wiki-agent source summary pages.

### 5. Confidence / provenance view

- **What**: per-page and per-claim confidence display; decay curve; list of
  reinforcements and contradictions that shaped the current score.
- **Binding**: reads the confidence field from P7; decay policy is stored with
  the fact type.
- **Minimum viable**: a colored chip next to each claim (green / yellow / red)
  with a tooltip showing confidence and last-reinforced date.

### 6. Editorial approval workflow

- **What**: explicit approve / reject / supersede path for reviewers, with a role
  gate. Approved facts move from "staged" to "published." Rejections record
  rationale.
- **Binding**: the write path splits — the ingest pipeline writes to a staging
  table; only approved rows are readable from production queries. This is an
  ACL-gated derivative of P4's non-destructive invalidation.
- **Example implementations (verify current state before relying on them)**: none known. This is the gap a practitioner request for a reviewable knowledge base named.

## Minimum viable vs. full review surface

**Minimum viable** (ships in 1–2 sprints on top of P4+P7):

- Graph view (static, read-only)
- Page view (markdown with source footnotes)
- Source trace (clickable from page to episode)

**Full review surface** (ships over a longer arc):

- Everything in minimum viable, plus:
- Contradiction queue with category grouping
- Confidence / provenance view with decay curves
- Editorial approval workflow with role gating and staging
- Inline feedback tied to `context_bundle_id` (see
  `references/context-assembly.md`)
- Reuse metrics (which pages are cited most often; which are stale)

## Binding requirements

Regardless of surface, every review layer must meet:

- **Every fact → `source_episode_id`** — no orphan claims. A claim without a
  traceable source does not render.
- **Every page → confidence summary + contradiction list** — visible in the
  header, not buried in a sidebar.
- **Every write → audit log row** — append-only; reviewers can answer "who
  approved this and when?".
- **Every inline feedback → `context_bundle_id`** — feedback must tie to the
  exact bundle that produced the shown output, not to a free-floating "was this
  helpful?".
- **Every staged fact → explicit visibility boundary** — staging writes are not
  readable from production queries by default.

## Known gaps across current frameworks

| Gap | Why it matters | Partial impls |
|-----|----------------|---------------|
| End-to-end editorial approval workflow | Required for regulated + user-visible KBs | None |
| Contradiction queue with category grouping | Users cannot act on flags that never surface | Flags on pages only |
| Confidence decay visualization | Reviewers cannot judge stale pages at a glance | Confidence as a number only |
| Cross-session reuse metrics | Cannot identify compile-worthy synthesis pages | Log-analysis workarounds |

These gaps are what a caller asking for a reviewable knowledge base should be told to check for before choosing a framework.

## When review UI is mandatory — the checklist

A design must ship at least the **minimum viable** review surface when any one of
these is true:

- end users or customers read the KB directly;
- the KB backs answers in a regulated domain;
- reviewers must approve facts before production exposure;
- contradictions have business consequences (not just aesthetic cost);
- the KB is multi-tenant with cross-customer data.

If none of the above apply, the review surface can be deferred to an
engineer-only inspection tool (e.g., a CLI that walks the episode chain) but
the **binding requirements** above still apply to the underlying data model.

## Check

The review layer is working if: (1) any fact on the user-visible KB can be
clicked and traced to a raw source in under three actions, (2) a contradiction
introduced at ingest appears in the queue within one pipeline run, (3) a
reviewer can resolve a contradiction without writing SQL, and (4) approved
facts move from staging to production without ever overwriting a prior row.
