# Uncertain engineering-work cost

Use this recipe after the dependency plan and verification gates are explicit, when uncertainty in review, rework, or execution volume could change staffing or budget. It estimates delivery cost; it does not infer elapsed time or the critical path.

1. Keep ordinary arithmetic for fixed work. Otherwise define independent inputs such as work-item count, implementation hours per item, review hours per item, rework multiplier, and loaded hourly rate. Give each a finite range, unit, dated source, provenance kind, and reason for its distribution.
2. Preserve observed pairing where it matters. For example, resample complete historical rows containing change size, review time, and rework together. Do not independently shuffle columns and erase their dependence.
3. Express each cost term explicitly: implementation, review, verification, migration, and contingency. Keep provider spend or external fees as separate terms.
4. Set the decision budget and the numerical precision that could change the staffing or scope call. Interpret quantiles and modeled budget-exceedance probability as conditional on the planning model.
5. Compare the result with the deterministic plan and low/base/high bounds. Stop if the plan's dependencies or units are unresolved, or if assigned probabilities are only narrative confidence.

Optional navigation: when the `ops-cost-optimization` bundle is available, its `scripts/cost_uncertainty.py` runner and `assets/cost-uncertainty-example.json` implement this contract. The planning bundle remains usable without that runner: record the inputs and scenarios in the plan artifact and do not claim a simulation result.

Morris screening can rank independently varied continuous assumptions such as review hours and rework multiplier. It is screening across the specified ranges, not schedule causality or Sobol variance attribution. Do not apply it to paired empirical scenarios.
