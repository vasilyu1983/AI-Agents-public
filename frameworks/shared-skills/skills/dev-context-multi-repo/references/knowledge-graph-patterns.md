# Knowledge Graph Patterns

## Table of Contents

- [1. Node Type Ontology](#1-node-type-ontology)
- [2. Edge Type Ontology](#2-edge-type-ontology)
- [3. Entity Normalization Rules](#3-entity-normalization-rules)
- [4. Graph Construction Pipeline](#4-graph-construction-pipeline)
- [5. Edge Weights](#5-edge-weights)
- [6. Node Enrichment Fields](#6-node-enrichment-fields)
- [7. Incremental Update Protocol](#7-incremental-update-protocol)
- [8. Query Patterns](#8-query-patterns)
- [9. Query Routing Discipline](#9-query-routing-discipline)
- [10. Consistency Checking](#10-consistency-checking)
- [11. Validation Checks](#11-validation-checks)
- [12. Bitemporal Edges (Schema-Ready, v2)](#12-bitemporal-edges-schema-ready-v2)
- [13. Personalized PageRank](#13-personalized-pagerank)
- [14. Community Detection (Leiden)](#14-community-detection-leiden)
- [15. Query Mode Taxonomy](#15-query-mode-taxonomy)

## 1. Node Type Ontology

| Type | Detection Signals |
|---|---|
| `repo` | Directory corresponds to a scanned git repository; `repo_id` in profile JSON; service listed under an api-catalog domain; Mermaid node in a producer/consumer subgraph; repository row in platform-summary or infrastructure-matrix |
| `domain` | Top-level group from `overview/README.md`; domain in `api-catalog.json`; domain owner in process-catalog |
| `provider` | Provider row in integration-matrix; external provider mentioned in a process detail card |
| `process` | `PRO-xxx` row in the process inventory table; process detail card heading |
| `artifact` | Overview documents indexed from `overview/README.md` or a parsed hub source such as api-catalog, platform-summary, or process-catalog |
| `service` | Reserved/manual type in the schema; not emitted by the current deterministic hub parsers |
| `library` | `dependencies_direct[]` entry in profile mode |
| `package` | NuGet Mermaid node whose label starts with uppercase and contains a `.`; package row in cross-repo-dependencies.md |
| `api_endpoint` | Entries in `endpoints[]` within an api-catalog service; node ID format `{repo_id}#{METHOD}#{path}` |
| `queue_topic` | Node inside a `topics`/`kafka`/`rabbit` Mermaid subgraph in messaging-topology.md; target of `publishes_to`, source of `subscribes_to` |
| `database` | Row in database-schemas.md with `Service` + `Engine` columns; node ID format `{repo_id}#{engine_norm}` |
| `table` | Individual comma-separated value in `Key Tables/Collections` column of database-schemas.md; node ID format `{db_id}#{normalize_id(name)}` |
| `entity` | Fallback type for `sub_entities[]` entries in a profile JSON that do not specify a `type` |
| `event` | `sub_entities[]` entry with `"type": "event"` in a profile JSON |
| `config` | `sub_entities[]` entry with `"type": "config"` in a profile JSON |
| `context_artifact` | `sub_entities[]` entry with `"type": "context_artifact"` in a profile JSON |
| `skill` | `sub_entities[]` entry with `"type": "skill"` in a profile JSON |
| `agent` | `sub_entities[]` entry with `"type": "agent"` in a profile JSON |

`api_endpoint` and `artifact` nodes are exempt from orphan validation. Endpoint leaves are expected, and artifact coverage is reported separately by `check_graph_consistency.py`.

---

## 2. Edge Type Ontology

### Structural

| Relation | When to use | Source evidence |
|---|---|---|
| `contains` | A parent logically owns a child as a constituent part. Domain→repo, repo→sub_entity, database→table | api-catalog domain→service mapping; `sub_entities[]` in profile; database-schemas.md rows; `--profiles` domain container logic |
| `imports` | One module or file imports another within the same codebase | `sub_entities[]` edge with `"relation": "imports"`; not emitted automatically by hub parsers |
| `exposes` | A repo publishes an API endpoint or NuGet package to external consumers | api-catalog `endpoints[]` parsed by `parse_api_catalog`; `published_by` column in cross-repo-dependencies.md |

### Behavioral

| Relation | When to use | Source evidence |
|---|---|---|
| `calls` | One service invokes another synchronously (HTTP/RPC) or via an unknown flow | Mermaid arrows not matching producer→topic or topic→consumer patterns in messaging-topology.md; integration-matrix rows with `messaging` containing `kafka` keyword |
| `subscribes_to` | A consumer repo receives messages from a queue/topic | Mermaid arrow from a `topics` subgraph node to a `consumers` subgraph node in messaging-topology.md |
| `publishes_to` | A producer repo sends messages to a queue/topic | Mermaid arrow from a `producers` subgraph node to a `topics` subgraph node in messaging-topology.md |
| `uses_provider` | A repo or process relies on an external provider | integration-matrix repo→provider rows; process detail card `External Providers` field |
| `implements_process` | A repo participates directly in a business process | Process detail card `Service Chain` entries extracted from backticks |

### Data Flow

| Relation | When to use | Source evidence |
|---|---|---|
| `reads_from` | A service queries a database it does not own | Not emitted by current hub parsers; add manually or via future profile fields |
| `writes_to` | A service writes data to a database it does not own | Not emitted by current hub parsers; add manually or via future profile fields |
| `owns_data_in` | A service is the authoritative owner of a database | database-schemas.md row: `repo_id → db_id`; emitted by `parse_database_schemas` |

### Dependency

| Relation | When to use | Source evidence |
|---|---|---|
| `depends_on` | One repo or service requires another to function (compile-time, runtime, or integration) | `dependencies_direct[]` in profile JSON; integration-matrix `repo → provider`; NuGet Mermaid arrows; `consumed_by` column in cross-repo-dependencies.md |
| `shares_library_with` | Two repos share a common internal library without a direct dependency edge | Not emitted automatically; add manually when `depends_on` edges converge on the same `package` node and a lateral relationship needs naming |
| `deploys_with` | Two repos are deployed as a unit | Not emitted automatically; add via profile `sub_entities` or manual edges |
| `replaces` | One repo or service is the successor of another | Not emitted automatically; add manually during migration mapping |
| `extends` | One repo adds capabilities to another without replacing it | Not emitted automatically; add manually |

### Semantic

| Relation | When to use | Source evidence |
|---|---|---|
| `documents` | An artifact node documents another node or another artifact | Overview artifacts created by hub parsers: api-catalog, platform-summary, process-catalog, database-schemas, integration-matrix, messaging-topology, cross-repo-dependencies, and overview-indexed docs |
| `governed_by` | A node is constrained by an explicit governance or policy artifact | Reserved/manual relation for future policy ingestion |
| `related_to` | Loose topical association that does not fit structural or behavioral groups | Manual; use when two nodes share a domain but have no direct runtime relationship |
| `similar_to` | Two nodes serve equivalent purposes in different contexts | Manual; useful for identifying consolidation candidates |
| `contradicts` | Two nodes hold conflicting definitions or responsibilities | Manual; flag for architecture review |
| `co_occurs` | Two nodes appear together in the same context artifact, document, or scan | Manual or future NLP-derived |

---

## 3. Entity Normalization Rules

**Engine canonicalization** (`normalize_engine`): the following aliases are mapped to canonical keys before graph insertion.

| Raw input | Canonical key |
|---|---|
| `sql server`, `sqlserver` | `sqlserver` |
| `mongodb`, `mongo` | `mongodb` |
| `postgresql`, `postgres`, `pg` | `postgresql` |
| `elasticsearch`, `es` | `elasticsearch` |
| `kafka` | `kafka` |
| `rabbitmq` | `rabbitmq` |
| `redis` | `redis` |
| `dynamodb` | `dynamodb` |
| `s3` | `s3` |

Any value not in the table is passed through `normalize_id`.

**Node ID normalization** (`normalize_id`): applied to every label before use as a graph node ID.

1. Lowercase the string.
2. Strip leading and trailing whitespace.
3. Replace any character outside `[a-z0-9._-]` with a hyphen.
4. Strip leading and trailing hyphens from the result.

Example: `"My Service (v2)"` → `"my-service--v2-"` → `"my-service--v2"`.

**Type-scoped collision handling**: the builder starts from `normalize_id(label)`. If that ID is already taken by a different ontology type, it scopes the later node as `{type}-{normalize_id(label)}`. This avoids collisions such as a domain `notifications` and a repo `notifications`.

**Node merge behavior**: when the same typed ID is seen again, `GraphBuilder.add_node` merges data into the existing node:

- `evidence` arrays are concatenated.
- `tags` are unioned.
- `properties` keys are merged non-destructively.
- Scalar fields already present in the existing node are left unchanged (first-writer wins).

Duplicate node IDs that reach the output JSON (which would indicate a bug in the builder) are detected by `check_duplicates` in `validate_graph.py`.

---

## 4. Graph Construction Pipeline

### Mode A — `--profiles <dir>`

Reads every `*.json` file in the given directory. Each file is a repo profile.

Processing per profile:
1. A `repo` node is created from `repo_id` (or stem of the filename) and `repo_name`.
2. If `repo_group` is set, a `domain` node is created and a `contains` edge is added from domain → repo.
3. Each entry in `sub_entities[]` becomes a child node (type from `sub_entities[].type`, default `entity`) with a `contains` edge from repo → sub_entity.
4. Each entry in `dependencies_direct[]` becomes a `library` node with a `depends_on` edge from repo → library.

Default output path: `<profiles_dir>/../graphs/knowledge-graph.json`.

### Mode B — `--hub <dir>`

Parses hub sources from a requirements-hub directory in this order:

| Step | Source file | Parser |
|---|---|---|
| 1 | `overview/README.md` | `parse_overview_readme` — creates `artifact` nodes for overview docs and external references |
| 2 | `overview/api-catalog.json` | `parse_api_catalog` — creates `domain`, `repo`, and `api_endpoint` nodes; collapses duplicate endpoint rows to unique `(repo, method, path)` routes; emits `contains`, `exposes`, and `documents` edges |
| 3 | `overview/messaging-topology.md` | `parse_messaging_topology` — extracts Kafka and RabbitMQ Mermaid blocks; `publishes_to`, `subscribes_to`, and fallback `calls` edges |
| 4 | `overview/database-schemas.md` | `parse_database_schemas` — parses markdown tables; `owns_data_in`, `contains`, and `documents` edges |
| 5 | `overview/integration-matrix.md` | `parse_integration_matrix` — creates `provider` nodes and `uses_provider` edges; optionally `calls` when messaging hints it |
| 6 | `overview/nuget-dependency-map.md` | `parse_nuget_dependency_map` — parses Mermaid blocks; `depends_on` edges; subgraph IDs resolve to domain nodes |
| 7 | `*/as-is/cross-repo-dependencies.md` | `parse_cross_repo_dependencies` — walks the hub recursively; `exposes`, `depends_on`, and `documents` edges |
| 8 | `overview/platform-summary.md` | `parse_platform_summary` — enriches repo nodes with LOC, language, type, domain; populates `meta.portfolio_metrics` |
| 9 | `overview/infrastructure-matrix.md` | `parse_infrastructure_matrix` — enriches repo nodes with storage, messaging, runtime, and infra version |
| 10 | `overview/process-catalog.md` | `parse_process_catalog` — creates `process` nodes; `contains`, `implements_process`, `uses_provider`, and `documents` edges |

Default output path: `<hub_dir>/graphs/knowledge-graph.json`.

**Mermaid parsing details (Mode B)**: both messaging and NuGet parsers use regex against raw Mermaid text.

- Arrow forms recognized: `A --> B`, `A ==> B`, `A -->|"label"| B`, `A -->|label| B & C & D`
- Compound targets (`& C & D`) are split and each target gets its own edge.
- Subgraph IDs are tracked in `subgraph_labels`; when an arrow target matches a subgraph ID rather than a node ID, the target resolves to the subgraph's domain node.
- Node labels with HTML `<br/>` or `<br>` are cleaned via `strip_br` before use as graph labels.

---

## 5. Edge Weights

Every edge has an optional `weight` field (0.0–1.0) representing dependency strength. `build_knowledge_graph.py` assigns weights automatically based on relation type:

| Weight | Relations |
|--------|-----------|
| `1.0` | `contains` |
| `0.9` | `exposes`, `owns_data_in` |
| `0.8` | `calls`, `publishes_to`, `subscribes_to`, `uses_provider`, `implements_process` |
| `0.7` | `imports`, `reads_from`, `writes_to` |
| `0.6` | `depends_on`, `extends` |
| `0.5` | `shares_library_with`, `deploys_with` |
| `0.4` | `replaces`, `documents`, `governed_by` |
| `0.3` | `related_to`, `similar_to`, `contradicts`, `co_occurs` |

Weights feed into fan-in ranking (`--rank` in `query_graph.py`): `weighted_fan_in = Σ weight` of all incoming edges. A node depended on via `contains` edges (weight 1.0) ranks higher than the same fan-in count via `related_to` edges (weight 0.3), matching architectural criticality more accurately than raw degree.

### Calibrated Weights (opt-in)

The static table above is the default. For noisy portfolios — many sources of varying reliability, contradictions across docs, edges inferred from prose — the static weight is too coarse: a `depends_on` edge confirmed by three manifests should outrank a `depends_on` edge inferred from one Mermaid arrow, but the static table assigns both `0.6`.

The opt-in `calibrated` mode replaces the static weight with a per-edge value derived from observed evidence:

```
weight_calibrated = base_weight(relation)
                  × evidence_factor
                  × provenance_factor
                  × agreement_factor
```

| Factor | Range | Formula |
|---|---|---|
| `base_weight(relation)` | 0.3–1.0 | Static §5 table — anchors the relation type |
| `evidence_factor` | 0.5–1.2 | `min(1.2, 0.5 + 0.1 × len(evidence))` — more evidence entries lifts the weight, capped at 1.2× |
| `provenance_factor` | 0.4–1.1 | `1.0` for direct evidence (manifest, schema, workflow); `0.7` for indirect (Mermaid, prose); `0.4` for inferred-only |
| `agreement_factor` | 0.6–1.2 | `1.2` if ≥3 distinct sources agree; `1.0` for 1–2; `0.6` if at least one source contradicts |

Final weight is clamped to `[0.05, 1.0]` to keep PPR transition probabilities well-defined and to respect the `confidence_floor` validator (§11 check #4).

### Storage Shape

When calibration runs, every edge gains two fields:

```json
{
  "source": "payments",
  "target": "audit.events.v1",
  "relation": "publishes_to",
  "weight": 0.8,
  "weight_static": 0.8,
  "weight_calibrated": 0.96,
  "weight_factors": {
    "evidence": 1.1,
    "provenance": 1.0,
    "agreement": 1.2
  }
}
```

`weight` remains the active value used by `--rank` and PPR. By default `weight = weight_static`. When the build runs with `--weights calibrated`, the builder copies `weight_calibrated → weight` and downstream queries pick up the calibrated values transparently.

### When to Switch

Stick with static weights when:
- the portfolio is small (under ~30 repos)
- evidence sources are uniformly trustworthy (e.g., only manifests + schemas)
- there is no operator capacity to investigate calibration drift

Switch to calibrated weights when:
- the hub ingests prose and Mermaid alongside manifests, and you want prose-only edges to rank lower
- multiple parsers contribute the same edge type and you want source-agreement to boost confidence
- `--rank` results are being driven by edges that operators don't trust

### Operating Calibrated Mode

```
# 1. Build with calibration enabled
python3 build_knowledge_graph.py --hub /path/to/hub --weights calibrated

# 2. Or recalibrate an existing graph in place without re-parsing sources
python3 calibrate_weights.py graphs/knowledge-graph.json \
  --output graphs/knowledge-graph.json

# 3. Inspect the top calibration changes vs the static baseline
python3 calibrate_weights.py graphs/knowledge-graph.json \
  --diff-against graphs/knowledge-graph.static.json \
  --top 20
```

Validation additions for calibrated mode:
- every edge must have `weight_static` populated even when `weight_calibrated` is missing — round-trip to static must always be possible
- `weight_calibrated` outside `[0.05, 1.0]` is a calibration bug, not a data quality issue
- `agreement_factor < 1.0` on an edge means at least one source contradicted the edge — surface these in the consistency report (§10) for review

Calibrated mode is purely additive: existing graphs without `weight_calibrated` fields keep working, and `--rank` / PPR queries default to `weight_static` unless `--weights calibrated` is passed at query time.

---

## 6. Node Enrichment Fields

Nodes support two LLM-enrichable fields and one computed field:

| Field | Type | Description |
|-------|------|-------------|
| `summary` | `string` | 1-2 sentence plain-English description of the node's purpose. Set during `parse_api_catalog` from service metadata; otherwise left unset for post-hoc LLM enrichment. |
| `tags` | `string[]` | 3-5 lowercase hyphenated tags (e.g. `["payments", "kafka-producer", "csharp"]`). Set during `parse_api_catalog`; otherwise empty. |
| `importance` | `number` | Fan-in count: number of edges whose target is this node. Higher = more critical. Computed and written by `query_graph.py --rank`, not by the builder. |

These three fields are intentionally left sparse by the deterministic parser passes. Populate them with an LLM pass after the initial build for maximum value (the schema marks them as `LLM-enrichable` in the description fields).

---

## 7. Incremental Update Protocol

### Full rebuild (standard workflow)

1. Optionally rename the existing file: `mv knowledge-graph.json knowledge-graph.prev.json`.
2. Re-run `build_knowledge_graph.py` with the same mode and source path.
3. Run `validate_graph.py graphs/knowledge-graph.json --output reports/graph-validation.json`.
4. Run `check_graph_consistency.py --hub /path/to/hub --graph graphs/knowledge-graph.json --output reports/consistency-report.json` when using hub mode.
5. Compare node and edge counts against the `.prev.json` backup. A drop of more than ~10% in either count without a corresponding source file removal is a data quality signal — investigate before discarding the previous graph.

### Incremental update (`incremental_update.py`)

Uses `meta.base_commit_shas` (a map of `repo_id → git SHA at last scan time`) to detect which repos have changed since the last build.

```
python3 incremental_update.py graphs/knowledge-graph.json \
    --repo-map repos.json          # {repo_id: "/abs/path/to/repo"}
    [--profiles profiles/]         # optional: re-scan and merge updated profiles
    [--dry-run]                    # report changes without writing
    [--output graphs/knowledge-graph.next.json]
    [--report reports/incremental-update.json]
    [--repo-root main=/work/platform]
```

`repos.json` format:
```json
{
  "payments-ledger": "/abs/path/to/Payments.Ledger",
  "sc-booking": "/abs/path/to/Sc.Booking"
}
```

Portable `repos.json` format:
```json
{
  "roots": {
    "main": ["../.."],
    "qa": ["../../../platform-qa"],
    "legacy": ["../../../platform-legacy", "../../../../platform-legacy"]
  },
  "repos": {
    "payments-ledger": {"root": "main", "path": "payments-ledger"},
    "qa-tests": {"root": "qa", "path": "qa-tests"},
    "platform-legacy-backend": {"root": "legacy", "path": "backend"}
  }
}
```
The loader resolves root candidates relative to the repo-map file, then applies any `--repo-root NAME=PATH` or `DEV_CONTEXT_REPO_ROOT_<NAME>` overrides. This lets one hub run across different checkout layouts without rewriting the graph.

**Protocol**:
1. Read `meta.base_commit_shas`. On the first incremental run this may be empty.
2. Run `git rev-parse HEAD` per repo; compare to stored SHA.
3. If there is no stored SHA yet, seed the baseline SHA without staling existing graph nodes.
4. If `--profiles` is given and the repo is new to the graph, queue it for profile merge.
5. Mark nodes for changed repos as `stale: true` (the repo node and all its children).
6. If `--profiles` is given, load updated profile JSONs for changed repos and merge.
7. Remove nodes that are still stale after merge.
8. Update `meta.base_commit_shas` with new HEADs.
9. Write the updated graph and optional report (unless `--dry-run`). Report path fields are rendered relative to the report file when `--report` is used, which keeps artifacts machine-neutral.

The script returns a JSON summary to stdout with `repos_changed`, `repos_unchanged`, `repos_bootstrapped`, `repos_not_found`, `repos_invalid_git`, `nodes_marked_stale`, `nodes_removed`, `profiles_merged`.

---

## 8. Query Patterns

All queries use `query_graph.py <graph.json> <command> [options]`.

**Service neighborhood** — who does this service directly talk to:
```
python3 query_graph.py graphs/knowledge-graph.json --node <id> --hops 1
```
BFS in both directions (outgoing and incoming edges). Returns all nodes and edges within 1 hop.

**Blast radius** — who is downstream if this node changes:
```
python3 query_graph.py graphs/knowledge-graph.json --impact <id> --hops 2
```
BFS on outgoing edges only. Use `--hops 2` or `--hops 3` for wider propagation analysis.

**Dependency path** — how are two services connected:
```
python3 query_graph.py graphs/knowledge-graph.json --from <id> --to <id> --max-hops 4
```
Returns all shortest paths. Uses outgoing edges only. Default `--max-hops` is 3.

**Domain inventory** — list all repos in the graph:
```
python3 query_graph.py graphs/knowledge-graph.json --type repo
```
Replace `repo` with any valid node type: `service`, `package`, `queue_topic`, `database`, etc.

**Lexical search** — search labels, summaries, tags, and flattened properties:
```
python3 query_graph.py graphs/knowledge-graph.json --search "sumsub kyc" --types provider,process,repo --limit 10
```

**Mermaid output for documentation**:
```
python3 query_graph.py graphs/knowledge-graph.json --node <id> --hops 1 --format mermaid
```
Outputs a Mermaid flowchart with labeled arrows. Use `--mermaid-direction` (`LR`, `RL`, `TD`, `TB`, `BT`) and `--mermaid-group-by` (`none`, `type`, `domain`) to tune layout, and `--output` to write `.mmd` files directly.

**Filtered portfolio diagram export**:
```
python3 query_graph.py graphs/knowledge-graph.json \
  --diagram \
  --include-types domain,repo,provider,process \
  --exclude-relations documents \
  --mermaid-group-by domain \
  --output diagrams/platform-overview.mmd
```
Use `--include-types` / `--exclude-types`, `--include-relations` / `--exclude-relations`, and `--diagram-limit` to shape portfolio diagrams for docs or reviews.

**Static report export**:
```
python3 export_graph_report.py graphs/knowledge-graph.json --output-dir reports/
```
Writes:
- `reports/graph-report.html` — self-contained local report with search, summary tables, relationship slices, and embedded Mermaid source
- `reports/graph-report.md` — repo-native Markdown companion with the same core sections and Mermaid blocks

This skill stays headless by design. Treat the HTML and Markdown reports as the default human-facing outputs. If a team needs richer visual exploration later, convert from `knowledge-graph.json` or Mermaid exports into an external viewer instead of adding an app runtime to the skill.

**Table format for quick inspection**:
```
python3 query_graph.py graphs/knowledge-graph.json --node <id> --hops 1 --format table
```

---

## 9. Query Routing Discipline

Do not send every question through the largest graph query. Pick the smallest reliable context path:

| User question shape | Default route | Escalate to graph when |
|---|---|---|
| "What is repo X?" | `catalog/<repo>.md` plus `profiles/<repo>.json` | The answer depends on upstream/downstream relationships |
| "Where is feature Y?" | Lexical search over catalog, profiles, and code graph reports | Search hits span repos and need ownership or dependency resolution |
| "What breaks if X changes?" | Per-repo `dev-context-code-graph` impact query if X is a file/symbol | The impact crosses service, provider, queue, package, or data boundaries |
| "How do these repos connect?" | Portfolio graph neighborhood or path query | Always: this is relationship-first |
| "Catch me up on this platform" | Compiled concept page plus freshness report | The concept page is stale or incomplete |
| "Find all dependencies/providers" | Structured profile fields and system edges | Manual docs disagree with manifests or generated edges |

April 2026 guardrail: graph-augmented retrieval helps most when the query is relational, multi-hop, or global. For simple lookup, dense/lexical retrieval and direct catalog reads are usually cheaper and less noisy. For broad portfolio questions, prefer dynamic pruning of irrelevant subgraphs or community reports before synthesis instead of static "include all graph summaries" prompts.

Every routed answer should preserve provenance:

- cite source artifact paths or graph node IDs
- state whether the answer came from direct evidence, generated graph edges, or inference
- include scan date / `last_verified` when freshness matters
- write reusable answers back to reports or concept pages

---

## 10. Consistency Checking

Use `check_graph_consistency.py` to compare source documents against graph coverage, freshness, and persisted reports.

Checks currently include:
- unique endpoint counts across `api-catalog.json`, `api-catalog.md`, and graph coverage
- duplicate raw endpoint rows in `api-catalog.json`
- process counts across process inventory, executive summary, and graph coverage
- provider counts across integration-matrix and graph coverage
- platform-summary metrics vs repository table rows
- missing `base_commit_shas`
- missing validation report
- source documents newer than the graph
- artifact nodes with no outgoing coverage and no incoming artifact documentation links

The script is intentionally strict: it surfaces source drift instead of normalizing it away.

Node lookup is case-insensitive: if the exact ID is not found, the query falls back to a case-insensitive match and logs the substitution to stderr.

**Criticality ranking** — most-depended-on nodes across all types:
```
python3 query_graph.py graphs/knowledge-graph.json --rank --top 20
```
Ranks nodes by `weighted_fan_in` (sum of incoming edge weights) then by raw `fan_in` count. The result includes `fan_in`, `weighted_fan_in`, `summary`, and `tags` fields per node. Use `--filter-type repo` to rank repos only, `--filter-type package` to rank NuGet packages, etc. Use `--top 0` to list all nodes.

---

## 11. Validation Checks

Run with:
```
python3 validate_graph.py graphs/knowledge-graph.json [--max-age-days N] [--fix]
```

Output is JSON with per-check `passed`, `issue_count`, and up to 10 `issues` per check. Exit code 0 = all checks passed, 1 = one or more failed.

Pass `--fix` to auto-repair before validation:
- Removes edges referencing missing nodes (dangling refs)
- Adds missing `contains` edge for any `parent_id` node that lacks one
- Deduplicates nodes (keeps first occurrence by list order)

The `repairs_applied` field in the output lists all changes made. The graph file is updated in place.

| # | Check name | What it verifies | Notes |
|---|---|---|---|
| 1 | `schema_compliance` | Every node `type` is in the 14-value enum; every edge `relation` is in the 18-value enum; every edge `group` is in the 5-value enum | Catches typos and manually authored nodes that use non-standard types |
| 2 | `dangling_refs` | Every edge `source` and `target` references a node ID that exists in the `nodes` array | A dangling ref means a node was removed or its ID was changed without updating edges |
| 3 | `orphans` | Every non-exempt node appears in at least one edge as source or target | `api_endpoint` nodes are fully exempt. `package` and `repo` orphans are surfaced as data quality findings, not hard errors — they indicate a scanned node with no detected relationships |
| 4 | `confidence_floor` | No node or edge has a `confidence` value below `0.05` | Only applies to entries where the `confidence` field is present; entries without the field are skipped |
| 5 | `duplicates` | No node ID appears more than once in the `nodes` array | Should not occur if `GraphBuilder` is used correctly; indicates a hand-edit or merge error |
| 6 | `containment_consistency` | Every node with a `parent_id` field has a corresponding edge from the parent using `contains`, `exposes`, or `owns_data_in` | Catches nodes created with `parent_id` but whose parent edge was not emitted |
| 7 | `staleness` | No node with a `last_verified_at` field is older than the threshold (default 90 days) | Pass `--max-age-days 60` for tighter freshness requirements. Nodes without `last_verified_at` are skipped |
| 8 | `circular_deps` | No cycles exist in the `depends_on` subgraph | Cycles indicate circular dependency chains that can cause build or startup failures. Uses iterative DFS over `depends_on` edges only |

---

## 12. Bitemporal Edges (Schema-Ready, v2)

<!-- Sources: MemPalace/mempalace@6614b9b4 (MIT, extracted 2026-04-13); Zep/Graphiti bitemporal pattern (Rasmussen et al., 2025); Memento LongMemEval 92.4% (April 2026). -->

The current schema captures the *current* state of the portfolio. It cannot answer temporal questions like "what did the architecture look like in Q3 2025?" or "when did `payments` stop publishing to the legacy topic?" — and it cannot distinguish "this was true on 2025-06-01" from "we discovered on 2026-04-15 that it was true on 2025-06-01." That second axis matters when facts are corrected retroactively, when source documents are re-ingested, or when a postmortem needs to know what the agent believed at decision time.

A minimal **bitemporal** extension is documented here as v2. Two timelines per edge, not one.

### Proposed Field Additions

Every edge gains four optional fields, two per timeline:

| Field | Timeline | Meaning |
|---|---|---|
| `t_valid_from` | event time | ISO-8601 date this relationship became true in the world |
| `t_valid_to` | event time | ISO-8601 date this relationship stopped being true in the world (absent / null = still current) |
| `t_ingest_from` | ingest time | ISO-8601 date the hub first observed this edge |
| `t_ingest_to` | ingest time | ISO-8601 date the hub stopped believing this edge (absent / null = still believed) |

Optional companion fields: `confidence` (already supported), `superseded_by` (ID of the edge that replaced this one), and `source_evidence_ref` (path or commit hash that the ingest decision was based on).

The single-timeline `valid_from / valid_to` shape from the original v2 sketch is a degenerate case where `t_ingest_from = t_valid_from` and `t_ingest_to = t_valid_to`. Tools that only need event time can ignore the ingest fields; tools that need audit and replay can rely on them.

### Query Semantics

- Default queries (`--node`, `--impact`, `--from/--to`) return edges currently valid in *both* timelines: `t_valid_to IS NULL AND t_ingest_to IS NULL`.
- `--as-of YYYY-MM-DD` filters by event time: `t_valid_from <= date AND (t_valid_to IS NULL OR t_valid_to > date)`.
- `--known-at YYYY-MM-DD` filters by ingest time: "what did the hub believe on this date?" Useful for postmortems and replay.
- `--as-of X --known-at Y` answers "what did the hub on date Y believe was true on date X?" — the canonical bitemporal question.
- `--timeline <node>` returns a chronological history of all edges touching the node across both axes.

### Invalidation, Not Deletion

When a relationship stops being true (or stops being believed), the edge is **not deleted**. Two example transitions:

```json
// World changed: payments service migrated to v2 topic on 2026-02-15
{
  "source": "payments",
  "target": "payments.settlement.v1",
  "relation": "publishes_to",
  "t_valid_from": "2025-06-01",
  "t_valid_to": "2026-02-15",
  "t_ingest_from": "2025-06-02",
  "superseded_by": "payments__publishes_to__payments.settlement.v2"
}

// Belief changed: edge was wrong, corrected by re-ingest on 2026-04-20
{
  "source": "payments-ledger",
  "target": "audit.events.v1",
  "relation": "publishes_to",
  "t_valid_from": "2025-09-01",
  "t_ingest_from": "2025-09-03",
  "t_ingest_to": "2026-04-20",
  "source_evidence_ref": "payments-ledger@d9f2a1e:src/Producers/AuditPublisher.cs"
}
```

The first edge is event-time invalidation: real change, both axes preserved. The second is ingest-time invalidation: belief retracted, world unchanged.

### Storage Format

JSON-first stays JSON-first. The same shape lives in `graphs/knowledge-graph.json` as long as:

1. Edge records gain the four optional fields.
2. `query_graph.py` filters by date when `--as-of` or `--known-at` is passed.
3. `validate_graph.py` adds a check: every edge with `t_valid_to` set must either be the most recent edge of its `(source, relation, target)` triple or point to a `superseded_by` ID that exists. Same check for `t_ingest_to`.
4. `build_knowledge_graph.py` switches from overwrite to merge: new scan adds edges with `t_ingest_from = today`; edges that disappeared get `t_ingest_to = today` instead of being dropped.
5. One-time migration: set `t_ingest_from = file_mtime` on every existing edge so default queries remain equivalent.

### Schema vs Engine Status (May 2026)

**Shipped**:
- Schema fields (`valid_at`, `valid_until`, `ingested_at`, `ingested_until`, `superseded_by`, `supersedes`, `edge_id`) are first-class in `schemas/knowledge-graph.schema.json`.
- Query-engine time filtering: `query_graph.py --as-of <date>` and `--known-at <date>` apply a bitemporal slice to every read path (BFS, impact, paths, rank, PPR, communities, search, diagram).
- Default semantics: with no flags, queries return only currently-valid edges (`valid_until` and `ingested_until` absent). Graphs without bitemporal fields are unaffected — the filter is bypassed when no edge carries time metadata.

**Not shipped yet**: scan→merge logic in `build_knowledge_graph.py` (so a fresh scan still overwrites instead of supersedes), `--timeline <node>` chronology view, and supersession integrity in `validate_graph.py`. The engineering side has shipped `check_supersession_integrity` in `dev-context-engineering/scripts/validate_context_graph.py` and that pattern is ready to port.

This split lets you start querying time-sliced views and writing bitemporal-aware ingest pipelines without waiting for the full engine.

### References

- [MemPalace/mempalace](https://github.com/MemPalace/mempalace) — SQLite-based temporal KG, minimal zero-dependency reference for invalidation lifecycle.
- [Zep / Graphiti](https://github.com/getzep/graphiti) — production bitemporal KG for agent memory; LongMemEval +18.5% over baselines, context tokens 115k → 1.6k, latency 30s → 3s.
- [Memento case study (April 2026)](https://explore.n1n.ai/blog/building-bitemporal-knowledge-graph-llm-agent-memory-longmemeval-2026-04-11) — 92.4% LongMemEval task-averaged with bitemporal modeling.

---

## 13. Personalized PageRank

<!-- Source: HippoRAG (NeurIPS'24), Bahmani et al. (Stanford SNAP), Microsoft GraphRAG local-search variant. -->

Global fan-in (§5, §10) answers "what is critical across the whole portfolio." It does not answer "what is contextually relevant *given that I'm working on this file or asking about this domain.*" That is the question every coding agent actually has, and Personalized PageRank (PPR) is the standard 2026 answer.

### What PPR Computes

Run a random walker from one or more **seed nodes**. At each step the walker either follows an outgoing edge (weighted by the §5 relation table) or teleports back to the seed set with probability `α` (typical: 0.15). After convergence, every node has a stationary score: how often the walker visited it. High-score nodes are the contextual neighborhood of the seed.

### When to Use PPR Over Hop-Bounded BFS

| Question shape | Default route | Why |
|---|---|---|
| "Show me the immediate neighborhood of X" | `--node <id> --hops 1` (BFS) | Bounded, fully deterministic, easy to read |
| "What in the portfolio is contextually relevant to X?" | `--ppr --seed <id>` | BFS at hops=2 either misses important distant nodes or floods unrelated ones; PPR weights by structural relevance |
| "Pull context for an agent working on X" | `--ppr --seed <id> --top 30` | Bounded by relevance, not by hop count |
| "Rank nodes globally" | `--rank` (existing weighted fan-in) | Global criticality, no seed |
| "What's similar to X structurally?" | `--ppr --seed <id> --filter-type repo` | PPR + type filter approximates structural similarity |

Rule of thumb: BFS for orientation and blast radius (deterministic, hop-bounded). PPR for retrieval (relevance-weighted, budget-bounded).

### Edge Weights as Transition Probabilities

The §5 weight table is reused directly. For a node with outgoing edges of weights `[1.0, 0.8, 0.4]`, the walker picks each with probability `[0.5, 0.4, 0.1]` after normalization. This is why the §5 weights matter algorithmically, not just for `--rank` ordering: PPR teleports along containment edges (weight 1.0) far more often than along `co_occurs` edges (0.3), which is the right behavior.

PPR honors the §5 calibration option: pass `--weights calibrated` to use `weight_calibrated` as transition probabilities instead of the static table. This concentrates the random walk along edges that the calibration pass judged most trustworthy (more evidence, direct provenance, multi-source agreement) and downweights edges from prose or single-source inference. Use calibrated PPR when retrieval results are being polluted by low-confidence edges; use static PPR otherwise.

### Seed-Set Patterns

| Seed | Returns |
|---|---|
| Single repo node | "What context belongs with this repo" — top related repos, providers, processes, domains |
| Single domain node | "What's in this domain and what does it touch outside" — child repos plus boundary nodes |
| File node from `dev-context-code-graph` | Use the per-repo code graph instead; do not mix symbol-level seeds with portfolio PPR |
| Process node | "What systems implement or depend on this process" |
| Multiple repos (e.g., a feature team) | "What context is shared across this team" — hubs in the team subgraph |

### Proposed CLI

```
python3 query_graph.py graphs/knowledge-graph.json \
  --ppr \
  --seed payments \
  --seed payments-ledger \
  --alpha 0.15 \
  --top 30 \
  --filter-type repo,provider,queue_topic \
  --weights calibrated \
  --format table
```

`--weights {static|calibrated}` defaults to `static`. Pass `calibrated` only when the graph carries `weight_calibrated` fields (see §5); otherwise the query falls back to `weight_static` with a one-line stderr notice.

Output is a ranked list with `node_id`, `type`, `ppr_score`, `summary`, `tags` per row. Exclude seed nodes from the result by default; offer `--include-seeds` for diagnostics.

### Implementation Notes

- For graphs under ~50k nodes, dense iteration via `numpy` converges in <100ms. Use sparse iteration for larger.
- Reference: [`asajadi/fast-pagerank`](https://github.com/asajadi/fast-pagerank) supports both vanilla and personalized PR with sparse matrices.
- Cache PPR results keyed by `(seed_set, alpha, graph_hash)`; recompute only when the graph hash changes (already tracked via `meta.base_commit_shas`).
- For the "agent context retrieval" use case, a token-budget wrapper is more useful than `--top N`: keep walking down the ranked list until a configurable token cap is hit.

### Validation

- PPR scores must sum to ~1.0 (within floating-point tolerance). A failure means the transition matrix has a row of zeros (sink node) — repair by adding a self-loop or by uniform teleport from sinks.
- Score must be non-negative for every node.
- Seeds should rank in the top 10% of their own PPR run (sanity check that the walker actually starts there).

---

## 14. Community Detection (Louvain shipped, Leiden upgrade path)

<!-- Sources: Blondel et al. (2008) "Fast unfolding of communities in large networks"; Traag et al. (2019) "From Louvain to Leiden" (Nature Scientific Reports); Microsoft GraphRAG community-summary tree; CoFine (Sci. Direct, 2025). -->

For portfolios with more than ~50 repos, "global" questions ("what's the architecture?", "catch me up on this platform") cannot be answered by single-seed traversal. Microsoft GraphRAG's answer is hierarchical: detect communities, summarize each one with an LLM, then route global questions to the community-summary tree instead of the raw graph.

### Algorithm Choice: Louvain (shipped) → Leiden (upgrade)

The skill ships a **pure-python Louvain** implementation (`query_graph.py --communities`) so it stays dependency-free. Louvain has a known pathology where it can produce internally-disconnected communities (a "community" with two halves that don't share an edge). For portfolios up to a few thousand nodes the partition is usually fine; we mitigate by running multiple resolutions and validating connectedness in `validate_graph.py`.

For larger portfolios or stability-critical use cases, swap to **Leiden** via `igraph`, `networkx`, or `graspologic`. Leiden adds a refinement phase that guarantees connectedness and runs faster on large graphs. The schema is the same — only the algorithm changes.

### What Gets Detected

Run Leiden on the full graph (or on a directed-edge variant for KGs where edge direction encodes semantics — see CoFine 2025). Output: a partition assigning each node to a `community_id`. Resolution parameter `γ` controls granularity:

- `γ = 0.5` → fewer, larger communities (~5–10 for a 100-repo portfolio)
- `γ = 1.0` → standard granularity (default; ~15–30 communities)
- `γ = 2.0` → many small communities (~40+; usually too fragmented)

Run Leiden at multiple resolutions to build a **hierarchy**: coarse partition for global queries, fine partition for sub-domain queries.

### Schema Additions

Each node gains an optional field:

```json
{
  "id": "payments",
  "type": "repo",
  "community_id": "c.payments-core",
  "community_path": ["c.platform", "c.transactions", "c.payments-core"]
}
```

`community_path` carries the hierarchy from coarsest to finest resolution. Nodes outside any non-trivial community (singletons) carry `community_id: null`.

### Workflow

```bash
# 1. Detect communities (Louvain) at the default γ=1.0 resolution
python3 query_graph.py graphs/knowledge-graph.json \
  --communities \
  --format json \
  --output reports/communities-medium.json

# 2. Re-run at coarse resolution for global summaries
python3 query_graph.py graphs/knowledge-graph.json \
  --communities \
  --resolution 0.5 \
  --weights calibrated \
  --output reports/communities-coarse.json

# 3. Generate one markdown summary per community using
#    assets/community-summary-template.md as the prompt
python3 query_graph.py graphs/knowledge-graph.json \
  --communities --resolution 0.5 --top 0 --format json \
  | jq '.communities[]' \
  > reports/community-summaries.jsonl
```

The shipped command emits modularity (Q), per-community size, type and domain breakdowns, and member ids. Routing global questions to the summary tree is still a manual step until a `--community-summary <query>` route is added.

### When to Use Communities Over PPR or BFS

| Question shape | Default route |
|---|---|
| "What does the platform look like?" | Coarse community summaries (`γ = 0.5`) |
| "Catch me up on the payments domain" | Medium community summary for the payments community |
| "Find clusters of repos that should probably be one repo" | Communities with high internal density and few external edges (consolidation candidates) |
| "What's contextually relevant to this file?" | PPR (§13), not communities |
| "What's the blast radius of changing X?" | BFS impact query, not communities |

### Validation

- Modularity score should be >0.3 for the partition to be meaningful (random graphs score near 0; well-clustered graphs score 0.4–0.7).
- Connectedness: every community must be a connected subgraph (Leiden guarantees this; verify on output anyway).
- Stability: re-run Leiden 5 times with different random seeds. Nodes should land in the same community ≥80% of the time. Below that, the graph genuinely lacks community structure and you should not rely on the partition.

### Integration with Markdown Hub

Each community gets a generated `catalog/communities/<community_id>.md` page listing member repos, dominant edge types within the community, and the boundary edges that cross out of it. Cross-link from the relevant repo catalog pages. This is the markdown surface for the GraphRAG-style "global search" route.

### References

- [Traag, Waltman, van Eck — Nature Scientific Reports (2019)](https://www.nature.com/articles/s41598-019-41695-z) — original Leiden paper, the canonical citation for "guaranteed well-connected communities."
- [Memgraph — Leiden algorithm reference](https://memgraph.com/docs/advanced-algorithms/available-algorithms/leiden_community_detection)
- [NVIDIA — GPU-accelerated Leiden in Python](https://developer.nvidia.com/blog/how-to-accelerate-community-detection-in-python-using-gpu-powered-leiden/) — relevant only for portfolios in the millions of nodes.
- Microsoft GraphRAG's "Global Search" mode is the architectural template for community-summary routing: [microsoft.github.io/graphrag](https://microsoft.github.io/graphrag/).

---

## 15. Query Mode Taxonomy

<!-- Source: Microsoft GraphRAG (Local / Global / DRIFT / Basic). Aligned with §9 routing discipline and §13/§14 algorithms. -->

Microsoft GraphRAG's four canonical query modes map cleanly onto this skill's existing tooling. Use the taxonomy when picking a route or when documenting why a query took the shape it did.

| Mode | Question shape | Default route here | Algorithm |
|---|---|---|---|
| **Basic** | Simple lookup: "what is repo X?" | `catalog/<repo>.md` plus `profiles/<repo>.json` | Lexical search / direct file read |
| **Local** | Entity-anchored: "what does X depend on?" "what breaks if X changes?" | `query_graph.py --node <id> --hops 1` or `--impact <id> --hops 2` | BFS (bidirectional or outgoing-only) |
| **DRIFT** | Entity-anchored *with broader context*: "pull everything contextually relevant to X" | `query_graph.py --ppr --seed <id> --top N` | Personalized PageRank (§13) |
| **Global** | Holistic: "what does the platform look like?" "catch me up on the architecture" | Community summaries at the right resolution | Louvain communities (§14, shipped) + LLM summaries; Leiden as drop-in upgrade |

The Local→DRIFT→Global progression also matches token cost: Local is cheapest (bounded BFS, ~10–50 nodes), DRIFT is medium (PPR + top-N, ~30–100 nodes), Global is most expensive (community summary tree, ~5–20 community summaries).

Rule: pick the cheapest mode that answers the question. Most agent queries are Basic or Local; only escalate to DRIFT or Global when the question genuinely needs them.
