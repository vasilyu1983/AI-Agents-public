# Graph And Relationship Layer

## Contents

- [When Graph Is Worth It](#when-graph-is-worth-it)
- [When Graph Is Not Worth It](#when-graph-is-not-worth-it)
- [Practical Rule](#practical-rule)
- [Temporal Validity](#temporal-validity)
- [Typed Ontology As Code](#typed-ontology-as-code)
- [Ontology Acceptance Questions](#ontology-acceptance-questions)
- [Required Checks](#required-checks)

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


## Ontology Acceptance Questions

Before adding a class or relationship, write an acceptance case: **question → required schema → independently sourced expected answer set → typed, directed query → source evidence**. Author expected answers from reviewed source records before inspecting graph-builder output; questions generated from that output are supplementary tests, not independent ground truth.

1. Record the question, tenant/as-of scope, required classes, inheritance rules, edge direction, and allowed evidence kinds. Record completeness separately for each queried scope; missing edges do not establish a negative.
2. Freeze reviewed source revisions and literal expected sets, including evidence locators for every asserted fact. For an empty answer, retain the source inventory that establishes completeness. Keep inferred edges outside the asserted projection.
3. Run the query against the actual builder's projection. Compare complete sets, status, and supporting provenance; checking one plausible answer misses omitted or extra results. Reject reversed edges and invalid endpoint types.
4. Replay after schema, extraction, source, or completeness changes. A reviewer updates gold answers from changed sources, never by copying new graph output. Record old/new source and schema revisions with failures.

### Compact Worked Fixture

This synthetic source ledger is authored independently of the graph. It demonstrates mechanics, not financial facts. In a real case, substitute immutable document revisions and page/row locators.

| Source locator | Reviewed statement |
|---|---|
| `schema-v1:1` | Stock is an Equity; Equity and Bond are FinancialInstrument subclasses. |
| `register-v1:1` | S1 is a Stock issued by Atlas. |
| `register-v1:2` | S2 is a Stock issued by Atlas. |
| `register-v1:3` | B1 is a Bond issued by Vale. |
| `register-v1:scope` | These are all instruments and issuers in this synthetic scope; Atlas and Vale are Organizations. |

Independent acceptance cases, fixed before building:

| Question | Schema requirement / traversal | Expected set; evidence |
|---|---|---|
| Which financial instruments exist? | `instance → type → subClassOf*` | `{B1,S1,S2}`; register rows 1–3 plus `schema-v1:1` |
| Who issued S1? | `FinancialInstrument -issuedBy→ Organization` | `{Atlas}`; `register-v1:1` |
| Which stocks did Atlas issue? | Reverse lookup of that same directed edge; Stock filter | `{S1,S2}`; register rows 1–2 |
| Which bonds did Atlas issue? | Bond filter plus directed issuer lookup | `{}`, `complete`; `register-v1:scope` |
| Which bonds did Vale issue after row 3 is omitted from the projection? | Same query; coverage marked incomplete | observed `{}`, `unknown`; source truth remains `{B1}`, `register-v1:3` |

Run the following SQL in a fresh SQLite database (for example, Python's standard-library `sqlite3`). The inserts stand in for the builder adapter. When testing a real builder, replace those inserts with its output; keep the source ledger and expected table independent. `type_of` derives only declared subclass closure; it does not infer new domain relationships.

```sql
CREATE TABLE entity(id TEXT PRIMARY KEY, kind TEXT NOT NULL, source TEXT NOT NULL);
CREATE TABLE subclass(child TEXT, parent TEXT, source TEXT NOT NULL,
                      PRIMARY KEY(child,parent));
CREATE TABLE edge(subject TEXT, predicate TEXT, object TEXT, source TEXT NOT NULL,
                  PRIMARY KEY(subject,predicate,object));
CREATE TABLE coverage(scope TEXT PRIMARY KEY, complete INTEGER CHECK(complete IN (0,1)),
                      source TEXT NOT NULL);
INSERT INTO entity VALUES
 ('S1','Stock','register-v1:1'), ('S2','Stock','register-v1:2'),
 ('B1','Bond','register-v1:3'), ('Atlas','Organization','register-v1:scope'),
 ('Vale','Organization','register-v1:scope');
INSERT INTO subclass VALUES
 ('Stock','Equity','schema-v1:1'), ('Equity','FinancialInstrument','schema-v1:1'),
 ('Bond','FinancialInstrument','schema-v1:1');
INSERT INTO edge VALUES
 ('S1','issuedBy','Atlas','register-v1:1'),
 ('S2','issuedBy','Atlas','register-v1:2'),
 ('B1','issuedBy','Vale','register-v1:3');
INSERT INTO coverage VALUES ('Atlas/bonds',1,'register-v1:scope'),
                            ('Vale/bonds',1,'register-v1:scope');
CREATE VIEW type_of AS
 WITH RECURSIVE closure(id,kind) AS (
   SELECT id,kind FROM entity
   UNION
   SELECT c.id,s.parent FROM closure c JOIN subclass s ON c.kind=s.child
 ) SELECT id,kind FROM closure;
-- Endpoint validation: expected zero rows. Reverse an edge to test rejection.
SELECT e.* FROM edge e WHERE e.predicate <> 'issuedBy'
 OR NOT EXISTS (SELECT 1 FROM type_of t
                WHERE t.id=e.subject AND t.kind='FinancialInstrument')
 OR NOT EXISTS (SELECT 1 FROM type_of t
                WHERE t.id=e.object AND t.kind='Organization');
-- Inheritance: expected B1, S1, S2. Evidence includes the subclass rules above.
SELECT id FROM type_of WHERE kind='FinancialInstrument' ORDER BY id;
-- Direction: expected (Atlas, register-v1:1).
SELECT object,source FROM edge WHERE subject='S1' AND predicate='issuedBy';
-- Multiple answers: expected (S1, register-v1:1), (S2, register-v1:2).
SELECT e.subject,e.source FROM edge e JOIN type_of t ON t.id=e.subject
 WHERE e.predicate='issuedBy' AND e.object='Atlas' AND t.kind='Stock'
 ORDER BY e.subject;
CREATE VIEW bond_issuers AS
 SELECT e.subject,e.object,e.source FROM edge e JOIN type_of t ON t.id=e.subject
 WHERE e.predicate='issuedBy' AND t.kind='Bond';
-- Complete empty: expected no rows, followed by (complete, register-v1:scope).
SELECT subject,source FROM bond_issuers WHERE object='Atlas';
SELECT CASE complete WHEN 1 THEN 'complete' ELSE 'unknown' END,source
 FROM coverage WHERE scope='Atlas/bonds';
-- Omission affects only the projection; retain the independent source ledger.
SAVEPOINT omission;
DELETE FROM edge WHERE subject='B1' AND predicate='issuedBy';
UPDATE coverage SET complete=0,source='test:omitted-register-v1:3'
 WHERE scope='Vale/bonds';
-- Incomplete empty: expected no rows, followed by (unknown, test:omitted-register-v1:3).
SELECT subject,source FROM bond_issuers WHERE object='Vale';
SELECT CASE complete WHEN 1 THEN 'complete' ELSE 'unknown' END,source
 FROM coverage WHERE scope='Vale/bonds';
ROLLBACK TO omission;
RELEASE omission;
```

The omission must fail the full-source answer-set case (`{B1}`) while passing the incomplete-projection status case (`unknown`). Never rewrite the gold set to `{}`. For partial nonempty results, return observed members and `unknown` coverage too. Absence can mean “none” only within the independently verified complete scope. Preserve each supporting source locator and inheritance rule in the answer trace; a bare entity ID is insufficient evidence. Label rule-derived type membership separately from asserted edges and model-proposed relationships.

Source: Keith Bourne, *Unlocking Data with Generative AI and RAG*, 2nd ed., Chapter 13, PDF pp. 351–355 (printed pp. 312–316), motivates competency questions, inheritance, and property domains/ranges. The fixture, completeness contract, and replay procedure above are an applied acceptance design, not a reproduced book implementation.

## Required Checks

- prove the graph query changes answer quality or action quality
- define graph freshness and rebuild policy
- define source-of-truth ownership for each edge
- separate inferred edges from declared or operational edges
- define temporal validity windows and expired-edge invalidation policy
