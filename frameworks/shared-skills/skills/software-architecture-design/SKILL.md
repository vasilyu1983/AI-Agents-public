---
name: software-architecture-design
description: Use when designing system architecture, choosing between monolith/microservices/serverless, planning scalability, or making technology decisions. Covers microservices, event-driven, CQRS, modular monoliths, distributed systems, and reliability patterns for production-grade software.
---

# Software Architecture Design — Quick Reference

Use this skill for **system-level design decisions** rather than implementation details within a single service or component.

## Quick Reference

| Task | Pattern/Tool | Key Resources | When to Use |
|------|-------------|---------------|-------------|
| Choose architecture style | Layered, Microservices, Event-driven, Serverless | [modern-patterns.md](references/modern-patterns.md) | Greenfield projects, major refactors |
| Design for scale | Load balancing, Caching, Sharding, Read replicas | [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | High-traffic systems, performance goals |
| Ensure resilience | Circuit breakers, Retries, Bulkheads, Graceful degradation | [modern-patterns.md](references/modern-patterns.md) | Distributed systems, external dependencies |
| Document decisions | Architecture Decision Record (ADR) | [adr-template.md](assets/planning/adr-template.md) | Major technical decisions, tradeoff analysis |
| Define service boundaries | Domain-Driven Design (DDD), Bounded contexts | [microservices-template.md](assets/patterns/microservices-template.md) | Microservices decomposition |
| Model data consistency | ACID vs BASE, Event sourcing, CQRS, Saga patterns | [event-driven-template.md](assets/patterns/event-driven-template.md) | Multi-service transactions |
| Plan observability | SLIs/SLOs/SLAs, Distributed tracing, Metrics, Logs | [architecture-blueprint.md](assets/planning/architecture-blueprint.md) | Production readiness |

## When to Use This Skill

Invoke when working on:

- **System decomposition**: Deciding between monolith, modular monolith, microservices
- **Architecture patterns**: Event-driven, CQRS, layered, hexagonal, serverless
- **Data architecture**: Consistency models, sharding, replication, CQRS patterns
- **Scalability design**: Load balancing, caching strategies, database scaling
- **Resilience patterns**: Circuit breakers, retries, bulkheads, graceful degradation
- **API contracts**: Service boundaries, versioning, integration patterns
- **Architecture decisions**: ADRs, tradeoff analysis, technology selection

## When NOT to Use This Skill

Use other skills instead for:

- **Single-service implementation** (routes, controllers, business logic) → [software-backend](../software-backend/SKILL.md)
- **API endpoint design** (REST conventions, GraphQL schemas) → [dev-api-design](../dev-api-design/SKILL.md)
- **Security implementation** (auth, encryption, OWASP) → [software-security-appsec](../software-security-appsec/SKILL.md)
- **Frontend component architecture** → [software-frontend](../software-frontend/SKILL.md)
- **Database query optimization** → [data-sql-optimization](../data-sql-optimization/SKILL.md)

## Decision Tree: Choosing Architecture Pattern

```text
Project needs: [New System or Major Refactor]
    ├─ Single team, evolving domain?
    │   ├─ Start simple → Modular Monolith (clear module boundaries)
    │   └─ Need rapid iteration → Layered Architecture
    │
    ├─ Multiple teams, clear bounded contexts?
    │   ├─ Independent deployment critical → Microservices
    │   └─ Shared data model → Modular Monolith with service modules
    │
    ├─ Event-driven workflows?
    │   ├─ Asynchronous processing → Event-Driven Architecture (Kafka, queues)
    │   └─ Complex state machines → Saga pattern + Event Sourcing
    │
    ├─ Variable/unpredictable load?
    │   ├─ Pay-per-use model → Serverless (AWS Lambda, Cloudflare Workers)
    │   └─ Batch processing → Serverless + queues
    │
    └─ High consistency requirements?
        ├─ Strong ACID guarantees → Monolith or Modular Monolith
        └─ Distributed data → CQRS + Event Sourcing
```

**Decision Factors:**

- **Team size threshold**: <10 developers → modular monolith typically outperforms microservices (operational overhead)
- Team structure (Conway's Law) — architecture mirrors org structure
- Deployment independence needs
- Consistency vs availability tradeoffs (CAP theorem)
- Operational maturity (monitoring, orchestration)

See [references/modern-patterns.md](references/modern-patterns.md) for detailed pattern descriptions.

## Workflow (System-Level)

Use this workflow when a user asks for architecture recommendations, decomposition, or major platform decisions.

1. Clarify: problem statement, non-goals, constraints, and success metrics
2. Capture quality attributes: availability, latency, throughput, durability, consistency, security, compliance, cost
3. Propose 2–3 candidate architectures and compare tradeoffs
4. Define boundaries: bounded contexts, ownership, APIs/events, integration contracts
5. Decide data strategy: storage, consistency model, schema evolution, migrations
6. Design for operations: SLOs, failure modes, observability, deployment, DR, incident playbooks
7. Document decisions: write ADRs for key tradeoffs and irreversible choices

Preferred deliverables (pick what fits the request):

- Architecture blueprint: `assets/planning/architecture-blueprint.md`
- Decision record: `assets/planning/adr-template.md`
- Pattern deep dives: `references/modern-patterns.md`, `references/scalability-reliability-guide.md`

## 2026 Considerations (Load Only When Relevant)

For ecosystem-sensitive questions (current vendor constraints, shifting best practices), use `data/sources.json` as the starting index:

- 2026 trends overview: `references/architecture-trends-2026.md`
- Platform engineering / IDPs: `.platform_engineering_2026`
- Data mesh and analytics architecture: `.scalability_reliability` (data mesh entries)
- AI-native systems (RAG, agents, MCP/A2A): `.optional_ai_architecture`

If fresh web access is not available, answer with best-known patterns and explicitly call out assumptions.

## Navigation

### Core Resources

- [references/modern-patterns.md](references/modern-patterns.md) — 10 contemporary architecture patterns with decision trees (microservices, event-driven, serverless, CQRS, modular monolith, service mesh, edge computing)
- [references/scalability-reliability-guide.md](references/scalability-reliability-guide.md) — CAP theorem, database scaling, caching strategies, circuit breakers, SRE patterns, observability
- [references/architecture-trends-2026.md](references/architecture-trends-2026.md) — Platform engineering, data mesh, AI-native systems (load only when relevant)
- [data/sources.json](data/sources.json) — 60 curated external resources (AWS, Azure, Google Cloud, Martin Fowler, microservices.io, SRE books, multi-agent patterns, MCP/A2A protocols, platform engineering 2026)

### Templates

**Planning & Documentation** ([assets/planning/](assets/planning/)):

- [assets/planning/architecture-blueprint.md](assets/planning/architecture-blueprint.md) — Service blueprint template (dependencies, SLAs, data flows, resilience, security, observability)
- [assets/planning/adr-template.md](assets/planning/adr-template.md) — Architecture Decision Record (ADR) for documenting design decisions with tradeoff analysis

**Architecture Patterns** ([assets/patterns/](assets/patterns/)):

- [assets/patterns/microservices-template.md](assets/patterns/microservices-template.md) — Complete microservices design template (API contracts, resilience, deployment, testing, cost optimization)
- [assets/patterns/event-driven-template.md](assets/patterns/event-driven-template.md) — Event-driven architecture template (event schemas, saga patterns, event sourcing, schema evolution)

**Operations & Scalability** ([assets/operations/](assets/operations/)):

- [assets/operations/scalability-checklist.md](assets/operations/scalability-checklist.md) — Comprehensive scalability checklist (database scaling, caching, load testing, auto-scaling, DR)

### Related Skills

**Implementation Details:**

- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Backend engineering, API implementation, data layer
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — Frontend architecture, micro-frontends, state management
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — REST, GraphQL, gRPC design patterns

**Reliability & Operations:**

- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD, deployment strategies, IaC, platform operations
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md) — Monitoring, tracing, alerting, SLOs

**Security & Data:**

- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Threat modeling, authentication, authorization, secure design
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database design, optimization, indexing strategies

**Quality & Code:**

- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Code review practices, architectural review

**Documentation:**

- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) — Architecture documentation, C4 diagrams, ADRs

---

## Freshness Protocol (When the Question Depends on "Now")

Use this when the user is asking for current best practices, vendor-specific constraints, or trend-sensitive recommendations.

1. If live web access is available, consult 2–3 authoritative sources from `data/sources.json` (cloud frameworks, SRE, pattern catalogs) and fold new constraints into the recommendation.
2. If live web access is not available, answer with durable patterns and explicitly state assumptions that could change (vendor limits, pricing, managed-service capabilities, ecosystem maturity).

## Operational Playbooks

**Shared Foundation**

- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) - Canonical clean code rules (`CC-*`) for citation
- Legacy playbook: [../software-clean-code-standard/references/code-quality-operational-playbook.md](../software-clean-code-standard/references/code-quality-operational-playbook.md) - `RULE-01`–`RULE-13`, operational procedures, and design patterns
- [../software-clean-code-standard/references/design-patterns-operational-checklist.md](../software-clean-code-standard/references/design-patterns-operational-checklist.md) - GoF pattern triggers and guardrails, when to apply vs avoid patterns

**Architecture-Specific**

- [references/operational-playbook.md](references/operational-playbook.md) — Detailed architecture questions, decomposition patterns, security layers, and external references
