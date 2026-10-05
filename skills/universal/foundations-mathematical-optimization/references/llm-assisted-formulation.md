# LLM-assisted formulation: draft, solve, validate

An LLM can draft variables, constraints, and solver code from a natural-language spec. The solver then certifies optimality *for the drafted model*, not for the spec. The weak link is fidelity, so validation must not reuse the drafting LLM's own reading of the spec.

## Loop

1. **Spec to structured contract.** Before any code, have the LLM fill in the [optimization contract](../assets/optimization-contract.md): variables with units and domains, objective direction, hard versus soft constraints, and data sources. A human or a separate reviewer approves this contract.
2. **Draft the model and code.** Keep the data out of the prompt where possible: pass parameter names and let the code load the data. That keeps long instances out of context.
3. **Solve** with an exact solver ([solver-selection.md](solver-selection.md)). Record the status, objective, bound, and gap.
4. **Validate independently.** Each check below catches a different error.
   - **Residual recomputation:** a separate script, not the solver's report, recomputes the objective and every constraint in original units from the returned decision values.
   - **Brute-force a toy instance:** shrink to a size you can enumerate (as with the knapsack counterexample in [formulation-and-methods.md](formulation-and-methods.md)) and compare the optima.
   - **Back-translation:** a fresh model or reviewer turns the code back into prose. Diff that prose against the original spec, looking for missing constraints, flipped signs, and wrong index ranges.
   - **Perturbation:** tighten a constraint from the spec and confirm that the objective moves in the expected direction.
   - **Infeasible or unbounded results:** follow [infeasibility-diagnosis.md](infeasibility-diagnosis.md). Do not let the LLM "fix" infeasibility by silently dropping constraints. Every relaxation needs sign-off.
5. **Iterate** on the failed checks. Keep a log of each fix for review.

## Evidence and caveats

- OptiMUS-0.3 (AhmadiTeshnizi et al., arXiv 2407.19633) is an LLM system that "can develop mathematical models, write and debug solver code, evaluate the generated solutions" and iterate on evaluation feedback. It uses a modular structure so long descriptions and data do not need long prompts. The authors report that "system architecture is a stronger driver of performance than model capability". Read the paper before quoting its benchmark percentages.
- A 2025 survey of LLMs for optimization modeling (Xiao et al., arXiv 2508.10047) analyzed benchmark quality and found "a surprisingly high error rate" in the datasets. The per-benchmark error percentages were not checked against the paper; read it before quoting any. A high score on a published natural-language-to-model benchmark is weak evidence that your formulation is correct.
- When NOT to use this loop: safety-critical or regulated allocations with no human model reviewer, or specs whose objective is still disputed. Resolve the preferences first.

Sources: [arXiv 2407.19633](https://arxiv.org/abs/2407.19633) and [arXiv 2508.10047](https://arxiv.org/abs/2508.10047); only the abstracts were read.
