## Core Architecture Questions

Use these questions to frame any design discussion:

- **Domain:**
  - What problem is this system solving?
  - What are the core domain concepts and invariants?
- **Boundaries:**
  - How should responsibilities be split across services or modules?
  - What must stay together for strong consistency?
- **Data:**
  - What data is stored, where, and in what shape?
  - What are the consistency and durability requirements?
- **Workload:**
  - What are the expected read/write patterns?
  - How does traffic scale over time (burst vs steady)?
- **Failure:**
  - What happens when dependencies fail or degrade?
  - What are the recovery paths and fallbacks?
- **AI-native systems (if applicable):**
  - Is this better modeled as a deterministic workflow, a single agent, or a multi-agent system?
  - Do tools, retrieval, and cross-agent communication need separate trust boundaries?

---
## Table of Contents

- [Core Architecture Questions](#core-architecture-questions)
- [Pattern: Layered Architecture](#pattern-layered-architecture)
- [Pattern: Service Decomposition](#pattern-service-decomposition)
- [Pattern: Data and Consistency](#pattern-data-and-consistency)
- [Pattern: Request-Driven vs Event-Driven](#pattern-request-driven-vs-event-driven)
- [Pattern: Security Architecture](#pattern-security-architecture)
- [Freshness Protocol](#freshness-protocol)
- [External Resources](#external-resources)


## Pattern: Layered Architecture

Use when the system is not yet highly distributed, or when clarity and separation of concerns are more important than aggressive scalability.

Typical layering:

- Presentation/API layer: HTTP or messaging interfaces, authentication, request validation.
- Application/service layer: orchestration, use cases, workflows.
- Domain layer: core business logic and invariants.
- Infrastructure layer: databases, queues, external services, file storage.

Checklist:

- Clear direction of dependencies (outer layers depend on inner, not vice versa).
- Domain code does not depend on transport or storage details.
- Cross-cutting concerns (logging, metrics, security) handled via composition, not duplication.

---

## Pattern: Service Decomposition

Use when deciding between monolith, modular monolith, and microservices.

- **Monolith:**
  - Use when the team is small and the problem space is still evolving
  - Focus on modular boundaries inside a single deployable
- **Modular monolith:**
  - Use when you need strong internal boundaries and clear ownership but still want a single deployment unit
- **Microservices:**
  - Use when you have clear bounded contexts, strong ownership boundaries, and operational maturity

**Decomposition heuristics:**

- Group code by domain boundary, not by technical layer only
- Avoid splitting entities that must be updated transactionally
- Prefer a small number of well-designed services over many tiny ones

---

## Pattern: Data and Consistency

Use when designing storage and consistency behavior.

- Choose the primary source of truth for each piece of data
- **Decide consistency model:**
  - **Strong:** transactions and immediate consistency; fewer consumers, higher coupling
  - **Eventual:** asynchronous updates; requires idempotency and reconciliation
- **Avoid writing to multiple sources in a single request without a clear strategy:**
  - Use a "single writer" or orchestrator service
  - Use outbox patterns for publishing events reliably

**Checklist:**

- Data ownership is clear for each service
- Failure modes for partial writes are understood and handled
- Migrations and schema evolution have a plan (backwards compatibility where needed)

---

## Pattern: Request-Driven vs Event-Driven

Use this pattern to decide between synchronous and asynchronous flows.

- **Request-driven (synchronous):**
  - Good for user-facing APIs needing immediate feedback
  - Latency and availability of dependencies directly affect the caller
- **Event-driven (asynchronous):**
  - Good for decoupling producers and consumers
  - Suited to background work, aggregations, notifications

**Guidelines:**

- Keep request paths shallow for user interactions; offload heavy work via events or queues
- In event-driven flows, design idempotent handlers and clear retry behaviors

---

## Pattern: Security Architecture

At this architecture boundary, identify which deployable owns each trust boundary and where authentication, authorization, and data protection decisions occur. Route the threat model, control design, and implementation checks to [software-security-appsec](../../software-security-appsec/SKILL.md).

---

## Freshness Protocol

When a decision depends on a vendor lifecycle, managed capability, price, limit, or protocol revision, look up that specific fact in the primary source listed in [data/sources.json](../data/sources.json). For MCP and A2A, check the revision implemented by the actual peers; for a mesh or managed platform, check its support and licence terms. If live verification is unavailable, leave the volatile claim unverified and decide from the durable boundary constraints.
