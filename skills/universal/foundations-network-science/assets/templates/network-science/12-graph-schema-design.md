# Primitive: Graph Schema Design

**Sources**: Broadwater & Stillman (2025), *Graph Neural Networks in Action*, ch. 8 §8.2–8.2.4.

## Definition

Graph schema design is the modelling discipline that decides *what becomes a node, what becomes an edge, and what becomes a property* before any algorithm runs. It is the graph analogue of table design, but with a critical asymmetry: tabular layout is largely unambiguous — rows are observations, columns are features, joins go through keys — whereas the same relational data admits several legitimate graph structures with no obvious default. Broadwater & Stillman state it directly: with graphs, "it's not always intuitive where to place the entities of interest," and it is that ambiguity that "drives the need for systemic methods."

The practical stakes are technical debt. Structure choices made implicitly at ingest time become expensive to reverse once a GNN pipeline, a query layer, and downstream tests are built on top of them. Addressing the dataset structure explicitly and up front is what makes the graph testable, parameterisable, and safe to experiment on.

## The Four-Step Loop

1. **Understand the domain and the use case** — read the raw data *and* the industry context. Basic counts already carry signal: a referral dataset with 1,933 candidates and 12,239 referrals is, on its face, an interconnected network rather than a sparse list. Domain questions ("what underlying structures govern these referrals?") are what align the model with expertise rather than with convenience.
2. **Create a data model, a schema, and an instance model** — the schema is the blueprint (elements, rules, constraints); the instance model is a small subset of real data laid out under that schema, which is what makes the schema testable at all.
3. **Test the model using the schema and instance model** — cast the instance model into the target system, then write queries that assert the constraints the schema claims: required attributes present and non-null, edge types consistent, unique identifiers, attribute data types, directedness, and edge cases (unconnected nodes, isolated cycles).
4. **Refactor if necessary** — adjust labels, properties, relationships, or constraints; then repeat. Testing and refactoring are iterative, not a one-time gate.

## The Five Schema Questions

A schema should answer all five:

- What are the elements (nodes, edges, properties), and what real-world entities and relationships do they represent?
- Does the graph include multiple types of nodes and edges?
- What are the constraints on what can be represented as a node?
- What are the constraints on relationships? Do certain nodes have restrictions on adjacency and incidence? Are there count restrictions on certain relationships?
- How are descriptors and metadata handled, and what are the constraints on that data?

Steps to build one: identify main entities and relationships → define node and edge labels → specify properties and constraints → (optional, database-oriented) define indices → (optional) apply the schema to a database.

## Conceptual vs. System Schema

- **Conceptual schema** — elements, rules, and constraints, *not* tied to any particular database or processing system.
- **System schema** — reflects the conceptual schema's rules for one specific system, and may omit conceptual elements that system does not need.

Keep both when the stack warrants it. Where more than one schema exists, a mapping asserting compatibility between them is part of the design, not an afterthought.

## Vocabulary

| Term | Meaning |
|---|---|
| Bi-graph / bipartite graph | Two node sets, no edges within a set |
| Homogeneous graph | One node type and one edge type |
| Heterogeneous graph | Several node and/or edge types — usefully imagined as layered graphs |
| Instance model | A model based on a schema, holding a real subset of the data |
| Property graph | Model using metadata (labels, identifiers, attributes/properties) to define graph elements |
| RDF graph / triple store | Subject–predicate–object pattern: nodes are subjects and objects, edges are predicates |
| Ontology | Structured framework describing concepts, roles, attributes, and interrelations in a knowledge domain |
| ER diagram | Figure showing entities, relationships, and constraints of a graph |
| Schema | Blueprint defining how graph elements are organised and which rules and constraints apply |

The vocabulary carries real compression: telling a colleague that a dataset is "a bi-graph implemented on a property graph" communicates most of the design in one clause.

## When to Use

- Before ingesting non-graph data (tabular, document, transactional) into a graph store or GNN pipeline
- When more than one plausible graph structure exists for the same entities — e.g. whether *Industry* is a candidate attribute or its own node type
- When several teams or downstream tasks will query the same graph and need shared constraints
- When a graph pipeline is already producing surprising results and the suspicion is that the structure, not the algorithm, is wrong

## Inputs

- Raw source data plus its documented semantics
- Use-case objectives and the queries the system must answer
- Operational constraints — the databases, libraries, and processing systems available
- Required outputs of the downstream application

## Outputs

- Conceptual schema (and system schema where a target system is fixed)
- Instance model over a real data subset
- A constraint test suite derived from the schema
- Documented refactor history — which structure was chosen and what was rejected

## Failure Modes

1. **Implicit structure choice.** Loading data into a graph store without writing a schema means the structure exists only in the loader code. Nothing can be tested against it and nothing can be varied deliberately.
2. **Property-vs-node decisions made by accident.** Promoting an attribute to a node type (Industry as node rather than candidate property) changes path lengths, community structure, and what a GNN can aggregate. Make the choice explicitly and record why.
3. **Skipping the instance model.** A schema with no worked instance is untested. The instance model is what turns constraints into runnable queries.
4. **Deferring compatibility.** Technical debt arises specifically when the model has to evolve and no backward/forward compatibility was planned — and when modelling choices fit the data but not the chosen database, forcing expensive workarounds.
5. **One schema where two are needed.** Mixing system-specific concerns into the conceptual schema couples the model to a database choice that may not survive the project.
6. **No mapping between multiple schemas.** Two schemas without an asserted mapping drift silently.

## Related

- [`09-graph-clustering.md`](09-graph-clustering.md) — partition quality depends on which entities were made nodes in the first place
- [`10-graph-embeddings.md`](10-graph-embeddings.md) — heterogeneous vs. homogeneous schema determines whether a homogeneous embedding method is even applicable
- [`08-link-prediction.md`](08-link-prediction.md) — edge-type constraints define what counts as a candidate edge
