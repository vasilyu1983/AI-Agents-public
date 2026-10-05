# Rule 05 — Operational Resilience

> **Stub.** Replace with your own resilience/continuity regime (e.g.
> DORA, SS1/23, or your internal standard). Illustrative scaffolding.

Constraints that keep agent activity from degrading the operational
resilience picture this hub is supposed to describe accurately.

## Source template

See the resilience portions of
`dev-context-engineering/assets/compliance-fca-emi.md` and your own
important-business-services (IBS) register.

## What goes here (replace)

- Which repos/flows map to important business services — and that the
  mapping in `&lt;domain&gt;/as-is/` must stay current.
- Change-impact expectation: cross-repo blast radius must be checked
  (via the knowledge graph) before claiming a change is low-risk.
- Freshness obligation: stale resilience claims must be flagged, not
  silently trusted (`context/scripts/README.md` → freshness checks).
