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
- **Migration boundary**: this skill owns the cross-system wave plan — which systems coexist, in what order, with what rollback and retirement criteria. It does not own the mechanics of extracting or decomposing inside one system (strangler fig steps, database decomposition, shadow traffic) — that is [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md)'s `migration-modernization-guide.md` and `estate-modernization.md`.

## Default Workflow

1. Define the business scenario, actors, and success measures.
2. Map current systems, ownership boundaries, and the critical pain points.
3. Map business capabilities to system owners and systems of record.
4. Capture hard constraints: compliance, latency, data residency, legacy dependencies, vendor limits, and rollout limits.
5. Propose 2-3 viable solution options at the system-landscape level.
6. Choose a target state and, if needed, the minimum viable interim state.
7. Define system responsibilities, integration style, data movement, trust boundaries, and validation checkpoints. Use the [integration decision matrix](references/integration-and-boundary-patterns.md#decision-matrix) to choose the boundary style.
8. Sequence migration waves with rollback points, coexistence rules, and retirement criteria.
9. Hand deeper slices to companion skills for software architecture, APIs, security, or platform ops.

## Required Output Shape

Every recommendation should include:

- problem statement and system scope
- explicit in-scope and intentionally out-of-scope boundaries
- capability, ownership, and system-of-record summary
- current-state and target-state summary
- interim-state summary when the change is phased
- recommended option plus rejected alternatives, scored against measurable NFR scenarios and a per-option cost (build, run, migrate, exit) — see [references/option-scoring.md](references/option-scoring.md)
- integration and data-flow shape
- migration-wave plan with rollback or exit criteria when relevant
- top risks, failure modes, and validation checkpoints
- what NOT to decide yet
- explicit handoffs to companion skills
- an ADR (or ADR-ready summary) for each option decision: context, decision, status, consequences — so the rejected alternatives are traceable later, not just the winner

## Build vs Buy vs Partner

| Signal | Lean toward | Why | Watch out for |
|--------|-------------|-----|----------------|
| Capability is undifferentiated and a mature vendor covers it (e.g., KYC, payments processing, email delivery) | Buy | Faster time-to-value; vendor operates the purchased capability | Vendor lock-in on data export, pricing tiers that punish growth; your integration and compliance duties remain |
| Capability is the core differentiator the business competes on | Build | Buying core differentiation means competitors can buy the same thing | Sunk-cost bias toward building things that are actually commodity |
| Capability needs deep, ongoing integration with proprietary internal data or workflow | Build or heavily customize | Off-the-shelf tools rarely model idiosyncratic internal processes well | Underestimating integration cost when "buy" quotes look cheap in isolation |
| No internal team can own long-term operation of a built solution | Buy or partner | An unowned custom system decays faster than a supported vendor product | Choosing "build" because of a one-time budget cycle, ignoring run-cost ownership |
| Regulatory or contractual terms require a named, audited third party | Partner (regulated vendor) | Some obligations cannot be satisfied by an internal build | Assuming vendor certification covers the whole integration surface, not just the vendor's own boundary |

Treat vendor capability claims as unverified until checked against the organization's actual constraints (data residency, auth model, support SLA, exit/export terms) — a capability that exists in a datasheet is not the same as a capability that fits this landscape's ownership and compliance boundaries.

## Landscape Choices Beyond Pattern Selection

- **Integration backbone**: a fully connected point-to-point landscape has quadratically many possible links; actual integration cost depends on the links and contracts needed. An iPaaS or event backbone can reduce duplicated integration work but adds a shared dependency and governance owner. Choose from the required connectivity and who owns cross-system change.
- **Agent and LLM participants in the landscape**: name which systems expose an agent-callable interface (for example MCP) and where the trust boundary for agent-initiated writes sits. Do not let an agent mutate a system of record without the same authoritative-data gate applied to any other writer. Runtime-level agent and tool-gateway design belongs to [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md).

## Team Topology and Conway's Law Check

Conway's Law predicts that the system landscape will mirror the organization's communication structure, whether or not that mirroring is intentional. Before finalizing a target state:

- Name which team owns each system-of-record and each integration boundary; a boundary with no clear owning team will accumulate ad hoc, undocumented coupling.
- Check whether the proposed target state requires a team structure that does not exist yet (e.g., a shared platform team, a new domain team). If so, the transition plan must include the org-design change as an explicit dependency, not an assumption.
- Prefer target states that match likely team boundaries over target states that are architecturally elegant but require cross-team coordination on every change — coordination cost is a real cost, not a rounding error.
- When a target state deliberately goes against current team structure (an "inverse Conway maneuver" to force a desired architecture), say so explicitly and name who owns driving the org change; do not let this be an implicit side effect of the diagram.

## Verification Checklist

**Authoritative-data gate.**

For every business entity that crosses systems, name the authoritative ownership and convergence rule: one writer, partition-owned writers, or deliberate multi-writer semantics. Document allowed replicas, propagation and causal-ordering rules, deterministic conflict or merge behavior, failure handling, and the reconciliation owner. Reject designs where systems can independently mutate the same fact without those semantics. Include temporary dual-write ownership in the transition plan and define the evidence required to retire it.

Before finalizing a solution recommendation:

- [ ] Business problem and success measures defined in non-technical terms
- [ ] Every participating system has an explicit owner and system-of-record role stated
- [ ] Hard constraints captured: compliance, latency, data residency, vendor limits, rollout limits
- [ ] 2-3 solution options compared with explicit reasons for rejection of alternatives
- [ ] Integration style chosen from the [decision matrix](references/integration-and-boundary-patterns.md#decision-matrix), not defaulted to API everywhere
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

Before including a managed-migration or refactoring service in an option, check the provider's documentation for availability, region support, migration scope and exit behavior. Cite the durable pattern (strangler fig, ACL, expand/contract) separately from the product chosen to implement it.

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
- [references/option-scoring.md](references/option-scoring.md) — NFR scenarios, cross-system availability/latency budgets, per-option cost skeleton, vendor due diligence and exit planning
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

Primary sources live in [data/sources.json](data/sources.json).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
