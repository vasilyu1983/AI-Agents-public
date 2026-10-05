# Tool selection: which method, at what cost, for which bug class

This skill owns method and tool selection, plus the meaning of each result. [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) owns the protocol case studies, deterministic simulation practice and Jepsen-style history checking. Tool URLs are listed in [sources](../data/sources.json). Release versions change; check the release page before pinning one.

## The ladder

Climb only as far as the bug class requires. Higher rungs can support stronger claims when their proof or search obligations complete; cost and coverage depend on the encoding and configuration.

| Rung | Tools | Bug class it catches | Claim it supports | When NOT to use it |
|---|---|---|---|---|
| 0. Types and contracts | Type system, assertions, runtime contracts | Local misuse and broken preconditions | Checked on the paths that execute | Never skip. Assertions are where an invariant found at a higher rung ends up in the code |
| 1. Property-based testing and fuzzing | Hypothesis, QuickCheck-family tools, coverage-guided fuzzers ([qa PBT reference](../../qa-testing-strategy/references/property-based-testing.md)) | Edge-case inputs and round-trip or model-equivalence failures | Found or not found in the sampled inputs | Rare interleavings, which random scheduling seldom hits |
| 2. Deterministic simulation | Seeded scheduler, clock, network and disk (see [distributed-systems](../../foundations-distributed-systems/SKILL.md)) | Interleaving and fault bugs in the **real code** | Found in the explored seeds; failures replay | When the code cannot run under a controlled scheduler, because retrofitting that is expensive |
| 3. Explicit-state model checking | TLA+/PlusCal with exhaustive TLC; PEx; this skill's [finite checker](finite-checker.md) | Design bugs in concurrency, failure and retry: races, lost updates, split brain | A completed exhaustive search covers the model within its constants; the finite checker covers state invariants only | When the design is not yet stable enough to write down, or the bug is in code rather than in the design |
| 3b. Symbolic or bounded model checking | Apalache (TLA+ via SMT; also the backend for Quint); Alloy 6 | The same classes, with larger or parametric data domains | Bounded checks cover the stated length; inductive claims need checked initialization, preservation and implication; Alloy complete temporal checks still bound signature sizes | When k cannot cover the bug depth; say so if it cannot |
| 4. SMT queries | Z3, cvc5 | Policy, configuration or permission equivalence; "can any input reach X?"; symbolic execution | `sat` gives a concrete witness. `unsat` holds for this encoding. `unknown` proves nothing | Quantified or nonlinear encodings that regularly return `unknown`. Use a bounded encoding or a different rung |
| 5. Bounded code verification | Kani (Rust), CBMC (C) | Overflow, panics, UB, and assertion failures in real code, up to loop bounds | No violation within the unwinding bounds | Unbounded loops or recursion, where the bounds hide the bug |
| 6. Deductive verification and proof assistants | Dafny, Verus (Rust), Lean 4, Rocq (formerly Coq), Isabelle/HOL; TLAPS for TLA+ | Anything expressible, for all sizes | Proved against the stated specification, trusting the kernel and axioms | Everywhere except a small, stable, high-value core. Proof effort grows with code churn |

Before interpreting a clean run, read the selected backend’s semantics:

