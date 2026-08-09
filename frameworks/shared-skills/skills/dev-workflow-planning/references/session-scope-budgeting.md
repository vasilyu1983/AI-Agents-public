# Session Scope Budgeting

Use this reference to keep long-running execution sessions reliable.

## Core Rule

One session should optimize for shipping one bounded outcome, not starting many partially complete streams.

## Scope Budget Model

- `S`: session scope budget (deliverables)
- Default `S = 1..2` deliverables
- If incoming tasks exceed `S`, split into follow-up milestones

## Drift Signals

Rescope when you detect:
- repeated re-reading of same files without new decisions
- increasing nonzero command retries without new evidence
- competing priorities across more than 3 domains

## Milestone Pattern

1. Discovery + plan
2. Implementation (single domain)
3. Verification + fixups
4. Handoff

## Enforcement

At each milestone, produce checkpoint record with:
- done
- blocked
- evidence
- next bounded step
