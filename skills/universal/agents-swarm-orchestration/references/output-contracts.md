# Output Contracts

Use structured outputs between nodes so the lead can validate, merge, and re-dispatch deterministically.

## Table of Contents

- [Task Graph Schema](#task-graph-schema)
- [Worker Report Schema](#worker-report-schema)
- [Status Vocabulary](#status-vocabulary)
- [Dependency Output Contract](#dependency-output-contract)
- [Lead Merge Contract](#lead-merge-contract)
- [Risk Levels](#risk-levels)
- [Stage Depth by Task Size](#stage-depth-by-task-size)
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
3. The report names the exact commit or tree state the worker verified against, plus the verification method (command run, or why it could not run). A report omitting either is dropped and the task re-dispatched — a gap here is never treated as a pass. Full delegate-result-hygiene rule, including the never-resume-with-changed-scope corollary: [../../agents-subagents/references/subagent-interruption-recovery.md](../../agents-subagents/references/subagent-interruption-recovery.md#delegate-result-hygiene).
4. Any interface or schema change is reflected in dependency outputs before the next wave launches.
5. The lead reads every worker's diff directly and writes its own summary; the worker's self-report informs but never replaces that read.
6. The worker branch applies cleanly to the integration branch. Merge in dependency order and run the full verifier after each merge. If it no longer applies, re-dispatch the task against the new base with the merged `contract_summary`; the lead does not hand-resolve worker conflicts. Put the failure itself in the new brief: the conflicting paths and hunks, the change that landed first, and any failing verifier output, with an instruction to restructure around them. A brief that says only "rebase and retry" gives the worker no signal about what to change.

## Risk Levels

Use a stable risk label to drive approvals and verification depth:

- `low` - read-only scans, summaries, doc edits, routine tests
- `medium` - bounded code changes with local verification
- `high` - auth, security, data flow, migrations, infrastructure, payment logic
- `critical` - production data access, destructive operations, external side effects

## Stage Depth by Task Size

Size the per-task pipeline before dispatch so small changes do not pay for full review, and large ones do not skip it. The size cut-offs belong in local policy.

| Task size | Stages |
|---|---|
| Trivial | implement, verify |
| Small | implement, verify, review |
| Medium | research, plan, implement, verify, spec review and code review, fix |
| Large | as medium, plus a final review gate |

Each review stage runs in a context that did not write the code under review.

**Optional cleanup pass.** After an implement stage, a separate fresh-context worker can strip over-defensive checks, tests that only exercise the language or framework, debug output and commented-out code, then rerun the verifier. The idea is to keep the implementer's brief free of "don't" lists that can make it timid about legitimate tests. This benefit is not yet measured here; treat the pass as an experiment and compare diff size and defect escapes with and without it.

## Recommended Launch Defaults

- Read-only workers: parallel by default if outputs are independent.
- Edit-capable workers: launch in waves, not free-for-all.
- High or critical risk work: add a dedicated verifier or reviewer pass before final synthesis.
