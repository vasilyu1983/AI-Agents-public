# Web Vitals and Performance Budgets (moved)

This content moved out of this skill. software-performance now covers diagnosis only; budget, gate, and load-test design live in [qa-testing-performance](../../qa-testing-performance/SKILL.md):

| Topic | New home |
|-------|----------|
| Core Web Vitals thresholds, INP, LCP, CLS, Lighthouse CI assertions and byte budgets, frontend traps | [frontend-performance.md](../../qa-testing-performance/references/frontend-performance.md) |
| CI performance gates, baselines, budget JSON | [performance-budgets-ci.md](../../qa-testing-performance/references/performance-budgets-ci.md), [template-performance-budget.md](../../qa-testing-performance/assets/template-performance-budget.md) |
| k6 smoke/load/stress/soak, arrival-rate executors, coordinated omission, `k6 cloud run` | [load-testing-patterns.md](../../qa-testing-performance/references/load-testing-patterns.md) |
| Budget checking of measured results | [perf_budget_checker.py](../../qa-testing-performance/scripts/perf_budget_checker.py); for raw Lighthouse JSON, this skill's [check_perf_budget.py](../scripts/check_perf_budget.py) |

Profiling tools and the "Neutral Is a Revert" rule stay in this skill: [perf-budgets-and-cwv.md](perf-budgets-and-cwv.md).
