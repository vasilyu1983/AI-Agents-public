---
name: foundations-mathematical-optimization
description: Formulates LP, MILP, CP-SAT models; diagnoses infeasibility and gaps. Use when a MILP is infeasible, shifts need scheduling under capacity, or choosing a solver.
version: "1.0"
last_validated: 2026-09-17
---

# Mathematical Optimization Foundations

Turn an allocation question into an explicit model and a defensible solution claim. Separate a good candidate, a feasible candidate, and a certified optimum.

## When to Use

**Trigger:** constrained allocation, linear programming, convex optimization, integer programming, scheduling and assignment under capacity, solver choice, infeasible or unbounded models, duality certificates, optimality gaps, multi-objective tradeoffs, or robust/stochastic optimization.

Examples: allocate a fixed capacity across products; schedule GPU jobs under a GPU cap; find which constraints make a MILP infeasible; check an LLM-drafted model; verify an LP primal/dual witness.

Use decision theory to choose preferences or utilities, planning/search for action sequences with preconditions and effects (this skill owns resource-constrained scheduling), and theory of constraints to identify where improvement should focus. This skill owns the mathematical allocation after those choices. Ordinary prioritization without a quantitative constrained model need not activate it.

## Quick Reference

| Task | Resource |
|---|---|
| Choose LP, convex, or discrete formulation | [formulation-and-methods.md](references/formulation-and-methods.md) |
| Verify a claimed optimum | [certificates-and-status.md](references/certificates-and-status.md) |
| Model uncertain coefficients | [uncertainty-and-sensitivity.md](references/uncertainty-and-sensitivity.md) |
| Pick a solver or modeling layer; look up versions and features | [solver-selection.md](references/solver-selection.md) |
| Model is infeasible, unbounded, INF_OR_UNBD, or numerically unstable | [infeasibility-diagnosis.md](references/infeasibility-diagnosis.md) |
| MIP is slow or has a large gap; big-M, symmetry; several objectives | [mip-formulation-and-multiobjective.md](references/mip-formulation-and-multiobjective.md) |
| Jobs, shifts, GPU or workflow scheduling; CP-SAT vs MIP vs greedy | [scheduling-cp-sat.md](references/scheduling-cp-sat.md) |
| An LLM drafts the model from a text spec | [llm-assisted-formulation.md](references/llm-assisted-formulation.md) |

## Workflow

1. Define decision variables, their domains and units, objective direction, resource constraints, and input provenance. Record which coefficients are estimates. Do not silently replace a disputed objective with a convenient proxy.
2. Use [formulation-and-methods.md](references/formulation-and-methods.md) to distinguish continuous from indivisible choices and choose LP, convex QP/conic, MILP, or explicitly nonconvex methods. Check formulation fidelity before solver choice, then pick the solver with [solver-selection.md](references/solver-selection.md); scheduling goes to [scheduling-cp-sat.md](references/scheduling-cp-sat.md).
3. Identify the evidence needed for the claim: feasible point, global bound, certificate, or heuristic result. For duality, numerical tolerances, and termination status, use [certificates-and-status.md](references/certificates-and-status.md).
4. When coefficients are uncertain, use [uncertainty-and-sensitivity.md](references/uncertainty-and-sensitivity.md). Distinguish scenario performance from a probabilistic or worst-case guarantee.
5. Return the [optimization contract](assets/optimization-contract.md) with candidate, constraint residuals, bounds/gap, method and termination status, and sensitivity. If no feasible candidate was found, distinguish search failure from proven model infeasibility and diagnose with [infeasibility-diagnosis.md](references/infeasibility-diagnosis.md).

## Exact LP Certificate Helper

Run `python3 scripts/check_lp_certificate.py input.json` (or `-` for standard input) to check supplied primal/dual witnesses for the canonical pair max `c^T x`, `Ax <= b`, `x >= 0` / min `b^T y`, `A^T y >= c`, `y >= 0` in exact rational arithmetic. It performs no optimization. Schema, parser limits, output fields, exit codes, and a worked answer: [certificates-and-status.md](references/certificates-and-status.md).

It certifies only the submitted continuous LP. It does not certify model fidelity, a MILP optimum, or a floating-point solver result, and a failed witness does not prove infeasibility or unboundedness.

## Completion Criteria

- Variables/domains, units, objective, and constraints match the stated problem.
- The global/local/heuristic claim has appropriate evidence and disclosed assumptions.
- Numerical feasibility, integrality, bounds, and stopping status are reported separately.
- Sensitivity includes important uncertain coefficients or a stated limitation.
- Any proposed external action stays within the user's existing authorization.
- Use dated primary material for mathematical guarantees and vendor documentation for current solver semantics. Check solver status and conventions before interpreting its bounds; do not promote a heuristic or sample result into a global guarantee.

## Navigation and Evidence

- [data/script-contracts.json](data/script-contracts.json) — parser limit documentation contract.
- [data/sources.json](data/sources.json) — primary and vendor sources; no solver version is pinned. [solver-selection.md](references/solver-selection.md) says where to look versions up.
- [scripts/check_lp_certificate.py](scripts/check_lp_certificate.py) — exact canonical LP witness checker.
- [scripts/test_lp_certificate.py](scripts/test_lp_certificate.py) — hand-answer, precision, shape, and CLI regressions; run `python3 scripts/test_lp_certificate.py`.

The helper's tests establish its arithmetic and input behavior. They do not establish live routing or improved optimization decisions by an agent.
