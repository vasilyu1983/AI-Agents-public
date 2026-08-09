# Context Graph Guide

A practical reference for generating, reading, and using the per-repo context graph produced by the dev-context-engineering skill.

## Table of Contents

- [What Is a Context Graph](#what-is-a-context-graph)
- [Generating the Graph](#generating-the-graph)
- [Loading Tiers](#loading-tiers)
- [Query Mode Taxonomy](#query-mode-taxonomy)
- [Relationship Detection](#relationship-detection)
- [Integration with CDLC](#integration-with-cdlc-context-driven-llm-collaboration)
- [Context Impact Analysis](#context-impact-analysis)
- [Maturity Model Integration](#maturity-model-integration)
- [Related References](#related-references)

---

## What Is a Context Graph

A context graph is a per-repo JSON graph (`context-graph.json`) that maps every context artifact in a repository and the relationships between those artifacts.

Artifacts include: AGENTS.md, CLAUDE.md, coding rules, specs, plans, subagent definitions, hooks, and other files that shape how AI coding agents understand and operate inside the repo.

The graph is produced by running `scan_context_artifacts.py` against a repository root. It complements the portfolio-level knowledge graph maintained by the `dev-context-multi-repo` skill, which aggregates context signals across many repositories. The per-repo graph gives fine-grained visibility into a single codebase; the portfolio graph gives cross-repo comparisons.

**Why it matters.** AI agents load context on every turn. Without a graph, agents reload all context blindly, wasting tokens and risking stale or conflicting instructions. With a graph, the loading tier of each artifact is explicit, relationships are traceable, and changes can be evaluated for downstream impact before context is reloaded.

---

## Generating the Graph

Run `scan_context_artifacts.py` from any environment that has Python 3:

```bash
python3 /path/to/scan_context_artifacts.py /path/to/repo
# Output: /path/to/repo/context-graph.json
```

The script walks the repository tree, identifies artifacts by path pattern and file name, classifies each into a loading tier, and detects edges between artifacts by scanning file content. The output is a single JSON file at the repository root.

Validate the result immediately after generation:

```bash
python3 /path/to/validate_context_graph.py /path/to/repo/context-graph.json --repo /path/to/repo
# Optional: --output reports/context-graph-validation.json
```

**12 artifact types detected:**

| Type | Matched paths |
|---|---|
| `agents_md` | `AGENTS.md` at root |
| `claude_md` | `CLAUDE.md` at root |
| `rule` | `.claude/rules/*.md` |
| `spec` | `docs/specs/*.md`, `specs/*.md`, `SPEC.md` |
| `plan` | `docs/plans/*.md`, `plans/*.md` |
| `subagent` | `.claude/agents/*.md`, `.github/agents/*.md` |
| `hook` | Entries under `.claude/hooks/` |
| `copilot_instructions` | `.github/copilot-instructions.md`, `.github/instructions/*.md`, `.github/instructions/*.instructions.md` |
| `github_agent` | `.github/agents/*.md` |
| `reference` | `docs/references/*.md` |
| `asset` | `assets/**/*` |
| `skill` | `skills/*/SKILL.md` |

Re-run the script whenever artifacts are added, renamed, or removed. For automated freshness, add it to CI or a git commit hook (see [Maturity Model Integration](#maturity-model-integration)).

---

## Loading Tiers

Every node in the graph carries a `loading_tier` field that tells agents when to load it:

| Tier | Label | Artifact types | Load policy |
|---|---|---|---|
| L1 | `L1_always` | `agents_md`, `claude_md`, `hook`, root `copilot_instructions` | Loaded on every agent turn, unconditionally |
| L2 | `L2_on_demand` | `rule`, `subagent`, path-scoped `copilot_instructions`, `github_agent` | Loaded when the agent determines it is relevant to the current task |
| L3 | `L3_referenced` | `spec`, `plan`, `reference`, `asset`, `skill` | Pulled only when explicitly referenced by the task, another artifact, or an agent instruction |

Loading tiers exist to control token budgets. L1 nodes are always in context; L2 and L3 nodes are lazy-loaded. Misclassifying a frequently-needed spec as L3 will cause agents to miss it; misclassifying a large asset file as L1 will waste tokens every turn.

---

## Query Mode Taxonomy

<!-- Source: Microsoft GraphRAG (Local / Global / DRIFT / Basic). Aligned with the loading-tier model above and the portfolio query taxonomy in dev-context-multi-repo/references/knowledge-graph-patterns.md §15. -->

Loading tiers say *when* to load an artifact. Query modes say *how* to find it. Microsoft GraphRAG's four canonical modes map onto this skill's context-graph operations:

| Mode | Question shape | Default route | Loading tier interaction |
|---|---|---|---|
| **Basic** | "What does this rule say?" "Show me the spec for X" | Direct file read by `id` or `path` | Pulls one L2/L3 artifact on demand |
| **Local** | "What rules apply to this subagent?" "What artifacts reference CLAUDE.md?" | Edge traversal at 1–2 hops in `context-graph.json` | L1 nodes always in scope; traversal pulls L2/L3 neighbors |
| **DRIFT** | "Pull all context relevant to this task" | Personalized PageRank from a seed (the task's anchor artifact); see `dev-context-multi-repo/references/knowledge-graph-patterns.md` §13 | L1 plus the highest-PPR L2/L3 nodes within token budget |
| **Global** | "What's the overall context architecture?" "How is this repo's context organized?" | Community detection (Leiden) over the artifact graph; see knowledge-graph-patterns.md §14 | Returns community summaries, not raw artifacts |

For most per-repo work, Basic and Local are sufficient — the artifact graph in a single repo rarely needs PPR or community detection. DRIFT becomes useful when the L2/L3 layer has 50+ artifacts and the agent needs to pull "task-relevant context" without reading everything. Global becomes useful when documenting the context system itself for new contributors.

The cheapest mode that answers the question wins. Escalate only when the question genuinely needs it.

---

## Relationship Detection

The current scanner auto-detects 4 edge types by inspecting file content:

| Edge type | Detection rule |
|---|---|
| `imports` | Explicit `!include`, `# @import`, or `@path` directive referencing another artifact path |
| `references` | Markdown link `[text](path)` where the path resolves to another artifact in the graph |
| `delegates_to` | A bracketed skill mention or `(skill:...)` reference that resolves to a discovered `skill` node |
| `enforces` | A hook node that references a rule node by filename stem in its trigger or command |

The schema also reserves `documents`, `triggers`, `validates`, `overrides`, and `extends` for future deterministic scanners or manual augmentation, but `scan_context_artifacts.py` does not emit those relations today.

Each edge in `context-graph.json` has the form:

```json
{
  "source": "relative-path-derived-node-id",
  "target": "relative-path-derived-node-id",
  "relation": "references"
}
```

Edges are directional. `source → target` means the source artifact depends on or is aware of the target. Backward traversal (finding all artifacts that depend on a given artifact) is used for impact analysis (see [Context Impact Analysis](#context-impact-analysis)).

Missing edges are a common finding on first scan. If a rule is never referenced by any other artifact, agents cannot discover it through graph traversal and must rely on L1 or L2 loading alone.

---

## Integration with CDLC (Context-Driven LLM Collaboration)

The context graph plugs directly into the four CDLC phases:

**Generate.** `scan_context_artifacts.py` produces `context-graph.json`. Run it once at repo setup, then re-run on any structural change to the context layer.

**Evaluate.** Inspect the graph to find:
- Artifacts with no edges (isolated nodes — often orphaned specs or stale rules)
- L1 nodes that are unexpectedly large (token cost risk)
- Missing `enforces` edges between hooks and the rules they are meant to enforce
- Broken paths or dangling refs reported by `validate_context_graph.py`

**Distribute.** When an agent session starts, load all L1 nodes. For L2 and L3, use the graph edges to identify which artifacts are reachable from the current task context and load only those.

**Observe.** Each node records `last_modified_at` from the file system at scan time. The scanner initializes `stale: false`; freshness is maintained by regenerating the graph after structural changes and validating it in CI or pre-commit.

---

## Context Impact Analysis

When an artifact changes, use graph edges to determine which other artifacts are affected before reloading context.

**Changed rule node — backward traversal:**

1. Find the rule node in the graph.
2. Collect all nodes with an edge pointing to it (`references`, `imports`, or `enforces` edges with this node as `to`).
3. Those dependent nodes may need to be reloaded or reviewed for consistency.

**Changed spec — subagent impact:**

1. Find the spec node.
2. Walk forward to find any subagent nodes that `delegates_to` a context that includes the spec, or that `references` the spec directly.
3. Reload those subagent definitions before the next agent turn.

**Changed CLAUDE.md or AGENTS.md (L1 nodes):**

Because these are always loaded, any change takes effect on the next turn automatically. However, if other artifacts `references` them, check whether those references are still valid after the change.

Impact analysis replaces the default behavior of reloading all context on any change. On large repositories with many artifacts, targeted reloading reduces token usage and avoids accidental context pollution from unrelated artifacts.

---

## Maturity Model Integration

The context graph is a gating requirement for L2 and above in the repository context maturity model (see [maturity-model.md](maturity-model.md)):

| Level | Name | Graph requirement |
|---|---|---|
| L0 | No Context | No graph. No documented context artifacts. |
| L1 | Basic Context | Has AGENTS.md or CLAUDE.md. No graph required. |
| L2 | Structured Context | `context-graph.json` present with at least `agents_md` or `claude_md` + at least one `rule` node. |
| L3 | Automated Context | Full graph: plans, specs, subagents, and documented edges between them. Graph passes `validate_context_graph.py` and hook-to-rule links are reviewed. |
| L4 | Full Context Engineering | Automated refresh: `scan_context_artifacts.py` and `validate_context_graph.py` run in CI or on git commit hook. |

To reach L4, add the scanner to a pre-commit hook or CI step:

```bash
# .git/hooks/pre-commit or CI step
python3 /path/to/scan_context_artifacts.py $(git rev-parse --show-toplevel)
python3 /path/to/validate_context_graph.py $(git rev-parse --show-toplevel)/context-graph.json --repo $(git rev-parse --show-toplevel)
git add context-graph.json
```

This ensures `context-graph.json` is always current when code is committed, and that agents in CI environments start with a fresh graph on every run.

---

## Related References

- [maturity-model.md](maturity-model.md) — Full 5-level maturity model with scoring checklists
- [context-development-lifecycle.md](context-development-lifecycle.md) — CDLC phases in depth
- [multi-repo-strategy.md](multi-repo-strategy.md) — Portfolio-level context graph (dev-context-multi-repo)
- [repo-conversion-playbook.md](repo-conversion-playbook.md) — Step-by-step guide for adding context engineering to an existing repository
