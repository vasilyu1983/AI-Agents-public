---
name: software-architecture-design
description: System design, architecture patterns, scalability tradeoffs, and distributed systems for production-grade software. Covers microservices, event-driven, CQRS, modular monoliths, and reliability patterns.
---

# Software Architecture Design — Quick Reference

Use this skill for **system-level design decisions** rather than implementation details within a single service or component.

## Quick Reference

| Task | Pattern/Tool | Key Resources | When to Use |
|------|-------------|---------------|-------------|
| Choose architecture style | Layered, Microservices, Event-driven, Serverless | [modern-patterns.md](resources/modern-patterns.md) | Greenfield projects, major refactors |
| Design for scale | Load balancing, Caching, Sharding, Read replicas | [scalability-reliability-guide.md](resources/scalability-reliability-guide.md) | High-traffic systems, performance goals |
| Ensure resilience | Circuit breakers, Retries, Bulkheads, Graceful degradation | [modern-patterns.md](resources/modern-patterns.md) | Distributed systems, external dependencies |
| Document decisions | Architecture Decision Record (ADR) | [adr-template.md](templates/planning/adr-template.md) | Major technical decisions, tradeoff analysis |
| Define service boundaries | Domain-Driven Design (DDD), Bounded contexts | [microservices-template.md](templates/patterns/microservices-template.md) | Microservices decomposition |
| Model data consistency | ACID vs BASE, Event sourcing, CQRS, Saga patterns | [event-driven-template.md](templates/patterns/event-driven-template.md) | Multi-service transactions |
| Plan observability | SLIs/SLOs/SLAs, Distributed tracing, Metrics, Logs | [architecture-blueprint.md](templates/planning/architecture-blueprint.md) | Production readiness |

## When to Use This Skill

Invoke when working on:

- **System decomposition**: Deciding between monolith, modular monolith, microservices
- **Architecture patterns**: Event-driven, CQRS, layered, hexagonal, serverless
- **Data architecture**: Consistency models, sharding, replication, CQRS patterns
- **Scalability design**: Load balancing, caching strategies, database scaling
- **Resilience patterns**: Circuit breakers, retries, bulkheads, graceful degradation
- **API contracts**: Service boundaries, versioning, integration patterns
- **Architecture decisions**: ADRs, tradeoff analysis, technology selection

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

- Team size and structure (Conway's Law)
- Deployment independence needs
- Consistency vs availability tradeoffs (CAP theorem)
- Operational maturity (monitoring, orchestration)

See [resources/modern-patterns.md](resources/modern-patterns.md) for detailed pattern descriptions.

---

## Navigation

### Core Resources

- [resources/modern-patterns.md](resources/modern-patterns.md) — 10 contemporary architecture patterns with decision trees (microservices, event-driven, serverless, CQRS, modular monolith, service mesh, edge computing)
- [resources/scalability-reliability-guide.md](resources/scalability-reliability-guide.md) — CAP theorem, database scaling, caching strategies, circuit breakers, SRE patterns, observability
- [data/sources.json](data/sources.json) — 42 curated external resources (AWS, Azure, Google Cloud, Martin Fowler, microservices.io, SRE books, 2024-2025 best practices)

### Templates

**Planning & Documentation** ([templates/planning/](templates/planning/)):

- [templates/planning/architecture-blueprint.md](templates/planning/architecture-blueprint.md) — Service blueprint template (dependencies, SLAs, data flows, resilience, security, observability)
- [templates/planning/adr-template.md](templates/planning/adr-template.md) — Architecture Decision Record (ADR) for documenting design decisions with tradeoff analysis

**Architecture Patterns** ([templates/patterns/](templates/patterns/)):

- [templates/patterns/microservices-template.md](templates/patterns/microservices-template.md) — Complete microservices design template (API contracts, resilience, deployment, testing, cost optimization)
- [templates/patterns/event-driven-template.md](templates/patterns/event-driven-template.md) — Event-driven architecture template (event schemas, saga patterns, event sourcing, schema evolution)

**Operations & Scalability** ([templates/operations/](templates/operations/)):

- [templates/operations/scalability-checklist.md](templates/operations/scalability-checklist.md) — Comprehensive scalability checklist (database scaling, caching, load testing, auto-scaling, DR)

### Related Skills

**Implementation Details:**

- [../software-backend/SKILL.md](../software-backend/SKILL.md) — Backend engineering, API implementation, data layer
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — Frontend architecture, micro-frontends, state management
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — REST, GraphQL, gRPC design patterns

**Reliability & Operations:**

<!-- TODO: Add when skills are created
- [../qa-resilience/SKILL.md](../qa-resilience/SKILL.md) — Resilience patterns, backpressure, failure handling
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md) — Monitoring, tracing, performance optimization
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Platform engineering, SRE, IaC, deployment strategies
-->

**Security & Data:**

- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Threat modeling, authentication, authorization, secure design
<!-- TODO: Add when skill is created
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database design, optimization, indexing strategies
-->

**Quality & Code:**

- [../software-code-review/SKILL.md](../software-code-review/SKILL.md) — Code review practices, architectural review
<!-- TODO: Add when skill is created
- [../qa-refactoring/SKILL.md](../qa-refactoring/SKILL.md) — Refactoring patterns, technical debt management
-->

**Documentation:**

- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md) — Architecture documentation, C4 diagrams, ADRs

---

## Operational Playbooks

**Shared Foundation**

- [../../_shared/resources/code-quality-operational-playbook.md](../../_shared/resources/code-quality-operational-playbook.md) — Canonical coding rules (RULE-01 to RULE-13), Section 6: Design Patterns & Application Rules (Strategy, Adapter, Repository, Observer, CQRS)
- [../../_shared/resources/design-patterns-operational-checklist.md](../../_shared/resources/design-patterns-operational-checklist.md) — GoF pattern triggers and guardrails, when to apply vs avoid patterns

**Architecture-Specific**

- [resources/operational-playbook.md](resources/operational-playbook.md) — Detailed architecture questions, decomposition patterns, security layers, and external references
