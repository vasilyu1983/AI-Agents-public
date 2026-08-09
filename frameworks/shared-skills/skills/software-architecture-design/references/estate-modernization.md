# Estate Modernization (2026)

Use this reference when the problem is no longer "which pattern fits one system?" but "why does the estate have too many repos, too many services, or too much platform drift?"

This is the right lens for regulated polyrepo estates, long-lived microservice portfolios, and organizations where operational complexity has outgrown the original decomposition.

## Table of Contents

- [Core Position](#core-position)
- [What Changed By 2026](#what-changed-by-2026)
- [Default Recommendations](#default-recommendations)
- [Anti-Patterns](#anti-patterns)
- [Practical Heuristics](#practical-heuristics)
- [Deliverable Shape](#deliverable-shape)
- [Current External Anchors To Verify](#current-external-anchors-to-verify)

## Core Position

The 2026 default is:

- Prefer **fewer runtime units** over blindly preserving every service boundary.
- Prefer **bounded-context platforms** over service-per-capability fragmentation.
- Prefer **internal developer platforms and golden paths** over architecture-by-convention.
- Treat **repositories as collaboration units** and **deployable runtimes as operational cost centers**.

Do not assume "many repos" is the core problem. Often the real problem is too many deployables, too many ownership seams, too many message hops, and too many partial standards.

## What Changed By 2026

- Teams are more skeptical of microservices-by-default and more explicit about the operational tax.
- Platform engineering has matured from "build a portal" to "reduce cognitive load with paved roads, scorecards, and self-service".
- Modern estates separate three concerns more clearly:
  - product/domain boundaries
  - deployable runtime boundaries
  - repo/package collaboration boundaries
- Regulated systems are more likely to keep hard domain boundaries while consolidating internal modules to reduce failure modes.

## Default Recommendations

### 1. Start with runtime rationalization, not repo merging

Ask:

- Which deployables genuinely need independent scaling?
- Which deployables need independent release cadence?
- Which boundaries are regulatory or security boundaries?
- Which boundaries exist only because of historical team splits or old templates?

If a service cannot justify independent deployment, scaling, or failure isolation, it is a consolidation candidate.

### 2. Build bounded-context platforms

For large estates, the common target is not one monolith and not hundreds of services. It is a small set of domain platforms:

- each platform owns a bounded context
- each platform exposes a small number of stable APIs and events
- internal modules can stay in one deployable or a few tightly controlled runtimes
- adapters, channels, and external-facing products stay outside the core boundary when they earn it

This reduces hop count, schema drift, and operational burden without collapsing domain ownership.

### 3. Use platform engineering to standardize the estate

Platform engineering is not just a catalog. The useful outputs are:

- golden-path service templates
- scorecards and fitness functions
- standard observability and security baselines
- standard contract and schema governance
- paved-road deployment, rollback, and incident patterns

If the estate keeps creating new snowflake services, solve that first.

### 4. Standardize cross-cutting runtime rules

Multi-team estates should make these defaults, not optional guidance:

- telemetry baseline (OpenTelemetry, traces, dependency-aware health checks)
- messaging baseline (transactional outbox, idempotent consumers, replayable DLQ)
- API baseline (versioning, deprecation, contract ownership, contract tests)
- security baseline (secret handling, audit trails, redaction, policy checks)
- migration baseline (expand/contract, strangler boundaries, rollback points)

### 5. Keep dedicated runtimes for the right reasons

A separate runtime is still justified when it has:

- an external provider boundary
- materially different scale profile
- materially different latency or availability target
- distinct security, PCI, or residency boundary
- independently operated product or team boundary with clear on-call ownership

Examples that often stay separate:

- provider adapters
- BFFs and edge aggregators
- externally exposed APIs
- isolated compute workflows
- high-risk compliance boundaries

## Anti-Patterns

- Counting repos as architecture quality.
- Treating a service mesh as the fix for bad decomposition.
- Preserving every microservice because "it might scale independently one day".
- Merging repos before clarifying runtime boundaries.
- Introducing choreography everywhere instead of using selective orchestration for high-stakes flows.
- Leaving outbox, idempotency, and replayability as team-by-team choices.
- Building a portal with no templates, scorecards, or paved roads.

## Practical Heuristics

### Repo Classification

For each repo, classify it as one of:

- `runtime-platform`
- `runtime-edge`
- `provider-adapter`
- `shared-library`
- `channel-client`
- `platform-tooling`
- `absorption-candidate`
- `retirement-candidate`

### Runtime Decision Rule

Keep or create a separate runtime only if at least one is true:

- independent scale is required
- independent release is required
- a hard trust boundary exists
- a hard compliance boundary exists
- asynchronous isolation is required for resilience

Otherwise, prefer an internal module inside a bounded-context platform.

### Migration Order

1. Freeze unjustified runtime creation.
2. Standardize platform defaults and scorecards.
3. Consolidate low-value internal services inside core bounded contexts.
4. Normalize adapters and external boundaries.
5. Strangle legacy dependencies behind facades and compatibility layers.
6. Retire compatibility infrastructure after traffic is removed.

## Deliverable Shape

When answering estate-modernization questions, produce:

- current-state problem statement
- repo-vs-runtime diagnosis
- target platform map
- consolidation candidates and non-candidates
- migration waves
- "what not to build"
- success metrics

## Current External Anchors To Verify

When live web access is available, prefer checking:

- Microsoft platform engineering guidance for interfaces and golden-path design
- Backstage docs for software templates and platform adoption patterns
- CNCF platform guidance and maturity model
- AWS strangler guidance for incremental modernization
- official observability and workflow docs when recommending telemetry or orchestration standards
