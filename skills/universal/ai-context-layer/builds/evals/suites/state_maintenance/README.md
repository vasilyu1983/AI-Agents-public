# State-maintenance Suite (A38 / A39 / P22)

Deterministic regression guard on the state-maintenance discipline in
`references/patterns-catalog.md` §P22: derive current state from a
deduplicated event log ordered by effective time, let only the
top-authority source write state, and store bi-temporal rows linked by
`supersedes_id`. No API key, no model.

## Run

```bash
PYTHONPATH=builds:builds/reference_app \
  pytest builds/evals/suites/state_maintenance -v
```

## What it asserts

1. **Replay invariance (A39).** Fifty seeded shuffles of the INC-42 stream,
   with extra redeliveries, all yield the same current owner, history, and
   as-of answers.
2. **Authority over arrival (A38).** A stale index row, a summary, and a chat
   topic that arrive after the real change never become state; they are
   returned as review candidates.
3. **As-of answers** follow `valid_from <= t < valid_to`, and transitions
   are linked by `supersedes_id`.
4. **Anti-tautology.** The naive arrival-order reducer must get the stream
   wrong; if it stops failing, the stream no longer tests anything.

## Extending

Add cases from the category table in
`references/evals-and-operations.md` §State-Maintenance Eval. Keep one
hard negative per case that is closer to the question than the right
answer. To guard your real adapter, replace `defended_reducer` with your
production reducer and keep the assertions unchanged.
