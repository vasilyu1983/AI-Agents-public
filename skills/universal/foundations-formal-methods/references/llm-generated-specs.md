# Gate for LLM-generated specifications, invariants and proofs

Read this reference whenever a model has drafted or edited a spec, an invariant, a proof, a TLC/Apalache config or an SMT encoding. The checker is the only soundness anchor. A fluent explanation, a parse, or "the proof compiles" is not evidence that the intended property holds.

## Why the gate exists

Benchmarks show that specifications, and not only proofs, are the weak point:

- **VERINA** (arXiv:2505.23135, v3, 2026-03-16) has 189 Lean tasks. For its top-performing general-purpose model, OpenAI o3, the [Introduction](https://arxiv.org/html/2505.23135v3#S1) reports “72.6% correct code solutions, 52.3% sound and complete specifications, and 4.9% successful proof in one trial.”
- **Vericoding benchmark** (arXiv:2509.22908, 2025) has 12,504 formal specifications. With off-the-shelf LLMs, it reported success rates of 27% in Lean, 44% in Verus/Rust and 82% in Dafny. It also found that success on pure Dafny verification rose from 68% to 96% over one year.

These are benchmark figures for specific models and dates, not expected rates for your task. The direction is stable across both benchmarks: a generated artifact that verifies may still verify the wrong property.

## Characteristic failure modes

1. **Weakened or vacuous property.** The postcondition becomes `true`, an implication has an unreachable antecedent, or `<=` becomes "exists" or "some".
2. **Escape hatches.** The artifact proves the goal by trusting an unproved step:
   - Lean: `sorry`, `admit`, new `axiom`
   - Rocq: `Admitted`, `admit`, `Axiom`
   - Isabelle: `sorry`, `oops`
   - Dafny: `assume`, `{:axiom}`, `{:verify false}`, bodiless `{:extern}` methods
   - Verus: `assume`, `admit()`, `#[verifier::external_body]`
   - TLA+: new `ASSUME`, or `CONSTRAINT`/`ACTION_CONSTRAINT` in the config
3. **Over-constrained environment.** Failures, retries or concurrent actors are removed from `Next`, or a state constraint prunes the bug. Example: one worker instead of two hides the race in [agent-workflows.md](agent-workflows.md).
4. **Property edited to pass.** After a counterexample, the model "fixes" the invariant rather than the design.
5. **Autoformalization drift.** The natural-language requirement and the formal property differ in quantifier scope, time ("eventually" versus "always"), or which object is constrained. Parsing catches none of this.

## Protocol (run in order; any failure blocks acceptance)

1. **Freeze the property first.** A human writes or approves the natural-language requirement and the formal property before any model generates a design, proof or config. Store both with their hashes.
2. **Back-translate.** Have a separate pass, or a human, restate each formal property in plain language without seeing the original requirement. Compare the restatement with the requirement. Differences in quantifiers or time operators block acceptance.
3. **Scan for escape hatches.** Grep for the terms listed under failure mode 2. Fail on any new hit relative to the frozen baseline. Lean's `#print axioms <thm>` lists the axioms a theorem depends on; any dependence on `sorryAx` fails.
4. **Diff the property and the environment.**
   - Compare the invariants, `Next` disjuncts, fairness conditions, constants and constraints against the frozen version.
   - Any removed action, added constraint or weakened formula is a finding. It needs explicit human sign-off.
5. **Probe for vacuity.**
   - Assert the negation of each intended good outcome, for example `NeverDone`. The checker must find a trace for each one.
   - Check that the antecedent of each implication is reachable.
6. **Run a mutation check.** Seed a known bug, such as removing a lock, dropping the dedup check or allowing one more retry. The checker must fail. If it still passes, the property or the environment cannot see that bug class.
7. **Rerun the checker yourself.** Use a pinned tool version and record the result, with bounds, per the [verification report](../assets/verification-report.md). An LLM's claim that it ran the checker does not count as a run.
8. **Keep the claim in scope.** A verified generated spec is evidence about that spec. Code correspondence still needs the obligations in [refinement.md](refinement.md).

## Where an LLM genuinely helps

- Drafting a first spec from a design doc, provided a human reviews it at steps 1–2.
- Proposing candidate inductive invariants. The checker validates them, so a wrong candidate is cheap.
- Proof search against a frozen statement. The kernel checks every step, so the remaining risk is escape hatches (step 3), not unsound steps.
- Explaining a counterexample trace. Every claim in the explanation must be checked against the raw trace.

For planning-domain autoformalization (PDDL), use the equivalent gate in [foundations-ai-planning-search](../../foundations-ai-planning-search/SKILL.md).
