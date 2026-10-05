---
name: foundations-formal-methods
description: Proves protocols and agent workflows with TLA+, P, Alloy, Z3, Dafny, or Lean. Use when proving protocols correct, writing TLA+ specs, or verifying LLM proofs.
version: "1.1"
last_validated: 2026-09-17
---

# Formal Methods Foundations

Turn a requirement into a checkable property, pick the cheapest method that can catch the bug class, and report precisely what the evidence establishes. A verified finite abstraction is evidence about that abstraction; implementation correctness needs a demonstrated correspondence.

## When to use

**Triggers**: "prove this protocol is correct", "write a TLA+ / PlusCal spec", "model check this workflow", "find a race condition formally", "verify with Z3 / cvc5 / Lean / Dafny / Verus", "TLA+ or property-based testing?", "check this LLM-generated proof or spec", "can any policy combination allow X", "safety versus liveness", "refinement mapping", "find a counterexample".

**Not this skill**:

- Routine unit tests or PBT harnesses belong to [qa-testing-strategy](../qa-testing-strategy/SKILL.md).
- Consensus, replication and lease design, deterministic simulation, and Jepsen histories belong to [foundations-distributed-systems](../foundations-distributed-systems/SKILL.md).
- Hazard analysis of agent actions belongs to [foundations-safety-engineering](../foundations-safety-engineering/SKILL.md).

Use this skill when the specification, the choice of verification method, or the meaning of a result is the central question.

## Quick Reference

Method ladder (full version in [tool-selection.md](references/tool-selection.md)):

| Bug class | Cheapest adequate rung | Result means |
|---|---|---|
| Edge-case inputs, sequential logic | Property-based testing or fuzzing | Found or not found in the sampled inputs |
| Rare interleavings in real code | Deterministic simulation | Found in the explored seeds |
| Design races, retries, failures, handoffs | TLA+/PlusCal (TLC), P, Alloy 6; Apalache for symbolic checks | Completed exhaustive checks cover the finite model; P schedule testing and bounded symbolic checks cover only their reported exploration |
| Policy or config equivalence; "can any input reach X" | SMT (Z3, cvc5) | `sat` gives a witness; `unsat` holds for the encoding; `unknown` proves nothing |
| Small high-value core, all sizes | Dafny, Verus, Lean 4, Rocq, Isabelle | Proof against the stated spec and trusted base |

Climb past PBT only for interleaving-heavy designs, authorization logic, irreversible side effects, or aggressive optimizations. For costs, when NOT to climb, and industrial evidence, read [tool-selection.md](references/tool-selection.md).

## Workflow

1. **State the requirement.**
   - Name the requirement, the prohibited or required behavior, the environment, and the observed interface.
   - Classify it as state safety, temporal safety, liveness, or a performance requirement. Read [specification.md](references/specification.md).
2. **Build the model.**
   - Define initial states, variables, transitions, atomicity, and environment assumptions, including the failures and concurrency the property depends on.
   - Choose constants large enough to express the bug class. Two concurrent actors is the minimum for a race.
   - Track every abstraction and every omitted behavior.
3. **Pick a rung.** Use [tool-selection.md](references/tool-selection.md) and [model-checking.md](references/model-checking.md). State the scope and tool limits before interpreting any result.
4. **Run the check.**
   - Preserve the model, config, tool version, property, result, and trace.
   - Triage each counterexample: it is a system defect, an abstraction artifact, or a wrong property.
   - Add vacuity probes: the good path must be reachable.
5. **Gate LLM output.** If a model drafted or edited the spec, invariant, proof, or config, run the gate in [llm-generated-specs.md](references/llm-generated-specs.md) before accepting any result.
6. **Tie the claim to code.** For claims about deployed code, read [refinement.md](references/refinement.md) and name the correspondence obligations. Trace conformance is the practical bridge.
7. **Report.** Produce the [verification-report.md](assets/verification-report.md). Use "holds in this finite model", "counterexample found", or "inconclusive". Never upgrade a bounded or model result to general correctness.

