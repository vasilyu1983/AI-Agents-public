# Context Rotation And Durable State

Operational patterns for keeping coding and multi-agent workflows reliable as sessions get longer and task graphs get larger.

## Table Of Contents

- [Core Distinction](#core-distinction)
- [Symptoms Of Context Rot](#symptoms-of-context-rot)
- [Preferred Mitigations](#preferred-mitigations)
- [When To Respawn A Worker](#when-to-respawn-a-worker)
- [State Shapes](#state-shapes)
- [Anti-Patterns](#anti-patterns)
- [Related References](#related-references)
- [Primary Sources](#primary-sources)

## Core Distinction

Treat these as different things:

- **Session context**: temporary conversation history, tool outputs, scratch reasoning, and intermediate exploration
- **Project state**: decisions, interfaces, constraints, task graph, progress, and verification evidence that must survive across sessions

The operational mistake is storing project state inside session context.

## Symptoms Of Context Rot

Use **context rot** here as practitioner shorthand for quality degradation caused by overloaded or polluted session context.

Common symptoms:

- the agent re-reads the same files and forgets prior decisions
- workers inherit irrelevant logs or stale assumptions
- task boundaries blur and edits expand beyond scope
- the model starts using outdated instructions from earlier in the conversation

## Preferred Mitigations

### 1. Fresh-context workers

Spawn each worker with:

- the bounded task brief
- owned files and explicit `do_not_touch` boundaries
- frozen interface contracts
- verification commands or acceptance checks

Do not pass the entire orchestrator transcript unless the task genuinely depends on it.

### 2. Durable external state

Persist project state in reviewable files such as:

- markdown with frontmatter
- YAML
- JSON
- task manifests or blueprints

Typical state to persist:

- active plan and milestones
- dependency graph and unblock conditions
- decisions and rationale
- changed-path ownership
- verification evidence and unresolved risks

### 3. Session-to-project promotion

Only promote durable information out of session context:

- approved decisions
- stable interfaces
- verified findings
- next-step checkpoints

Do not persist raw chain-of-thought, noisy logs, or unverified guesses as project state.

## When To Respawn A Worker

Prefer a fresh worker or fresh agent session when:

- the task changes from exploration to implementation
- a worker has crossed a meaningful phase boundary
- the context now contains multiple unrelated branches of reasoning
- the same task needs to be resumed after a long pause
- the worker would benefit more from a clean brief than from conversational history

## State Shapes

Keep the shape simple and explicit.

```yaml
task:
  id: auth-session-fix
  owner: dev-worker-2
  owned_files:
    - src/auth/session.ts
    - tests/auth/session.test.ts
  depends_on:
    - session-contract-approved
  verify:
    - npm test -- session
  status: in_progress
```

```yaml
decision:
  id: use-session-cookie-refresh
  date: 2026-03-25
  approved_by: lead
  rationale: Avoid token refresh race in middleware chain
  affected_interfaces:
    - src/auth/contracts.ts
```

## Anti-Patterns

- using one giant conversation as the system of record
- passing raw worker transcripts between workers
- keeping task ownership implicit instead of written down
- persisting every thought instead of only verified state
- making workers reconstruct project state from memory rather than files

## Related References

- [`agent-delivery-methods.md`](agent-delivery-methods.md)
- [`context-engineering.md`](context-engineering.md)
- [`multi-agent-patterns.md`](multi-agent-patterns.md)
- [`../../dev-workflow-planning/references/session-patterns.md`](../../dev-workflow-planning/references/session-patterns.md)

## Primary Sources

- GSD: <https://github.com/gsd-build/get-shit-done>
- BMAD Method docs: <https://docs.bmad-method.org/>
- Anthropic Claude Code best practices: <https://www.anthropic.com/engineering/claude-code-best-practices>
- OpenAI Codex workflows: <https://developers.openai.com/codex/workflows>
