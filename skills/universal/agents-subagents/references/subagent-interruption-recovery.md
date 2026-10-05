---
description: Recovery protocol for interrupted or background workers.
last_verified: 2026-09-16
status: stable
---

# Subagent Interruption Recovery

Use this guide when a Claude Code subagent is interrupted, times out, or returns partial work.

## Goal

Recover the smallest affected unit of work without restarting unrelated tasks.

## Delegate Result Hygiene

Drop and re-dispatch any worker result that omits the exact commit (or tree state) it verified against, and the method used to verify it — a gap here is never treated as a pass, no matter how confident the summary reads. The lead reads every delegate's diff directly and writes its own summary; a worker's self-report informs that summary but never substitutes for it. Never resume an interrupted worker with changed scope (different files, different objective, different acceptance criteria than the run it started with) — spawn a fresh worker with the consolidated brief instead, so the transcript and the scope stay in sync. This governs every worker result, not only interrupted ones; see [Recovery Steps](#recovery-steps) below for the interruption-specific checkpoint format.

## Recovery Steps

1. Capture the last useful output from the subagent.
2. Classify the interruption:
   - `manual_redirect`
   - `timeout`
   - `tool_error`
   - `context_overflow`
   - `background_cancelled`
3. Record the current checkpoint:
   - completed work
   - pending work
   - owned files
   - unresolved blocker
   - next exact step
4. Decide whether to:
   - **resume the same subagent** via `SendMessage` with the agent's ID, only when scope is unchanged from the interrupted run (see [delegate result hygiene](#delegate-result-hygiene)). Subagent transcripts persist independently of the main conversation's compaction, so the resumed turn still sees full prior context. This is the first-class recovery path in current docs for unchanged scope.
   - spawn a replacement subagent with the checkpoint embedded in the new handoff (required when scope changed; also use when the prior context is genuinely noisy or the role should change).
5. Re-run verification on any touched boundary before accepting the result.

### Transcript retention and cleanup

- Subagent transcripts survive compaction in the parent conversation and are addressable by the agent's ID until they are cleaned up.
- Retention is bounded by the `cleanupPeriodDays` setting (default **30 days**). Plan long-running resume flows accordingly — an agent ID from a session six weeks ago will no longer resolve.
- If you need a resume path beyond 30 days, raise `cleanupPeriodDays` deliberately in settings, or capture the checkpoint to a file before the window closes.

## Resume Heuristics

- Resume the same subagent when the scope is still narrow and the context is still clean.
- Replace the subagent when the prompt got noisy, ownership changed, or the failure suggests a fresh context window will be cheaper.
- Escalate to the parent thread when the blocker is really a spec problem, not an execution problem.

## Background Worker Notes

- Background workers should always return a compact checkpoint if they cannot finish.
- Do not silently restart a background verifier from the beginning if you already know the failing step.
- If the parent thread has moved on, restate the original goal in the recovery brief instead of assuming it is still obvious.

## Anti-Patterns

- Restarting the full fan-out after one worker fails
- Reusing a vague handoff that caused the first failure
- Accepting partial output without rerunning boundary verification

## Related

- [agent-patterns.md](agent-patterns.md) - Role and handoff patterns
- [../SKILL.md](../SKILL.md) - Main subagent guide
- [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md) - Multi-worker retry policy
