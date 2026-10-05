# Delivery Milestones Contract

Load this when a PRD or spec will be delivered across more than one session or by more than one worker. The milestone table is the delivery state: a planner reads it to pick the next work, and an implementer closes a row only with evidence. Skip it for a single-session change; a goal and an acceptance-criteria list are enough there.

## The table

| Column | Rule |
|---|---|
| id | Short and stable (`M1`, `M2`). Never renumber after work starts, because other rows and plans refer to it. |
| outcome | The observable state when done: a system behavior or a user ability, not an activity. "Users can download the filtered list as CSV", not "work on export". |
| depends-on | Ids that must be `done` first, or `-`. List only hard prerequisites: the milestone needs an artifact, interface or state that the other one produces. Preferred order is not a dependency. |
| acceptance check | The command, test or named review that proves the outcome, runnable by someone who did not build it. Reference acceptance-criteria ids where they exist. |
| status | `pending`, `in-progress`, `done` or `blocked`. A `blocked` row names its blocker in a note. |

Owner and plan-link columns are optional. Add them when several people or plans share the table.

Labelled example (illustrative, not a real project):

| id | outcome | depends-on | acceptance check | status |
|---|---|---|---|---|
| M1 | The export endpoint returns one account's filtered list as CSV | - | `pytest tests/export/test_csv.py` passes (AC-1, AC-2) | done |
| M2 | The list view's export button downloads that file | M1 | End-to-end test `export downloads csv` passes (AC-3) | in-progress |
| M3 | Exports above the inline limit run as a background job with a download link | M1 | Job test with the largest fixture completes and the link serves the file (AC-4) | pending |
| M4 | Each export writes an audit record | M1 | Test asserts one audit row per export (AC-5) | pending |

## Validity rules

Check these before handoff and again whenever a row is added or re-cut:

1. **Every depends-on id exists.** A dangling id silently makes a row look eligible or permanently blocked.
2. **No dependency cycle.** A topological order exists only when the graph has no directed cycle (`foundations-graph-theory`, Quick Reference). A cycle means the milestones are cut wrong: merge them or split out the shared part. Do not hide it by dropping an edge.
3. **Each acceptance check can fail.** Apply the "can't picture the failing test" tell from [SKILL.md](../SKILL.md#acceptance-criteria-testability-the-judgment-beyond-the-checklist) to every row.
4. **Each milestone leaves the system working.** After any `done` row, the system builds, its checks pass, and unfinished behavior is absent or off by default.

## Status transitions

| From → to | Who | Condition |
|---|---|---|
| `pending` → `in-progress` | The planner that picks it | Every dependency is `done`. [dev-workflow-planning](../../dev-workflow-planning/SKILL.md#next-eligible-milestone) owns the pick order. |
| `in-progress` → `done` | The implementer | The acceptance check ran and passed. Record where: commit, CI run or log path. A check that did not run keeps the row `in-progress`. |
| any → `blocked` | Anyone | Name the blocker and what would clear it. Return to `pending` when it clears. |

When implementation shows an outcome or check cannot be met, revise the row as the `[revised]` rule in [SKILL.md](../SKILL.md#decision-and-unknown-ledger) describes. Do not quietly weaken the check.
