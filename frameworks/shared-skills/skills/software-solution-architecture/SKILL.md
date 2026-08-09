---
name: software-solution-architecture
description: "Designs cross-system target states and transition plans from business workflows and system boundaries. Use when comparing end-to-end solution options or phased migrations."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Software Solution Architecture

Use this skill when the question starts from a business workflow, operating model, system landscape, or transition problem rather than from a single service or deployable boundary.

This skill chooses the solution shape first. It does not default to runtime patterns such as modular monolith vs microservices, CQRS, service mesh, or MCP/A2A until the business flow, participating systems, and transition shape are already clear.

Start here for:

- target architecture across multiple systems or domains
- business journeys that cross product, integration, data, and operational boundaries
- solution options and tradeoffs before deeper runtime design
- system-of-record, ownership, and trust-boundary mapping across the landscape
- phased migration or coexistence design with interim and final states
- regulated or enterprise contexts where the main problem is stitching systems together coherently

Use [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) after the solution shape is known and the next question is service decomposition, distributed consistency, platform engineering, or runtime topology.

## Quick Reference

| Need | Default move | Read next |
|------|--------------|-----------|
| Design a target solution across multiple systems | Map business flow to systems, responsibilities, and constraints before choosing patterns | [references/solution-workflow.md](references/solution-workflow.md) |
| Compare integration styles and boundaries | Choose API, event, batch, file, webhook, BFF, or anti-corruption boundaries from a decision matrix | [references/integration-and-boundary-patterns.md](references/integration-and-boundary-patterns.md) |
| Map capabilities, owners, and systems of record | Capture business capability, owning team, boundary type, and source-of-truth decisions | [assets/planning/capability-boundary-map.md](assets/planning/capability-boundary-map.md) |
| Plan a phased migration | Define current, interim, and target states with coexistence, cutover, and rollback rules | [references/transition-architecture.md](references/transition-architecture.md) |
| Sequence delivery into safe waves | Capture migration wave entry, rollback, and retirement criteria | [assets/planning/transition-wave-planner.md](assets/planning/transition-wave-planner.md) |
| Package the final recommendation | Summarize target state, options, transition, risks, and handoffs | [assets/planning/solution-blueprint.md](assets/planning/solution-blueprint.md) |

## When to Use This Skill

- Cross-system target architecture
- End-to-end business flow design across several services or platforms
- Integration landscape design and dependency mapping
- Capability ownership, system-of-record, and trust-boundary decisions
- Interim-state and final-state solution planning
- Large migration workstreams with multiple systems changing at different times
- Solution option analysis before coding or service decomposition

## When NOT to Use This Skill

- **Deep runtime or distributed-system design** → [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md)
- **Single-service implementation** → [../software-backend/SKILL.md](../software-backend/SKILL.md)
- **API contract depth** → [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md)
- **Infrastructure/platform ops as the main problem** → [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)
- **Security architecture as the main problem** → [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md)

## Boundary Rules

- This skill owns the system landscape, option comparison, and transition shape.
- This skill should name what stays untouched, what changes now, and what is intentionally deferred.
- This skill should stop short of deciding deployable-unit count, internal service topology, or deep consistency mechanisms inside a chosen solution.
- Once the main question becomes runtime boundaries, bounded contexts, resilience internals, or platform defaults, hand off to [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md).

## Default Workflow

1. Define the business scenario, actors, and success measures.
2. Map current systems, ownership boundaries, and the critical pain points.
3. Map business capabilities to system owners and systems of record.
4. Capture hard constraints: compliance, latency, data residency, legacy dependencies, vendor limits, and rollout limits.
5. Propose 2-3 viable solution options at the system-landscape level.
6. Choose a target state and, if needed, the minimum viable interim state.
7. Define system responsibilities, integration style, data movement, trust boundaries, and validation checkpoints.
8. Sequence migration waves with rollback points, coexistence rules, and retirement criteria.
9. Hand deeper slices to companion skills for software architecture, APIs, security, or platform ops.

## ASCII Flow

