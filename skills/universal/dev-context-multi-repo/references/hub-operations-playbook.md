# Hub Operations Playbook

## Table of Contents

- [Graph Assembly](#graph-assembly)
- [Incremental Updates](#incremental-updates)
- [Queries And Reports](#queries-and-reports)
- [Freshness Monitoring](#freshness-monitoring)
- [Resolver-Driven Filing Discipline](#resolver-driven-filing-discipline)
- [Recommended Hub Layout](#recommended-hub-layout)
- [Stable Types](#stable-types)
- [Validation Checklist](#validation-checklist)
- [Workspace Alignment](#workspace-alignment)

## Graph Assembly

After verification, materialize the portfolio graph.

Mode A, from profiles:

```bash
python3 scripts/build_knowledge_graph.py --profiles profiles/
```

Mode B, from an existing hub:

```bash
python3 scripts/build_knowledge_graph.py --hub /path/to/hub
```

Validate every build:

```bash
python3 scripts/validate_graph.py graphs/knowledge-graph.json \
  --output reports/graph-validation.json
```

Run consistency checks after validation:

```bash
python3 scripts/check_graph_consistency.py \
  --hub /path/to/hub \
  --graph graphs/knowledge-graph.json \
  --output reports/consistency-report.json
```

For ontology, normalization, and parser behavior, use [knowledge-graph-patterns.md](knowledge-graph-patterns.md).

## Incremental Updates

Bootstrap or refresh graph state after the first build:

```bash
python3 scripts/incremental_update.py graphs/knowledge-graph.json \
  --repo-map graphs/repos.json \
  --output graphs/knowledge-graph.json \
  --report reports/incremental-update.json
```

`graphs/repos.json` can stay portable by using named roots plus repo-relative paths:

```json
{
  "roots": {
    "main": ["../.."],
    "qa": ["../../../platform-qa"],
    "legacy": ["../../../platform-legacy"]
  },
  "repos": {
    "payments-ledger": {"root": "main", "path": "payments-ledger"}
  }
}
```

Override roots at runtime when local checkout layout differs:

```bash
python3 scripts/incremental_update.py graphs/knowledge-graph.json \
  --repo-map graphs/repos.json \
  --repo-root main=/work/platform
```

## Queries And Reports

Generate static graph reports for humans:

```bash
python3 scripts/export_graph_report.py graphs/knowledge-graph.json \
  --output-dir reports/
```

Common query patterns:

```bash
python3 scripts/query_graph.py graphs/knowledge-graph.json --node <id> --hops 1
python3 scripts/query_graph.py graphs/knowledge-graph.json --impact <id> --hops 2
python3 scripts/query_graph.py graphs/knowledge-graph.json --from <id> --to <id>
python3 scripts/query_graph.py graphs/knowledge-graph.json --type repo
python3 scripts/query_graph.py graphs/knowledge-graph.json --search "sumsub kyc" --types provider,process,repo --limit 10
python3 scripts/query_graph.py graphs/knowledge-graph.json --node <id> --hops 1 --format mermaid
```

Prefer static HTML or Markdown reports as the default human-facing output. Treat richer visualization layers as downstream consumers of `knowledge-graph.json`, not as required outputs of this skill.

## Resolver-Driven Filing Discipline

<!-- Source: github.com/garrytan/gbrain@adb02b7826a010700efc968b18df8aaf17d8ffa1 (MIT), extracted 2026-04-13 -->

Hubs rot when filing is ambiguous. The same fact ends up on three pages with three slightly different versions, nobody knows which is current, and agents stop trusting the system. The fix is **MECE directories + per-directory resolvers**, enforced with a hard rule that no page gets created without walking the resolver first.

### Three Founding Rules

1. **Every piece of knowledge has exactly one primary home.** Directories are mutually exclusive and collectively exhaustive. A repo catalog entry lives in `catalog/`. A cross-repo concept lives in `concepts/`. A system map lives in `graphs/` (generated) or `diagrams/` (hand-authored). *MECE applies to directories, not to reality* — a complex repo can be referenced from multiple concept pages, but its primary catalog page exists in exactly one place.

2. **Every directory has a `README.md` resolver.** The resolver answers two questions:
   - **What goes here** — a positive definition with a concrete test. Example: "`catalog/` holds one page per repo scanned into `profiles/`. If a topic does not correspond to a single repo, it does not go here."
   - **What does NOT go here** — the key distinctions from neighbouring directories. Example: "Architecture patterns that span many repos do not go here; they go in `concepts/`. Generated dependency maps do not go here; they go in `graphs/`."

3. **Top-level `RESOLVER.md` is the decision tree.** A numbered walk that answers "where does this new item go?" When two directories seem to fit, explicit disambiguation rules break the tie. When nothing fits, the item goes in `inbox/` — which is itself a signal the schema needs to evolve.

### The Agent Must Read the Resolver Before Filing

This is not optional. If an agent creates a page without walking `RESOLVER.md`, the discipline collapses within a month. Wire this into the hub's `AGENTS.md` as a hard rule, not buried guidance:

```markdown
# Hub AGENTS.md (excerpt)

## Filing rule (hard)

Before creating ANY new page in this hub:
1. Read `RESOLVER.md` from the hub root.
2. Walk the decision tree for the item type.
3. Read the target directory's `README.md` resolver.
4. If the item does not fit cleanly, place it in `inbox/` and flag for schema review — do NOT force-fit into an existing directory.
```

### Resolver Template (Per Directory)

```markdown
# <directory>/ README (resolver)

## What goes here
<positive test — one sentence, concrete>

Example: A repo catalog page (`catalog/<repo>.md`) belongs here if and only if `profiles/<repo>.json` exists. No profile, no catalog entry.

## What does NOT go here
- <distinction from neighbouring directory 1> → goes in `<neighbour1>/`
- <distinction from neighbouring directory 2> → goes in `<neighbour2>/`
- <distinction from inbox> → goes in `inbox/` if the schema does not cover this case

## Naming convention
<slug rule>

## Required fields
<what every page in this directory must include>

## Related directories
- `<neighbour1>/` — <one-line relationship>
- `<neighbour2>/` — <one-line relationship>
```

### Why the Inbox Matters

The `inbox/` directory is not a dumping ground — it's a *signal channel*. When items keep landing there, the schema needs a new directory or a new resolver rule. Treat `inbox/` contents as the agenda for the next schema-evolution review (weekly or monthly depending on hub velocity). A well-governed hub aims for a near-empty inbox; a consistently full inbox means the resolver has an unaddressed gap.

### Why This Beats "Just Be Consistent"

Agents (and humans under time pressure) cannot "be consistent" across 50-100 directories by willpower. The resolver turns filing into a deterministic walk: read rule, check test, place file. Same input → same destination, every time. That's what makes the hub an artifact that can be rebuilt and audited rather than a pile of human judgment calls that drift with whoever filed things most recently.

## Freshness Monitoring

Use `check_hub_freshness.sh` after source repo pulls, before planning sessions, and on scheduled CI runs:

```bash
check_hub_freshness.sh ~/repos ~/docs-hub
check_hub_freshness.sh ~/repos ~/docs-hub --json --out freshness.json
```

Default change categories:

- `SCHEMA`
- `API`
- `MESSAGING`
- `CONFIG`
- `INFRA`
- `OTHER`

The script ships with .NET/C#-biased patterns. Adapt the regexes for Node, Python, Go, Java, or mixed stacks.

Detailed guidance lives in [hub-freshness-checking.md](hub-freshness-checking.md).

## Recommended Hub Layout

Preferred shape:

```text
portfolio-hub/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── context/
│   ├── docs/
│   ├── overview/
│   ├── scripts/
│   ├── templates/
│   ├── graphs/
│   ├── reports/
│   ├── schemas/
│   └── profiles/
├── {domain}/
│   ├── README.md
│   ├── as-is/
│   ├── assessment/
│   └── initiatives/
└── sources/
```

Rules:

- keep the root clean and domain-focused
- keep hub infrastructure under `context/`
- keep root `AGENTS.md` short and navigation-first
- keep generated inventories in `profiles/`, `catalog/`, `graphs/`, and `reports/`
- use [assets/coordination-repo-layout-template.md](../assets/coordination-repo-layout-template.md) as the starting layout

## Stable Types

Do not invent alternate contracts unless a downstream system requires a transform layer. The canonical schema set is:

- `schemas/repo-profile.schema.json`
- `schemas/evidence-ref.schema.json`
- `schemas/system-edge.schema.json`
- `schemas/scan-registry-entry.schema.json`
- `schemas/hub-summary.schema.json`
- `schemas/knowledge-graph.schema.json`

## Validation Checklist

- every repo has one `RepoProfile`
- every nontrivial claim has at least one evidence reference
- portfolio-wide claims are only marked universal when the full scope was verified
- active and legacy repos are not conflated
- storage engine claims are verified from manifests, not docs
- `graphs/knowledge-graph.json` has been built and validated
- `reports/consistency-report.json` has been generated and reviewed
- root `AGENTS.md` remains navigation-focused
- domain folders include `as-is/`, `assessment/`, and `initiatives/` where the assessment model is in use

## Workspace Alignment

Domain folder names should match team mental models, usually the IDE workspace prefixes used by the organization.

This is naming alignment only. Do not physically move git repos into domain folders. Use workspace files for IDE grouping and the hub for documentation grouping.
