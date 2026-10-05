# Solution Blueprint

Use this as the final answer shape for cross-system solution recommendations.

- **Problem and scope:** Business scenario, systems in scope, and what is intentionally out of scope
- **Current state:** Pain points, hard dependencies, manual seams, and non-negotiable constraints
- **Capability and ownership map:** Teams, systems of record, trust boundaries, and approval boundaries
- **Options considered:** 2-3 viable landscape options with the rejected alternatives explained
- **Recommended target state:** System landscape, responsibilities, and why this option wins
- **Interim state:** Temporary architecture that is acceptable during migration, if needed
- **Integration boundaries:** API, event, file, webhook, BFF, ACL, or batch boundaries plus owners
- **Data movement:** Sources of truth, projections, synchronization, replay, reconciliation, and audit needs
- **Migration waves:** Ordered slices, validation gates, rollback points, and retirement criteria
- **Risks and failure modes:** Business, technical, compliance, vendor, and rollout risks
- **What not to decide here:** Runtime topology, service-internal patterns, or implementation-level tradeoffs for handoff
- **Success metrics:** Business outcome, lead time, reliability, operational burden, and migration progress
