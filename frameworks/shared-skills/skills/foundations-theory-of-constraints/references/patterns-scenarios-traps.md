---
description: Applied patterns, scenarios, anti-patterns, and known traps for Theory of Constraints foundations.
last_verified: 2026-05-02
status: stable
---

# Theory of Constraints Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Flow recovery | Work piles up before one step | 5FS -> DBR -> buffer management |
| Roadmap sequencing | Too many bets compete for one scarce team | Constraint ID -> T/CU ranking -> policy audit |
| Recurring incidents | Symptoms repeat after local fixes | CRT -> Evaporating Cloud -> FRT |
| Change execution | Strategy is right but blocked | PRT -> Transition Tree |
| Project lateness | Tasks look on time but projects slip | Critical Chain -> project buffer -> buffer burn |
| Policy bottleneck | Capacity exists but throughput does not improve | Policy constraint audit -> cloud -> injection |

## Known Traps

- A local bottleneck is not always the system constraint.
- Exploit comes before elevate.
- Subordination often feels inefficient locally; that is expected.
- Throughput accounting ranks by constraint use, not gross margin.
- Policy constraints are often protected by incentive metrics.
- Thinking Process diagrams need rigorous logic checks, not attractive formatting.
- **AI coding tools shift the constraint downstream.** After AI coding adoption, the constraint typically moves from code writing to code review, QA, or integration — not to code generation. Optimizing code generation without identifying the new downstream constraint merely shifts the bottleneck (reported pattern 2024–2026; sources: IT Revolution "Revenge of QA" Jan 2026; Logilica Dec 2025; Faros AI 2025 telemetry). Re-run 5FS when DORA metrics stay flat despite improved individual coding velocity.

## Constraint vs. Bottleneck-of-the-Day (Expert Judgment)

The single highest-leverage skill a non-expert lacks is telling these apart before recommending an intervention:

| | System Constraint (TOC sense) | Bottleneck-of-the-Day |
|---|---|---|
| Stability | Persists across weeks/sprints/releases; same step or resource caps throughput repeatedly | Whichever step happens to have the deepest queue *this week*; shifts with staffing, mix, or seasonality |
| Evidence | Queue depth and wait time in front of it are structurally larger than anywhere else, over multiple observation windows | A single snapshot of utilization or a single bad sprint |
| Root cause | Often a policy, incentive, or approval rule — not a missing seat or machine | Usually a transient capacity dip: someone on leave, a spike in demand, a one-off incident |
| Correct response | 5FS: exploit, subordinate, elevate, repeat — a structural program | Absorb the spike; do not restructure the org around a one-week anomaly |
| Misdiagnosis cost | Treating it as noise means the real limiter never gets fixed and throughput stays flat forever | Treating it as the constraint triggers a reorg, a hire, or a tooling investment that solves nothing once the anomalous week passes |

**Diagnostic rule of thumb**: before naming a constraint, require at least 3–4 observation cycles (sprints, weeks, batches) showing the same step as the deepest queue. A constraint identified from one bad week is a bottleneck-of-the-day misdiagnosed as a constraint — the single most common practitioner error TOC literature warns about (Goldratt 1984; Cox & Spencer 1998).

## The Real Constraint Is Often Policy, Not Capacity

Practitioners default to physical explanations ("we need more people/machines/GPUs") because physical constraints are visible and politically safe to name — nobody personally owns a queue depth chart. Policy constraints are invisible and often trace back to a decision someone in the room made, which makes them harder to surface honestly. Expert diagnosis routine:

1. Ask "why is this step slow?" repeatedly (see primitive #5, CRT) until the answer is a rule, metric, or approval gate rather than a resource.
2. Before recommending capacity elevation (hiring, buying, GPU spend), explicitly rule out: an approval/sign-off gate, a batch-size policy, an incentive metric that rewards the wrong behavior, or a stale risk rule kept "because we've always done it this way."
3. If elevating physical capacity has already been tried and throughput did not move, that is strong evidence the real constraint is a policy co-located with or upstream of the physical step — see `10-policy-constraints.md`.

## When the Single-Constraint Assumption Breaks

TOC's core simplifying assumption — exactly one constraint gates the whole system at any moment — is a modeling choice, not a law of nature. It breaks down in identifiable, common situations. Naming these explicitly is what separates expert application from mechanical checklist use:

| Situation | Why Single-Constraint TOC Misfires | What To Do Instead |
|---|---|---|
| Multiple roughly equal capacity constraints (within ~20% of each other) | Elevating "the" constraint just promotes the next one within one cycle; ranking noise dominates the T/CU signal | Use queueing-network analysis (`foundations-queueing-theory`) to model joint capacity, or treat the near-tied resources as a combined constraint pool |
| Matrix / shared-resource organizations | The same senior engineer, approver, or specialist is claimed as "the constraint" by every team simultaneously; there is no single system, only overlapping systems competing for one resource | Model it explicitly as a shared-resource contention problem: build one T/CU ranking across *all* competing initiatives, not a separate ranking per team — a per-team ranking will always claim the same person as available |
| Constraint oscillates between two steps run-to-run | No stable constraint exists yet; the system has not reached steady state (new team, volatile demand, unstable process) | Stabilize the process first (reduce variability, fix the worst process defects) before applying 5FS — 5FS assumes a discoverable, holdable constraint |
| Network/graph-structured work (not a simple serial line) | DBR assumes one drum sets the pace for a linear flow; in a fan-out/fan-in dependency graph, several paths can each carry their own local constraint | Decompose into sub-flows with their own DBR configuration, or fall back to project/critical-chain scheduling (#9) which explicitly handles resource contention across paths |
| The "constraint" is a deliberate strategic choice | Some limits are chosen on purpose (e.g., "we cap sales headcount to force product-led growth") — TOC is a diagnostic tool for unwanted limits, not a normative claim that every limit must be broken | Confirm with stakeholders whether the limit is wanted before applying exploit/elevate; TOC does not adjudicate strategy |

**Evidence-grade note**: These breakdown conditions are derived from TOC's own stated assumptions and from queueing-theory critique of single-constraint models, not from a dedicated peer-reviewed study of TOC failure modes — treat as informed practitioner synthesis, consistent with the disclosed evidence grade for this skill's practitioner-literature claims.

## Exit Checklist

- [ ] System goal is stated.
- [ ] Current constraint is evidenced by flow, queue, or decision blockage.
- [ ] Exploitation move is defined before added capacity.
- [ ] Non-constraints have a subordination rule.
- [ ] Policy constraints were checked before physical capacity spend.
- [ ] Throughput change is measured after intervention.
