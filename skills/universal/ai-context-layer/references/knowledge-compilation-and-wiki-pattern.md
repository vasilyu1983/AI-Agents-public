# Knowledge Compilation And LLM Wiki Pattern (P7)

## Table of Contents

- [When this pattern is the right answer](#when-this-pattern-is-the-right-answer)
- [Core pipeline](#core-pipeline)
- [Page types](#page-types)
- [Provenance classes](#provenance-classes)
- [Ingest-time contradiction detection](#ingest-time-contradiction-detection)
- [Confidence model](#confidence-model)
- [Relationship to other patterns](#relationship-to-other-patterns)
- [Reference implementations](#reference-implementations)
- [Failure modes](#failure-modes)
- [Check](#check)

**Purpose.** Deep dive on the pattern for building a
**human-reviewable, accumulating** knowledge asset for agents — the LLM Wiki
pattern popularized by Andrej Karpathy's 2026 post and implemented in
SamurAIGPT/llm-wiki-agent and Ar9av/obsidian-wiki. Pair with `patterns-catalog.md`
(P7 entry) and `inspection-and-review-surfaces.md` (the review UI layer).

## When this pattern is the right answer

Use P7 when all of the following are true:

- The product needs a knowledge asset **humans will read or review**, not only an
  index an LLM queries.
- Sources arrive over time and knowledge must be **accumulated**, not recomputed
  per turn.
- Reviewers need to **trace** any claim to its source, **inspect** confidence, and
  **resolve** contradictions.
- Recurring synthesis work is worth compiling (the same questions get asked; the
  same patterns get re-derived).

Do **not** use P7 as a default. If the consumer is an LLM only and no human will
read the artifact, prefer P2+P8 (structured memory + evidence-bearing retrieval).

## Core pipeline

```text
source → extract → reconcile → supersede → emit
                 ↘ contradiction detection (ingest-time)
                 ↘ confidence + provenance tagging
```

Four stages, each with its own contract:

1. **Extract.** Parse the source, produce typed entities, relations, and atomic
   facts. Tag every emitted item with `source_episode_id` and extraction confidence.
   This is the stage most skipped in "just embed it" systems (anti-pattern A16).
2. **Reconcile.** For each extracted item, look up existing pages, entities, and
   facts by identity (not embedding similarity). Decide: new item, update to
   existing item, or contradiction.
3. **Supersede.** Never overwrite. When new evidence displaces an old claim,
   close the old row's validity window (`valid_to = now`, `superseded_at = now`,
   `supersedes_id = new_row`) and insert the new row. Keep the audit trail.
4. **Emit.** Update the affected wiki pages: rewrite the main page if the entity
   changed, append a "superseded" section, and add a contradiction flag at the
   page head if reconciliation surfaced a conflict.

## Page types

A well-formed LLM wiki has at least these page types, each with a stable layout:

- **Entity page** — one per person, project, product, org, or concept. Contains
  extracted facts, confidence, source list, and wikilinks to related entities.
- **Concept page** — one per idea, framework, or term. Produced from multiple
  sources; explicitly synthesized.
- **Synthesis page** — generated to answer a recurring query class; future queries
  hit this page first, not the retriever.
- **Source summary page** — one per ingested source; records what was extracted
  and where it landed.
- **Index page** — navigation. Flat list or categorized hierarchy.
- **Log page** — audit trail of every ingest, extract, reconcile, and supersede
  operation with timestamps and rationale.

## Provenance classes

Every claim on a wiki page carries one of three provenance tags:

- **extracted** — directly extracted from a source with a specific location
  (`source_episode_id` + chunk/page pointer).
- **inferred** — synthesized by an LLM from multiple extracted claims. The
  synthesis must cite its inputs.
- **ambiguous** — multiple sources disagree; the page shows the disagreement
  rather than picking a winner silently.

A per-page **provenance block** in the frontmatter summarizes the mix
(e.g., `extracted: 12, inferred: 4, ambiguous: 1`). Pages that drift into mostly
inferred content should surface in lint output.

## Ingest-time contradiction detection

Contradictions are detected **at write time**, not at query time (blocks A4).
Use the MemPalace categories:

- **Attribution** — same claim asserted by multiple sources with different details.
  Resolution: record all attributions, flag the page, require reviewer decision
  if the delta is material.
- **Temporal** — new fact supersedes an old fact that is still in the current
  window. Resolution: close the old validity window, link `supersedes_id`, leave
  the old row readable via as-of query.
- **Stale** — a fact is past its validity window but still being read. Resolution:
  filter from current queries by default; keep point-in-time access.

<!-- Source: github.com/MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), cross-routed 2026-04-15 -->

## Confidence model

Every fact carries a confidence score that **decays with time** and **strengthens
with reinforcement**. The Karpathy/rohitg00 writeup uses Ebbinghaus-style
exponential decay, reset on access or new source confirmation.

Key rules:

- Architecture-level facts (long-lived, high-stakes) decay slowly.
- Transient facts (bug states, in-flight decisions) decay quickly.
- Reinforcement comes from either a new source confirming the fact or a human
  reviewer approving it; a query alone is not reinforcement.
- Below a threshold (system-tunable, typical 0.4) the fact is marked "low
  confidence" and the wiki refuses to cite it without an inline warning.

The confidence field is visible in the review UI (see
`inspection-and-review-surfaces.md`).

## Relationship to other patterns

- **P4 (Temporal KG)** — P7 pages *cite* P4 facts. The wiki is the human view;
  the graph is the machine view; they share `source_episode_id`s.
- **P5 (Ontology-grounded poly-store)** — P7 can sit on top of P5's entity/relation
  schema so extraction produces typed instances directly.
- **P8 (Evidence-bearing retrieval)** — P7 compiles *synthesis pages* that answer
  recurring queries. Queries hit the synthesis page first; retrieval falls back
  for gaps. This is the answer to A15 (RAG re-run per turn).
- **P9 (Composed review surface)** — P9 is P7 + P4 + the review UI. See the next
  reference file for the UI specifics.

## Reference implementations

- **Karpathy LLM Wiki v2 writeup (2026-04)** — architectural description of the
  three-layer pattern (raw sources → wiki pages → typed schema), confidence decay,
  and the ingest-extract-reconcile pipeline.
- **SamurAIGPT/llm-wiki-agent** — open-source reference for the ingest pipeline
  and the `graph.html` inspection UI (wikilink graph with community detection).
- **Ar9av/obsidian-wiki** — reference targeting Obsidian as the storage and UI
  surface.

Code-level extraction of these repos is **deferred** to a follow-up
`research-git` pass; this skill registers them as candidates in
`data/sources.json`.

## Failure modes

- **Query-time contradiction detection (A4)** — worst-common failure. Fix by moving
  the contradiction check into the reconcile stage.
- **No extraction pipeline (A16)** — "wiki" that is actually an index wearing a
  costume. No typed entities, no supersession, no reviewable pages.
- **No confidence model (A14)** — every claim equally weighted. Fix with decay +
  reinforcement.
- **No review surface (A17)** — the wiki is human-visible but there is no way to
  inspect, trace, or correct. Fix with P9.
- **Provenance as metadata (A13)** — claims cannot be traced to sources. Fix with
  `source_episode_id` on every row.

## Check

A P7 implementation is working if: (1) a reviewer can trace any wiki claim to a
specific source episode, (2) a contradiction can be surfaced at ingest and
resolved by closing a validity window rather than overwriting, (3) confidence on
a page decays visibly when not reinforced, and (4) a recurring query hits a
compiled synthesis page instead of re-running retrieval end-to-end.
