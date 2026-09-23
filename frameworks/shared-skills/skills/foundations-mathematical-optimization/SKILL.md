---
name: foundations-mathematical-optimization
description: Formulates optimization problems. Use when allocating constrained resources or checking feasibility, duality, optimality gaps, and sensitivity.
version: "1.0"
last_validated: 2026-09-17
---

# Mathematical Optimization Foundations

Turn an allocation question into an explicit model and a defensible solution claim. Separate a good candidate, a feasible candidate, and a certified optimum.

## When to Use

**Trigger:** constrained allocation, linear programming, convex optimization, integer programming, duality certificates, optimality gaps, or robust/stochastic optimization.

Examples: allocate a fixed capacity across products; verify an LP primal/dual witness; choose a formulation for uncertain demand.

Use decision theory to choose preferences or utilities, planning/search for action sequences, and theory of constraints to identify where improvement should focus. This skill owns the mathematical allocation after those choices. Ordinary prioritization without a quantitative constrained model need not activate it.

## Quick Reference

| Task | Resource |
|---|---|
| Choose LP, convex, or discrete formulation | [formulation-and-methods.md](references/formulation-and-methods.md) |
| Verify a claimed optimum | [certificates-and-status.md](references/certificates-and-status.md) |
| Model uncertain coefficients | [uncertainty-and-sensitivity.md](references/uncertainty-and-sensitivity.md) |

## Workflow

1. Define decision variables, their domains and units, objective direction, resource constraints, and input provenance. Record which coefficients are estimates. Do not silently replace a disputed objective with a convenient proxy.
2. Use [formulation-and-methods.md](references/formulation-and-methods.md) to distinguish continuous from indivisible choices and choose LP, convex QP/conic, MILP, or explicitly nonconvex methods. Check formulation fidelity before solver choice.
3. Identify the evidence needed for the claim: feasible point, global bound, certificate, or heuristic result. For duality, numerical tolerances, and termination status, use [certificates-and-status.md](references/certificates-and-status.md).
4. When coefficients are uncertain, use [uncertainty-and-sensitivity.md](references/uncertainty-and-sensitivity.md). Distinguish scenario performance from a probabilistic or worst-case guarantee.
5. Return the [optimization contract](assets/optimization-contract.md) with candidate, constraint residuals, bounds/gap, method and termination status, and sensitivity. If no feasible candidate was found, distinguish search failure from proven model infeasibility.

## Exact LP Certificate Helper

Run `python3 scripts/check_lp_certificate.py input.json`, or pipe JSON to standard input using `-` (default). Python standard library only; it performs no search or optimization.

The helper accepts only the continuous canonical pair:

- Primal: maximize `c^T x`, subject to `Ax <= b`, `x >= 0`.
- Dual: minimize `b^T y`, subject to `A^T y >= c`, `y >= 0`.

Input has exactly `A`, `b`, `c`, `x`, `y`; `A` is a nonempty rectangular matrix with at least one column. Scalars are finite JSON numbers or decimal strings, including exponent notation. Decimal text is converted directly to exact fractions; no expressions or rational strings are evaluated. See [certificates-and-status.md](references/certificates-and-status.md) for schema and worked answer.

Output contains exact rational strings for objectives, gap, and slacks; violations are arrays of indexed constraint-name strings. `optimal` is true only when both supplied witnesses are feasible and their objective gap is exactly zero. Invalid input exits 2 with a JSON error on standard output; valid input exits 0 even when a witness fails.

A failed witness does not prove model infeasibility or unboundedness. This helper certifies the submitted rational continuous LP, not the fidelity of the model, a MILP optimum, a rounded approximation, or an external solver's floating-point result. Convert other LP forms explicitly and preserve the mapping back to original variables.

## Completion Criteria

- Variables/domains, units, objective, and constraints match the stated problem.
- The global/local/heuristic claim has appropriate evidence and disclosed assumptions.
- Numerical feasibility, integrality, bounds, and stopping status are reported separately.
- Sensitivity includes important uncertain coefficients or a stated limitation.
- Any proposed external action stays within the user's existing authorization.

## Fact-Checking

Use dated primary material for mathematical guarantees and vendor documentation for current solver semantics. Check solver status and conventions before interpreting its bounds; do not promote a heuristic or sample result into a global guarantee.

## Navigation and Evidence

- [data/script-contracts.json](data/script-contracts.json) — parser limit documentation contract.
- [data/sources.json](data/sources.json) — primary sources verified by 17 September 2026; no solver-version pin.
- [scripts/check_lp_certificate.py](scripts/check_lp_certificate.py) — exact canonical LP witness checker.
- [scripts/test_lp_certificate.py](scripts/test_lp_certificate.py) — hand-answer, precision, shape, and CLI regressions; run `python3 scripts/test_lp_certificate.py`.

The helper's tests establish its arithmetic and input behavior. They do not establish live routing or improved optimization decisions by an agent.