- [P Checker](https://p-org.github.io/P/getstarted/usingP/) explores the requested schedules with a selected strategy. Record testcase, strategy, seed, schedule count and step bounds; it is not an exhaustive guarantee merely because it is called a checker. Use [PEx](https://p-org.github.io/P/advanced/pex/) when exhaustive exploration is intended, and confirm completion and configured bounds. Normal termination at a step limit still establishes only that bounded exploration.
- [Alloy 6](https://alloytools.org/alloy6.html) bounds signatures and, for bounded analysis, lasso-trace steps. Complete temporal checking requires `1.. steps` and a supporting backend; it removes the time bound, not the finite signature scope. Check the installed version’s time-scope default when the command omits it.
- [Apalache](https://apalache-mc.org/docs/apalache/running.html) bounded checking covers the requested length. Supplying a candidate inductive invariant is insufficient: check initialization, transition preservation and implication of the target safety property.

## Choose by the question being asked

- **"Is this concurrent or retry design correct?"** Use rung 3: TLA+/PlusCal with TLC, or P when engineers who own the service should also own the model and you want production trace checking later.
  - Start with the smallest constants that can express the bug: two concurrent actors for a race, one crash for a recovery bug. See [agent-workflows.md](agent-workflows.md).
- **"Does the real code have the interleaving bug?"** Use rung 2. If the scheduler cannot be controlled, check traces from real runs against a rung-3 model.
- **"Can any rule combination allow X?"** Use rung 4. Encode requests and rules, then assert X. The authorization and permission policies of AI agents belong here.
- **"Are these structural constraints consistent?"** Examples are schemas, permission lattices and ownership graphs. Use Alloy for small-scope instance finding, or TLA+ when the data is rich.
- **"Can this small core never fail?"** Examples are a parser, an authorizer and a crypto routine. Use rung 6 on the core, with differential random testing against the production code.
- **"Did the LLM's proof or spec pass?"** Apply [llm-generated-specs.md](llm-generated-specs.md) before trusting any rung.

## When formal methods pay, and when they do not

Climb to rung 3 or higher when **at least one** of these holds:

- Many interleavings or partial failures. Examples are replication, leases, retries with side effects, and multi-agent handoff.
- Security or authorization logic, where one reachable bad state is enough to cause harm.
- Irreversible side effects, such as money movement, deletion, or outbound messages.
- A planned aggressive optimization, such as removing a lock or splitting a transaction, on a design that already works.

Stay at rungs 0–2 when:

- The logic is sequential and its input space is well sampled by PBT.
- The design is still changing week to week. Write the prose design first.
- No one will own the model after the first pass.
- The risk sits in the code, and the model would only restate the code.

## Industrial evidence (read; figures as published)

- **Newcombe et al., "How Amazon Web Services Uses Formal Methods", *CACM* 58(4), 2015** (DOI 10.1145/2699417). The figures below were read in the authors' 2014 technical-report version (dated 29 September 2014).
  - TLA+ was used on 10 large complex systems, and 7 teams were using it at the time.
  - Engineers "from entry level to Principal" got useful results in 2–3 weeks.
  - In DynamoDB, the model checker found a data-loss bug whose shortest error trace had 35 high-level steps. The bug had passed design reviews, code reviews and testing.
  - The paper's table records a limitation: in one system, TLA+ "failed to find a liveness bug as we did not check liveness".
  - Asked how they know the code implements the verified design, the authors answer "we don't".
  - The authors found the Alloy of that time not expressive enough for rich data structures. Alloy 6 has since added mutable state and temporal logic ([Alloy 6 notes](https://alloytools.org/alloy6.html)); judge current Alloy on its own docs, not on this paper.
- **Brooker & Desai, "Systems Correctness Practices at Amazon Web Services", *CACM*, 2025** (DOI 10.1145/3729175; also ACM Queue, DOI 10.1145/3712057). Only the abstract-level scope is cited here; the full text has not been read.
  - AWS combines model checking, fuzzing, property-based testing, fault-injection testing, deterministic simulation, event-based simulation and runtime validation of execution traces.
  - Formal specifications serve as test oracles for these methods.
  - The [P case-study page](https://p-org.github.io/P/casestudies/) adds that P is used across storage, database and compute teams. It also says PObserve validates "structured service logs against P specifications post hoc".
  - Do not quote cost or benefit figures from this article until the full text has been read.
- **Disselkoen et al., "How We Built Cedar: A Verification-Guided Approach", arXiv:2407.01688, 2024.** The method has three parts:
  - an executable model with machine-checked proofs
  - differential random testing of the production code against the model
  - PBT for the parts that are not modeled

  Proofs found 4 bugs in the policy validator, and DRT and PBT found 21 more. This is the reference pattern for rung 6 when the production code is not itself verified.

## Result hygiene for every rung

- Record the tool name and version, the spec and config hashes, the constants or bounds, the property, the result, and the trace.
- Report "no error" together with the constants. A pass with one actor says nothing about races.
- A run that timed out or hit a resource limit is **inconclusive**, not a pass.
- Rerun after every model edit. Never edit the property to get a pass; see [llm-generated-specs.md](llm-generated-specs.md).
