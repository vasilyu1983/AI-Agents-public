# Option Scoring: NFRs, Cost, Due Diligence, and Exit

Use this reference when two or more landscape options are on the table and the recommendation must be defensible on measurable quality attributes and total cost, not on pros and cons alone.

## Contents

- [NFR Scenarios](#nfr-scenarios)
- [Cross-System Budgets](#cross-system-budgets)
- [Per-Option Cost Skeleton](#per-option-cost-skeleton)
- [Vendor Due Diligence and Exit](#vendor-due-diligence-and-exit)
- [Scoring the Options](#scoring-the-options)
- [When Not to Run This](#when-not-to-run-this)

## NFR Scenarios

Write each non-functional requirement as a scenario with a measurable response, not as an adjective ("highly available", "fast", "secure"):

| Field | Example shape |
|---|---|
| Source and stimulus | Peak-hour order submissions from the web channel |
| Affected systems | Checkout → order system of record → payment provider |
| Response | Order is accepted or rejected with a stable reason |
| Response measure | A target the business signs off, e.g. latency percentile, availability over a window, RTO/RPO per system of record |

Minimum set for a landscape decision: availability, end-to-end latency across synchronous hops, RTO/RPO per system of record, data residency, security and trust boundaries, and operability (who is on call for each boundary). Take the target values from the business owner; do not invent them.

## Cross-System Budgets

- **Serial synchronous chains multiply under independence.** When every dependency must succeed, independent dependency availabilities multiply; the composed path cannot be more available than its weakest required dependency. Shared failure domains invalidate the independence assumption. Every synchronous hop spends availability and latency budget.
- **Latency adds along the critical path.** Budget the end-to-end percentile target across hops and name which hop owns which slice. Percentiles do not add exactly; measure the composed path rather than summing per-hop percentiles.
- **Set RTO/RPO for each system of record and its recovery path.** Validate replication lag, durable acknowledgement and retained recovery logs; a standby can recover more recent state than an older primary backup. An asynchronous replica or cache does not by itself guarantee no data loss. See [PostgreSQL's standby guidance](https://www.postgresql.org/docs/current/warm-standby.html) for a concrete example.
- If a budget cannot be met synchronously, that is a signal to move the boundary to async, batch, or a local copy with an explicit staleness contract (see [integration-and-boundary-patterns.md](integration-and-boundary-patterns.md)).

## Per-Option Cost Skeleton

Compare options over the same horizon and with the same cost lines. Leave a line blank with a note rather than omitting it:

| Cost line | What to include |
|---|---|
| Build | Engineering effort, integration work, data migration, testing |
| Run | Infrastructure, licences or subscriptions, support contracts, egress |
| People | On-call, operational ownership, skills the team does not have yet |
| Migrate | Coexistence period, dual-running, reconciliation, cutover risk |
| Exit | Data export, contract termination, re-platforming if the option is later abandoned |

Use the organization's actual quotes and rates. Hand the bill-level analysis and unit-cost modelling to [../../ops-cost-optimization/SKILL.md](../../ops-cost-optimization/SKILL.md).

## Vendor Due Diligence and Exit

For any buy or partner option, check:

- Certification scope versus the actual integration surface (a vendor's audit report covers the vendor's boundary, not your integration).
- Data export: formats, completeness, and whether export works at production volume.
- Data residency and sub-processors.
- Auth model and identity integration.
- Support SLA and the escalation path.
- Financial and product viability; escrow for critical dependencies.
- Contractual exit terms: notice, transition assistance, switching charges.

Plan exit before entry: name the trigger that would make you leave, the export path, and the fallback system. Where cloud-switching or ICT third-party exit obligations may apply (for example EU data-portability or financial-sector operational-resilience rules), route the legal reading to the owning legal skill rather than restating it here.

## Scoring the Options

1. List the NFR scenarios and cost lines as rows; options as columns.
2. Mark each row pass / at risk / fail with a one-line reason and the evidence source.
3. Use a cloud provider's Well-Architected framework as a review lens for missed concerns; check the provider's current pillar list rather than relying on memory.
4. Reject any option that fails a hard constraint (residency, regulatory, RTO) regardless of its total score. Weighted totals are for choosing among options that pass every hard constraint.
5. Record the result in the ADR, including why each rejected option lost.

## When Not to Run This

Skip full scoring for a single-team change or a cheap, reversible (two-way-door) decision. State the chosen option, the reversal path, and move on.
