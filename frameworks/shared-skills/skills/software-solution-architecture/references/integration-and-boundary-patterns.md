# Integration And Boundary Patterns

Choose integration style based on ownership, latency, coupling, and failure tolerance.

## Decision Matrix

| Situation | Default pick | Why | Watch out for |
|----------|--------------|-----|---------------|
| Client-specific aggregation | BFF or gateway aggregation | Keeps channel needs out of core services | Turning the BFF into domain logic |
| Internal request/response with tight correctness needs | HTTP API | Clear contract, simpler debugging | Hidden retries, timeouts, and chatty call graphs |
| Cross-domain propagation and loose coupling | Events | Decouples producers and consumers | Weak ownership, replay gaps, and unclear delivery semantics |
| Legacy coexistence with semantic mismatch | Anti-corruption layer | Protects the new model from legacy contamination | ACLs that become permanent because retirement was never planned |
| Low-frequency bulk exchange | File or batch interface | Often cheaper and simpler than forcing realtime | Missing reconciliation, delayed failure detection |
| External provider callbacks | Webhook boundary plus idempotency | Matches provider shape while containing side effects | Duplicate deliveries and partial side effects |

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
