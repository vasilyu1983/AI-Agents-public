---
title: "Cybernetics and VSM Applied to Software Solution Architecture: Bounded Contexts, Integration Platforms, and Enterprise Control"
skill: software-solution-architecture
foundation: foundations-cybernetics-vsm
last_updated: "2026-09-23"
last_verified: "2026-09-23"
status: stable
---

# Cybernetics and VSM Applied to Software Solution Architecture

> **Gate before invoking:** Check [`foundations-cybernetics-vsm` § When to Apply](../../foundations-cybernetics-vsm/SKILL.md#when-to-apply) first. If the foundation's skip conditions match, use the foundation it names instead.

This file is a link adapter. It maps VSM functions onto architecture roles: bounded contexts, integration platforms, capability owners, forums and principles. It keeps the architecture-specific tests and pitfalls. The theory lives in the foundation:

- Primitive definitions: [`primitives-overview.md`](../../foundations-cybernetics-vsm/references/primitives-overview.md) and the templates in [`assets/templates/cybernetics-vsm/`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/).
- Ashby's law and the coverage test: [`02-ashbys-law.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md) and [`response-coverage-audit.md`](../../foundations-cybernetics-vsm/references/response-coverage-audit.md).

Read [solution-workflow.md](solution-workflow.md) and [integration-and-boundary-patterns.md](integration-and-boundary-patterns.md) first. Come here to decide where a capability boundary goes, how control flows between the platform and its domains, and why governance keeps missing drift.

---

## Table of Contents

- [Architecture-to-VSM Map](#architecture-to-vsm-map)
- [Pattern Catalog](#pattern-catalog)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
- [Recipes](#recipes)
- [Composition](#composition)
- [Cross-References](#cross-references)

---

## Architecture-to-VSM Map

| VSM function | Architecture role | Primitive |
|---|---|---|
| S1 | Bounded context owning an aggregate and a business outcome | [03](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/03-vsm-system-1.md) |
| S2 | Integration platform: event bus, gateway, mesh, schema registry | [04](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/04-vsm-system-2.md) |
| S3 / S3* | Capability owner or domain architect; direct audit of deployed contracts | [05](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/05-vsm-system-3.md), [06](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/06-vsm-system-3-star.md) |
| S4 | Architecture forum: technology, vendor and regulatory horizon | [07](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/07-vsm-system-4.md) |
| S5 | Architectural principles and north-star target | [08](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/08-vsm-system-5.md) |
| Algedonic | Red-flag escalation for privacy, security and irreversible decisions | [11](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/11-algedonic-channels.md) |

---

## Pattern Catalog

### P1 — Bounded Context as System 1 Unit

| S1 property | Bounded-context question |
|---|---|
| Primary value | Which business outcome does this context own end to end? |
| Local environment | Which events, requests or feeds does it consume directly? |
| Autonomy within policy | Can the team make design and delivery decisions without cross-context approval? |
| System of record | Is there one source of truth for its core aggregate? |

A context that must escalate routine design decisions has one of three problems: the boundary straddles two owners, S3 policy prescribes *how* instead of *what*, or the team lacks the skills to use the autonomy it has. Example: in e-commerce, a Pricing context ships experiments freely unless they change its contract with Order Management.

**Breaks when** two capabilities share a transactional aggregate. Resolve the data model before drawing VSM boundaries.

### P2 — Integration Platform as System 2 Coordinator

| S2-appropriate | Not S2 (belongs in a context) |
|---|---|
| Route events by type | Choose consumers by business rules |
| Enforce schema contracts | Transform data to resolve domain-model conflicts |
| Throttle and retry delivery | Set retry policy by business criticality |
| Publish health signals | Hold state on whether a context should be active |
| Sequence events to avoid races | Orchestrate multi-step business workflows |

Logic that fails the test moves to the sending context, the receiving context, or an explicit orchestration context that is an S1 unit with its own system of record. For example, a customer-tier rule for choosing notification consumers belongs in Notification, not on the bus. Genuinely cross-cutting rules such as global rate limits or data-residency routing may live in the platform, but only when traceable to an S5 principle.

### P3 — Capability Owners as System 3 Internal Control

| S3 decision (capability owner) | S1 decision (context team) |
|---|---|
| Which context owns which aggregate | Internal aggregate model |
| Contract style between contexts | Internal schema |
| Shared NFRs (SLA, residency, auth) | How NFRs are met inside |
| Integration pattern at a new boundary (e.g., an anti-corruption layer) | How the ACL is built |
| Whether a capability goes in an existing or a new context | Decomposition inside the owner |

S3 also runs the S3* audit: read deployed API contracts, not the documented ones, and compare them with the catalogue. Drift between the two is the usual finding. Run the audit at an interval set by release rate and contract risk, and after major changes. **Breaks when** one owner is asked to govern independent value streams; give them separate S3s.

### P4 — Architecture Forum as System 4 Intelligence

The forum scans technology, vendors and regulation and sends two outputs: **signals to S3** ("no new integrations on the gateway being retired") and **inputs to S5** ("does a data-residency rule conflict with our single-global-platform principle?"). Short-horizon design review is S3 work. Set the forum's horizons and cadence by how fast its environment changes. The forum fails when it models the future from a stale picture of the present, so have each capability owner bring one current decision to every session as ground truth.

### P5 — Principles and North Star as System 5 Identity

A principle is S5-quality only if it settles a real S3/S4 conflict. "Bounded contexts own their data exclusively" settles "reuse the shared schema for speed?" with a no. "Prefer modern technology where possible" settles nothing, so it is a slogan. Principles are system-wide and change rarely; ones that change every cycle are S3 policy. Periodically retire any principle that resolved no real conflict since the last review.

### P6 — Recursion Across Enterprise, Domain, and Service

```text
L1 enterprise: S5 tech principles, residency, security baseline · S4 EA forum · S3 chief architect
               S2 enterprise integration platform · S1 domains
L2 domain:     S5 domain principles · S4 domain review · S3 capability owner
               S2 domain event bus / internal gateway · S1 bounded contexts
L3 context:    S5 context charter · S4 tech-lead scan · S3 team lead
               S2 internal async channels / CQRS refresh · S1 services or modules
```

Checks: enterprise S5 must not dictate internal service design; domain S3 decisions must not need enterprise S5 sign-off; services must not escalate domain-level decisions to the enterprise forum. Primitive: [`09-recursion-levels.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/09-recursion-levels.md).

### P7 — API Contract Coverage (Requisite Variety in API Design)

Do **not** compute `V(environment) − V(regulator)` or multiply field cardinalities into a "variety gap". Ashby's relation bounds residual outcome variety from below, in logarithmic units under his table conditions; products of enum sizes are not that quantity. Audit coverage of distinctions instead:

1. **List the distinctions consumers legitimately need to express:** currency, fulfilment mode, customer type (B2B/B2C), lifecycle state, partial update, idempotency, bulk, tenancy, locale. Include transitions such as requests made before and after a state change.
2. **For each distinction, check** that the contract can express it and that the context handles it correctly. For example, an `amount` with no currency cannot route EUR differently from GBP, and a PATCH that requires every field cannot do partial updates without races.
3. **Attenuate** dimensions the context does not need: a single-currency service needs no currency field; normalise locale at the gateway; use defaults for the common case.
4. **Amplify the long tail** with a typed extension point rather than widening the core contract.
5. **Test** against real consumer use cases before publishing. Consumers stuffing data into `description` or `metadata` show an uncovered distinction.

**Breaks when** input is genuinely open-ended (generic ingestion). Validate and normalise at the gateway, or use a schema registry and late binding and accept weaker static guarantees. Primitives: [`02-ashbys-law.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md), [`10-variety-engineering.md`](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/10-variety-engineering.md).

### P8 — Algedonic Channels in Architecture Review

| Red-flag class | Trigger | Bypass route |
|---|---|---|
| Data privacy | Personal data leaves its declared residency boundary, or crosses contexts without a lawful basis or processing agreement | DPO and chief architect |
| Security baseline | Unapproved auth, unencrypted data at rest, a new unreviewed trust boundary | Security architect and CISO |
| Principle violation | Design contradicts an S5 principle (e.g., a shared database) | Chief architect and domain architect |
| Irreversible data change | Migration that cannot roll back, or a change to a shared canonical model | Capability owner plus forum representative, before implementation |

Set the response window per class from the consequence deadline (before merge, before the release, before data moves). Embed triggers in the delivery process rather than relying on volunteers: an ADR red-flag checklist, a PR policy for cross-context contract changes, a CI schema-change classifier. S3-level issues such as a deprecated library stay in normal capability-owner review; routing them here floods S5.

---

## Anti-Pattern Catalog

### AP1 — Dictator Architecture: S5 Collapse onto S1

A central group approves frameworks, data models and schema changes inside contexts. Queues form, and decisions are made far from implementation reality. Fix:

1. Classify a month of the group's decisions as S5, S3 or S1, and return S1 decisions to teams with a policy statement.
2. Turn oversight into policy plus S3* audit.
3. Keep P8 so genuine S5 violations still reach the centre.

### AP2 — Integration Platform Managed as S3 Command

Every new consumer needs a platform change request, the bus filters on business criteria, and workflow state lives in the integration layer. Fix: apply the P2 test, move business logic to the owning contexts, and create an explicit orchestration context where no single context owns it.

### AP3 — Thin API Facing a Wide Environment

Consumers encode currency in strings, tell B2B from B2C by heuristics, and the changelog is mostly breaking retrofits. Fix: run the P7 coverage audit before publishing. Every workaround shipped becomes an implicit protocol you can never break.

### AP4 — Architecture Forum with No Ground Truth (Missing S3*)

The target-state diagram contradicts production, and guidance cites capabilities teams already replaced. Fix: spot-check deployed architecture against the real infrastructure, sample ADRs, and talk to teams without the capability-owner filter. Set the interval by delivery cadence. This is calibration, not punishment.

---

## Recipes

### R1 — VSM Boundary Mapping for a New Domain Capability

1. **Recursion level.** Usually Level 2. Confirm that the enterprise S5 constraints and the Level 1 integration platform standards are documented; if not, report that gap first.
2. **S1 contexts.** For each candidate context record its name, value, local inputs, system-of-record aggregate(s), autonomous decisions and S3 boundary. → verify: every aggregate has exactly one owner.
3. **S3 decisions:** inter-context contract style, event schema ownership and versioning, shared NFRs, the canonical data model, and the integration pattern with other domains (see [integration-and-boundary-patterns.md](integration-and-boundary-patterns.md)). → verify: none needs enterprise sign-off.
4. **S2 split.** Cross-domain routing and the gateway belong to Level 1; intra-domain sequencing and discovery belong to Level 2. → verify: no Level 2 need forces a Level 1 platform change without an enterprise S3 decision.
5. **Algedonic check (P8):** residency, principle breaches, new trust boundaries, irreversible cross-domain dependencies. → verify: every item is clear or escalated; none is "resolve in delivery".
6. **Contract coverage (P7)** for every externally facing API.

### R2 — Algedonic Review for Compliance and Data-Privacy Risk

1. **Trigger inventory**, reviewed with the DPO and legal:

   | Trigger | Severity |
   |---|---|
   | Cross-context transfer of personal data | High |
   | New store with no retention or deletion policy | High |
   | New third-party processor | High |
   | Automated decisions with legal or similarly significant effects | Critical, plus DPIA |
   | Weakening a security control | High |
   | Restricted cross-border transfer without an applicable lawful transfer mechanism | Critical, plus legal review |

   Confirm the applicable regime (e.g., UK GDPR and ICO guidance; FCA rules where financial data is involved) for the jurisdiction before relying on this list.
2. **Embed** the triggers in the ADR checklist, in PR policy (with personal-data field detection), and in the facilitator's close-out of cross-context design reviews. → verify: replay three past decisions (one that should fire, two that should not).
3. **Route by severity:** name recipients, channel and response windows set from the regulatory and consequence deadlines. The alert carries the triggering decision, the proposed data use, the regime and the artefact link. → verify: fire a synthetic trigger at an interval set by risk and change rate, and after any change to recipients or process.
4. **Post-event review** for every activation: trigger, decision, resolution, threshold calibration, inventory update. If nothing has fired in a year, either confirm with a manual audit or test the embedding.

### R3 — Recursive Decomposition: Enterprise to Service Level

1. **System-in-focus** in one sentence, with its parent, children and current problem. If the problem is "teams ignore the forum's guidance", the level is enterprise; do not fix it with service-level governance.
2. **Assign S1–S5 and S3*** at that level, each with a named owner. An unoccupied role is the main finding.
3. **Interference check:**

   | Decision | Wrong level | Right level | Interference |
   |---|---|---|---|
   | Framework inside a context | Enterprise S5 | Service S1 | Recursion collapse |
   | Contract style within a domain | Enterprise S5 | Domain S3 | Over-centralisation |
   | Cross-domain data sovereignty | Domain S3 | Enterprise S5 | Identity fragmentation |
   | Platform vendor selection | Service S1 | Enterprise S4/S3 | Cross-level decision without S4 input |

4. **Feedback loops per level:** each level needs a loop whose delay is short compared with its rate of change. An annual enterprise review against fortnightly delivery lets drift accumulate between cycles. Add S3* spot-checks where the loop is slow.

---

## Composition

| Situation | Start with | Add |
|---|---|---|
| New domain capability | R1 | P7 for its external APIs |
| Governance not catching drift | AP4 + P4 | R3 |
| Compliance risk found late | R2 | P8 embedding points |
| Central architecture is a bottleneck | AP1 | R3 step 3 |
| Integration layer accumulating logic | AP2 + P2 | R1 step 4 |
| API breaking on legitimate inputs | AP3 + P7 | R1 step 2 |
| New programme needs governance | R3 | P5 + P4 + P3 |

Sequence: recursion level → roles → S2 layer → API coverage → feedback loops → algedonic channels. Do not design the integration layer before the context boundaries exist.

---

## Cross-References

- Foundation: [foundations-cybernetics-vsm](../../foundations-cybernetics-vsm/SKILL.md)
- [solution-workflow.md](solution-workflow.md), [integration-and-boundary-patterns.md](integration-and-boundary-patterns.md), [transition-architecture.md](transition-architecture.md)
- [software-architecture-design](../../software-architecture-design/SKILL.md): runtime topology inside a context
- [software-security-appsec](../../software-security-appsec/SKILL.md): security triggers in R2
- [ops-devops-platform](../../ops-devops-platform/SKILL.md): service-level feedback loops and alerting
