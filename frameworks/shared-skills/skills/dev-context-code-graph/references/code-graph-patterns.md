# Code Graph Patterns

## Table of Contents

- [Node Types](#node-types)
- [Edge Relations](#edge-relations)
- [ID Rules](#id-rules)
- [Confidence Rules](#confidence-rules)
- [Query Semantics](#query-semantics)
- [Structural Risk Analysis](#structural-risk-analysis)
- [V1 Boundaries](#v1-boundaries)

## Node Types

- `repo`: root node for one repository scan
- `file`: individual source or test file
- `module`: reserved for future file-to-module enrichment
- `class`: class or equivalent type declaration
- `function`: top-level function
- `method`: class or instance method
- `test`: executable test function or test method
- `external_symbol`: unresolved or third-party import/call target

## Edge Relations

- `contains`: repo contains file
- `defines`: file or class defines a symbol
- `imports`: file imports a local file or external symbol
- `calls`: function or method calls another symbol
- `inherits`: class extends or derives from another symbol
- `references`: unresolved or weakly-resolved symbol usage
- `tests`: test symbol exercises a function, method, or class

## ID Rules

- Normalize IDs to lowercase and replace non-safe characters with `-`.
- Scope file IDs by repo: `{repo_id}#file#{normalized_path}`.
- Scope symbol IDs by parent: `{parent_id}#{type}#{normalized_label}`.
- Scope unresolved targets as `external#{kind}#{normalized_label}`.
- Never reuse one raw ID for two ontology types.

## Confidence Rules

- Python AST extraction: `0.9` to `0.98`
- Heuristic extraction: `0.45` to `0.75`
- Explicit external targets: `0.4` to `0.7`
- Unsupported-language file node: `0.35`

## Query Semantics

- `--node`: bounded neighborhood in both directions
- `--impact`: downstream blast radius using outgoing edges only
- `--from/--to`: shortest path search
- `--search`: lexical search across labels, paths, tags, summaries, and properties

Use the smallest query that proves the answer. A one-hop neighborhood is the default for orientation; two or three hops are for explicit blast-radius or path questions. Whole-graph export belongs in reports and diagrams, not in the model context window.

When the user asks for code behavior, use the graph to choose files and symbols to inspect, then read the source. The graph is evidence about structure; source files, tests, and runtime traces remain the authority for behavior.

## Structural Risk Analysis

Beyond bounded blast radius, three classical algorithms surface *structural* risk that fan-in and BFS miss. All three are O(V+E) on the graph and run in milliseconds for repos under ~50k symbols.

### Articulation Points and Bridges (Tarjan)

An **articulation point** (cut vertex) is a node whose removal disconnects the graph. A **bridge** (cut edge) is an edge whose removal does the same. These are the literal single points of failure: the file or import that, if changed wrong, severs whole subsystems.

```bash
python3 query_code_graph.py graphs/code-graph.json --articulation-points --top 20
python3 query_code_graph.py graphs/code-graph.json --bridges --top 20
```

When to use:
- Pre-merge review for changes that touch high-degree files. If the changed file is an articulation point, the change deserves extra scrutiny — not because of edit volume, but because a regression breaks more of the graph than a typical edit would.
- Onboarding: articulation points are the files a new engineer should read first. They sit on the most paths.
- Refactoring planning: bridges are candidates for explicit interface boundaries.

Output: ranked list with `node_id`, `path`, `components_disconnected_if_removed`. A node listed alongside `weighted_fan_in` from the portfolio graph (§5 in `dev-context-multi-repo/references/knowledge-graph-patterns.md`) gives a richer picture than either alone — fan-in says "many things point at this," articulation says "many things are reachable *only through* this."

### Extended Cycle Detection

The portfolio validator (§11 of knowledge-graph-patterns.md) runs cycle detection only on `depends_on`. The single-repo code graph should run it on three more relations:

| Relation | Why cycles matter |
|---|---|
| `imports` | Circular imports are a real footgun in Python, JS/TS, Swift; they cause runtime errors, partial-init bugs, or silent type-resolution failures depending on the language. |
| `inherits` | Cyclic inheritance is a compile error in most languages but possible to construct via heuristic extraction over partial files. A reported cycle here usually means the parser misidentified a class — useful as a parser sanity check. |
| `calls` | Recursion is legal but worth surfacing: cycles in `calls` highlight intentional recursion, mutual recursion across modules, and accidental call loops that bypass tail-call optimization. |

```bash
python3 query_code_graph.py graphs/code-graph.json --cycles --relations imports,inherits,calls
```

Output groups cycles by relation and lists the smallest cycle covering each strongly-connected component. Treat `imports` cycles as findings to investigate; `inherits` cycles as parser-correctness signals; `calls` cycles as informational.

### Topological Sort

For DAGs derived from the graph (`imports` after cycle removal, `depends_on`, `inherits`), a topological sort gives canonical build / load / read order:

```bash
python3 query_code_graph.py graphs/code-graph.json --topo-sort --relation imports
```

Useful for:
- Generating module-by-module documentation in the right reading order (read leaves first, root last).
- Picking a valid edit sequence when a refactor must touch multiple modules without breaking intermediate states.
- Planning incremental migrations: edit leaves first, then walk up.

If the chosen relation has cycles, return them via `--cycles` first. Topological sort is only defined on DAGs.

### k-Shortest Paths

`--from <a> --to <b>` returns one shortest path. For propagation analysis ("how could a change in A reach B"), one path understates the risk surface. Add `--k 3` to return the top three node-disjoint shortest paths instead.

```bash
python3 query_code_graph.py graphs/code-graph.json --from <id> --to <id> --k 3
```

When to use:
- Estimating coupling: more paths between two nodes = harder to cleanly separate them.
- Test planning: each disjoint path is a separate way the change can propagate, so each path deserves its own test.
- Architecture review: zero paths between two modules is a healthy sign of separation; many paths is a coupling smell.

## V1 Boundaries

- Prefer deterministic extraction over speculative graph enrichment.
- Emit partial but labeled output rather than hallucinating precise relationships.
- Treat test-link resolution as best effort and confidence-scored, not exact coverage proof.
- Do not merge symbol-level nodes into portfolio-level knowledge graphs. Publish code graph reports and link them from repo catalog pages.
- Do not re-ingest LLM-authored module summaries as source evidence unless the original file paths and graph node IDs remain attached.

This discipline — *code for data, LLMs for judgment* — is the same one adopted independently in document-ingest systems for knowledge hubs. See [garrytan/gbrain](https://github.com/garrytan/gbrain) `docs/guides/deterministic-collectors.md` (MIT, commit `adb02b7`) for a parallel articulation in the note-ingest domain. Convergent evidence that deterministic collectors + latent judgment on structured output is a robust pattern across both symbol-level code graphs and entity-level knowledge graphs.
