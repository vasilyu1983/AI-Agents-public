# Certificates, tolerances, and solver status

For this skill's max-form LP, feasible witnesses satisfy `c^T x <= y^T Ax <= b^T y`. Thus the dual objective is an upper bound, and zero gap proves global optimality. For general convex problems, a suitable constraint qualification such as Slater's condition supports strong duality; convexity alone is not sufficient. KKT conditions are sufficient for differentiable convex problems; necessity needs appropriate regularity. A nonconvex stationary point alone is not a global certificate. Source: [Boyd–Vandenberghe duality lectures, sections 5.12–5.21](https://web.stanford.edu/class/ee364a/lectures/duality.pdf).

## Exact helper interface

```json
{"A":[[1,1],[1,0],[0,1]],"b":[4,2,3],"c":[3,2],"x":[2,2],"y":[2,1,0]}
```

Here `Ax = [4,2,2]`, `A^T y = [3,2]`, primal slacks `[0,0,1]`, dual slacks `[0,0]`, and both objectives 10. The exact helper reports zero gap and `optimal: true`. In contrast `x=[1,3]` is feasible with objective 9 and the same dual upper bound 10: gap 1 and no optimality certificate.

Schema: exactly five object keys; `A` is `m` rows of `n` scalars, with `m,n >= 1`; `b,y` have length `m`; `c,x` length `n`. Scalars may be integers, decimal JSON numbers, or decimal strings matching signed decimal/exponent notation. Booleans, null, nonfinite values, fraction strings, empty/ragged arrays, duplicate keys, and unknown keys are rejected. To bound parser resource use, scalar text is limited to 1000 characters and decimal exponent magnitude to 1000; larger values are rejected. Exact outputs use reduced strings such as `"1/10"` or `"10"`.

| Parser limit | Value |
|---|---|
| `scalar_characters` | 1000 |
| `decimal_exponent_magnitude` | 1000 |

Output fields: `primal_feasible`, `dual_feasible`, `optimal`, `primal_objective`, `dual_objective`, `gap` (dual minus primal), `primal_slacks` (`b-Ax`), `dual_slacks` (`A^Ty-c`), `primal_violations` and `dual_violations` (indexed violated nonnegativity/constraint names). A negative gap between failed witnesses has no bound interpretation.

## Floating-point solvers

External solvers use tolerances. Evaluate residuals in original units, record feasibility/integrality tolerances and scaling, and inspect solution quality after termination. A small objective gap does not excuse a large constraint violation. Exact rational checking of rounded output can fail even when the floating-point run met its tolerance; disclose the different claims. Source: [Gurobi constraints documentation](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/constraints.html).

Report the actual stopping status. A time limit may have an incumbent, no incumbent, or a useful bound; it is not synonymous with solved. “Infeasible or unbounded” is unresolved, and numerical failure is not an infeasibility proof. A solver's “optimal” is subject to its tolerances. Source: [Gurobi status documentation](https://docs.gurobi.com/projects/optimizer/en/current/reference/numericcodes/statuscodes.html), verified 2026-09-17.

For MILP record incumbent, best bound, absolute gap and solver-defined relative gap (including its zero-objective convention). This bundle's helper does not check integrality or branch-and-bound proofs. Sensitivity multipliers are not automatically valid discrete shadow prices; perturb and resolve where necessary.
