# Solution Workflow

Use this when the user starts from a business scenario or a target-state question rather than a specific runtime.

## Default Sequence

1. Name the business journey or operating scenario.
2. Identify actors, systems, and owners.
3. Capture current-state pain: latency, coupling, manual work, compliance risk, migration pressure, or duplication.
4. Map capabilities to systems of record, boundary owners, and approval paths.
5. Define the solution options at the system-landscape level before choosing software patterns.
6. Pick the target state and the minimum viable interim state.
7. Define integration boundaries, data movement, and operational ownership.
8. Sequence delivery into migration waves and handoffs.

## Questions To Answer

- What business outcome is the solution meant to improve?
- Which systems must participate, and which can stay untouched?
- Where is the system of record for each important data set?
- Which boundaries are trust, compliance, or ownership boundaries?
- Which integrations must be synchronous, and which can be asynchronous?
- What can be deferred until after the first target state is live?
- For each capability under consideration for a vendor purchase: is this a commodity capability worth buying, or the thing the business actually competes on?
- Does the target state assume a team structure (a platform team, a new domain team) that does not exist yet? If so, who owns that org-design dependency?

## Default Deliverables

Use the [required output shape](../SKILL.md#required-output-shape) and [solution blueprint](../assets/planning/solution-blueprint.md) to package the recommendation.

## What This Workflow Does NOT Decide

Do not settle these questions here unless the user explicitly asks for them after the solution shape is chosen:

- modular monolith vs microservices
- saga vs orchestration vs event sourcing
- service mesh, gateway, or runtime internals
- repo layout and deployable-unit count
