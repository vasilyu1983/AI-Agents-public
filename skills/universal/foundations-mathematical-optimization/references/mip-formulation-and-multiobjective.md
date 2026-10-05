# MIP formulation strength and multiple objectives

## Formulation strength

Different MILPs can have the same integer solutions but different LP relaxations. A tighter relaxation gives a better bound, a smaller gap, and less branching. Check strength before tuning a solver.

**Big-M worked example (LP relaxation solved by hand).** A fixed-charge facility has open cost 100, one unit of cost per unit shipped, and demand 5 (`x >= 5`, `0 <= x <= 5`). Linking constraint: `x <= M*y`, with binary `y`.

| M | LP-relaxation bound | Integer optimum | Relative gap at the root |
|---|---|---|---|
| 1000 | 5.5 (`y = 0.005`) | 105 | about 95% |
| 5 (the real upper bound on `x`) | 105 (`y = 1`) | 105 | 0 |

The loose M lets the relaxation "open 0.5% of a facility". Use the tightest M valid for the domain: the variable's own upper bound, or a bound derived from capacity or demand.

Decision rules:

- **Derive M, never guess it.** When no finite bound exists, use an indicator constraint (Gurobi: "if the binary indicator variable y equals f, then a^T x <= b must hold"; CP-SAT: `only_enforce_if`) or restructure the model. A huge M also causes numerical errors ([infeasibility-diagnosis.md](infeasibility-diagnosis.md)).
- **Disaggregate linking constraints.** `x_ij <= y_i` for each customer j is tighter than `sum_j x_ij <= n*y_i`. It has more rows but gives a stronger bound; test both.
- **Break symmetry.** Identical machines, vehicles, or GPUs create many equivalent solutions that branch-and-bound explores separately. Add ordering constraints (for example "machine k is used only if machine k-1 is used", or `load_1 >= load_2 >= ...`), or aggregate identical resources into one integer count.
- **Warm-start.** Give the solver a feasible incumbent (for example a greedy solution) as a MIP start. It improves the primal side only; the bound still has to come from the solver.
- **Watch the root gap.** If the LP bound at the root is far from the incumbent, and the gap stalls, the formulation is weak. Tighten it (valid inequalities, better M, a different variable choice) before raising the time limit.
- **Time-indexed versus big-M scheduling.** Time-indexed binaries (`x_jt = 1` if job j starts at t) give tight relaxations but grow with the horizon. Big-M disjunctive formulations are compact but weak. For many scheduling problems, CP-SAT interval models avoid both ([scheduling-cp-sat.md](scheduling-cp-sat.md)).

## Multiple objectives

Do not invent weights. First ask whether one objective can become a constraint that stakeholders can state ("latency at most 200 ms").

| Method | How | Use when | Limit |
|---|---|---|---|
| Lexicographic (hierarchical) | Optimize by priority. Each later pass keeps earlier objectives within a stated tolerance | Priorities are strict (safety > cost > speed) | The tolerance choice sets the tradeoff. Gurobi supports priorities via `ObjNPriority` |
| ε-constraint | Optimize one objective with the others bounded by ε, and sweep ε | You need the Pareto frontier, including on discrete or nonconvex models | One solve per ε. Choose the ε grid deliberately |
| Weighted sum | Minimize `Σ λ_i f_i` with λ > 0 | Convex problems with agreed, commensurable weights | For convex problems it can find "(almost) all Pareto optimal points" (Boyd–Vandenberghe 4.63). On discrete or nonconvex problems it misses unsupported Pareto points |

**Weighted-sum miss.** Three discrete options have (cost, latency) of A = (0, 10), B = (10, 0), and C = (6, 6). C is Pareto-optimal: no option is at least as good on both. For weight w on cost, C wins only if `6 < 10w` and `6 < 10(1-w)`, meaning w > 0.6 and w < 0.4, which is impossible. Sweeping w from 0 to 1 returns only A or B. The ε-constraint "minimize cost subject to latency <= 6" returns C.

Report a frontier, or name the agreed priority or constraint, rather than one "optimal" point under made-up weights.

Sources: [Gurobi constraints (indicator definition)](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/constraints.html); [Gurobi multiple objectives](https://docs.gurobi.com/projects/optimizer/en/current/features/multiobjective.html); [Boyd–Vandenberghe problem formulations, scalarization slide 4.63](https://web.stanford.edu/class/ee364a/lectures/problems.pdf). The big-M and Pareto examples were derived in this bundle.
