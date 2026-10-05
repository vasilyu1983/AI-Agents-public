# Solver and technique selection

Choose the model class first ([formulation-and-methods.md](formulation-and-methods.md)), then the solver. A solver switch never fixes a wrong formulation.

## Decision table

| Problem shape | Default choice | Escalate when | Evidence it can give |
|---|---|---|---|
| LP, continuous, linear | HiGHS (open source, via `highspy`, SciPy, Pyomo, linopy) | Very large LP where moderate accuracy is acceptable: a first-order method (PDLP/PDHG); state its looser accuracy | Primal/dual solution; check with [certificates-and-status.md](certificates-and-status.md) |
| MILP, mostly linear with binaries/integers | HiGHS or SCIP | The gap or time limit binds on real instances: commercial MIP (Gurobi, others), after tightening the formulation | Incumbent, best bound, gap |
| Scheduling, sequencing, assignment with logical side rules, all-integer data | OR-Tools CP-SAT | Large continuous parts or a tight LP relaxation: MIP instead | FEASIBLE/OPTIMAL status and objective bound; see [scheduling-cp-sat.md](scheduling-cp-sat.md) |
| Convex QP / SOCP / SDP | CVXPY as the modeling layer (checks convexity rules), with a conic/QP backend | CVXPY rejects the expression as non-DCP: reformulate, do not force it | Convexity by construction, solver status |
| Nonconvex continuous (NLP) | A local NLP solver with multistart | A global claim is needed: a global solver (for example SCIP or Gurobi for supported nonlinear forms), and expect it to be slow | Local: stationary point only. Global: bound and gap |
| Black-box objective, simulation, no model | Metaheuristic (local search, evolutionary) or Bayesian optimization | Anything can be modeled explicitly: model it | No optimality evidence; report as heuristic |

Decision rules:

- Prefer an exact solver with a bound when an explicit model exists. A metaheuristic gives no bound, so its result is only a "candidate" in the [optimization contract](../assets/optimization-contract.md).
- Tighten the formulation ([mip-formulation-and-multiobjective.md](mip-formulation-and-multiobjective.md)) before buying a faster solver. A weak big-M model stays weak on every solver.
- Fix the time limit and acceptable gap before solving, and report both.
- Keep the model in a solver-neutral layer (Pyomo, linopy, CVXPY, or OR-Tools MathOpt) when you may switch solvers. Then a solver comparison is a configuration change.
- Do not choose a solver from a vendor's own benchmark alone. Run your instance family on each candidate under the same time limit.
- When NOT to optimize: few options that can be enumerated (enumerate them), or disputed objectives (settle the preferences first with decision theory).

## Versions and new features (look up, do not assume)

This file pins no solver version. Before relying on a feature, read the package's release notes or PyPI page (`https://pypi.org/pypi/<package>/json` gives the current release) for the version you actually run:

- Gurobi (`gurobipy`): whether a first-order PDHG LP method or a local nonlinear barrier exists, and whether statuses such as LOCALLY_OPTIMAL/LOCALLY_INFEASIBLE are still marked preview.
- HiGHS (`highspy`): parallel MIP, interior-point support for convex QP, and GPU first-order LP support.
- OR-Tools (`ortools`), CVXPY, PySCIPOpt (and the SCIP version it bundles), Pyomo: API changes between releases.

First-order LP (PDLP/PDHG) accuracy versus speed: no primary benchmark was read for this bundle. Do not quote a speedup; measure on your own instances and check residuals at the tolerance you need.
