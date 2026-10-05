# Architecture Decision Records (ADRs) - Writing Guide

Decision rules for ADRs. The section skeleton and a filled example are in [assets/architecture/adr-template.md](../assets/architecture/adr-template.md); the formats themselves are [MADR](https://adr.github.io/madr/) and Nygard's original ([Nygard, 2011](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)). This file covers when to write one, what makes each section useful, and how ADRs stay true.

## Table of Contents

- [When to Write an ADR](#when-to-write-an-adr)
- [Section Rules](#section-rules)
- [Lifecycle: Immutable Decision, Living Status](#lifecycle-immutable-decision-living-status)
- [Naming and Index](#naming-and-index)
- [ADR Anti-Patterns](#adr-anti-patterns)
- [ADR Review Checklist](#adr-review-checklist)
- [Migration ADRs](#migration-adrs)
- [After-Action Reviews](#after-action-reviews)

---

## When to Write an ADR

Write one when the decision is expensive to reverse or will be questioned later by someone who was not in the room:

- choosing a datastore, framework, protocol, or hosted platform
- architectural patterns (event-driven, service split, multi-tenancy model)
- auth approach, API standards, deployment and testing strategy
- any decision a future engineer or agent might "fix" without knowing why it was made

Skip it for refactors, bug fixes, and temporary workarounds; those belong in the PR description or a gotcha entry.

Write the ADR while the decision is being made (status `Proposed`), not months later. A retroactive ADR is acceptable for a critical legacy decision, but label it as reconstructed and say what evidence it rests on.

## Section Rules

- **Title:** `NNNN: [Verb] [technology/pattern] for [purpose]`, e.g. "Use PostgreSQL for the primary datastore". The title states the decision, not the topic.
- **Context:** the forces, with numbers: load, data size, latency budget, team skills, budget, deadline, compliance constraints. A context without numbers cannot be re-evaluated when the numbers change.
- **Decision:** one declarative sentence first, then the specifics that matter for reversal (hosting model, critical configuration). Pin versions in the implementation docs, not in the ADR: the decision outlives the version.
- **Consequences:** positive, negative, and neutral, each concrete. An ADR with no negatives was not thought through; name the cost in time, money, and operational load.
- **Alternatives considered:** at least two real alternatives, including "keep the current state", each with honest pros, cons, and the specific reason it lost. A straw-man alternative is worse than none.
- **Revisit trigger:** the condition that would reopen the decision (a load threshold, a cost ceiling, a vendor end-of-life). This is what makes the ADR re-evaluable instead of historical.
- **References:** link the discussion, spike results, benchmarks, and PRs. Put implementation code in PRs, not in the ADR.

## Lifecycle: Immutable Decision, Living Status

- The **decision text** of an accepted ADR does not change. If the decision changes, write a new ADR that supersedes it, and link both ways.
- The **status line, "superseded by" links, and dated after-action notes** are appended to the existing ADR; that is the only editing allowed.
- Statuses: `Proposed`, `Accepted`, `Deprecated` (still in use, being phased out), `Superseded` (link the replacement), `Rejected` (kept so the question is not relitigated).
- **Freshness rule:** when runtime behavior changes in a way that contradicts an accepted ADR, write the superseding ADR in the same delivery cycle as the behavior change. A stale accepted ADR is not cosmetic: engineers and agents treat it as current and reintroduce the assumption the change removed.
- Never delete an ADR; rejected and superseded ones are the record of what not to try again.

## Naming and Index

- Store ADRs in the repo (`docs/adr/`), zero-padded and sequential (`0001-use-postgresql-for-primary-datastore.md`); never reuse a number.
- Keep `docs/adr/README.md` as the index: number, title, status, date, superseded-by. Update it in the same PR as the ADR; the index is what agents and new hires read first.
- If you use a CLI to scaffold ADRs, check its current docs for the command set; do not hand-maintain the index when the tool can generate it.

## ADR Anti-Patterns

- No context, or context without numbers
- No alternatives, or only straw-man alternatives
- Consequences with no negatives
- Too vague ("use a database") or too detailed (implementation code)
- No date or no status
- Editing the decision text of an accepted ADR instead of superseding it
- An accepted ADR contradicted by the running system

## ADR Review Checklist

Before accepting an ADR:

- [ ] Title states the decision
- [ ] Status and date set
- [ ] Context quantifies the forces and constraints
- [ ] Decision is specific enough to act on
- [ ] Consequences include negatives and costs
- [ ] At least two real alternatives, including keep-current-state, with the reason each lost
- [ ] Revisit trigger stated
- [ ] References link discussion and evidence
- [ ] Index updated in the same PR

## Migration ADRs

Migration ADRs document how to get from the current state to the target state, not just what the target state is. Use them when a decision includes phased rollout, coexistence, decommissioning, or regulated cutover work.

When writing migration ADRs:
- **Context** should include the current-state problems, what triggers the migration, and any compliance, contractual, or customer deadlines.
- **Decision** should name the target architecture and the proven patterns, packages, or workflows being reused from the current estate.
- **Alternatives** should include keeping the current state as an explicit option, with concrete downsides and risk acceptance.
- **Consequences** should separate positive outcomes, negative trade-offs, operational risks, and external dependencies.
- **Implementation** should define phase ordering, validation windows, rollback triggers, ownership, and exit criteria.

Migration ADR checklist:
- source and target systems named explicitly
- migration trigger and deadline stated
- keep-current-state alternative documented
- rollback and cutover criteria included
- dependencies and validation period called out

## After-Action Reviews

Review each significant ADR about a month after acceptance, after a major milestone, or when unexpected issues trace back to the decision. Compare what the ADR predicted with what happened.

Questions:

- Did the decision achieve its stated goals?
- Which predicted costs and benefits materialized, and which did not?
- What consequences were not predicted?
- Would we make the same decision today? If not, is a superseding ADR needed now?
- Did the revisit trigger fire?

Append the findings to the ADR as a dated note (this is allowed; the decision text stays unchanged):

```markdown
### After-Action Review - YYYY-MM-DD

**Goals achieved**: [goal] - met / partially met / not met, with the measurement
**Unexpected consequences**: [positive and negative]
**Lessons**: [what future ADRs should check]
**Outcome**: No change / Supersede with ADR-NNNN
```

For review meetings, a silent-reading start (attendees read the ADR and leave written comments before discussion) keeps the discussion on the document rather than on whoever speaks first; keep the group small enough that everyone reads.

Checklist:

- [ ] Review scheduled when the ADR is accepted
- [ ] Original decision-makers and affected teams included
- [ ] Goals vs actuals recorded with measurements
- [ ] Dated note appended; index updated if status changed
