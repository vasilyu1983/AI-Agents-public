# Refinement and implementation correspondence

State the concrete-to-abstract mapping. Show that concrete initial states map to abstract initial states and concrete steps map to permitted abstract behavior, including justified stuttering. For temporal claims, account for fairness and progress rather than importing a safety-only simulation argument.

Example: implementation states `queued`, `executing`, `persisted`, `acknowledged` map to abstract `pending`, `pending`, `committed`, `committed`. This mapping can hide the persistence/acknowledgement distinction. If the requirement is “acknowledge only after persistence”, retain history or a separate state variable so the check can distinguish an early acknowledgement. A coarse mapping can erase the very defect under review.

Review correspondence at three separate levels:

1. Requirement → formal property: meaningful triggers, relevant losses/outputs, no unintended weakening.
2. Implementation → model: atomicity, failure semantics, retry/concurrency behavior, data bounds, omitted components.
3. Verification artifact → stated conclusion: completed method, exact property/configuration, bounds, trusted tool assumptions.

Generated specifications deserve these same checks. Compilation/parsing catches syntax errors; it does not establish intended semantics. Differential execution, trace replay, or conformance tests provide empirical correspondence evidence, but do not alone prove all implementation behaviors refine the model.

Primary basis: Lamport, *Specifying Systems*, chapters 5, 8, 10; [sources](../data/sources.json).
