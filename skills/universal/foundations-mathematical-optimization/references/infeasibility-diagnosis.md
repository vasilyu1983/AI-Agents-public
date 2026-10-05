# Infeasibility, unboundedness, and numerical failure

A status is a claim with conditions. First decide which of these you actually have, then diagnose.

## Triage order

1. **Read the exact status.** Gurobi statuses (quoted from the status-code page; re-read it for your version):
   - INFEASIBLE: "Model was proven to be infeasible."
   - INF_OR_UNBD: proven infeasible *or* unbounded. Gurobi's remedy: "set the DualReductions parameter to 0 and reoptimize." This separates the two cases.
   - UNBOUNDED: an improving ray exists. It "says nothing about whether the model has a feasible solution". To check feasibility, set the objective to zero and reoptimize.
   - NUMERIC: stopped on numerical difficulties. It is not an infeasibility proof.
   - LOCALLY_INFEASIBLE (nonlinear barrier; check whether your version still marks it preview): "appears to be locally infeasible". It is not a proof.
   - CP-SAT UNKNOWN: no solution was found *and* infeasibility was not proven. It is not "infeasible" ([scheduling-cp-sat.md](scheduling-cp-sat.md)).
   - HiGHS reports `kUnboundedOrInfeasible` as a separate model status. No HiGHS source for the remedy was read here; check the HiGHS docs for your version. A common first try is to rerun with presolve off.
2. **Validate the data before blaming the model.** Check units, signs, missing rows that became zero capacity, demand greater than total capacity, and empty time windows. Most real infeasibility is a data or indexing error.
3. **Isolate the conflict with an IIS.** An irreducible inconsistent subsystem is a set of constraints and bounds that is infeasible on its own and becomes feasible if any member is removed.
   - Gurobi: `Model.computeIIS()`. The vendor warns that "the MIP version can be quite expensive".
   - HiGHS: `Highs.getIis()`. In one local run on a toy LP (`x+y>=12, x<=3, y<=4`, plus one harmless row), the default strategy returned an empty IIS, and setting `iis_strategy` to `IisStrategy.kIisStrategyIrreducible` returned exactly the three conflicting rows. The default may differ in your version; check which strategy you ran before concluding anything.
   - An IIS is one conflict, not necessarily the only one. Fix it, re-solve, and repeat.
4. **Measure the minimum violation (elastic or slack reformulation).** Add a nonnegative slack to each soft-candidate constraint, penalize it in the objective, and read which slacks are nonzero.
   - Gurobi `feasRelax` does this. Its routines are "destructive": they modify the model, so run them on a copy. It offers three penalties: the sum of violations, the sum of squared violations, or the count of violated constraints (binary).
   - Only relax constraints that a stakeholder agrees can bend. Relaxing a legal or physical limit produces an unusable plan.
   - Ship the relaxation as a proposal ("feasible if budget +7%"), not as the solution to the original problem.
5. **Unbounded.** Look for a missing bound, a wrong objective sign, or a cost that should be positive. Real resources are bounded, so a real model should not be unbounded.

## Numerics and scaling

- Big-M constants far larger than the variable's real bound cause trouble. A binary at 1e-6 can then "switch on" a constraint within the integrality tolerance. Derive M from the domain, or use indicator constraints ([mip-formulation-and-multiobjective.md](mip-formulation-and-multiobjective.md)).
- Rescale units so coefficients sit within a few orders of magnitude (for example, thousands of dollars rather than cents, when cents are not decision-relevant). Record the scaling and map the results back.
- After any solve, recompute residuals in original units ([certificates-and-status.md](certificates-and-status.md)). A solver "optimal" that violates a constraint by more than the business tolerance is a failure.
- Reoptimizing with different seeds or methods and getting different feasibility verdicts is a symptom of numerical trouble, not of luck.

Sources: [Gurobi status codes](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html), [Gurobi infeasibility analysis](https://docs.gurobi.com/projects/optimizer/en/current/features/infeasibility.html), [HiGHS advanced features: IIS](https://ergo-code.github.io/HiGHS/dev/guide/advanced/).
