# Output Contracts

Use structured outputs between nodes so the lead can validate, merge, and re-dispatch deterministically.

## Table of Contents

- [Task Graph Schema](#task-graph-schema)
- [Worker Report Schema](#worker-report-schema)
- [Status Vocabulary](#status-vocabulary)
- [Dependency Output Contract](#dependency-output-contract)
- [Lead Merge Contract](#lead-merge-contract)
- [Risk Levels](#risk-levels)
- [Recommended Launch Defaults](#recommended-launch-defaults)

## Task Graph Schema

Every task should have enough structure that the lead can decide launch order and detect conflicts before execution.

```json
{
  "task_id": "T3",
  "objective": "Implement auth middleware for protected API routes",
  "depends_on": ["T1"],
  "owned_files": [
    "src/middleware/auth.ts"
  ],
  "read_only_files": [
    "src/routes/index.ts",
    "docs/auth-spec.md"
  ],
  "do_not_touch": [
    "src/routes/*.ts",
    "tests/integration/*.test.ts"
  ],
  "deliverable": "Middleware implementation plus any local helper updates within owned files",
  "verification": [
    "npm test -- auth.middleware",
    "npm run lint -- src/middleware/auth.ts"
  ],
  "report_schema": "worker_report_v1",
  "risk_level": "medium"
}
```

## Worker Report Schema

Require every worker to return the same top-level shape.

```json
{
  "schema": "worker_report_v1",
  "task_id": "T3",
  "status": "completed",
  "summary": "Added token parsing and route guard checks.",
  "files_touched": [
    "src/middleware/auth.ts"
  ],
  "tests_run": [
    {
      "command": "npm test -- auth.middleware",
      "result": "passed"
    }
  ],
  "interface_changes": [],
  "blockers": [],
  "follow_ups": [],
  "notes_for_lead": "No contract changes required."
}
```

## Status Vocabulary

Use a small stable status set:

- `pending` - task exists but has not started
- `in_progress` - worker owns it right now
- `completed` - output is ready for validation
- `blocked` - waiting on dependency, approval, or missing information
- `failed` - worker could not complete; lead must decide retry or re-plan

## Dependency Output Contract

When a downstream task depends on upstream work, do not forward raw logs or full transcripts. Distill the dependency into a short structured payload:

```json
{
  "from_task": "T1",
  "artifacts": [
    "db/schema.sql"
  ],
  "contract_summary": "Added users.id UUID primary key and sessions.user_id foreign key.",
  "breaking_changes": [],
  "open_risks": [
    "Session cleanup migration still pending."
  ]
}
```

## Lead Merge Contract

Before the lead merges or marks a task complete, confirm:

1. `files_touched` stay within `owned_files`.
2. `status` is valid and consistent with the evidence.
3. Verification commands actually ran or the worker explicitly reported why they could not.
4. Any interface or schema change is reflected in dependency outputs before the next wave launches.
5. The worker report is concise enough to keep the main thread clean.

## Risk Levels

Use a stable risk label to drive approvals and verification depth:

- `low` - read-only scans, summaries, doc edits, routine tests
- `medium` - bounded code changes with local verification
- `high` - auth, security, data flow, migrations, infrastructure, payment logic
- `critical` - production data access, destructive operations, external side effects

## Recommended Launch Defaults

- Read-only workers: parallel by default if outputs are independent.
- Edit-capable workers: launch in waves, not free-for-all.
- High or critical risk work: add a dedicated verifier or reviewer pass before final synthesis.
