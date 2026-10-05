# Specification and property classification

Record the externally visible requirement before choosing notation. A transition system has initial states and a next-state relation; nondeterminism represents alternative behavior, not a probability distribution.

A state invariant is a predicate true in every reachable state. Temporal safety excludes bad behavior prefixes (for example, an acknowledgement before persistence); an appropriate state model can encode relevant history. Liveness requires something eventually to occur, such as eventual response to each request. A finite prefix normally cannot establish a liveness violation without additional reasoning about infinite continuations. State invariants alone do not verify liveness.

Specify environment assumptions: allowed inputs, failures, concurrency, scheduling, and resource bounds. Fairness is an assumption or established implementation property, not something supplied by the word “eventually”. Weak and strong fairness impose different scheduling obligations; choose them per action, and justify the actual scheduler relationship. Do not add fairness merely to hide possible starvation.

Check nonvacuity: at least one initial state exists; antecedents such as “request received” are reachable; environmental restrictions do not exclude the failures the requirement addresses. State what counts as completion so intended terminal states are not misreported as faults.

## Worked specification

For a task with states `idle`, `running`, `done`, and `lost`, use initial state `idle`, transitions `idle→running`, `running→done`, `running→lost`, and allowed invariant states `idle`, `running`, `done`. The trace `idle→running→lost` violates “task state never lost”. Removing the lost transition changes the model; whether removal is justified is a requirements question.

## Counterexample to overclaiming

`idle→running` with a `running→running` self-loop satisfies the allowed-state invariant but permits infinite running. “Every started task completes” needs a temporal property and suitable assumptions. The invariant check does not establish it.

Primary basis: Lamport, *Specifying Systems*, chapters 2, 7, and 8; source and verification date in [sources](../data/sources.json).
