# Output Model And Gap Analysis

## Table of Contents

- [Artifact Root Model](#artifact-root-model)
- [Core Outputs](#core-outputs)
- [Extended Domain Assessment Model](#extended-domain-assessment-model)
- [Assessment vs Initiatives](#assessment-vs-initiatives)
- [Initiative Lifecycle](#initiative-lifecycle)
- [Gap Analysis Categories](#gap-analysis-categories)

## Artifact Root Model

Every run should target one artifact root and keep generated outputs grouped consistently.

Recommended shapes:

- coordination repo style: `<artifact-root>/profiles`, `<artifact-root>/catalog`, `<artifact-root>/graphs`, `<artifact-root>/reports`
- embedded repo-local style: `docs/context/profiles`, `docs/context/catalog`, `docs/context/graphs`, `docs/context/reports`

Use `scripts/build_artifact_set.py --artifact-root <dir> ...` when you want one command to materialize the whole set into a location such as `docs/context/`.

## Core Outputs

Minimum standard outputs:

- `profiles/<repo>.json`
  Machine-readable repo profile conforming to `schemas/repo-profile.schema.json`
- `catalog/<repo>.md`
  Canonical human-readable repo profile generated from the JSON profile plus evidence
- `graphs/system-edges.json`
  Cross-repo and repo-to-external-system relationships
- `graphs/knowledge-graph.json`
  Primary machine-readable graph output for query, blast radius, and report generation
- `reports/coverage.md`
  Coverage, completeness, and low-confidence gaps
- `reports/drift.json`
  Profiles whose evidence is stale relative to source repos

Common optional outputs:

- `reports/graph-validation.json`
- `reports/consistency-report.json`
- `reports/graph-report.html`
- `reports/graph-report.md`
- `catalog/database-schemas.md`
- `catalog/data-catalog.md`

If you need per-repo symbol graphs, keep them as a sibling artifact set via [../../dev-context-code-graph/SKILL.md](../../dev-context-code-graph/SKILL.md) instead of forcing symbol-level nodes into the portfolio graph.

## Extended Domain Assessment Model

For regulated or complex platforms, extend the standard outputs with a per-domain assessment shape:

```text
{domain}/
├── README.md
├── as-is/
│   ├── README.md
│   ├── services/
│   ├── providers/
│   ├── cross-repo-dependencies.md
│   └── diagrams.md
├── assessment/
│   ├── README.md
│   ├── gap-analysis.md
│   ├── architecture-proposal.md
│   ├── migration-roadmap.md
│   └── business-gaps.md
└── initiatives/
    ├── README.md
    ├── NNN-short-name/
    │   ├── README.md
    │   ├── gap-analysis.md
    │   ├── adr-*.md
    │   └── ...
    └── _graduated/
```

Three layers:

| Layer | Folder | Purpose | Lifespan |
|-------|--------|---------|----------|
| Current state | `as-is/` | What exists today — per-repo docs, architecture, dependencies | Permanent |
| Strategic assessment | `assessment/` | Domain-wide gap analysis, architecture proposals, migration roadmap | Long-lived |
| Tactical initiatives | `initiatives/` | Scoped improvement work that graduates back into `as-is/` | Temporary |

## Assessment vs Initiatives

Use `assessment/` for domain-wide strategic review that spans all repos and all gap categories.

Use `initiatives/` for scoped tactical work on one sub-area, for example:

- incoming payments refactoring
- contract-governance rollout
- provider adapter normalization
- observability hardening

Multiple initiatives can run in parallel inside the same domain.

Use `assets/initiative-doc-template.md` for new initiatives.

## Initiative Lifecycle

Standard lifecycle:

`draft → proposed → accepted → in-progress → done → graduated`

| Status | Meaning |
|--------|---------|
| `draft` | Author is writing the proposal |
| `proposed` | Ready for team review |
| `accepted` | Approved, not yet started |
| `in-progress` | Implementation underway |
| `done` | Implementation complete, awaiting graduation |
| `graduated` | Findings merged into `as-is/`, folder moved to `_graduated/` |

Graduation rule:

- findings from a completed initiative must be merged into `as-is/` before moving the folder to `_graduated/`
- `_graduated/` is historical archive only; agents and humans should skip it by default

## Gap Analysis Categories

Use the A-O framework when producing regulated or platform-wide gap reviews:

| Cat | Name | Key checks |
|-----|------|------------|
| A | Messaging & Event Architecture | Broker migration, DLQ patterns, serialization, schema versioning |
| B | Data Consistency | Dual writes, outbox, entity ownership, reconciliation |
| C | Migration & Legacy Decomposition | Legacy dependencies, framework remnants, decomposition roadmap |
| D | Provider Integration Patterns | Shared adapters, webhook validation, deduplication, circuit breakers |
| E | Observability & Operations | OpenTelemetry, tracing, health checks, SLI/SLO |
| F | Security & Compliance | PII in logs, secrets, encryption, OWASP |
| G | Missing Modern Patterns | Outbox, idempotency, caching, CQRS, feature flags |
| H | Regulatory Compliance | ICT risk, incident reporting, resilience testing, exit strategies |
| I | Regulatory Readiness | Upcoming regulation preparation, API evolution, enhanced requirements |
| J | AI Governance | AI in regulated decisions, agent instruction coverage |
| K | Runtime Migration | Framework version currency, migration timeline, breaking changes |
| L | API Contract Governance | OpenAPI coverage, versioning, contract testing, breaking change detection |
| M | Test Coverage & Automation | Test pyramid balance, emulator coverage, performance testing |
| N | Documentation Freshness | AGENTS.md coverage, freshness metadata, template adherence |
| O | Data Residency & Cross-Border | Transfer mechanisms, data classification, residency requirements |

Use severity levels appropriate to the context: `BLOCKER`, `HIGH`, `MEDIUM`, `LOW`.
