---
title: "Cybernetics and VSM Applied to Software Solution Architecture: Bounded Contexts, Integration Platforms, and Enterprise Control"
skill: software-solution-architecture
foundation: foundations-cybernetics-vsm
last_updated: "2026-05-02"
last_verified: "2026-07-11"
status: stable
---

# Cybernetics and VSM Applied to Software Solution Architecture

> **Gate before invoking:** Check [`foundations-cybernetics-vsm` § When to Apply](../../foundations-cybernetics-vsm/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Applied layer on top of the 11 VSM primitives in `foundations-cybernetics-vsm`. This file maps those primitives to the architectural questions that arise when designing system landscapes, drawing capability boundaries, integrating domains, and governing change across an enterprise or multi-domain platform.

Read the solution-design workflow in `references/solution-workflow.md` and the boundary and integration decision matrix in `references/integration-and-boundary-patterns.md` first. Come here when you need to answer: _Where is the right boundary for this capability, how should control flow between the platform and its domains, and why does the governance structure keep failing to catch architectural drift before it becomes a crisis?_

---

## Table of Contents

- [Why Cybernetics for Solution Architecture](#why-cybernetics-for-solution-architecture)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Bounded Context as System 1 Unit](#p1--bounded-context-as-system-1-unit)
  - [P2 — Integration Platform as System 2 Coordinator](#p2--integration-platform-as-system-2-coordinator)
  - [P3 — Capability Owners as System 3 Internal Control](#p3--capability-owners-as-system-3-internal-control)
  - [P4 — Architecture Forum as System 4 Intelligence](#p4--architecture-forum-as-system-4-intelligence)
  - [P5 — Principles and North Star as System 5 Identity](#p5--principles-and-north-star-as-system-5-identity)
  - [P6 — Recursive Architecture Across Enterprise, Domain, and Service](#p6--recursive-architecture-across-enterprise-domain-and-service)
  - [P7 — Requisite Variety in API Design](#p7--requisite-variety-in-api-design)
  - [P8 — Algedonic Channels in Enterprise Architecture Review](#p8--algedonic-channels-in-enterprise-architecture-review)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [AP1 — Dictator Architecture: S5 Collapse onto S1](#ap1--dictator-architecture-s5-collapse-onto-s1)
  - [AP2 — Absent Coordination Layer: Integration Platform Managed as S3 Command](#ap2--absent-coordination-layer-integration-platform-managed-as-s3-command)
  - [AP3 — Variety Mismatch: Thin API Facing a Wide Environment](#ap3--variety-mismatch-thin-api-facing-a-wide-environment)
  - [AP4 — Architecture Forum with No S3 Ground Truth (Missing S3*)](#ap4--architecture-forum-with-no-s3-ground-truth-missing-s3)
- [Recipes](#recipes)
  - [R1 — VSM Boundary Mapping for a New Domain Capability](#r1--vsm-boundary-mapping-for-a-new-domain-capability)
  - [R2 — Designing Algedonic Architecture Review for Compliance and Data Privacy Risk](#r2--designing-algedonic-architecture-review-for-compliance-and-data-privacy-risk)
  - [R3 — Recursive Decomposition: Enterprise to Service Level](#r3--recursive-decomposition-enterprise-to-service-level)
- [Composition](#composition)
- [Cross-References](#cross-references)

---

## Why Cybernetics for Solution Architecture

Solution architecture is fundamentally a control problem. The architect's job is not to draw the "right" diagram — it is to design a system that remains viable as its environment changes: business strategy shifts, regulatory requirements evolve, technology constraints move, and teams grow and reorganize.

Stafford Beer's Viable System Model (VSM) provides five analytical tools that map directly onto the decisions architects make every day:

- **Variety management (Ashby's Law, primitive 02):** Why API contracts break when the downstream environment is more complex than the interface design anticipated.
- **S1–S5 separation:** Why a single enterprise architect making all design decisions for individual services produces brittle architectures that cannot adapt locally.
- **Recursion (primitive 09):** Why the right design at the service level looks different from the right design at the domain or enterprise level — and why confusing levels causes category errors in governance.
- **Algedonic channels (primitive 11):** Why architectural drift goes undetected until a compliance breach or a production incident forces an emergency redesign.
- **Feedback loops (primitive 01):** Why architecture review processes that run only annually fail to regulate drift — the feedback delay is too long relative to the rate of change in modern software delivery.

The patterns and recipes below apply these primitives to the concrete questions in `software-solution-architecture`: capability ownership, integration landscape design, boundary drawing, transition architecture, and governance.

---

## Pattern Catalog

### P1 — Bounded Context as System 1 Unit

**When to use:** When decomposing a business capability landscape into owned, deployable units; when deciding whether two capabilities should be part of the same bounded context or separate ones; when diagnosing why a context is being micro-managed from outside its boundary.

**The VSM insight:**

In the VSM, every S1 unit must satisfy three properties: it produces primary value, it interacts with its own local environment, and it has sufficient internal management to operate within policy without constant S3 intervention. A bounded context in DDD satisfies exactly these properties at the service/domain level of recursion.

**Mechanic:**

Map each candidate bounded context against the S1 checklist:

| S1 Property | Bounded Context Question |
|-------------|--------------------------|
| Primary value production | What business outcome does this context own end-to-end? |
| Local environment interaction | Which external events, user requests, or integration inputs does this context consume directly? |
| Autonomy within policy | Can the owning team make architectural and delivery decisions inside this context without cross-context approval? |
| System of record | Is there a single source of truth for the core aggregate that this context owns? |

When a context fails the autonomy test — when its team must escalate routine design decisions outside the boundary — the context is being treated as an S3-managed execution unit rather than an S1 viable sub-system. The fix is usually one of three things: the boundary is drawn in the wrong place (the context straddles two capabilities that have different owners), the policy governing the context is too prescriptive (S3 is specifying how, not what), or the team lacks the skills to exercise the autonomy the design grants them.

**Domain example:**

An e-commerce platform decomposes into Order Management, Inventory, Catalogue, Pricing, and Fulfilment bounded contexts. Each is an S1 unit at the domain level of recursion. The Pricing context interacts directly with its local environment (competitive price feeds, elasticity models, A/B experiment results). It owns the pricing aggregate as its system of record. Its team ships pricing experiments without seeking cross-domain approval — provided they do not violate the S3 policy: "no pricing change that modifies the contract between Order Management and Pricing without a shared API version review."

**Breaks when:** Two capabilities share a transactional aggregate (e.g., Order and Payment must commit atomically) — in that case, splitting into separate S1 units requires explicit distributed-transaction handling or a compensating design. The boundary is a data coupling problem before it is a VSM problem; resolve the data model first.

**Canonical primitives:** [03-vsm-system-1](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/03-vsm-system-1.md), [09-recursion-levels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/09-recursion-levels.md).

---

### P2 — Integration Platform as System 2 Coordinator

**When to use:** When designing an event bus, API gateway, service mesh, or integration middleware layer; when diagnosing whether the integration layer is creating coordination bottlenecks or accumulating business logic it should not own; when deciding what belongs in the integration platform versus in the bounded contexts it connects.

**The VSM insight:**

S2 coordinates S1 units; it does not command them. The critical property of S2 is that it carries no authority over S1 — it provides shared scheduling, routing, and conflict-avoidance signals that S1 units use to avoid interfering with each other. When an integration platform starts owning business logic, making routing decisions that encode business rules, or acting as a gatekeeper to shared data, it has crossed the line from S2 coordinator into a shadow S3 — without the accountability structures or feedback loops that a legitimate S3 should have.

**Mechanic:**

For each piece of logic in the integration platform, apply the S2 test:

| S2-appropriate | Not S2-appropriate |
|----------------|-------------------|
| Route events to the correct consumer based on event type | Decide which event consumers are allowed to receive an event based on business rules |
| Enforce message schema contracts | Transform business data to resolve domain model conflicts |
| Throttle and retry delivery | Own retry backoff policy based on business criticality |
| Publish availability/health signals | Hold state about whether a downstream context should be active |
| Sequence events to prevent race conditions | Implement orchestration logic that coordinates multi-step business workflows |

Logic that fails the S2 test belongs either in the sending bounded context, the receiving bounded context, or — if it truly coordinates the whole — in an explicit orchestration context defined as its own S1 unit (e.g., a Workflow Orchestration service with a clear system-of-record for workflow state).

**Domain example:**

A financial services platform uses an event bus as its S2. The S2-appropriate configuration: the bus routes `PaymentInitiated`, `PaymentSettled`, and `PaymentFailed` events to the Fraud Detection, Ledger, and Notification contexts respectively. It enforces schema versions and delivers at-least-once with ordered delivery within partitions. It does not decide whether a payment is valid (Fraud Detection's job), does not hold the authoritative payment record (Ledger's job), and does not decide which notification channel to use (Notification's job). When a team proposes adding routing logic to the bus that selects event consumers based on customer tier, that logic is rejected from the bus and placed in the Notification bounded context where business rules about communication preferences belong.

**Breaks when:** The platform has genuine cross-cutting coordination requirements — for example, global rate-limiting or data-residency routing that no single context can own. In those cases, the platform may legitimately implement policy-level rules, but those rules must be traceable to explicit S5 architectural policy, not accumulated organically.

**Canonical primitives:** [04-vsm-system-2](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/04-vsm-system-2.md), [03-vsm-system-1](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/03-vsm-system-1.md).

---

### P3 — Capability Owners as System 3 Internal Control

**When to use:** When establishing accountability for capability areas in a multi-domain architecture; when diagnosing why decisions about cross-context data flow or shared resources stall; when designing the architecture review process for a delivery programme.

**The VSM insight:**

S3 is the "inside and now" function: it allocates resources across S1 units, negotiates accountability, sets policy within which S1 units operate autonomously, and optimises the whole — not individual units. In software architecture, S3 maps to the capability owner or domain architect role: the person or group responsible for the coherence of a capability area across multiple services, ensuring that the S1 bounded contexts within that area are not individually optimising in ways that produce system-level dysfunction.

The critical S3 failure mode in architecture is the collapse of S3 into S1 — when the capability owner starts making implementation decisions inside bounded contexts rather than setting the policy within which those contexts make their own decisions. This is micromanagement at the architecture level: it eliminates context autonomy, creates a decision bottleneck, and breaks the recursion principle.

**Mechanic:**

Define S3-level decisions and S1-level decisions explicitly:

| S3 Decision (Capability Owner) | S1 Decision (Context Team) |
|-------------------------------|---------------------------|
| Which contexts own which aggregates | How the aggregate is modelled internally |
| API contract style (REST, gRPC, event) between contexts | Internal data representation and schema |
| Shared non-functional requirements (SLA, data residency, auth model) | How NFRs are implemented inside the context |
| Integration pattern for new context boundary (e.g., anti-corruption layer) | How the ACL is implemented internally |
| Whether a new capability belongs in an existing or new context | How the new capability is decomposed within the owning context |

S3 also owns the audit channel (S3*): the capability owner should periodically inspect actual architectural state directly — not through the filtered reports of sprint reviews and architecture diagrams — to verify that policy is being followed and that reported reality matches actual system behaviour.

**Domain example:**

A retail platform has a Merchandising capability area containing three bounded contexts: Catalogue, Pricing, and Promotions. The Merchandising capability owner (S3) sets the policy: all three contexts expose their primary aggregates through versioned REST APIs, changes to the shared `product-id` namespace require capability-owner review, and no context may write directly to another context's data store. Within that policy, each team decides its own internal schema, deployment cadence, and tooling. The capability owner performs a quarterly S3* audit: reading a sample of actual API contracts as deployed, not as documented, and comparing them to the registered API catalogue. Drift between documented and actual contracts is the most common finding.

**Breaks when:** The capability area spans genuinely independent value streams with no shared data or coordination requirements — in that case, separate S3 roles are appropriate, not a single capability owner trying to govern unrelated contexts from a single vantage point.

**Canonical primitives:** [05-vsm-system-3](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/05-vsm-system-3.md), [06-vsm-system-3-star](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/06-vsm-system-3-star.md).

---

### P4 — Architecture Forum as System 4 Intelligence

**When to use:** When establishing or redesigning an architecture review board (ARB) or architecture forum; when diagnosing why architecture decisions consistently lag behind technology change; when the strategy-execution gap in an architecture organisation manifests as a backlog of unanswered design questions.

**The VSM insight:**

S4 is the "outside and future" function: it scans the external environment, models what the system needs to become, and translates intelligence into adaptation signals for S3 and S5. In software architecture, the architecture forum or ARB functions as S4 when it is scanning the technology and regulatory landscape, modelling the future-state architecture, and translating that intelligence into concrete guidance for capability owners (S3) and architectural principles (S5).

The S3/S4 homeostat is the most important coupling in the enterprise architecture model. If the architecture forum is disconnected from capability owners — producing strategy documents that never influence delivery — the S3/S4 interface is broken. If the architecture forum is consumed by S3 firefighting — reviewing every design decision at the sprint level — S4 has been absorbed into operations and there is no one scanning the future.

**Mechanic:**

Calibrate the forum's horizon to the rate of environmental change in the organisation's technology landscape:

| Horizon | Forum cadence | Typical agenda |
|---------|---------------|----------------|
| Short (0–3 months) | S3 concern — not the forum's primary role | Design reviews for in-flight delivery |
| Medium (3–18 months) | Monthly forum session | Technology deprecation, platform migration options, emerging patterns |
| Long (18 months+) | Quarterly strategy session | Buy/build/partner decisions, architectural north-star evolution, regulatory horizon |

The forum produces two types of output: **signals to S3** (specific guidance for capability owners facing near-term decisions — "use the new identity platform for all new context authentication, don't build a new one") and **inputs to S5** (questions that challenge architectural identity — "if we standardise on a cloud-native event mesh, does that change our position on vendor lock-in?").

**Domain example:**

A global logistics platform has an Architecture Forum (S4) that runs a monthly session. In a given month, S4's environmental scan surfaces three signals: (1) the existing API gateway vendor is ending support for their on-premises offering in 14 months; (2) a new open-source alternative has reached production maturity; (3) a draft EU regulation requires data-residency controls that the current gateway cannot enforce. S4 translates these into a signal to S3 (capability owners): "no new integrations should be built on the current gateway; all capability owners should plan for migration within 12 months." S4 also sends an input to S5: "the data-residency requirement may conflict with our current 'single global platform' architectural principle — this is an identity question, not an implementation question." S5 then revises the principle to: "single global platform where permitted by data sovereignty; regionally segmented where required by law."

**Breaks when:** The forum has no feedback channel from S3 about which decisions are actually being made in delivery — S4 is scanning the future on the basis of an outdated model of the present. Fix: require every capability owner to bring one near-term decision to each forum session; S4 uses the collection of these decisions as its ground-truth model of current operational state.

**Canonical primitives:** [07-vsm-system-4](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/07-vsm-system-4.md), [05-vsm-system-3](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/05-vsm-system-3.md).

---

### P5 — Principles and North Star as System 5 Identity

**When to use:** When defining architectural principles for a programme or enterprise; when diagnosing recurring conflicts between teams about which architectural direction to follow; when two architectural decisions contradict each other and there is no shared frame for resolving the contradiction.

**The VSM insight:**

S5 provides closure: the system's sense of itself as a whole — what it is, what it stands for, and what it will not compromise on. Architectural principles are S5 artefacts. They are not implementation guidelines (those are S3 policy). They are identity statements that resolve conflicts between operations (S3) and strategy (S4) in the light of what the architecture fundamentally is.

Good S5 architectural principles have three properties: they resolve real conflicts (a principle that does not give a clear answer to a specific architectural decision is not a principle — it is a slogan), they are stated at the level of the whole system (not at the level of a single context or capability), and they change rarely (principles that change with every delivery cycle are S3 policy, not S5 identity).

**Mechanic:**

Test each candidate principle against a real S3/S4 conflict:

```
Conflict:  S3 (capability owner): "The fastest path to delivery is reusing
           the existing Oracle database schema for the new Fulfilment context."
           S4 (architecture forum): "The target architecture eliminates shared
           databases between contexts by 2027."

Principle candidate: "Bounded contexts own their data exclusively."

Test: Does the principle give a clear answer?
Yes: the principle rejects the reuse of the shared schema, even at cost to delivery speed.
The principle is S5-quality — it resolves the conflict definitively.

Principle candidate: "We prefer modern technology choices where possible."
Test: Does the principle give a clear answer?
No: "possible" and "modern" are undefined. This is a slogan, not a principle.
```

The north-star architecture — the long-horizon target state — is also an S5 artefact. It defines what the system is becoming, not just what it currently is. It should be stable enough that S3 and S4 can make decisions in its light without needing to re-negotiate the destination at every quarterly planning cycle.

**Domain example:**

A healthcare platform has three S5 architectural principles: (1) "Patient data is never copied outside the context that is its system of record — it is referenced, not replicated." (2) "Every context must be deployable and rollbackable independently." (3) "No shared database between contexts, regardless of delivery cost or timeline." When a delivery team proposes a shared read-replica between the Patient Record and Appointment contexts for performance reasons, principle (1) and (3) give a clear answer: no. The team is directed to implement an explicit Appointment context read model populated by events from the Patient Record context — a higher-cost but architecturally consistent path. The principle resolves the conflict without requiring S4 or S3 intervention.

**Breaks when:** Principles are added to resolve a single short-term conflict and never revisited — the list accumulates contradictory or redundant principles until no conflict can be resolved cleanly. Audit S5 principles annually: each principle must resolve at least one real conflict that occurred in the past year; remove principles that pass no real test.

**Canonical primitives:** [08-vsm-system-5](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/08-vsm-system-5.md), [07-vsm-system-4](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/07-vsm-system-4.md).

---

### P6 — Recursive Architecture Across Enterprise, Domain, and Service

**When to use:** When a governance model designed for one level of the architecture is being applied incorrectly at another level; when diagnosing why architecture decisions made at the enterprise level keep conflicting with decisions made at the service level; when designing multi-level architecture governance for a large programme.

**The VSM insight:**

Every viable system is composed of S1 units that are themselves viable systems. The same VSM structure — S1 through S5 — applies at every level of recursion. The recursion principle has a direct implication for software architecture: the governance mechanisms, boundary types, and decision rights that apply at the enterprise level are not the same as those at the domain level or the service level. Applying enterprise-level governance tools directly to service-level decisions is a category error that produces over-governed services, under-governed domains, and a single architecture review bottleneck that cannot scale.

**Three recursion levels for a large software organisation:**

**Level 1 — Enterprise Architecture (system-in-focus: the enterprise)**

- S5: Technology principles, vendor policy, data sovereignty rules, security baselines.
- S4: Enterprise Architecture Forum — technology horizon, platform strategy, regulatory landscape.
- S3: Chief Architect / Architecture Governance — allocation of shared platform investment, boundary policy between domains.
- S2: Enterprise Integration Platform — cross-domain routing, shared identity, API gateway.
- S1 units: Domain capabilities (Commerce, Logistics, Fulfilment, Customer, Finance).

**Level 2 — Domain Architecture (system-in-focus: a domain, e.g., Commerce)**

- S5: Domain principles — e.g., "Commerce owns the order lifecycle end-to-end."
- S4: Domain Architecture Review — technology choices within Commerce, migration roadmap within the domain.
- S3: Domain Architect / Capability Owner — API contract policy, shared-data model governance within the domain.
- S2: Domain event bus or internal API gateway — coordination between Commerce bounded contexts.
- S1 units: Bounded contexts (Order, Pricing, Catalogue, Promotions).

**Level 3 — Service Architecture (system-in-focus: a bounded context, e.g., Pricing)**

- S5: Context charter — what Pricing owns, its quality contract, its system-of-record responsibility.
- S4: Tech lead environment scan — new pricing model capabilities, upstream data feed changes.
- S3: Tech lead / team lead — sprint-level resource allocation, internal design decisions.
- S2: Internal service coordination — event sourcing, CQRS read-model refresh, internal async channels.
- S1 units: Individual deployable services or modules within the context.

**The recursion check:** Enterprise S5 principles must not specify internal service design (that is Level 3 S1 autonomy). Domain S3 decisions must not require enterprise-level S5 sign-off (that is recursion confusion). Service teams must not escalate to the Enterprise Architecture Forum for decisions that belong to Domain Architecture (that is missing recursion level).

**Canonical primitives:** [09-recursion-levels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/09-recursion-levels.md), [08-vsm-system-5](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/08-vsm-system-5.md).

---

### P7 — Requisite Variety in API Design

**When to use:** When designing API contracts for a bounded context that faces a complex or variable input space; when diagnosing why an existing API is either too brittle (breaking on legitimate inputs) or too permissive (accepting inputs the context cannot actually handle); when evaluating whether an API design will survive the full range of conditions its consumers will generate.

**The VSM insight:**

Ashby's Law (primitive 02) states: only variety can absorb variety. An API contract is a regulator. Its job is to absorb the variety of requests that the environment (consumers) generates and produce controlled, valid responses. If the API's variety — the number of valid input combinations it can handle — is lower than the variety of the environment it faces, the API will fail on legitimate inputs. If the API's variety is higher than necessary, the contract is overengineered and the implementation carries unnecessary complexity.

**Variety audit for API design:**

```
V(environment) = all distinct request states consumers legitimately need to express
V(regulator)   = all distinct request states the API contract accepts and handles
Variety gap    = V(environment) − V(regulator)

If gap > 0: the API is under-specified — consumers cannot express legitimate needs.
If gap < 0: the API is over-specified — complexity beyond the environment's actual needs.
```

**Mechanic:**

1. **Enumerate the environment's variety.** List all the distinct input conditions that legitimate consumers will generate. Not just the happy path — include: optional fields, polymorphic input types, partial updates, bulk requests, idempotency requirements, multi-tenancy variants, locale and currency dimensions, and any time-variant state (e.g., requests before and after a lifecycle transition).

2. **Map the API contract against the inventory.** For each input condition, verify the API can express and handle it. Common gaps: an API that accepts a single `amount` field cannot express currency — consumers in multi-currency environments have no way to route a EUR payment differently from a GBP payment. An API that requires all fields on a PATCH request cannot support partial update — consumers must send a full resource to change one field, introducing race conditions.

3. **Apply variety attenuation where possible.** Not every input dimension needs to be absorbed by the API contract. Some can be attenuated by convention (a service that operates in a single currency does not need a currency field), by upstream filtering (the API gateway enforces locale normalisation before the request reaches the context), or by default values that collapse a dimension to a single state for the common case.

4. **Design amplifiers for low-frequency edge cases.** High-variety edge cases that occur rarely can be absorbed by an escape hatch: a generic `metadata` field, an extended-attributes endpoint, or a formal extension point in the schema. The core contract remains simple; edge cases do not degrade the common-case interface.

**Domain example:**

An Order Management API is being designed. The environment variety audit finds: 12 supported currencies, 3 fulfilment modes (standard, express, click-and-collect), 6 payment methods, 4 order lifecycle states, 2 customer types (B2C, B2B), and partial-update requirements for at least 5 fields. A first-draft API that accepts a flat JSON body with no currency field, no fulfilment mode enum, and no lifecycle-state machine has a variety gap of approximately `12 × 3 × 6 × 4 × 2 = 1,728` distinct legitimate order states — none of which the API can distinguish. Fix: model currency, fulfilment mode, payment method, lifecycle state, and customer type as first-class discriminated fields. Apply attenuation: restrict currency to the 3 that >95% of orders use; expose the remaining 9 through an `extended-currency` extension endpoint. The core contract handles `3 × 3 × 3 × 4 × 2 = 216` common states; the extension handles the long tail without polluting the common-case contract.

**Breaks when:** The environment variety is genuinely unbounded (e.g., a generic data ingestion API with unknown upstream schema). In those cases, variety attenuation must be applied at the gateway level (schema validation, normalisation) before the request reaches the context, or the context must be designed as a variety amplifier (schema registry, late binding) with explicit trade-offs on the loss of static contract guarantees.

**Canonical primitives:** [02-ashbys-law](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md), [10-variety-engineering](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/10-variety-engineering.md).

---

### P8 — Algedonic Channels in Enterprise Architecture Review

**When to use:** When architecture drift, compliance failures, or data-privacy red flags are consistently discovered late — in production incidents, audit findings, or regulatory reviews; when the normal architecture governance process (forum review, design sign-off, ADR catalogue) has too long a feedback delay to catch high-severity decisions before they are irreversible; when designing the escalation path for architecture decisions that cross S5 constraints.

**The VSM insight:**

In a normally functioning architecture governance model, design decisions flow upward through the hierarchy: team → capability owner (S3) → architecture forum (S4) → principles (S5). This is efficient for routine decisions. But it introduces delay and the risk that high-severity signals — a design that embeds a GDPR violation, a decision that creates unresolvable data coupling between domains, a technology choice that violates a security baseline — are absorbed by lower-level filters before reaching the authority that can act on them.

Algedonic channels bypass this hierarchy. When triggered, they deliver a direct signal to S5 (or the highest appropriate governance authority) with no intermediate filtering, and with a defined response window.

**Mechanic — designing an architecture algedonic channel:**

Define the trigger, bypass route, signal content, response window, and post-event review for each class of architectural red flag:

| Red Flag Class | Trigger Condition | Bypass Route | Response Window |
|----------------|-------------------|--------------|-----------------|
| Data privacy violation | Design proposes moving personal data outside the declared data-residency boundary, or cross-context personal data sharing without explicit DPA | Direct alert to Data Protection Officer and Chief Architect | 24 hours |
| Security baseline breach | Design uses an unapproved authentication mechanism, exposes data without encryption at rest, or introduces a new trust boundary without security review | Direct alert to Security Architect and CISO | 24 hours |
| Architectural principle violation | Design directly contradicts an S5 architectural principle (e.g., proposes a shared database between two bounded contexts) | Direct notification to Chief Architect and relevant Domain Architect | 48 hours |
| Irreversible data model change | Design proposes a schema migration that cannot be rolled back or that modifies a shared canonical model | Mandatory pre-implementation review with capability owner and architecture forum representative | 72 hours |

**The algedonic trigger must be embedded in the delivery process**, not left as a voluntary escalation. Common embedding points: architecture decision record (ADR) template includes a red-flag checklist; code review policy requires explicit sign-off for API changes that cross context boundaries; CI pipeline includes a schema-change classifier that triggers the irreversible-data-model channel automatically.

**Domain example:**

A logistics platform has a data privacy algedonic channel triggered by any design that routes customer location data to a context outside the Customer domain. The channel fires automatically when a proposed data flow diagram includes a `customer_location` field flowing to the Route Optimisation context (an Operations domain context). The signal reaches the Data Protection Officer and Chief Architect within 30 minutes of the design being submitted — before any implementation begins. The DPO determines that the data transfer is lawful under a legitimate interest basis but requires a data minimisation step (coordinate precision reduced from GPS to 1km grid). The design is updated before any code is written. Without the algedonic channel, this transfer would have been discovered in a GDPR audit 18 months later, requiring a full data-flow remediation.

**Breaks when:** The algedonic channel is triggered too frequently — if every routine architectural decision fires the channel, S5 authority is overwhelmed and the channel loses its urgency signal. Calibrate the threshold: only genuine S5-level violations (principle breaches, compliance risks, irreversible decisions) should fire the channel. S3-level architectural policy violations (e.g., using a deprecated library version) belong in the capability owner review, not the algedonic channel.

**Canonical primitives:** [11-algedonic-channels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/11-algedonic-channels.md), [01-feedback-loops](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/01-feedback-loops.md), [08-vsm-system-5](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/08-vsm-system-5.md).

---

## Anti-Pattern Catalog

### AP1 — Dictator Architecture: S5 Collapse onto S1

**VSM diagnosis:** S5 (architectural principles, north star) has collapsed downward and is directly governing S1 operational units (bounded contexts, services). Instead of setting non-negotiable identity constraints within which S3 and S4 operate with autonomy, the architecture function is making implementation decisions inside contexts — selecting frameworks, approving data models, reviewing schema changes — at a level of detail that belongs to the context teams.

**How it shows up:** Every non-trivial design decision in a bounded context requires approval from a central architecture group. Architecture review meetings are heavily attended and produce queues. Context teams wait weeks for design sign-off on decisions that affect only their own service internals. Delivery slows not because of technical complexity but because of governance bottleneck. The architecture group is simultaneously over-extended (too many decisions) and under-informed (decisions are taken out of context, too far from implementation reality).

**Why it persists:** In many organisations, architecture authority is vested in a senior individual or small group whose legitimacy depends on being the decision-maker. Delegating decisions feels like losing authority. The group rationalises the bottleneck by noting that "quality would decline without oversight" — but this confuses S5 identity constraints with S3 policy prescriptions with S1 execution decisions.

**The recursion violation:** S5 should set identity constraints that apply to the enterprise architecture as a whole. S3 (capability owners) should set policy for their capability area. S1 teams should have full autonomy within that policy. When S5 directly governs S1, the intermediate levels (S3, S4) are bypassed and the recursion model collapses. Bounded contexts cannot be viable sub-systems if they have no self-management capacity.

**Fix:**

1. Audit every decision the architecture group makes in a month. Classify each as: S5 (identity/principle), S3 (capability policy), or S1 (implementation). Anything classified as S1 should be returned to the context team with a policy statement, not a decision.
2. Rewrite architectural oversight as policy-setting plus audit (S3*), not as decision-making.
3. Define the algedonic channel (P8) so that genuine S5-level violations still reach central authority — without routing every S3 and S1 decision through the same channel.

**Primitive cross-references:** [08-vsm-system-5](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/08-vsm-system-5.md), [05-vsm-system-3](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/05-vsm-system-3.md), [09-recursion-levels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/09-recursion-levels.md).

---

### AP2 — Absent Coordination Layer: Integration Platform Managed as S3 Command

**VSM diagnosis:** The S2 coordination layer (integration platform, event bus, API gateway) is being managed as an S3 command channel — changes to integration contracts require centralised approval, the platform team makes routing decisions that encode business rules, or the integration platform has become the de-facto owner of cross-domain business logic.

**How it shows up:** Adding a new event consumer requires a change request to the integration platform team. The event bus configuration contains filtering logic that determines which downstream contexts receive which events based on business criteria. Cross-domain workflow state is managed in the integration layer's database. The integration platform team has become a bottleneck for every cross-context interaction — they are doing S3 work (governing business logic) dressed up as S2 work (coordination infrastructure).

**Why it persists:** In large organisations, a centralised integration team often has cross-cutting visibility that no individual context team has. This visibility is genuinely valuable — but it should be used to provide S2 coordination signals (event routing, schema governance, delivery guarantees), not to make S3 business logic decisions. The centralised team gradually accumulates business logic because it is in the right position to see cross-domain conflicts — but that visibility should translate into escalation to S3 capability owners, not direct implementation of business rules in the platform layer.

**Fix:** Apply the S2 test from P2. Extract all business logic from the integration platform into the bounded contexts that own the relevant aggregates. If logic belongs to no single context, create an explicit orchestration context as an S1 unit with a clear system-of-record responsibility — do not leave it as implicit logic in the infrastructure layer.

**Primitive cross-references:** [04-vsm-system-2](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/04-vsm-system-2.md), [03-vsm-system-1](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/03-vsm-system-1.md), [05-vsm-system-3](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/05-vsm-system-3.md).

---

### AP3 — Variety Mismatch: Thin API Facing a Wide Environment

**VSM diagnosis:** Ashby's Law violation. The API contract (regulator) has lower variety than the environment it faces (disturbances from consumers). The regulator cannot absorb the legitimate input variety the environment generates, resulting in errors, workarounds, or consumer-side hacks that grow over time.

**How it shows up:** Consumers are sending data in the `description` or `metadata` fields of a generic API because there is no typed field for what they need to express. Multi-currency support is implemented by consumers prefixing amounts with a currency code string because the API has no currency dimension. B2B and B2C order flows are indistinguishable in the API, so downstream contexts use fragile heuristics (order amount, field presence) to distinguish them. The API changelog is dominated by breaking changes required to retrofit variety that should have been in the original contract.

**Why it persists:** API design commonly proceeds from the happy path — the most common consumer need in the most common scenario. Edge cases and low-frequency input dimensions are deferred. Deferred variety accumulates as a debt that compounds: every consumer that implements a workaround for a missing variety dimension creates a new implicit protocol that the API must never break, even after the proper field is added.

**Fix:** Apply the variety audit from P7 before the API is published. Enumerate the environment's full input variety — not just the happy path. Apply attenuation to reduce the contract surface to the variety that the context can actually handle, with explicit extension points for the long tail. Test the contract against at least three real consumer use cases before publication; if all three fit comfortably into the same request shape, the variety is likely under-audited.

**Primitive cross-references:** [02-ashbys-law](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md), [10-variety-engineering](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/10-variety-engineering.md).

---

### AP4 — Architecture Forum with No S3 Ground Truth (Missing S3*)

**VSM diagnosis:** The architecture forum (S4) is producing strategy and guidance on the basis of an outdated model of the current operational state. Without a direct audit channel (S3*) from S4 to the actual state of deployed systems, the forum's environmental model is filtered through capability owner reports, architecture diagrams that may not match reality, and quarterly planning documents that lag the delivery cadence by weeks.

**How it shows up:** The architecture forum produces a technology radar or target-state diagram that is inconsistent with the actual systems running in production. Guidance issued by the forum references capabilities that have already been superseded by delivery teams making pragmatic choices in the field. Forum members are surprised by architectural decisions that teams made months ago. The forum's S3/S4 interface is weak — capability owners receive guidance that does not reflect their actual constraints, and the forum receives status reports that obscure the real state of the architecture.

**Why it persists:** Architecture forums typically receive information through formal channels: architecture decision records (when they are written), quarterly architecture reviews, and project status updates. These channels apply heavy attenuation — only the decisions that teams consider significant enough to document reach the forum. Routine decisions, deferred decisions, and workarounds are rarely documented. The forum's model of current state is a curated subset of reality.

**Fix:** Introduce a direct S3* audit channel for the architecture forum: quarterly spot-checks of actual deployed architecture (run against the real infrastructure, not the documentation), sampled ADR reviews, and direct conversations with context teams that bypass the capability-owner filter. The audit is not punitive — it is a calibration mechanism that ensures the forum's environmental model stays grounded in operational reality.

**Primitive cross-references:** [06-vsm-system-3-star](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/06-vsm-system-3-star.md), [07-vsm-system-4](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/07-vsm-system-4.md), [01-feedback-loops](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/01-feedback-loops.md).

---

## Recipes

### R1 — VSM Boundary Mapping for a New Domain Capability

**Objective:** Produce a VSM-grounded capability boundary definition for a new domain being added to an existing architecture. The output is a boundary map with explicit S1–S5 assignments at the domain recursion level and a set of S2 coordination decisions for the integration layer.

**Step 1 — Assign the recursion level**

Confirm the level at which the VSM is being applied. For a new domain capability, this is typically Level 2 (domain architecture). The parent level (Level 1, enterprise) provides the S5 constraints and S2 integration platform that the new domain must respect. The child level (Level 3, service architecture) is left to the domain's own bounded contexts.
→ verify: the enterprise S5 principles, integration platform standards, and cross-domain data model constraints are documented and current. If they are not, surface this as a gap before proceeding — designing a domain boundary against an unknown enterprise constraint produces rework.

**Step 2 — Define the domain's S1 bounded contexts**

For each candidate bounded context within the new domain, complete the S1 checklist (from P1):

```
Context name:
Primary value produced:
Local environment (external inputs consumed directly):
System-of-record aggregate(s):
Autonomy test (decisions the team makes without cross-context approval):
S3 policy boundary (decisions that require capability-owner involvement):
```

Boundary conflicts surface here: if two candidate contexts share a system-of-record aggregate, they either belong in the same context or the aggregate must be split with explicit ownership assignment.
→ verify: no two contexts claim ownership of the same aggregate. Every aggregate has exactly one owning context.

**Step 3 — Define the domain's S3 (capability owner) decisions**

List the decisions that belong at the domain S3 level — above individual contexts but below the enterprise S4/S5:

- API contract style between contexts within the domain.
- Event schema ownership and versioning policy.
- Shared non-functional requirements within the domain.
- Data model governance for the domain's canonical entities.
- Integration pattern for the domain's interface with external domains (anti-corruption layer, open-host service, shared kernel — see `references/integration-and-boundary-patterns.md`).

→ verify: every S3 decision listed can be made by the capability owner without escalating to the enterprise architecture forum. If a decision requires enterprise-level sign-off, it belongs at Level 1, not Level 2.

**Step 4 — Define the domain's S2 coordination layer**

Identify which coordination signals the domain needs from the enterprise integration platform (Level 1 S2) and which coordination signals are internal to the domain (Level 2 S2):

| Coordination need | Level 1 S2 (enterprise) or Level 2 S2 (domain)? |
|-------------------|-------------------------------------------------|
| Cross-domain event routing | Level 1 — enterprise integration platform |
| Intra-domain event sequencing | Level 2 — domain-internal event bus or async channel |
| Cross-domain API gateway | Level 1 — enterprise API gateway |
| Intra-domain service discovery | Level 2 — domain-internal service mesh or registry |

→ verify: no S2 signal at Level 2 requires a change to the Level 1 enterprise integration platform. If it does, the cross-domain coordination requirement belongs in the enterprise S3 (Chief Architect) decision, not in the new domain design.

**Step 5 — Check the algedonic triggers**

Run the new domain boundary design through the algedonic checklist (P8):

- Does any data flow in the design move personal data outside the declared data-residency boundary?
- Does any context boundary violate an existing S5 architectural principle (e.g., shared database, cross-context synchronous dependency that creates coupling)?
- Does the domain introduce a new trust boundary that requires security review?
- Does the domain's integration pattern create an irreversible data model dependency on another domain?

If any trigger fires, escalate before delivery begins — not during implementation.
→ verify: all algedonic checklist items are marked clear or escalated. No item is marked "to be resolved in delivery."

**Canonical primitives used:** #03 (S1 boundary definition), #04 (S2 coordination layer), #05 (S3 capability owner decisions), #09 (recursion level assignment), #11 (algedonic checklist).

---

### R2 — Designing Algedonic Architecture Review for Compliance and Data Privacy Risk

**Objective:** Design and embed an algedonic channel for architecture decisions that carry data privacy or compliance risk, so that red-flag signals reach the appropriate authority before implementation — not after an audit finding.

**Step 1 — Define the trigger inventory**

List all classes of architectural decision that, if implemented without review, could produce a compliance or data-privacy violation in the current regulatory context. For a UK-regulated platform, the relevant frameworks include ICO guidance under UK GDPR, CMA market guidance for platform operators, and FCA rules if financial data is involved:

| Trigger class | Example condition | Severity |
|---------------|-------------------|----------|
| Personal data cross-context transfer | A bounded context begins receiving fields that constitute personal data from another context | High — algedonic |
| New data retention period | A context introduces a new data store with no defined retention and deletion policy | High — algedonic |
| Third-party data processor | A design introduces a new SaaS or cloud service that processes personal data | High — algedonic |
| Profiling or automated decision | A design implements an automated decision-making feature with legal or significant effects on individuals | Critical — algedonic plus DPIA |
| Security control bypass | A design proposes disabling or weakening an existing security control for performance or delivery reasons | High — algedonic |
| Cross-border data transfer | A design transfers personal data to a system hosted outside the UK or EU without an adequacy decision or SCCs | Critical — algedonic plus legal review |

→ verify: the trigger inventory is reviewed with the Data Protection Officer and Legal. Triggers not on this list that they know from past audits should be added. The inventory is a living document — add to it after every incident where a design produced a compliance finding that was not caught by an existing trigger.

**Step 2 — Embed the trigger in the delivery process**

The algedonic channel fires only if the trigger is encountered during design review. Embedding points:

- **Architecture Decision Record (ADR) template:** add a mandatory "compliance and data privacy checklist" section. Every ADR that involves a new data flow, a new integration, or a new data store must complete the checklist. A "yes" on any checklist item triggers the algedonic channel.
- **Pull request policy:** changes to API contracts or data schemas in a context that handles personal data require a reviewer with architecture authority. Automated tooling flags API fields that match the personal data taxonomy (name, email, IP address, location, device ID).
- **Design review agenda:** for any design review that involves cross-context data flow, the facilitator runs the algedonic checklist before closing the session.

→ verify: run the embedding against three recent design decisions — one that should have triggered the channel and two that should not. Confirm the embedding catches the trigger and does not produce false positives on the non-trigger cases.

**Step 3 — Define the bypass route and response window**

For each severity level, define who receives the signal, through what channel, and within what response window:

| Severity | Recipients | Channel | Response window |
|----------|-----------|---------|-----------------|
| High | Data Protection Officer + Chief Architect | Direct message (Slack/email) with design artefact attached | 24 hours to acknowledge; 72 hours to decision |
| Critical | DPO + Chief Architect + Legal + CISO | Dedicated escalation channel (e.g., `#arch-algedonic`) | 4 hours to acknowledge; 24 hours to decision |

The signal content must include: what decision triggered the channel, what the design proposes to do with the data, which regulatory framework applies, and a link to the relevant design artefact (ADR, design document, PR).

→ verify: the bypass route is tested quarterly with a synthetic trigger — a design decision that clearly fires an algedonic condition, submitted through the normal process to confirm the channel fires correctly and reaches the right recipients within the response window.

**Step 4 — Post-event review**

After every algedonic activation:

- Record the trigger, the decision reached, and the resolution (design modified, design approved with compensating controls, design rejected).
- Review whether the trigger threshold is calibrated correctly: if the channel fires on routine decisions, the threshold is too low; if a compliance finding is discovered post-implementation that should have fired the channel, the threshold is too high or the trigger is not embedded in the right process step.
- Update the trigger inventory if the activation revealed a new risk class not previously covered.

→ verify: a post-event review document exists for every algedonic activation in the last 12 months. If no activations have occurred, either the architecture is genuinely clean (confirm with a manual audit) or the channel is not embedded correctly (test it).

**Canonical primitives used:** #11 (algedonic channel design), #01 (feedback loop for trigger calibration), #08 (S5 policy as the frame within which the channel operates).

---

### R3 — Recursive Decomposition: Enterprise to Service Level

**Objective:** Apply the VSM recursion model to decompose an enterprise architecture governance problem into the correct three levels, assign S1–S5 roles at each level, and verify that decisions are made at the right level — not escalated upward or imposed downward.

**Step 1 — Define the system-in-focus and its context**

State the recursion level explicitly before any other design work:

```
System-in-focus: [name the system being designed or diagnosed]
Parent system: [the viable system that contains the system-in-focus as an S1 unit]
Child systems: [the viable systems that are S1 units within the system-in-focus]
Current problem: [what decision or failure is being addressed at this level]
```

If the current problem is: "the Architecture Forum is producing guidance that teams are not following," the system-in-focus is the enterprise architecture governance system (Level 1). The parent system is the organisation as a whole. The child systems are the domain capability areas. Do not try to fix this problem by redesigning service-level governance — the recursion level is wrong.

→ verify: the system-in-focus definition can be stated in one sentence without ambiguity. If it takes more than one sentence, the recursion level is not cleanly defined.

**Step 2 — Assign S1–S5 roles at the system-in-focus level**

Complete the VSM role assignment table for the chosen level:

| VSM Role | Name / Function | Key outputs | Key inputs |
|----------|----------------|-------------|------------|
| S5 | [identity, principles, non-negotiables] | Architectural principles, north-star direction, principle conflict resolutions | S3/S4 conflicts, algedonic signals, stakeholder expectations |
| S4 | [environment scanning, future modelling] | Technology radar, adaptation proposals, signals to S3 | External technology signals, regulatory changes, S3 operational model |
| S3 | [internal control, resource allocation, policy] | Capability boundary policy, resource allocation, accountability agreements | S1 performance reports, S5 constraints, S4 intelligence |
| S3* | [audit channel] | Direct operational reality check | S3 audit triggers, anomaly signals |
| S2 | [coordination, anti-oscillation] | Routing signals, shared protocols, conflict-avoidance mechanisms | S1 unit schedules, resource claims, conflict reports |
| S1 | [operational units] | Primary value, operational state reports | Resource allocation, policy constraints, S2 coordination signals |

→ verify: each role has a named individual or group responsible for it. If a role is unoccupied, this is the most important design finding — not an implementation detail. An unoccupied S4 means no one is scanning the architectural future. An unoccupied S5 means conflicts are resolved by whoever shouts loudest.

**Step 3 — Apply the recursion interference check**

For each decision currently being made in the organisation, assign it to the correct VSM level and role:

| Decision | Current level | Correct level | Interference type |
|----------|--------------|---------------|-------------------|
| Which framework to use inside a bounded context | Enterprise S5 | Service S1 | S5 imposing on S1 — recursion collapse |
| API contract style within a domain | Enterprise S5 | Domain S3 | S5 imposing on S3 — over-centralisation |
| Cross-domain data sovereignty policy | Domain S3 | Enterprise S5 | S3 usurping S5 — identity fragmentation |
| Technology vendor selection for a platform | Service S1 | Enterprise S4/S3 | S1 making cross-level decisions without S4 intelligence |

For each interference found, define the correction: return the decision to its correct level, ensure the correct level has the information and authority needed to make it, and verify the feedback loop that would have surfaced the interference earlier is in place.

→ verify: after correction, each identified decision is being made at its assigned level without requiring escalation or cross-level override.

**Step 4 — Verify the feedback loops at each level**

For each level, confirm the balancing feedback loops exist:

| Level | Feedback loop | Current state | Gap |
|-------|--------------|---------------|-----|
| Enterprise (Level 1) | Architecture forum receives ground-truth operational state from capability owners | Annual review only | Increase to quarterly; add S3* spot-checks |
| Domain (Level 2) | Capability owner reviews API contract compliance against deployed state | No regular audit | Add quarterly S3* audit of actual contracts |
| Service (Level 3) | Context team detects and responds to SLA breaches, dependency failures, and schema drift | Automated — alerting in place | None identified |

Feedback loops with delays longer than the system's rate of change will fail to regulate — architectural drift accumulates between feedback cycles. If the enterprise-level feedback loop runs annually but the delivery cadence is fortnightly, the loop cannot catch drift in time to prevent accumulation.

**Canonical primitives used:** #09 (recursion levels), #01 (feedback loops), #05 (S3 role assignment), #07 (S4 role assignment), #08 (S5 role assignment), #06 (S3* audit channel), #04 (S2 coordination layer).

---

## Composition

The eight patterns and three recipes in this file compose naturally for a complete VSM-grounded solution architecture practice:

| Situation | Start with | Add |
|-----------|-----------|-----|
| New domain capability to design | R1 (VSM boundary mapping) | P7 (variety audit for the domain's external APIs) |
| Architecture governance failing to prevent drift | AP4 (missing S3* in the forum) + P4 (forum as S4) | R3 (recursion decomposition to find interference) |
| Compliance risk discovered late in delivery | R2 (algedonic channel design) | P8 (embed triggers at the right process step) |
| Central architecture becoming a bottleneck | AP1 (dictator architecture diagnosis) | R3 Step 3 (recursion interference check) |
| Integration platform accumulating business logic | AP2 (absent S2 coordination) + P2 (integration platform as S2) | R1 Step 4 (S2 coordination layer assignment) |
| API contract breaking on legitimate consumer inputs | AP3 (variety mismatch) + P7 (requisite variety audit) | R1 Step 2 (context boundary as S1 with variety-adequate API) |
| New programme needs architecture governance model | R3 (full recursion decomposition) | P5 (principles as S5) + P4 (forum as S4) + P3 (capability owners as S3) |
| Architecture principles not being followed | P5 (test principles against real conflicts) | AP1 (check for S5 collapse) + R2 Step 1 (algedonic triggers for principle violations) |

When combining primitives, the recommended sequence is: identify the recursion level (P6/R3) → assign S1–S5 roles → design the coordination layer (P2) → audit API variety (P7) → verify feedback loops at each level → embed algedonic channels for S5-level risks (R2/P8). Never design the integration layer before the bounded-context boundaries are defined; never define principles before the S3/S4 governance structure exists to act on them.

---

## Cross-References

**Foundation skill:** [../../foundations-cybernetics-vsm/SKILL.md](../../foundations-cybernetics-vsm/SKILL.md) — all 11 primitives; apply this file after loading the relevant primitives.

**Within this skill:**

- [solution-workflow.md](solution-workflow.md) — business-flow-first workflow; use before applying VSM boundary mapping (R1 is a VSM overlay on the workflow defined there).
- [integration-and-boundary-patterns.md](integration-and-boundary-patterns.md) — integration style decision matrix; use alongside P2 (integration platform as S2) to select the correct pattern for a given boundary.
- [transition-architecture.md](transition-architecture.md) — current, interim, and target-state planning; VSM recursion levels (P6) clarify which level of the architecture each transition wave is changing.

**Companion skills:**

- [../../software-architecture-design/SKILL.md](../../software-architecture-design/SKILL.md) — once VSM boundary mapping is complete and the solution shape is known, use this skill for runtime topology, distributed consistency, and service decomposition within a bounded context.
- [../../software-security-appsec/SKILL.md](../../software-security-appsec/SKILL.md) — algedonic triggers for security baseline breaches (R2) should be designed in conjunction with the security architecture skill.
- [../../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md) — feedback loop implementation at the service level (P1 primitive, R3 Step 4) depends on the observability and alerting infrastructure defined in the platform operations skill.
