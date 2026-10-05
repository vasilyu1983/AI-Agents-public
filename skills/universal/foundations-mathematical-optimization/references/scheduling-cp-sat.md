# Scheduling and assignment with CP-SAT

This skill owns resource-constrained scheduling: jobs, shifts, GPU and batch runs, rosters, and workflow steps with capacities, precedence, time windows, makespan, or tardiness. Action sequences with preconditions and effects (PDDL-style planning) belong to `foundations-ai-planning-search`.

## CP-SAT facts that change the model (from the OR-Tools docs)

- **Integer variables and constraints.** Scale rational durations and constraint coefficients into integer units; disclose any rounding and check whether it changes feasibility. Floating objective coefficients are supported by `FloatObjectiveProto` and internally scaled: inspect the installed version’s scaling guarantees and returned objective bound before rounding costs or weights yourself ([model protocol](https://github.com/google/or-tools/blob/stable/ortools/sat/cp_model.proto)).
- **Statuses:**
  - OPTIMAL: optimality established under the configured stopping rules; this status is also returned when a requested objective-gap limit is met or a pure feasibility solution is found. Report objective, best bound and gap settings before claiming exact optimization ([status and parameter definitions](https://github.com/google/or-tools/blob/stable/ortools/sat/sat_parameters.proto)).
  - FEASIBLE: "a feasible solution was found, but we don't know if it's optimal".
  - INFEASIBLE: proven infeasible.
  - MODEL_INVALID: the model failed validation.
  - UNKNOWN: no solution *and* no infeasibility proof before stopping. UNKNOWN is not INFEASIBLE.
- **Core primitives:**
  - An interval variable (`new_interval_var`) ties start + duration = end.
  - `add_no_overlap(intervals)`: a unary resource (one machine, one person).
  - `add_cumulative(intervals, demands, capacity)`: at every time t, the demand of active intervals is at most the capacity (for example GPUs).
  - Optional intervals (`new_optional_interval_var` with a presence literal) model "job may run on resource r". The no-overlap and cumulative constraints "correctly ignore inactive intervals".
  - Makespan: `add_max_equality(makespan, ends)`, then minimize it.
  - Precedence: `start[b] >= end[a]`.

## Worked example: GPU batch jobs

An 8-GPU pool runs five jobs, given as (duration h, GPUs): (3,2), (3,4), (4,4), (4,3), (3,3).

- **Lower bound:** GPU-hours are 6+12+16+12+9 = 55. 55/8 = 6.875, so no schedule finishes before 7.
- **Naive greedy** (longest job first, earliest feasible start): makespan 10.
- **CP-SAT** (`add_cumulative` plus minimize the max end): status OPTIMAL, makespan 7. The incumbent equals the area bound, so this is certified by hand as well. Exhaustive search over integer start times gives the same optimum of 7 (for example: (3,2), (4,3) and (3,3) start at 0, (4,4) at 3, (3,4) at 4).

The claim ladder applies: report the status, the objective, and the solver's `best_objective_bound`. A FEASIBLE result at a time limit is a candidate with a gap, not the optimum.

## When CP-SAT, when MIP, when greedy

These are practitioner heuristics, not measured rules. Try both on real instances when it matters.

- **Prefer CP-SAT** for disjunctive or cumulative resources, sequencing, many logical or conditional rules, all-integer data, and shift rostering with pattern rules. Big-M MIP scheduling formulations are weak ([mip-formulation-and-multiobjective.md](mip-formulation-and-multiobjective.md)).
- **Prefer MIP** for mostly linear models with significant continuous variables (flows, blending, costs), or a tight LP relaxation. Also prefer it when a dual or sensitivity output is needed; CP-SAT gives no LP duals.
- **Greedy or list scheduling is enough** when a cheap lower bound (area bound, critical path) is already close to the greedy makespan. The residual gap is then provably small. When the gap is large, as in the example above, solve.
- Set `max_time_in_seconds` and, where available, a gap target before the run. Report the stopping status.
- For online or rolling scheduling (jobs arrive continuously), re-solve on a horizon with frozen started jobs. Do not re-plan running work.

Sources: [OR-Tools CP-SAT solver](https://developers.google.com/optimization/cp/cp_solver), [job-shop example](https://developers.google.com/optimization/scheduling/job_shop), [CP-SAT scheduling docs](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/scheduling.md), and the [cp_model API (`add_cumulative`)](https://or-tools.github.io/docs/pdoc/ortools/sat/python/cp_model.html).
