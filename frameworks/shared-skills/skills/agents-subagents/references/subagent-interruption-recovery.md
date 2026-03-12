# Subagent Interruption Recovery

Use this guide when parallel agent runs are interrupted or errored mid-execution.

## Objective

Recover progress with minimal rework and without restarting unaffected tasks.

## Recovery Steps

1. Capture last known output for interrupted agent.
2. Tag interruption reason:
   - `manual_interrupt`
   - `timeout`
   - `tool_error`
   - `context_overflow`
3. Create recovery handoff with:
   - what is already done
   - what remains
   - owned files
   - changed assumptions
4. Resume only impacted task, not whole wave.
5. Re-run verification for integration boundaries touched by recovered task.

## Decision Matrix

- Resume same agent when context is still valid and scope is narrow.
- Spawn replacement agent when previous context is noisy or ownership changed.
- Escalate to orchestrator-only fix when multiple agents now conflict on shared interfaces.

## Tracking

Maintain an interruption ledger per wave:
- agent id
- task id
- cause
- recovery action
- final status
