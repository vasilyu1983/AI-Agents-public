# Operational Guardrails

These defaults keep orchestration useful instead of chaotic.

## Table of Contents

- [Default Limits](#default-limits)
- [Prompt And Data Safety](#prompt-and-data-safety)
- [Verification Gates](#verification-gates)
- [Observability](#observability)
- [Large-Scale Write Swarm Patterns](#large-scale-write-swarm-patterns)
- [Stop Conditions](#stop-conditions)
- [Escalation Defaults](#escalation-defaults)

## Default Limits

- Keep edit-capable workers at 3 or fewer unless the user explicitly wants broader fan-out.
- Use larger swarms only for read-only work such as exploration, tests, triage, or summarization.
- Do not allow multiple edit-capable workers to touch the same file in parallel.
- Retry transient failures once. If the same task fails again, the lead must re-plan or escalate.
- If conflict resolution would invalidate more than half of completed tasks, stop and re-plan.

### Platform concurrency defaults

- **Codex**: `max_threads: 6`, `max_depth: 1`, `job_max_runtime_seconds: 1800`. Increasing `max_depth` beyond 1 risks recursive fan-out.
- **Claude Code**: no hard thread cap, but subagents cannot spawn other subagents (depth is always 1). Background subagents auto-deny unapproved permissions; if this causes failure, retry in foreground with interactive prompts.

## Prompt And Data Safety

Sources:

- https://developers.openai.com/api/docs/guides/agent-builder-safety
- https://code.claude.com/docs/en/sub-agents

Use these rules when constructing worker prompts:

- Never inject untrusted data directly into privileged developer or system instructions.
- Pass untrusted external text through user-style payloads or validated structured fields.
- Sanitize dependency outputs before reuse; do not pass raw tickets, logs, stack traces, or copied web content if a summary will do.
- Use structured outputs between nodes so freeform text cannot silently become instructions.
- Keep tool approvals enabled for MCP or other risky actions whenever the platform supports them.
- Scope tools and MCP servers to the smallest worker that needs them.

## Verification Gates

Every swarm run needs two layers of verification:

### Worker-level gate

- Confirm the worker stayed inside `owned_files`.
- Confirm it ran the declared verification commands or reported why it could not.
- Confirm the worker report matches the expected schema.

### Lead-level gate

- Re-run integration checks after merging worker output.
- Recompute dependency summaries if any interface changed.
- Use a dedicated verifier or reviewer worker for high-risk tasks.

For repeatable productized systems, add evals or trace grading so the orchestrator can measure routing quality, tool discipline, and failure modes over time.

## Observability

Track these metrics per run:

- wall-clock time vs sum of individual task times
- time to first useful worker result
- retries per task
- conflict count
- blocked-task count
- permission or approval prompts triggered
- worker verification pass rate
- cache-hit efficiency for repeated worker prompt prefixes

High conflict rates usually mean ownership is wrong. High retries usually mean the graph or interface contract is wrong.

## Large-Scale Write Swarm Patterns

Lessons from running 8-13+ parallel write-capable agents creating multiple files each (e.g., gap analyses across domains):

### Context exhaustion
- Agents reading many large files (~10+ docs) AND writing 4+ large files (~500 lines each) can exhaust context mid-task.
- **Mitigation**: Be explicit in agent prompts. List exact file paths to read (don't say "all files in directory"). Provide key facts inline to reduce reads needed. Specify exact output file paths with the Write tool.

### Stalled agents
- Agents may stall without error when they hit permission prompts, tool limits, or context boundaries.
- **Detection**: Monitor output file line counts. If they stop growing for 2+ checks, the agent is likely stalled.
- **Recovery**: Re-launch with a cleaner, more explicit prompt. Include `mkdir -p` as an explicit step. Remind the agent to use the Write tool.

### Phased execution for ordered dependencies
- When later phases depend on earlier outputs (e.g., "Phase 4 synthesis reads all Phase 1-3 gap analyses"), execute in waves rather than launching everything at once.
- Pattern: Launch Phase 1 agents → verify files created → launch Phase 2 → verify → launch Phase 3 → verify → launch synthesis.
- Independent phases (e.g., Phase 2 and Phase 3 touching different domains) CAN run in parallel.

### Agent prompt structure for file creation
Effective pattern for agents creating new directories and files:
```
Step 1: Read [specific file list]
Step 2: Run mkdir -p /path/to/output/dir
Step 3: Write file using Write tool to /path/to/output/file.md
```
This explicit sequencing prevents agents from trying to write before directories exist.

### Monitoring parallel agents
- Use periodic file-count checks: `find /path/v2/ -name "*.md" | wc -l` per domain.
- Track "X/4 files" progress to know which agents are complete.
- Mark tasks complete as soon as verified, don't wait for all agents.

## Stop Conditions

Stop and re-plan when any of these occur:

- two workers need the same file or unresolved interface
- a dependency output changes the contract for downstream tasks
- repeated retries happen without new evidence
- a worker cannot complete because permissions or tools are insufficient
- the lead is spending more effort reconciling reports than it would take to execute sequentially

## Escalation Defaults

- Low risk: lead may auto-merge after validation.
- Medium risk: require worker verification plus one lead-level check.
- High risk: require explicit reviewer or verifier pass before merge.
- Critical risk: require human approval before side effects and before final completion.

## Worker Self-Rejection

Full tradeoff discussion for the pattern introduced in [../SKILL.md](../SKILL.md) §Worker Self-Rejection Rules.

### Why self-rejection

Most worker failures are plausible-but-wrong output reaching the lead. Lead-level validation catches these, but every round-trip costs a budget cycle. Moving rejection into the worker as a named negative criterion is cheaper: one self-check per draft vs. a full wave round-trip.

### Examples by worker type

| Worker type | Self-rejection clause |
|-------------|----------------------|
| Spec-writer | Reject if the success metric is a vanity metric (page views, time on page) instead of an action |
| Cold-email | Reject if the first line could apply to any company in the recipient's industry |
| Hook-writer | Reject any hook containing 'ultimate', 'game-changing', or 'revolutionary' |
| Lead-researcher | Reject the brief if no buying signal has a dated source |
| Daily-plan | Reject if the must-ship task cannot fit in the declared focus window |
| Edge-case generator | Reject any case that is just 'what if input is null' without a specific scenario |
| Code-reviewer | Reject the review if it contains zero inline line references |

### Tradeoffs

- **Token cost is the point**: self-rejection burns worker tokens on output the lead never sees. Moving rejection from lead-side wave round-trips into single-worker iteration is cheaper overall. Per-worker token budgets still apply; a worker that rejects itself five times has the same budget-breach behavior as any other breach.
- **Not a substitute for lead validation**: self-rejection is a pre-filter. Lead-side schema and integration validation still runs.
- **System prompt, not dispatch brief**: dispatch briefs change per task; the self-rejection rule is a worker invariant and lives with the worker definition.
- **2–3 clause max**: past that, compliance falls off the same cliff as long behavior contracts (see `agents-memory` for the 200-line compliance ceiling). Pick criteria that map to failures you actually see.

Source: [Nav Toor — *30 Claude Code Sub-Agents I Actually Use*](https://x.com/heynavtoor/status/2050148589134045443) (2026-05-01).
