# Session Patterns

Patterns for keeping long-running implementation work reliable across sessions and handoffs.

---
## Table of Contents

- [Core Rule](#core-rule)
- [Session Lifecycle](#session-lifecycle)
- [Pattern 1: Durable Context Handoff](#pattern-1-durable-context-handoff)
- [Checkpoint — [YYYY-MM-DD]](#checkpoint-—-yyyy-mm-dd)
- [Done](#done)
- [Verified](#verified)
- [Decisions](#decisions)
- [Blockers](#blockers)
- [Next bounded action](#next-bounded-action)
- [Pattern 2: Milestone Recovery](#pattern-2-milestone-recovery)
- [Pattern 3: Multi-Day Project Tracking](#pattern-3-multi-day-project-tracking)
- [Pattern 4: Decision Log](#pattern-4-decision-log)
- [Pattern 5: Session Reset](#pattern-5-session-reset)
- [Pattern 6: Parallel Workstreams](#pattern-6-parallel-workstreams)
- [Anti-Patterns](#anti-patterns)
- [Lessons from Production](#lessons-from-production)
- [Navigation](#navigation)


## Core Rule

Conversation history is not a durable plan.

Keep state in a repo artifact the next session can reload safely:

- existing plan doc
- `docs/plans/...`
- `PLANS.md`
- issue or PR description
- repo memory file if that is already part of the workflow

---

## Session Lifecycle

```text
SESSION START
1. Reload the durable plan artifact
2. Confirm today's bounded outcome
3. Check the latest checkpoint and blockers

ACTIVE WORK
- Execute one bounded batch
- Record evidence after each milestone
- Rescope if interfaces or priorities drift

SESSION END
1. Record what changed
2. Record what was verified
3. Record what remains
4. Record the exact next bounded action
```

---

## Pattern 1: Durable Context Handoff

Use a structured checkpoint in an existing artifact instead of a chat-only handoff.

```markdown
## Checkpoint — [YYYY-MM-DD]

### Done
- [x] Implemented auth middleware contract
- [x] Added integration test skeleton

### Verified
- `npm test -- auth`
- `npm run lint`

### Decisions
- JWT remains the transport token
- Refresh token logic deferred to follow-up milestone

### Blockers
- Need product decision on remember-me duration

### Next bounded action
Complete login form validation against the current contract
```

---

## Pattern 2: Milestone Recovery

Resume from the last checkpoint, not from memory.

Recovery checklist:

1. Read the latest checkpoint and referenced files.
2. Confirm whether the plan still matches repo reality.
3. Re-run only the minimum checks needed to re-establish confidence.
4. Continue with the documented next bounded action.

---

## Pattern 3: Multi-Day Project Tracking

For work spanning multiple days, keep one plan artifact with:

- current milestone
- completed milestones
- open questions
- risk log
- next action

Do not scatter status across multiple scratch files unless the repo already has a documented process for that.

---

## Pattern 4: Decision Log

If a decision will matter later, log it near the plan or ADR instead of relying on chat.

Minimum fields:

- decision
- context
- alternatives considered
- rationale
- consequences

---

## Pattern 5: Session Reset

Start a new session when:

- the task changes meaningfully
- the current session keeps re-reading the same files
- you are carrying more than one bounded outcome
- verification failures repeat without new evidence

Before switching sessions:

1. update the durable artifact
2. record the next bounded action
3. leave exact commands or review evidence if verification is incomplete

---

## Pattern 6: Parallel Workstreams

Parallel workstreams are safe only when:

- they own different files
- shared interfaces are already fixed
- one owner remains responsible for reconciliation

If any of those fail, collapse back to a single workstream.

---

## Anti-Patterns

| Anti-Pattern | Problem | Better Pattern |
|--------------|---------|----------------|
| Context hoarding | History gets long and vague | Durable checkpoints in repo artifacts |
| Vague handoff | "Continue from before" loses state | One explicit next bounded action |
| Chat-only decisions | Important rationale disappears | Decision log near the plan or ADR |
| Parallel overlap | Agents fight over interfaces | Stable contracts first, then bounded fan-out |

---

## Lessons from Production

- One feature per session beats five partially complete streams.
- Pre-written plans reduce rework dramatically on 3+ file tasks.
- If context starts feeling thin, start a new session with a clean checkpoint instead of forcing more continuity out of chat history.

---

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Planning Templates](planning-templates.md)
- [Session Scope Budgeting](session-scope-budgeting.md)
