# Transition Wave Planner

Use this when the target state requires coexistence instead of a single cutover.

## Per-Wave Checklist

| Wave | Goal | Systems Touched | Coexistence Rule | Validation | Rollback | Exit / Retirement Trigger |
|------|------|-----------------|------------------|-----------|----------|---------------------------|
| 0 | Baseline visibility | Legacy + target candidate | Observe only | Dashboards, trace coverage, parity checks | Remove observer path | Metrics stable for one release window |

## Questions To Answer

- What is the smallest safe cutover unit for this wave?
- Which interim boundary exists only for migration, and who owns its retirement?
- What evidence is required before traffic or writes move?
- What condition forces rollback rather than continued coexistence?

## Guardrails

- Every wave needs a rollback path or a written reason why rollback is impossible.
- Compatibility layers must have an owner and a retirement trigger.
- Validation must cover both business correctness and operational health.
