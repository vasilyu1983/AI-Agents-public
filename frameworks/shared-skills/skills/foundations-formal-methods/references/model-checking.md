# Model checking and SAT/SMT

| Question | Suitable method | Interpretation boundary |
|---|---|---|
| Is a prohibited named state reachable in a complete finite graph? | Exhaustive reachability | All reachable states of this graph, not omitted executions |
| Do temporal properties hold? | Temporal model checker with stated semantics/fairness | Property and configuration checked; tool-dependent treatment of termination/stuttering |
| Is an encoded constraint satisfiable? | SAT/SMT | Witness or unsatisfiability for the encoding/theory; `unknown` is inconclusive |
| Is there a violating execution of length at most k? | Bounded model checking | No witness through k does not exclude a longer witness |
| Does the invariant hold for arbitrary system size? | Inductive/deductive argument or justified parameterized method | Requires proof obligations beyond finite instances |

Preserve tool output and inputs. Distinguish completed exhaustive search from timeouts or resource-limited exploration. A model constraint that prunes states is not automatically a faithful abstraction. Do not treat successful parsing as semantic verification.

For inductive invariants establish initial-state inclusion and preservation by every permitted transition. A property can hold on reachable states without being inductive over all states; strengthen it with justified supporting invariants if needed.

For SMT, report chosen theory, quantified versus quantifier-free encoding, bounds, assumptions, solver result, and witness interpretation. A solver's `unsat` result is conditional on the encoded problem. Unsat cores aid diagnosis; they are not themselves independent proofs of the intended requirements.

For a counterexample, record the initial state, each transition, the first failing property, and whether the trace is realizable. Correct an artifact with evidence and rerun; retain the original failure when comparing models.

Primary basis: Lamport, *Specifying Systems*, chapters 5, 8, 14; SMT-LIB language/theory documentation, [sources](../data/sources.json).
