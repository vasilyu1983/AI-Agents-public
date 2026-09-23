# Formulation and method selection

Specify variables before equations. A quantity of divisible material can be continuous; a server, job, or mutually exclusive project often requires integer/binary choices. List capacity, budget, precedence, exclusivity, and time-index constraints separately. Confirm whether unused capacity is allowed and whether startup costs apply. Penalizing a violation makes it a soft constraint; it does not enforce a hard requirement.

| Form | Appropriate evidence |
|---|---|
| LP: linear objective/constraints, continuous variables | Primal feasibility plus a dual bound; matching witnesses certify global optimality |
| Convex QP: minimize a quadratic with positive-semidefinite Hessian over a convex domain | Valid convexity argument and appropriate optimality certificate |
| Conic: affine mapping into convex cones | Cone membership plus justified primal/dual certificate conditions |
| MILP: linear model with integer/binary variables | Feasible integer incumbent, global bound, and stated gap/termination |
| Nonconvex continuous model | Distinguish local stationary points, heuristics, and globally certified bounds |

An apparent convex expression can become nonconvex through equality or direction changes. Equality constraints in a standard convex model are affine. For maximization, the objective must be concave. Sources: [Boyd–Vandenberghe problem formulations, sections 4.2–4.6](https://web.stanford.edu/class/ee364a/lectures/problems.pdf).

Check proxy objectives against the actual outcome: minimizing latency alone can violate quality, fairness, or capacity requirements. Report a Pareto tradeoff or constrained objective when weights have not been agreed. Do not invent utility weights.

## Counterexample: ratio ranking with indivisible choices

Capacity 10; three items have `(size,value)` of `(6,12)`, `(5,9)`, `(5,9)`. Descending value/size selects the first for value 12; selecting the second and third gives 18. Enumerating these eight binary combinations certifies 18. A greedy ratio rule is valid for divisible fractional knapsack, not general binary knapsack or multiple-resource allocation.

Use explicit binary domains in the original formulation. An LP relaxation can give a bound but may propose fractional items; rounding can violate constraints or discard the optimum. Derive a tight valid big-M bound from the domain when encoding logic; an arbitrary large constant can weaken bounds and numerical behavior. Prefer a supported indicator formulation when it fits the chosen solver.
