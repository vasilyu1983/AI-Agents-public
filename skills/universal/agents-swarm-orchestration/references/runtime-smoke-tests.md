# Runtime Smoke Tests

Runtime-surface smoke-test matrix for `agents-swarm-orchestration`.

Use this checklist when you want stronger confidence than repo validation alone. The goal is to confirm that the orchestration layer actually dispatches workers, enforces declared budgets through a configured counter or supervisor, and writes checkpoints at wave boundaries on the runtimes you use.

Mirror-companion to [`../../agents-subagents/references/runtime-smoke-tests.md`](../../agents-subagents/references/runtime-smoke-tests.md), which covers the agent-definition / registry side. Run both when auditing a runtime.

## Table of Contents

- [What This Covers](#what-this-covers)
- [Prerequisites](#prerequisites)
- [Test 1 — 2-Worker Read-Only Dry Run](#test-1--2-worker-read-only-dry-run)
- [Test 2 — Per-Worker Budget Breach](#test-2--per-worker-budget-breach)
- [Test 3 — Checkpoint Write At Wave Boundary](#test-3--checkpoint-write-at-wave-boundary)
- [Pass Criteria](#pass-criteria)

## What This Covers

This matrix validates three load-bearing orchestration behaviors:

1. **Wave dispatch** — the lead can launch multiple read-only workers in parallel and collect structured reports without polluting the main thread.
2. **Per-worker budget enforcement** — a configured counter or supervisor stops dispatch at the cap. A prompt requesting a stop tests instruction-following only; it cannot prove enforcement.
3. **Wave-boundary checkpoints** — the orchestration layer snapshots task state and worker reports to disk at each wave boundary so a fresh lead can resume.

It does **not** cover: agent-definition correctness (see sibling matrix), MCP server plumbing, Agent Teams communication topology, or noninteractive CI dispatch.

## Prerequisites

- A Claude Code release that supports Agent Teams (for the team tests) and exposes the `Agent` tool name; check the changelog for the minimum versions rather than trusting a pinned number
- A scratch directory the smoke-test run can write to:
  ```bash
  mkdir -p tmp/swarm-smoke/{reports,checkpoints}
  ```
- `jq` installed for parsing structured reports from the workers

All commands below run from the repo root and write into the scratch `tmp/swarm-smoke/` paths only. Built-in Explore cannot Write or Edit: it returns structured output, and the lead validates and writes it. Confirm that scratch writes are authorized before running.

## Test 1 — 2-Worker Read-Only Dry Run

**Purpose:** confirm the lead can dispatch two read-only workers in the same turn and collect structured reports back to files, not the conversation transcript.

**Setup:** In a fresh Claude Code session, use a prompt that fans out two `Explore` workers that return JSON to the lead:

```text
Dispatch these two read-only workers in the same turn. Each returns JSON; the lead validates it and writes the report path.
Do not ask Explore to write files. Summarize briefly after writing the reports.

Worker 1 (Explore):
  Task: list all files under skills/universal/agents-subagents/references/ with line counts.
  Report path: tmp/swarm-smoke/reports/worker-1.json
  Schema: { "files": [{"path": "...", "lines": N}], "total_files": N }

Worker 2 (Explore):
  Task: list all files under skills/universal/agents-swarm-orchestration/references/ with line counts.
  Report path: tmp/swarm-smoke/reports/worker-2.json
  Schema: { "files": [{"path": "...", "lines": N}], "total_files": N }
```

**Verify after the run:**

```bash
# Both reports exist and parse as JSON
for report in tmp/swarm-smoke/reports/worker-{1,2}.json; do
  jq -e '(.files | type == "array") and (.total_files == (.files | length))' "$report" || exit 1
done

# Main transcript did not swallow the raw file listings (look for brief summary only)
# This is a manual check — review the conversation for brevity.
```

**Expected:** both files exist, parse as valid JSON matching the schema, and the lead's final message is a short summary that names the two reports instead of restating their contents.

**Fail modes:**
- Worker start/end timestamps show no overlap (elapsed time alone cannot prove serialization). Add the canonical fan-out line to `AGENTS.md` / `CLAUDE.md` — see `SKILL.md` §"Explicit Fan-Out Is The Durable Default".
- Either report missing or malformed JSON. The launch prompt lacked an explicit schema or output path; tighten the worker brief.
- Main transcript contains the full raw file listings. The lead is not using the structured-report pattern — revisit the prompt and require "report to file, summarize briefly inline."

## Test 2 — Per-Worker Budget Breach

**Purpose:** confirm that a worker given an explicit token or tool-call budget stops and reports a breach instead of running to session limits.

**Setup:** configure a supported tool-call counter or supervisor to stop the worker at a cap and record observed usage. If none is available, mark enforcement **unverified** and run this only as an instruction-following check. Use a synthetic scratch corpus too large for the cap:

```text
Dispatch one Explore worker with these limits:
  Max tool calls: 3
  Token budget: 2000
  Task: read synthetic .md fixtures under tmp/swarm-smoke/input/ one tool call per fixture.
  Return partial progress and status to the lead; the lead writes the report.
  Report path: tmp/swarm-smoke/reports/budget-breach.json
  On budget breach: return status = "budget_breach" and stop. Do not continue past 3 tool calls.
```

**Verify after the run:**

```bash
# The worker stopped and flagged the breach
jq -e '.status == "budget_breach"' tmp/swarm-smoke/reports/budget-breach.json
# Expected: true, with exit status 0

# The worker did not exceed 3 tool calls (check the conversation's tool-use log)
# Manual check: scan the conversation for the worker span and count tool_use blocks.
```

**Expected:** `status` is `"budget_breach"`, the worker used ≤3 tool calls, and it returned partial progress (not a blank report) so the lead can decide whether to re-scope or escalate.

**Fail modes:**
- Worker continued past the budget. Stop the run and fix the counter/supervisor. Strengthening a prompt cannot substitute for an enforced cap.
- Worker returned a normal `"completed"` status. The task was not actually too big for the budget; raise the task size or lower the budget further.

## Test 3 — Checkpoint Write At Wave Boundary

**Purpose:** confirm the orchestration layer snapshots task state and merged worker outputs at each wave boundary, so a fresh lead session could resume without re-reading raw worker transcripts.

**Setup:** run a 2-wave orchestration. The lead must write a checkpoint file between waves.

```text
Run a 2-wave orchestration, read-only. Between waves, write a checkpoint to disk.

Wave 1 (dispatch two Explore workers in the same turn):
  A: count .md files under skills/universal/agents-subagents/
  B: count .md files under skills/universal/agents-swarm-orchestration/

After Wave 1 merges, write tmp/swarm-smoke/checkpoints/wave-1.json with:
  { "wave": 1, "completed_tasks": ["A", "B"], "outputs": {"A": N, "B": N}, "next_wave": "2" }

Wave 2 (one Explore worker, depends on Wave 1):
  C: using the two counts from Wave 1, report which skill has more .md files. The lead must read wave-1.json before briefing C.

After Wave 2, write tmp/swarm-smoke/checkpoints/wave-2.json with:
  { "wave": 2, "completed_tasks": ["C"], "outputs": {"C": "..."}, "next_wave": null }
```

**Verify after the run:**

```bash
# Both checkpoints exist and contain the expected schema
jq '.wave, .completed_tasks' tmp/swarm-smoke/checkpoints/wave-1.json
jq '.wave, .completed_tasks' tmp/swarm-smoke/checkpoints/wave-2.json

# Wave 2 checkpoint's "outputs.C" references the Wave 1 counts (simulates resume)
jq -r '.outputs.C' tmp/swarm-smoke/checkpoints/wave-2.json
```

**Expected:** both checkpoint files exist with valid JSON matching the schema, Wave 1 lists both A and B as completed, Wave 2's output cites the Wave 1 counts (proving the checkpoint was load-bearing, not just ceremonial).

**Fail modes:**
- Lead skipped the checkpoint write and only produced the final summary. Tighten the prompt: "checkpoint after each wave is required for the test to pass — do not merge Wave 2 without writing Wave 1's checkpoint first."
- Wave 2 did not read the checkpoint, re-derived the counts from source. The orchestration is not using the checkpoint as the resume surface — re-brief the lead to read Wave 1's checkpoint before dispatching Wave 2.

## Pass Criteria

Record these checks for the tested runtime and configuration when all of these are true:

1. Test 1 (2-worker dry run) produces two structured reports and the main transcript stays short.
2. Test 2 records the enforcing counter/supervisor, returns `"budget_breach"`, and its tool log shows ≤3 calls. Prompt-only results leave enforcement unverified.
3. Test 3 (wave-boundary checkpoints) produces two checkpoint files, and Wave 2 demonstrably consumed Wave 1's checkpoint.
4. The sibling `agents-subagents` runtime smoke tests also pass on the same runtime.

If only Tests 1–3 pass but agent-definition smoke tests fail, treat the skill as **orchestration-ready, agent-definition drift possible**. These smoke checks cover only the declared dispatch, budget and checkpoint behaviors; they do not establish production readiness.
