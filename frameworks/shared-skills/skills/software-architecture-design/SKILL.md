---
name: software-architecture-design
description: "Designs runtime and platform architecture inside a chosen solution. Use when deciding modular monolith vs services, consistency, resilience, or estate topology."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Software Architecture Design

Use this skill for **deep software and platform architecture decisions inside a known solution shape** rather than implementation details within a single service or component.

If the question starts from a business workflow, system landscape, target state, or phased cross-system migration, use [../software-solution-architecture/SKILL.md](../software-solution-architecture/SKILL.md) first and come here for runtime, decomposition, and operability depth.

Treat estate modernization, platform engineering, and AI-native interoperability as optional deep dives. Do not load them unless the user is explicitly asking for those concerns.

## Quick Reference

| Task | Pattern/Tool | Key Resources | When to Use |
|------|-------------|---------------|-------------|
| Choose architecture style | Layered, Microservices, Event-driven, Serverless | [modern-patterns.md](references/modern-patterns.md) | Greenfield projects, major refactors |
| Design for scale | Load balancing, Caching, Sharding, Read replicas | [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | High-traffic systems, performance goals |
| Ensure resilience | Circuit breakers, Retries, Bulkheads, Graceful degradation | [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | Distributed systems, external dependencies |
| Document decisions | Architecture Decision Record (ADR) | [adr-template.md](assets/planning/adr-template.md) | Major technical decisions, tradeoff analysis |
| Define service boundaries | Domain-Driven Design (DDD), Bounded contexts | [microservices-template.md](assets/patterns/microservices-template.md) | Microservices decomposition |
| Model data consistency | ACID vs BASE, Event sourcing, CQRS, Saga patterns | [data-architecture-patterns.md](references/data-architecture-patterns.md) | Multi-service transactions |
| Plan observability | SLIs/SLOs/SLAs, Distributed tracing, Metrics, Logs | [architecture-blueprint.md](assets/planning/architecture-blueprint.md) | Production readiness |
| Migrate from monolith | Strangler fig, Database decomposition, Shadow traffic | [migration-modernization-guide.md](references/migration-modernization-guide.md) | Legacy modernization |
| Design inter-service comms | API Gateway, Service mesh, BFF pattern | [api-gateway-service-mesh.md](references/api-gateway-service-mesh.md) | Microservices networking |
| Design delivery platform | IDP, golden paths, fitness functions | [architecture-trends.md](references/architecture-trends.md) | Multi-team platforms, governance |
| Rationalize service sprawl | Bounded-context platforms, repo-vs-runtime matrix, platform scorecards | [estate-modernization.md](references/estate-modernization.md) | 20+ repos, too many services, uneven platform maturity |
| Plan estate modernization | Platform-first migration waves, consolidation, compatibility boundaries | [estate-modernization-blueprint.md](assets/planning/estate-modernization-blueprint.md) | Polyrepo estates, regulated migrations, legacy reduction |
| Design AI-native systems | RAG boundaries, tool gateways, agent interoperability, MCP, A2A | [architecture-trends.md](references/architecture-trends.md) | LLM-powered products when architecture, not implementation, is the main question |

## When to Use This Skill

Invoke when working on:

- **Software shape inside a known solution**: Turning a chosen solution shape into runtime boundaries, bounded contexts, and platform decisions
- **System decomposition**: Deciding between monolith, modular monolith, microservices
- **Architecture patterns**: Event-driven, CQRS, layered, hexagonal, serverless
- **Platform architecture**: Internal developer platforms, golden paths, policy and delivery guardrails
- **Estate modernization**: Too many repos, too many runtime units, polyrepo rationalization, platform-first operating models
- **Data architecture**: Consistency models, sharding, replication, CQRS patterns
- **Scalability design**: Load balancing, caching strategies, database scaling
- **Resilience patterns**: Circuit breakers, retries, bulkheads, graceful degradation
- **API boundary design**: Service-to-service contract posture, versioning strategy, and integration shape when the boundary decision is architectural
- **Architecture decisions**: ADRs, tradeoff analysis, technology selection
- **Migration planning**: Monolith decomposition, strangler fig, database separation
- **AI-native architecture**: RAG boundaries, tool gateways, and interoperability protocols when the request is architecture-level rather than tool/server implementation

## When NOT to Use This Skill

Use other skills instead for:

- **Cross-system solution design** (business flow, target state, integration landscape, phased transition across systems) → [software-solution-architecture](../software-solution-architecture/SKILL.md)
- **Single-service implementation** (routes, controllers, business logic) → [software-backend](../software-backend/SKILL.md)
- **API endpoint design** (REST conventions, GraphQL schemas) → [dev-api-design](../dev-api-design/SKILL.md)
- **Security implementation** (auth, encryption, OWASP) → [software-security-appsec](../software-security-appsec/SKILL.md)
- **Frontend component architecture** → [software-frontend](../software-frontend/SKILL.md)
- **Database query optimization** → [data-sql-optimization](../data-sql-optimization/SKILL.md)
- **Agent workflow implementation / MCP server implementation** → [ai-agents](../ai-agents/SKILL.md), [agents-mcp](../agents-mcp/SKILL.md)

## Boundary Rules

- This skill owns runtime boundaries, deployable-unit decisions, data consistency tradeoffs, resilience internals, and platform defaults.
- Start from the simplest architecture that satisfies the constraints; do not default to microservices, event sourcing, service mesh, or multi-agent splits without explicit evidence.
- If the unresolved question is still "which systems participate, where is the system of record, or what is the target-state landscape?" route back to [software-solution-architecture](../software-solution-architecture/SKILL.md).
- If the unresolved question is implementation of agent protocols, tool servers, or runtime-specific integrations, route to [ai-agents](../ai-agents/SKILL.md) or [agents-mcp](../agents-mcp/SKILL.md).

## Decision Tree: Choosing Architecture Pattern

```text
Primary question: [What kind of architecture problem is this?]
    ├─ Large estate with many repos/services and rising cognitive load?
    │   ├─ Runtime count is the main problem → Bounded-context platforms + selective consolidation
    │   ├─ Delivery inconsistency is the main problem → IDP + golden paths + scorecards
    │   └─ Both are true → Platform-first modernization, then consolidate low-value runtime units
    │
    ├─ Deterministic workflow, known steps?
    │   ├─ Single deployable acceptable → Modular Monolith
    │   ├─ Independent teams/capabilities required → Sequential or event-driven services
    │   └─ Burst-driven or edge-triggered workload → Serverless / event-driven
    │
    ├─ Adaptive workflow with tool use and reasoning?
    │   ├─ One agent can own the task → Single-agent system
    │   ├─ Specialized roles truly needed → Multi-agent with explicit stop conditions
    │   └─ High stakes / regulated workflow → Human-in-the-loop + audit trail
    │
    ├─ Strong consistency inside one domain boundary?
    │   ├─ Keep data and writes together → Monolith or Modular Monolith
    │   └─ Split only at stable bounded contexts → Microservices with owned data
    │
    └─ Need platform-level consistency across many teams?
        ├─ Repeated service creation / compliance needs → IDP + golden paths
        └─ Cross-agent or cross-vendor interoperability → MCP for tools/context, A2A for agent-to-agent
```

**Decision Factors:**

- **Default posture**: prefer modular monolith over microservices unless independent deployment, ownership, and operability benefits are clear — see the explicit team-size/release-cadence/operational-maturity gates in [modern-patterns.md § Modular Monolith vs. Microservices](references/modern-patterns.md#modular-monolith-vs-microservices-explicit-gates-2026-default)
- **Estate posture**: optimize for fewer runtime units before fewer repos; repositories are collaboration units, runtimes are operational cost centers
- **Agent posture**: prefer deterministic workflows or a single agent before introducing multi-agent coordination
- **Connectivity posture**: prefer gateway plus application-library patterns until mTLS, traffic policy, or shared telemetry needs justify mesh complexity
- Team structure (Conway's Law) — architecture mirrors org structure
- Deployment independence needs
- Consistency and failure-domain boundaries
- Operational maturity (monitoring, orchestration)
- Interoperability needs (protocols, contracts, external systems)

See [references/modern-patterns.md](references/modern-patterns.md) for detailed pattern descriptions.

## Output Guidelines

The references in this skill are background knowledge for you — absorb the patterns and present them as your own expertise. Do not cite internal reference file names (e.g., "from data-architecture-patterns.md") in user-facing output. Users don't know these files exist.

Every architecture recommendation must cover the following; skip elements only with explicit justification:

- [ ] **Simplest sufficient topology** — state the least-complex architecture that still satisfies requirements
- [ ] **Concrete technology picks** — name specific technologies (e.g., "Temporal.io for workflow orchestration", not just "an orchestrator")
- [ ] **Recommended option + rejected alternatives** — what was considered, why alternatives lost
- [ ] **What NOT to build** — explicitly defer or exclude premature scope
- [ ] **Team and process alignment** — CODEOWNERS, deployment ownership, on-call boundaries
- [ ] **Repo and runtime model** — for multi-repo estates, distinguish repo count from deployable count
- [ ] **Operability model** — deployment topology, failure domains, rollback points, SLO ownership, incident boundaries
- [ ] **Migration path** — sequencing, cutover strategy, reversibility (for refactors or new subsystems)
- [ ] **Key risks and failure modes** — named breakpoints, how to detect early
- [ ] **Success metrics** — measurable indicators: deploy frequency, lead time, error rates, MTTR

## Workflow (System-Level)

Use this workflow when a user asks for architecture recommendations, decomposition, or major platform decisions.

1. Clarify: problem statement, non-goals, constraints, and success metrics
2. Capture quality attributes: availability, latency, throughput, durability, consistency, security, compliance, cost
3. Decide workload shape: deterministic workflow, single-agent, or multi-agent; synchronous vs asynchronous
4. Propose 2–3 candidate architectures and compare tradeoffs
5. Default to the least-complex viable topology before justifying more distributed patterns
6. For 20+ repo estates, classify each repo as runtime, adapter, library, channel, platform, tooling, or absorption candidate
7. Define boundaries: bounded contexts, ownership, APIs/events, protocol contracts, interoperability needs
8. Decide data strategy: storage, consistency model, schema evolution, migrations
9. Design for operations: SLOs, failure modes, observability, deployment, DR, incident playbooks
10. Design governance and safety: policy enforcement, auditability, evaluation gates, rollback controls
11. Call out scope limits: what NOT to build yet, what to defer, what to buy vs build
12. Document decisions: write ADRs for key tradeoffs and irreversible choices

Preferred deliverables (pick what fits the request):

- Architecture blueprint: `assets/planning/architecture-blueprint.md`
- Estate modernization blueprint: `assets/planning/estate-modernization-blueprint.md`
- Decision record: `assets/planning/adr-template.md`
- Pattern deep dives: `references/modern-patterns.md`, `references/scalability-reliability-guide.md`

## ASCII Flow

```text
Architecture design request
  -> Define quality attributes and system boundaries
  -> Map domain model, dependencies, and failure modes
  -> Choose architecture pattern and integration style
  -> Document rejected options and tradeoffs
  -> Define migration, observability, and verification checks
  -> Hand off implementable decisions and open risks
```

## Known Traps

- Choosing microservices because the estate already has many repos, even though runtime sprawl and weak ownership are the real issue.
- Drawing a target-state diagram without a migration sequence, rollback boundary, or compatibility plan between old and new paths.
- Splitting domains before ownership, on-call, and deploy authority are ready to support the additional surface area.
- Introducing async and event-driven workflows on every boundary before deciding which paths actually need decoupling.
- Calling something platform engineering while the golden path remains optional, inconsistent, or under-owned.

## Common Anti-Patterns

- Using deployable services as the default decomposition unit instead of bounded contexts, team ownership, and operational cost.
- Copying hyperscaler or vendor reference architectures into teams that do not have equivalent scale, tooling, or platform staffing.
- Designing for peak optional futures instead of the current throughput, failure, compliance, and change-management constraints.
- Keeping every repo and runtime because each has "some value" despite obvious coordination and governance cost.
- Conflating "modern" with "more distributed" and "AI-native" with "multi-agent by default."

## Navigation

### Core References

Read **at most 2–3 references** per question — pick the ones most relevant to the specific ask. Do not read all of them.

| Reference | Contents | When to Read |
|-----------|----------|--------------|
| [modern-patterns.md](references/modern-patterns.md) | 11 architecture patterns with decision trees, incl. modular-monolith-vs-microservices gates and cell-based architecture | Choosing or comparing patterns |
| [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | CAP theorem, DB scaling, caching, circuit breakers, SRE | Scaling or reliability questions |
| [data-architecture-patterns.md](references/data-architecture-patterns.md) | CQRS variants, event sourcing, data mesh, sagas, consistency | Data flow across services |
| [migration-modernization-guide.md](references/migration-modernization-guide.md) | Strangler fig, DB decomposition, feature flags, risk assessment | Refactoring a monolith |
| [api-gateway-service-mesh.md](references/api-gateway-service-mesh.md) | Gateway patterns, service mesh, mTLS, observability | Inter-service communication |
| [architecture-trends.md](references/architecture-trends.md) | Platform engineering, ambient mesh, AI-native systems, MCP/A2A | Current trends only |
| [estate-modernization.md](references/estate-modernization.md) | Runtime-vs-repo rationalization, bounded-context platforms, consolidation heuristics | Multi-repo estates and service sprawl |
| [operational-playbook.md](references/operational-playbook.md) | Architecture questions framework, decomposition heuristics | Design discussion framing |

### Templates

**Planning & Documentation** ([assets/planning/](assets/planning/)):

- [architecture-blueprint.md](assets/planning/architecture-blueprint.md) — Service blueprint (dependencies, SLAs, data flows, resilience, security, observability)
- [estate-modernization-blueprint.md](assets/planning/estate-modernization-blueprint.md) — Estate blueprint (repo/runtime classification, target platform map, migration waves, scorecards)
- [adr-template.md](assets/planning/adr-template.md) — Architecture Decision Record for tradeoff analysis

**Architecture Patterns** ([assets/patterns/](assets/patterns/)):

- [microservices-template.md](assets/patterns/microservices-template.md) — Microservices design (API contracts, resilience, deployment, testing)
- [event-driven-template.md](assets/patterns/event-driven-template.md) — Event-driven architecture (event schemas, saga patterns, event sourcing)

**Operations** ([assets/operations/](assets/operations/)):

- [scalability-checklist.md](assets/operations/scalability-checklist.md) — Scalability checklist (DB scaling, caching, load testing, auto-scaling, DR)

### Validation

- [evals/evals.json](evals/evals.json) — trigger, non-trigger, and near-boundary behavioral checks for this skill

### Applied-Recipe Toolkits

- [references/decision-theory-applied.md](references/decision-theory-applied.md) — Decision-theory applied recipes for architecture: ADRs with EU + sensitivity, real-options for irreversible choices, VoI on spikes.
- [references/queueing-theory-applied.md](references/queueing-theory-applied.md) — Queueing-theory applied recipes for architecture: service sizing, backpressure topology, tail-latency budget.
- [references/theory-of-constraints-applied.md](references/theory-of-constraints-applied.md) — TOC applied recipes for architecture: system-wide bottleneck hunt, refactor scope, stability-vs-velocity ADR.
- [references/distributed-systems-applied.md](references/distributed-systems-applied.md) — Distributed-systems primitives applied to architecture: CAP-conscious service boundaries, consensus algorithm selection, idempotency at API surfaces, leases-with-fencing for leader-elected jobs, quorum sizing, consistency-vs-latency ADR template.
- [references/reliability-theory-applied.md](references/reliability-theory-applied.md) — Reliability primitives (MTBF/MTTR, availability, FMEA, error budgets) applied to software architecture design.

### Related Skills

- [software-solution-architecture](../software-solution-architecture/SKILL.md) — End-to-end solution design, system landscape, target-state and migration architecture
- [software-backend](../software-backend/SKILL.md) — Backend engineering, API implementation, data layer
- [software-frontend](../software-frontend/SKILL.md) — Frontend architecture, micro-frontends, state management
- [dev-api-design](../dev-api-design/SKILL.md) — REST, GraphQL, gRPC design patterns
- [ops-devops-platform](../ops-devops-platform/SKILL.md) — CI/CD, deployment strategies, IaC
- [qa-observability](../qa-observability/SKILL.md) — Monitoring, tracing, alerting, SLOs
- [software-security-appsec](../software-security-appsec/SKILL.md) — Threat modeling, auth, secure design
- [data-sql-optimization](../data-sql-optimization/SKILL.md) — Database design, optimization, indexing
- [docs-codebase](../docs-codebase/SKILL.md) — Architecture documentation, docs-as-code structure
- `docs-diagram-design` — Whether a diagram earns its place, and what it must show
- [ai-agents](../ai-agents/SKILL.md) — Agent system design, orchestration, evaluation
- [agents-mcp](../agents-mcp/SKILL.md) — MCP server/client patterns and integration

## Freshness Protocol

When users ask version-sensitive questions about architecture patterns, platform engineering, or AI-native systems, verify current information before answering.

### Trigger Conditions

- "What's the best architecture for [use case]?"
- "Microservices vs monolith — what's the current recommendation?"
- "What's the latest in platform engineering / service mesh / AI architecture?"
- "How do I modernize 50/100+ repos or reduce service sprawl?"
- "Is [pattern] still recommended?"

### How to Freshness-Check

1. Start from `data/sources.json` and prefer official docs, standards, release notes, and lifecycle pages.
2. Run a targeted web search for the specific architecture pattern or platform.
3. Use non-primary sources only as durable background, not as freshness authority.

Load only when the question explicitly involves current trends, vendor-specific constraints, AI-native architecture, or "what's the latest thinking on X?"

- [references/architecture-trends.md](references/architecture-trends.md) — Platform engineering, ambient mesh, MCP/A2A interoperability, AI-native systems
- [references/estate-modernization.md](references/estate-modernization.md) — Estate rationalization, bounded-context platforms, platform-first migration posture
- [data/sources.json](data/sources.json) — curated resources organized by category:
  - `platform_engineering_2026` — IDPs, software catalogs, and template-driven platform defaults
  - `estate_modernization_2026` — strangler migration, anti-corruption layers, repo-vs-runtime guidance
  - `optional_ai_architecture` — MCP/A2A protocols and architecture-level AI interoperability references
  - `modern_architecture_2026` — ambient mesh and other version-sensitive platform patterns

If live web access is available, consult 2–3 authoritative sources from `data/sources.json` and fold findings into the recommendation. If not, answer with durable patterns and explicitly state assumptions that could change (vendor limits, pricing, managed-service capabilities, or lifecycle status).

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

