# Integration And Boundary Patterns

Choose integration style based on ownership, latency, coupling, and failure tolerance.

## Decision Matrix

| Situation | Default pick | Why | Watch out for |
|----------|--------------|-----|---------------|
| Browser/mobile-specific aggregation | BFF or gateway aggregation | Keeps channel needs out of core services and limits over-fetching | Turning the BFF into domain logic |
| Request/response requiring an immediate result | HTTP API (REST or GraphQL) | Caller needs the result to proceed; explicit latency contract | Hidden retries, timeouts, and chatty call graphs |
| Cross-domain propagation or fan-out | Events | Decouples producers and consumers | Weak ownership, replay gaps, and unclear delivery semantics |
| Legacy/vendor coexistence with semantic mismatch | Anti-corruption layer | Protects the new model from upstream semantics | Rate limits alone call for throttling or buffering; plan ACL retirement when temporary |
| Scheduled bulk exchange with latency tolerance | File or batch interface | Avoids forcing realtime on bulk movement | Missing reconciliation, delayed failure detection |
| External provider pushes callbacks | Inbound webhook plus idempotency | Source owns event timing | Duplicate deliveries and partial side effects |
| Your system pushes changes to external consumers | Outbound webhook | Receivers need timely updates without polling | Receiver outages, retries, signing and replay protection |

## Boundary Heuristics

- Use APIs when the caller needs immediate answer semantics.
- Use events when the main need is propagation, not immediate confirmation.
- Use an anti-corruption layer when one side should not inherit the other's model.
- Keep BFFs outside core bounded contexts; they are solution-shaping edges, not domain cores.
- Avoid shared databases as an integration strategy.

## Selection Questions

- Which side owns the business deadline for success or failure?
- Is the boundary crossing a trust, tenant, compliance, or vendor seam?
- Does the caller need an answer now, or only durable propagation?
- Can the downstream system tolerate replay, delay, or duplicate delivery?
- Is this boundary temporary for migration, or permanent in the target state?

## Failure Questions

- What happens when the dependency is slow or unavailable?
- Which side owns retries and idempotency?
- Can messages be replayed safely?
- Does the integration cross a trust or compliance boundary?
