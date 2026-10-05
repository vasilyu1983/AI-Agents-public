# Graph And Relationship Layer

## When Graph Is Worth It

Use a graph or graph+vector layer when the task depends on:

- ownership or attribution chains
- entity relationships across many hops
- influence paths or citation networks
- dependency traversal
- community summaries or cluster reasoning

## When Graph Is Not Worth It

Avoid graph as the default when:

- SQL joins solve the problem directly
- search already returns the right evidence
- the graph would mostly duplicate operational tables
- the graph is added for novelty rather than measurable quality gains

## Practical Rule

Graph belongs behind a contract such as `relationship_context`, not as the universal store for all app context.

## Temporal Validity

Graph edges are not permanent. Facts about relationships have lifespans:

- **valid_from / valid_to**: every edge should carry a validity window. An employee–employer edge is valid from hire date to termination date. A product–category edge is valid from the classification date until re-categorized.
- **Expired-edge handling**: expired edges should be excluded from traversal by default. Keep them in the store for audit but filter them at query time.
- **Bitemporal tracking**: distinguish assertion time (when the system learned the fact) from validity time (when the fact was true in the real world). This matters for compliance and debugging.
- **Temporal KG pattern (Zep/Graphiti)**: temporal knowledge graphs store every fact with a validity window and support real-time incremental updates. Use this pattern when relationships change frequently and stale edges cause incorrect answers.
- **Non-destructive invalidation**: when new evidence contradicts an existing edge, close the validity window (`valid_to = now`, `superseded_at = now`) rather than deleting the edge. Keeps the audit trail, lets the user trace *why* a fact was superseded, and preserves point-in-time queries. Deletion is reserved for corrections and compliance requests.
- **As-of queries**: the graph should answer "what's true now" and "what was true on date X" against the same store. Two query modes: current (`valid_to IS NULL OR valid_to > now`) and point-in-time (`valid_from <= X AND (valid_to IS NULL OR valid_to > X)`). Both should be first-class, not implemented as ad-hoc filters.

Temporal validity is especially important for org charts, ownership structures, and compliance-sensitive relationships where acting on expired facts is a failure.

## Typed Ontology As Code

Prefer a typed ontology — entity and edge classes defined in code — over freeform `(subject, predicate, object)` triples.

- **Pattern**: declare `class Person(Entity)`, `class Company(Entity)`, `class WorkedAt(Edge)` with required fields, types, and validators. Extraction pipelines return typed instances; queries filter by type cleanly.
- **Why**: an untyped `(Alice, worked_at, Acme)` triple is a string. A `WorkedAt(subject=Alice, object=Acme, start_date=2024-01-01, end_date=None, role="DSL engineer")` edge is queryable, validatable, and survives schema migration because the rename surfaces as a compiler error.
- **Reference implementation**: Graphiti's Pydantic-based entity/edge types. Simpler variant: Letta's labeled memory blocks — each block has a label, value, and character limit, so the "type" is just a string tag and the schema is flat. Use the simpler variant when the ontology has fewer than ~10 entity kinds and no cross-entity validation.
- **Check**: if you find yourself writing string-compare code against predicate names in query logic, the ontology should be typed. If queries are mostly over a flat key-value memory, the labeled-block variant is enough.

<!-- Source: github.com/getzep/graphiti@98d8344d531aa74160f2e33b8db84c5bdc9954ba (Apache-2.0), github.com/letta-ai/letta@bb52a8900a79cf1378e6e9cdecf244b673a13a72 (Apache-2.0), extracted 2026-04-15 -->
<!-- Non-destructive invalidation and as-of queries also described in MemPalace/mempalace@6614b9b4e71e67da2236493b036b7bf42ba2d55f (MIT), pattern M4 -->


## Required Checks

- prove the graph query changes answer quality or action quality
- define graph freshness and rebuild policy
- define source-of-truth ownership for each edge
- separate inferred edges from declared or operational edges
- define temporal validity windows and expired-edge invalidation policy