## Agent-shaped worked example

[agent-workflows.md](references/agent-workflows.md) holds a TLC-checked spec of an idempotent tool call with retries ([spec](assets/tla/IdempotentRetry.tla), [TLC config](assets/tla/IdempotentRetry.cfg)). It shows three things:

- A check-then-act race that TLC finds only with two workers, so a one-worker model gives a false "holds".
- A phantom-acknowledgement bug introduced by the first fix.
- The protocol that passes both invariants, with vacuity probes.

The same reference covers approval gates bound to argument hashes, cancellation, leases, and policy-as-SMT.

## Lightweight finite checker

[scripts/check_finite_model.py](scripts/check_finite_model.py) checks a state invariant over an explicit, fully enumerated finite graph and returns the shortest violating trace. It does not check liveness or code correspondence. For the contract and tests, see [finite-checker.md](references/finite-checker.md). Run it with `python3 scripts/check_finite_model.py model.json`.

## Assumptions and pitfalls

- An invariant must hold in initial states as well as after transitions. An unreachable prohibited state is not a violation of reachable-state safety.
- Stuttering, action granularity, scheduling, and fairness can change temporal claims. Safety success cannot establish eventual completion.
- A bounded SAT/SMT `unsat` result excludes counterexamples only within its encoding and bound. `unknown`, timeouts, and partial searches establish no absence claim.
- A satisfiable formula is a witness for its encoded constraints, not automatically an execution. Inspect the encoding and decode the witness.
- Symmetry reduction, constraints, abstractions, and omitted failures each need justification relative to each property. Undersized constants hide races.
- A proof of a wrong specification does not establish the intended requirement. Check requirements and implementation mappings separately.
- Verify tool semantics and versions against the tool's current primary documentation before treating them as current. Quote benchmark figures with model, version, and date. Do not present generated claims, parser success, or bounded searches as proof beyond their stated evidence.

## Completion criteria

A useful result identifies:

- the property and the model
- the assumptions and the method or tool, with its version
- the bounds and constants
- the evidence and the counterexample status
- the vacuity probes
- the conformance gap

Report verification failures directly, and never silently weaken a property to make a check pass.

## Navigation

- [Tool selection](references/tool-selection.md): the method ladder, cost and benefit, when NOT to use formal methods, and industrial evidence.
- [LLM-generated specs and proofs](references/llm-generated-specs.md): the acceptance gate, escape-hatch scan, vacuity and mutation checks, and benchmarks.
- [Agent workflows](references/agent-workflows.md): the TLC-checked idempotent-retry example and agent protocol properties.
- [Specification](references/specification.md): requirements, invariants, temporal properties, and nonvacuity.
- [Model checking and SAT/SMT](references/model-checking.md): method choice, bounded results, and counterexamples.
- [Refinement](references/refinement.md): mapping models to requirements and implementations.
- [Finite checker contract](references/finite-checker.md): the strict JSON schema and deterministic outputs.
- [Verification report](assets/verification-report.md): the output worksheet.
- [Sources](data/sources.json): primary materials behind each tool, benchmark and industrial claim.

## Related skills

- [foundations-distributed-systems](../foundations-distributed-systems/SKILL.md): protocol case studies, deterministic simulation, and Jepsen/Elle.
- [foundations-safety-engineering](../foundations-safety-engineering/SKILL.md): STPA hazards for agents, and safety cases that cite verification evidence.
- [foundations-ai-planning-search](../foundations-ai-planning-search/SKILL.md): the LLM-as-formalizer gate for PDDL.
- [qa-testing-strategy](../qa-testing-strategy/references/property-based-testing.md): property-based testing, the lowest rung.
- [agents-subagents](../agents-subagents/SKILL.md): handoff, cancellation, and retry protocols to model.
