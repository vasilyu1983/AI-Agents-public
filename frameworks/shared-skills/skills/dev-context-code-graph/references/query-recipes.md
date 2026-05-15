# Code Graph Query Recipes

Concrete invocation patterns for the most common review packets. Each recipe assumes you have already built `graphs/code-graph.json` via `scripts/build_code_graph.py`.

All commands use `python3 scripts/query_code_graph.py graphs/code-graph.json` as the prefix; the prefix is omitted below for brevity.

## Table of Contents

- [PR-impact packet](#pr-impact-packet) — what does this change touch
- [Refactor-risk packet](#refactor-risk-packet) — where is the structural risk
- [Hot-symbol context (PPR)](#hot-symbol-context-ppr) — budget-bounded retrieval around a symbol
- [Dead-code candidates](#dead-code-candidates) — what is unused or weakly connected
- [Test-coverage cone](#test-coverage-cone) — which tests cover this code
- [Cycle inventory](#cycle-inventory) — circular imports and inheritance loops
- [Module-boundary check](#module-boundary-check) — articulation points and bridges
- [Diff vs canonical layering](#diff-vs-canonical-layering) — topo-sort drift checks
- [Module discovery via communities](#module-discovery-via-louvain-communities) — what are the natural modules

## When to use which recipe

| Trigger | Recipe |
|---------|--------|
| About to merge a PR | PR-impact + Test-coverage cone |
| Considering renaming or moving a symbol | PR-impact + Refactor-risk |
| Onboarding to an unfamiliar module | Hot-symbol context + Module-boundary check |
| Cleaning up before a release | Dead-code + Cycle inventory |
| Planning architectural changes | Refactor-risk + Diff vs canonical layering |

---

## PR-impact packet

**Goal**: list every symbol and file that reaches the changed symbol, plus their tests, within 2 hops.

```bash
# 1. Two-hop blast radius from the changed symbol
--impact "fn:src/api.py:create_user" --hops 2 --format json --output reports/pr-impact.json

# 2. Mermaid view for the PR description
--impact "fn:src/api.py:create_user" --hops 2 --format mermaid --output reports/pr-impact.mmd

# 3. Tests that exercise this symbol
--node "fn:src/api.py:create_user" --hops 1 --format table | grep -E "^test|tests_"
```

**Sanity checks**:
- If the impact node count is > 50, your symbol is too central — break the change into smaller commits.
- If no test edges appear, flag missing coverage before merging.

---

## Refactor-risk packet

**Goal**: surface the structural risk that a refactor would carry — articulation points, bridges, and cycles in the affected subgraph.

```bash
# 1. Articulation points across the import graph
--articulation-points --relations imports --top 30 --format table --output reports/refactor-articulation.md

# 2. Bridges (single edges whose removal disconnects the graph)
--bridges --relations imports,inherits --top 30 --format table --output reports/refactor-bridges.md

# 3. Cycles that the refactor must preserve or break carefully
--cycles --relations imports,inherits,calls --format json --output reports/refactor-cycles.json

# 4. Topological depth of the affected files
--topo-sort imports --format json --output reports/refactor-topo.json
```

**Reading the output**:
- An articulation point with high `betweenness_proxy` is a load-bearing module — refactor with feature-flag rollout.
- A bridge between two large components is a likely seam for splitting the codebase.
- Cycles in `imports` are usually fixable; cycles in `inherits` indicate deeper coupling.

---

## Hot-symbol context (PPR)

**Goal**: budget-bounded retrieval around 1–3 hot symbols. Use this instead of `--impact --hops N` when the symbol's neighbourhood blows past 100 nodes.

```bash
# Single hot symbol — top 30 most-related nodes
--ppr --seed "fn:src/api.py:create_user" --top 30 --format table

# Multiple hot symbols (tax-rate calculation cluster)
--ppr \
  --seed "fn:src/tax/calc.py:apply_vat" \
  --seed "fn:src/tax/calc.py:apply_corp_tax" \
  --seed "class:src/tax/rates.py:RateTable" \
  --top 50 \
  --filter-type function,method,class \
  --output reports/tax-context.json

# Tighter teleport (smaller neighbourhood, less drift)
--ppr --seed "fn:src/api.py:create_user" --alpha 0.3 --top 20
```

**When PPR beats hop-bounded BFS**:
- Your symbol has high fan-out (>20 callers) so 2-hop BFS already exceeds 200 nodes.
- You want a *ranked* retrieval set, not the full neighbourhood.
- The reviewer needs context for an LLM that has a token budget.

**α (alpha) tuning**:
- α = 0.10–0.15 — wide context, follows long call chains
- α = 0.20–0.30 — tight context, stays close to the seed
- α = 0.50+ — almost only the seed and direct neighbours

---

## Dead-code candidates

**Goal**: find symbols with zero or near-zero fan-in.

```bash
# Rank by fan-in, ascending — bottom of the list is suspicious
--rank --top 0 --format json --output reports/rank-all.json

# Then surface bottom-fan-in functions in code (jq):
jq '.results | map(select(.type == "function" and .importance == 0)) | .[].id' reports/rank-all.json

# Cross-check against tests — a function with fan-in 0 but a test edge is a public API, not dead
--node "fn:src/utils.py:helper" --hops 1 --format table
```

**Disambiguation**:
- Fan-in 0 + no test edge + no `external_symbol` reference → strong dead-code candidate.
- Fan-in 0 + a test edge → public API; do not delete.
- Fan-in 0 + a CLI/handler decorator → entrypoint; do not delete.

---

## Test-coverage cone

**Goal**: confirm that a module is covered by tests via the `tests` edge type.

```bash
# Outgoing tests edges from the test files in the module
--node "file:tests/test_api.py" --hops 2 --format table

# Reverse: which tests cover a production symbol
--impact "fn:src/api.py:create_user" --hops 2 --format json \
  | jq '.edges | map(select(.relation == "tests")) | .[].source'
```

**Failure modes**:
- Heuristic parsers (JS/TS/Swift/C#) under-resolve test edges — treat absence of edges as "unknown coverage", not "no coverage".
- Always cross-check parse-status fields: `confidence < 0.7` means the call resolution may be wrong.

---

## Cycle inventory

**Goal**: locate circular imports, mutually-recursive class hierarchies, and call cycles.

```bash
# All cycles, all relations
--cycles --format json --output reports/cycles.json

# Imports-only (most actionable)
--cycles --relations imports --format table

# Class-level cycles (rare but dangerous)
--cycles --relations inherits --format json
```

**Triage**:
- Import cycles → break with lazy import or interface extraction.
- Inheritance cycles → almost always a bug or invalid heuristic parse.
- Call cycles → expected for recursive algorithms; ignore if intentional.

---

## Module-boundary check

**Goal**: validate that a logical module corresponds to a structurally-cohesive subgraph.

```bash
# Articulation points limited to the imports relation
--articulation-points --relations imports --top 50 --format table

# Bridges between subsystems
--bridges --relations imports --top 50 --format table

# Manually inspect a candidate boundary
--from "file:src/payments/checkout.py" --to "file:src/notifications/email.py" --max-hops 5 --k 3 --format table
```

**Healthy signs**:
- Articulation points are a small set of well-named "facade" or "interface" modules.
- Bridges run through these facades, not through ad-hoc helper files.
- 3+ disjoint paths exist between two subsystems → loose coupling.
- 1 disjoint path → fragile boundary; refactor before further decoupling.

---

## Diff vs canonical layering

**Goal**: detect when a new commit adds an edge that violates the canonical layer order (e.g. `domain → infra` instead of `infra → domain`).

```bash
# 1. Topological sort of imports
--topo-sort imports --format json --output reports/topo-current.json

# 2. Compare against the previous run committed at reports/topo-baseline.json
diff <(jq '.results' reports/topo-baseline.json) <(jq '.results' reports/topo-current.json)

# 3. If the topo-sort errors with cycles_detected, drill into the cycle
--cycles --relations imports --format json | jq '.results[].nodes'
```

**Workflow**:
- Commit a `reports/topo-baseline.json` after each architectural review.
- Run a CI check that fails if the diff introduces backward edges.
- Treat new cycles as PR-blocking unless explicitly approved.

---

## Module discovery via Louvain communities

**Goal**: discover the codebase's natural module boundaries from call/import structure, then compare them against the directory layout.

```bash
# 1. Detect communities at default resolution
--communities --format table

# 2. Tighten or loosen modularity (γ=1 default)
#    Higher γ → smaller, more cohesive modules; lower γ → larger, looser modules
--communities --resolution 1.4 --top 30 --format json --output reports/communities-tight.json
--communities --resolution 0.7 --top 30 --format json --output reports/communities-loose.json

# 3. Inspect cross-directory cohesion in each community
jq -r '.communities[] | {community_id, size, top_files: (.top_files | keys)}' reports/communities-tight.json
```

**Reading the output**:
- `modularity` Q ≈ 0.4–0.7 = strong community structure; <0.3 = weak partition (tightly coupled or single-module repo).
- A community whose `top_files` span more than two directories is a cross-cutting concern — refactor candidate or evidence the directory structure has drifted from actual coupling.
- `--community-seed` is deterministic; freeze it for reproducible review reports.

**When to use**: onboarding into an unfamiliar codebase, validating a planned package split, finding hidden coupling, or grounding a "natural module map" before proposing architectural moves.

**Limitation**: pure-python Louvain is fine to ~50k edges. For very large graphs, swap in a native Leiden implementation (igraph) — same input/output contract, better partition stability.

---

## Output discipline

When a recipe produces durable knowledge, file the report into a stable path:

- `reports/pr-impact-<pr-number>.md` — one-shot, link from the PR
- `reports/refactor-<area>.md` — durable, link from the area's onboarding doc
- `reports/cycles.json` + `reports/cycles.md` — pair JSON + summary, regenerate on each release
- `reports/topo-baseline.json` — long-lived, regenerate on architectural reviews
- `reports/communities.json` + `reports/modules.md` — pair JSON + narrative summary, regenerate during architectural reviews

Anything reused once should not stay only in chat output.
