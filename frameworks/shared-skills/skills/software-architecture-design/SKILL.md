---
name: software-architecture-design
description: System design, architecture patterns, scalability tradeoffs, and distributed systems for production-grade software. Covers microservices, event-driven, CQRS, modular monoliths, and reliability patterns.
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

**Industry Data (CNCF 2025):** 42% of organizations that adopted microservices have consolidated at least some services back into larger deployable units. Primary drivers: debugging complexity, operational overhead, network latency.

See [references/modern-patterns.md](references/modern-patterns.md) for detailed pattern descriptions.

---

## Modern Architecture Patterns (Jan 2026)

### Data Mesh Architecture

Use when data silos impede cross-functional analytics.

**Principles:**

- Domain-oriented data ownership
- Data as a product
- Self-serve data platform
- Federated computational governance

| Do | Avoid |
|----|-------|
| Assign data ownership to domain teams | Centralized data lake without ownership |
| Publish data with SLAs and documentation | Schema changes without consumer notification |
| Use standard interfaces (APIs, SQL) | Proprietary formats without discoverability |

### Composable Architecture

Use when business demands rapid capability assembly.

**Characteristics:**

- Packaged business capabilities (PBCs)
- API-first integration
- Low-code/no-code composition layer
- Event-driven coordination

| Do | Avoid |
|----|-------|
| Design components with clear contracts | Tightly coupled monolithic modules |
| Use standard protocols (REST, GraphQL, gRPC) | Custom integration patterns |
| Enable runtime composition | Build-time-only assembly |

### Continuous Architecture

Architecture evolves with software, not separate from it.

**Practices:**

- Just-enough upfront design
- Delay decisions to responsible moment
- Architect roles on delivery teams
- Architecture fitness functions (automated checks)

### Edge Computing Patterns

Use when latency or bandwidth constraints require local processing.

| Pattern | Use Case |
|---------|----------|
| Edge gateway | Protocol translation, local caching |
| Edge compute workloads | Validation, transforms, local control loops |
| Edge-cloud hybrid | Local processing, cloud aggregation |

### Platform Engineering (2026)

Internal developer platforms (IDPs) for self-service infrastructure. By 2026, 80% of large software engineering organizations will have platform teams (Gartner).

**IDP Stack:**

| Component | Tools | Purpose |
| --------- | ----- | ------- |
| Portal | Backstage (89% market share), Port | Service catalog, tech docs |
| Golden paths | Scaffolder templates | Standardized project creation |
| Infrastructure | Terraform, Crossplane | Self-service provisioning |
| AI agents | First-class citizens with RBAC | Automated workflows |

**FinOps Integration:** Platforms now implement pre-deployment cost gates that block services exceeding unit-economic thresholds.

**Unified Delivery:** Single pipeline for app developers, ML engineers, and data scientists.

---

### Optional: AI/Automation Extensions

> **Note**: This section covers AI-specific architectural patterns. Skip if building traditional systems.

#### RAG Architecture Patterns

Retrieval-Augmented Generation for enterprise AI.

| Component | Purpose |
| --------- | ------- |
| Vector store | Embedding storage (Pinecone, Weaviate, pgvector) |
| Retriever | Semantic search over documents |
| Generator | LLM produces responses with context |
| Orchestrator | Chains retrieval and generation |

#### Google's 8 Multi-Agent Design Patterns (Jan 2026)

The agentic AI field is experiencing its "microservices revolution" — single all-purpose agents are being replaced by orchestrated teams of specialized agents.

**Three foundational execution patterns:** Sequential, Loop, Parallel

| Pattern | Description | Use Case |
| ------- | ----------- | -------- |
| Sequential Pipeline | Agents in assembly line, output → next input | Document processing, ETL |
| Parallel Fan-out | Concurrent agent execution, results merged | Multi-source research |
| Loop/Iterative | Agent refines until condition met | Code review, optimization |
| Hierarchical | Manager delegates to worker agents | Complex task decomposition |
| Bidding/Auction | Agents compete for task assignment | Resource allocation |
| Human-in-the-loop | Approval gates for critical decisions | High-stakes workflows |
| Reflection | Agent critiques and improves own output | Quality assurance |
| Tool Use | Agent selects and invokes external tools | API integration |

**Anti-patterns:**

- Unbounded agent loops without termination conditions
- Missing human-in-the-loop for critical decisions
- No observability into agent actions and reasoning
- Single monolithic agent trying to do everything

#### Agent Communication Protocols

| Protocol | Purpose | Standard |
| -------- | ------- | -------- |
| MCP (Model Context Protocol) | LLM-to-data source connection | Anthropic open standard |
| A2A (Agent-to-Agent) | Inter-agent communication at scale | Google Cloud Agent Engine |

**MCP enables:** Agents access external data (databases, APIs, file systems) through standardized interfaces.

**A2A enables:** Cross-system agent orchestration, discovery, and collaboration between agents from different platforms.

---

## Navigation

### Core Resources

- [references/modern-patterns.md](references/modern-patterns.md) — 10 contemporary architecture patterns with decision trees (microservices, event-driven, serverless, CQRS, modular monolith, service mesh, edge computing)
- [references/scalability-reliability-guide.md](references/scalability-reliability-guide.md) — CAP theorem, database scaling, caching strategies, circuit breakers, SRE patterns, observability
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

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about software architecture, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best architecture for [use case]?"
- "What should I use for [microservices/serverless/event-driven]?"
- "What's the latest in system design?"
- "Current best practices for [scalability/resilience/observability]?"
- "Is [architecture pattern] still relevant in 2026?"
- "[Monolith] vs [microservices] vs [modular monolith]?"
- "Best approach for [distributed systems/data consistency]?"

### Required Searches

1. Search: `"software architecture best practices 2026"`
2. Search: `"[microservices/serverless/event-driven] architecture 2026"`
3. Search: `"system design patterns 2026"`
4. Search: `"[specific pattern] vs alternatives 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What architecture patterns are popular NOW
- **Emerging trends**: New patterns gaining traction (AI-native, edge)
- **Deprecated/declining**: Approaches that are losing relevance
- **Recommendation**: Based on fresh data and real-world case studies

### Example Topics (verify with fresh search)

- Modular monolith renaissance
- AI-native architecture patterns
- Edge computing and CDN-first design
- Event-driven microservices evolution
- Platform engineering and internal developer platforms
- Observability-driven development

---

## Operational Playbooks

**Shared Foundation**

- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md) - Canonical clean code rules (`CC-*`) for citation
- Legacy playbook: [../software-clean-code-standard/references/code-quality-operational-playbook.md](../software-clean-code-standard/references/code-quality-operational-playbook.md) - `RULE-01`–`RULE-13`, operational procedures, and design patterns
- [../software-clean-code-standard/references/design-patterns-operational-checklist.md](../software-clean-code-standard/references/design-patterns-operational-checklist.md) - GoF pattern triggers and guardrails, when to apply vs avoid patterns

**Architecture-Specific**

- [references/operational-playbook.md](references/operational-playbook.md) — Detailed architecture questions, decomposition patterns, security layers, and external references