```text
Solution architecture request
  -> Define business scenario, actors, and success measures
  -> Map current systems, owners, records, and pain points
  -> Compare target-state options and interim-state needs
  -> Choose system responsibilities, integrations, data flows, and trust boundaries
  -> Sequence migration waves with rollback and retirement criteria
  -> Hand deep runtime, API, security, or platform slices to companion skills
```

## Required Output Shape

Every recommendation should include:

- problem statement and system scope
- explicit in-scope and intentionally out-of-scope boundaries
- capability, ownership, and system-of-record summary
- current-state and target-state summary
- interim-state summary when the change is phased
- recommended option plus rejected alternatives
- integration and data-flow shape
- migration-wave plan with rollback or exit criteria when relevant
- top risks, failure modes, and validation checkpoints
- what NOT to decide yet
- explicit handoffs to companion skills
- an ADR (or ADR-ready summary) for each option decision: context, decision, status, consequences — so the rejected alternatives are traceable later, not just the winner

## Integration Style Decision

| Situation | Choose | Why |
|-----------|--------|-----|
| Synchronous request with immediate response needed | REST/GraphQL API | Caller needs the result to proceed; latency SLA known |
| One event triggers many downstream consumers | Event bus (Kafka, SNS, EventBridge) | Decouples publishers from consumers; enables fan-out |
| Bulk data movement between systems on a schedule | Batch / file | High volume; latency tolerance exists; no real-time requirement |
| Upstream system is authoritative and rate-limited or politically hard to change | Anti-corruption layer (ACL) | Prevents downstream from inheriting upstream's model and constraints |
| Browser/mobile needs tailored API across multiple backend services | BFF (Backend for Frontend) | Reduces over-fetching; isolates client contract from service internals |
| External system pushes events to your system | Webhook (inbound) | Source system owns event timing; polling would waste quota |
| Your system pushes state changes to external consumers | Webhook (outbound) | Receivers need near-real-time without polling |

## Build vs Buy vs Partner

| Signal | Lean toward | Why | Watch out for |
|--------|-------------|-----|----------------|
| Capability is undifferentiated and a mature vendor covers it (e.g., KYC, payments processing, email delivery) | Buy | Faster time-to-value; vendor carries compliance and scaling burden | Vendor lock-in on data export, pricing tiers that punish growth |
| Capability is the core differentiator the business competes on | Build | Buying core differentiation means competitors can buy the same thing | Sunk-cost bias toward building things that are actually commodity |
| Capability needs deep, ongoing integration with proprietary internal data or workflow | Build or heavily customize | Off-the-shelf tools rarely model idiosyncratic internal processes well | Underestimating integration cost when "buy" quotes look cheap in isolation |
| No internal team can own long-term operation of a built solution | Buy or partner | An unowned custom system decays faster than a supported vendor product | Choosing "build" because of a one-time budget cycle, ignoring run-cost ownership |
| Regulatory or contractual terms require a named, audited third party | Partner (regulated vendor) | Some obligations cannot be satisfied by an internal build | Assuming vendor certification covers the whole integration surface, not just the vendor's own boundary |

Treat vendor capability claims as unverified until checked against the organization's actual constraints (data residency, auth model, support SLA, exit/export terms) — a capability that exists in a datasheet is not the same as a capability that fits this landscape's ownership and compliance boundaries.

## Team Topology and Conway's Law Check

Conway's Law predicts that the system landscape will mirror the organization's communication structure, whether or not that mirroring is intentional. Before finalizing a target state:

- Name which team owns each system-of-record and each integration boundary; a boundary with no clear owning team will accumulate ad hoc, undocumented coupling.
- Check whether the proposed target state requires a team structure that does not exist yet (e.g., a shared platform team, a new domain team). If so, the transition plan must include the org-design change as an explicit dependency, not an assumption.
- Prefer target states that match likely team boundaries over target states that are architecturally elegant but require cross-team coordination on every change — coordination cost is a real cost, not a rounding error.
- When a target state deliberately goes against current team structure (an "inverse Conway maneuver" to force a desired architecture), say so explicitly and name who owns driving the org change; do not let this be an implicit side effect of the diagram.

## Verification Checklist

Before finalizing a solution recommendation:

