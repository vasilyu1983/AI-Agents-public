---
name: foundations-formal-methods
description: Specify invariants, safety/liveness properties, model checking, SAT/SMT, and refinement. Use when a system needs explicit verification claims and counterexamples.
version: "1.0"
last_validated: 2026-09-17
---

# Formal Methods Foundations

Turn a requirement into a checkable property and report precisely what the evidence establishes. A verified finite abstraction is evidence about that abstraction; implementation correctness needs a demonstrated correspondence.

## When to use

**Triggers**: “prove this invariant”, “model check this workflow”, “safety versus liveness”, “temporal specification”, “SAT/SMT verification”, “refinement mapping”, “find a counterexample”.

A routine unit-test request belongs to testing; protocol design belongs to distributed systems. Use this skill when the specification, formal property, or verification boundary is the central question.

## Quick Reference

| Need | Resource |
|---|---|
| Define a property | [Specification](references/specification.md) |
| Choose verification method | [Model checking](references/model-checking.md) |
| Connect model to code | [Refinement](references/refinement.md) |
| Check an explicit graph | [Finite checker](references/finite-checker.md) |

## Workflow

1. Name the requirement, prohibited or required behavior, environment, and observed interface. Distinguish state safety, temporal safety, liveness, and performance requirements. Read [specification.md](references/specification.md).
2. Define the initial states, state variables, transitions, atomicity, and environment assumptions. Include failures and concurrency relevant to the property. Track each abstraction and omitted behavior.
3. Select a method from [model-checking.md](references/model-checking.md): explicit finite reachability for invariants, temporal model checking for temporal properties, SAT/SMT for encoded constraints, or deductive proof for unbounded claims. State scope and tool limitations before interpreting results.
4. Execute the selected check if feasible. Preserve model/input, configuration, tool identity, property, result, and trace. Inspect counterexamples against requirements: they may expose a system defect, an abstraction artifact, or an erroneous property.
5. For claims about deployed code, read [refinement.md](references/refinement.md) and identify correspondence obligations. Generated specifications require semantic review even when parsing succeeds.
6. Produce [verification-report.md](assets/verification-report.md). Use “holds in this finite model”, “counterexample found”, or “inconclusive” rather than upgrading a bounded/model result to general correctness.

## Lightweight finite checker

Use [scripts/check_finite_model.py](scripts/check_finite_model.py) only for an explicit, fully enumerated finite graph and state invariant. Read its [input/output contract](references/finite-checker.md).

```bash
python3 scripts/check_finite_model.py model.json
python3 scripts/check_finite_model.py - < model.json
python3 scripts/test_check_finite_model.py
```

The helper evaluates reachable state membership, returns a deterministic shortest violating trace, and lists reachable terminal states neutrally. It does not interpret formulas, infer missing transitions, check liveness, or prove code correspondence. Terminal states can be intended completion; call them deadlocks only when the specification requires an enabled transition.

## Assumptions and pitfalls

- An invariant must hold in initial states as well as after transitions. An unreachable prohibited state is not a violation of reachable-state safety.
- Stuttering, action granularity, scheduling, and fairness can change temporal claims. Safety success cannot establish eventual completion.
- A bounded SAT/SMT `unsat` result excludes counterexamples only within its encoding/bound. `unknown`, timeouts, and partial searches establish no absence claim.
- A satisfiable formula is a witness for its encoded constraints, not automatically an execution; inspect encoding and decode the witness.
- Symmetry reduction, constraints, abstractions, and omitted failures need justification relative to each property.
- A proof of a wrong specification does not establish the intended requirement. Check requirements and implementation mappings separately.

## Fact-Checking

Verify tool semantics against current primary documentation when using an external checker. Sources below were checked on 2026-09-17. Do not present generated claims, parser success, or bounded searches as proof beyond their stated evidence.

## Completion criteria

A useful result identifies the property, model, assumptions, method, bounds, evidence, counterexample status, and conformance gap. Report verification failures directly; do not silently weaken properties to make a check pass.

## Navigation

- [Specification](references/specification.md) — requirements, invariants, temporal properties, and nonvacuity.
- [Model checking and SAT/SMT](references/model-checking.md) — method choice, bounded results, and counterexamples.
- [Refinement](references/refinement.md) — mapping models to requirements and implementations.
- [Finite checker contract](references/finite-checker.md) — strict JSON schema and deterministic outputs.
- [Verification report](assets/verification-report.md) — output worksheet.
- [Sources](data/sources.json) — primary materials checked on 2026-09-17.