- [ ] Business problem and success measures defined in non-technical terms
- [ ] Every participating system has an explicit owner and system-of-record role stated
- [ ] Hard constraints captured: compliance, latency, data residency, vendor limits, rollout limits
- [ ] 2-3 solution options compared with explicit reasons for rejection of alternatives
- [ ] Integration style chosen from decision table above, not defaulted to API everywhere
- [ ] Interim state defined when change is phased (not just current and target)
- [ ] Migration wave has rollback criteria, exit conditions, and retirement plan
- [ ] What NOT to decide yet is stated explicitly
- [ ] Handoffs to companion skills (architecture, API, security, platform) named
- [ ] Each option decision has an ADR or ADR-ready summary (context, decision, status, consequences)
- [ ] Build/buy/partner reasoning stated for any capability considered for a vendor or platform purchase
- [ ] Target state checked against actual team ownership (Conway's Law); org-design dependencies named if the target state requires teams that do not yet exist

## Known Traps

- Jumping from business pain directly to microservices, event buses, or platform purchases before clarifying ownership and system-of-record boundaries.
- Drawing a clean target state that ignores interim coexistence, contract duplication, or rollback constraints the organization must actually live through.
- Treating integrations as symmetric when one side is authoritative, rate-limited, legally constrained, or politically hard to change.
- Letting future-state diagrams hide current operational pain such as manual workarounds, support load, or data reconciliation burden.
- Choosing one transition wave that spans too many teams, too many systems, or too much irreversible data movement.
- Mistaking enterprise tool capabilities for guaranteed adoption, governance, or runtime fit without validating team ownership and operating model.
- Recommending "buy" for a capability that is the business's actual differentiator, or "build" for a commodity capability a mature vendor already solves, without stating the tradeoff explicitly.
- Designing an elegant target-state diagram that silently requires a team structure the organization does not have, without naming the org-design dependency.

## Common Anti-Patterns

- Producing a solution recommendation that is really a runtime architecture preference in disguise.
- Treating every boundary as an API problem when batch, file, event, or anti-corruption patterns fit the landscape better.
- Hand-waving trust boundaries, stewardship, and source-of-truth conflicts as implementation details.
- Writing migration plans with start and end states only, leaving no explicit interim controls, exit criteria, or retirement plan.
- Forcing standardization on one platform everywhere when the cost of replacement exceeds the business value of uniformity.

## Navigation

### References

- [references/solution-workflow.md](references/solution-workflow.md) — business-flow-first workflow for solution design
- [references/integration-and-boundary-patterns.md](references/integration-and-boundary-patterns.md) — decision matrix for API, event, file, batch, webhook, BFF, and ACL boundaries
- [references/transition-architecture.md](references/transition-architecture.md) — current, interim, and target-state planning with wave controls
- [references/cybernetics-vsm-applied.md](references/cybernetics-vsm-applied.md) — VSM, Ashby's law, feedback loops, algedonic channels applied to solution architecture and system viability.

### Templates

- [assets/planning/solution-blueprint.md](assets/planning/solution-blueprint.md) — final recommendation blueprint
- [assets/planning/capability-boundary-map.md](assets/planning/capability-boundary-map.md) — capability, ownership, and system-of-record worksheet
- [assets/planning/transition-wave-planner.md](assets/planning/transition-wave-planner.md) — migration wave planner with rollback and retirement criteria

### Validation

- [evals/evals.json](evals/evals.json) — trigger, non-trigger, and near-boundary behavioral checks for this skill

### Related Skills

- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md)
- [../software-backend/SKILL.md](../software-backend/SKILL.md)
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md)
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md)
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify version-sensitive claims about cloud services, managed integration products, platform limits, or vendor lifecycle before final answers.
- Prefer primary sources for cloud patterns, migration guidance, and standards.
- If live verification is unavailable, separate durable solution-architecture guidance from unverified vendor specifics.
- Treat named managed-migration or refactoring services (e.g., a cloud vendor's specific "assisted decomposition" tooling) as high-churn: vendors retire, rename, or fold these into newer offerings faster than the durable pattern (strangler fig, ACL, expand/contract) they implement changes. Cite the durable pattern; hedge the specific product name and its current availability.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

