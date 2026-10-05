# Recipe: Wave Dispatch — 3-Worker Shell Example

A self-contained example you can run and verify without reading any other reference. Copy, paste, run.

## Table of Contents

- [What This Recipe Does](#what-this-recipe-does)
- [File Layout](#file-layout)
- [Step 1 — Create the task inputs](#step-1--create-the-task-inputs)
- [Step 2 — worker.sh](#step-2--workersh)
- [Step 3 — synthesizer.sh](#step-3--synthesizersh)
- [Step 4 — orchestrator.sh](#step-4--orchestratorsh)
- [Step 5 — Run it](#step-5--run-it)
- [Adapting to Real Claude Subagents](#adapting-to-real-claude-subagents)
- [Key Patterns Demonstrated](#key-patterns-demonstrated)
- [What to Read Next](#what-to-read-next)

---

## What This Recipe Does

Dispatches 3 workers in parallel (a "wave"), collects their outputs, then runs a synthesizer that merges the results. The pattern applies to any fan-out task: parallel research, parallel file audits, parallel API calls.

This shell version uses background processes. In a real Claude Code session you would replace each `worker_N.sh` call with a separate `claude -p` CLI session; it does not invoke the parent session's Agent tool.

**Sizing the wave.** A wave finishes when its slowest worker does, so plan on the expected maximum of K durations, not the mean; a wider wave raises that maximum. Cap K by the wait target and by the parent's remaining context, and run leftover items as a further wave. Formulas and a worked sizing example: [queueing-theory-applied.md](../../agents-subagents/references/queueing-theory-applied.md).

---

## File Layout

```
/tmp/wave-demo/
  orchestrator.sh      # dispatches workers, waits, runs synthesizer
  worker.sh            # generic worker — takes a task ID and a payload
  synthesizer.sh       # merges worker outputs into one result
  tasks/
    task-1.txt
    task-2.txt
    task-3.txt
  outputs.<suffix>/    # fresh directory per run
```

---

## Step 1 — Create the task inputs

```bash
mkdir -p /tmp/wave-demo/tasks

printf 'Summarise: apples are a fruit\n'  > /tmp/wave-demo/tasks/task-1.txt
printf 'Summarise: bananas are yellow\n'  > /tmp/wave-demo/tasks/task-2.txt
printf 'Summarise: cherries are red\n'    > /tmp/wave-demo/tasks/task-3.txt
```

---

## Step 2 — worker.sh

```bash
#!/usr/bin/env bash
# worker.sh — simulates a worker processing one task.
# In production: replace the body with `claude -p "$WORKER_PROMPT" < "$task_file"`
set -euo pipefail

TASK_ID="$1"
TASK_FILE="$2"
OUTPUT_DIR="$3"

payload=$(cat "$TASK_FILE")

# Simulate work (replace with real agent call or tool invocation)
result="Worker ${TASK_ID} processed: ${payload}"

# Write output atomically to avoid partial reads by the synthesizer
tmp_out="${OUTPUT_DIR}/.${TASK_ID}.tmp"
final_out="${OUTPUT_DIR}/${TASK_ID}.txt"
printf '%s\n' "$result" > "$tmp_out"
mv "$tmp_out" "$final_out"

printf '[%s] worker %s done → %s\n' "$(date -u +%H:%M:%SZ)" "$TASK_ID" "$final_out" >&2
```

---

## Step 3 — synthesizer.sh

```bash
#!/usr/bin/env bash
# synthesizer.sh — merges all worker outputs in order.
set -euo pipefail

OUTPUT_DIR="$1"
# This recipe has exactly three expected artifacts. Validate all before printing.
for task_id in task-1 task-2 task-3; do
  [[ -s "$OUTPUT_DIR/$task_id.txt" ]] || {
    printf 'missing or empty artifact: %s\n' "$task_id" >&2
    exit 1
  }
done

printf '=== SYNTHESIS RESULT ===\n'
for task_id in task-1 task-2 task-3; do
  f="$OUTPUT_DIR/$task_id.txt"
  printf '\n--- %s ---\n' "$(basename "$f")"
  cat "$f"
done
printf '\n=== END ===\n'
```

---

## Step 4 — orchestrator.sh

```bash
#!/usr/bin/env bash
# orchestrator.sh — wave dispatch: 3 workers in parallel, then synthesize.
set -euo pipefail

DEMO_DIR="${1:-/tmp/wave-demo}"
TASKS_DIR="${DEMO_DIR}/tasks"
OUTPUT_DIR=""
WORKER="${DEMO_DIR}/worker.sh"
SYNTHESIZER="${DEMO_DIR}/synthesizer.sh"

# Reject incomplete task inventories before launching anything.
shopt -s nullglob
TASK_FILES=("${TASKS_DIR}"/task-*.txt)
[[ "${#TASK_FILES[@]}" -eq 3 ]] || { printf 'expected exactly 3 tasks\n' >&2; exit 1; }
for task_id in task-1 task-2 task-3; do
  [[ -s "$TASKS_DIR/$task_id.txt" ]] || { printf 'missing or empty task: %s\n' "$task_id" >&2; exit 1; }
done
# Fresh per-run outputs prevent stale artifacts from satisfying this run.
OUTPUT_DIR=$(mktemp -d "${DEMO_DIR}/outputs.XXXXXX")

printf '[orchestrator] starting wave — 3 workers\n'

# ── Dispatch wave ─────────────────────────────────────────────────────────────
declare -a PIDS=()

for task_file in "${TASK_FILES[@]}"; do
  task_id=$(basename "$task_file" .txt)
  bash "$WORKER" "$task_id" "$task_file" "$OUTPUT_DIR" &
  pid=$!
  PIDS+=("$pid")
  printf '[orchestrator] dispatched %s (pid %d)\n' "$task_id" "$pid"
done

# ── Collect results ───────────────────────────────────────────────────────────
FAILED=0
for i in "${!PIDS[@]}"; do
  pid="${PIDS[$i]}"
  if wait "$pid"; then
    printf '[orchestrator] pid %d finished OK\n' "$pid"
  else
    printf '[orchestrator] pid %d FAILED (exit %d)\n' "$pid" "$?"
    FAILED=$((FAILED + 1))
  fi
done

if [[ "$FAILED" -gt 0 ]]; then
  printf '[orchestrator] %d worker(s) failed — aborting synthesis\n' "$FAILED" >&2
  exit 1
fi

printf '[orchestrator] all workers done — running synthesizer\n\n'

# ── Synthesize ────────────────────────────────────────────────────────────────
bash "$SYNTHESIZER" "$OUTPUT_DIR"
```

---

## Step 5 — Run it

```bash
# Make scripts executable
chmod +x /tmp/wave-demo/worker.sh /tmp/wave-demo/synthesizer.sh /tmp/wave-demo/orchestrator.sh

# Run
bash /tmp/wave-demo/orchestrator.sh
```

**Expected output (stderr + stdout combined):**

```
[orchestrator] starting wave — 3 workers
[orchestrator] dispatched task-1 (pid 12345)
[orchestrator] dispatched task-2 (pid 12346)
[orchestrator] dispatched task-3 (pid 12347)
[HH:MM:SSZ] worker task-2 done → /tmp/wave-demo/outputs/task-2.txt
[HH:MM:SSZ] worker task-1 done → /tmp/wave-demo/outputs/task-1.txt
[HH:MM:SSZ] worker task-3 done → /tmp/wave-demo/outputs/task-3.txt
[orchestrator] pid 12345 finished OK
[orchestrator] pid 12346 finished OK
[orchestrator] pid 12347 finished OK
[orchestrator] all workers done — running synthesizer

=== SYNTHESIS RESULT ===

--- task-1.txt ---
Worker task-1 processed: Summarise: apples are a fruit

--- task-2.txt ---
Worker task-2 processed: Summarise: bananas are yellow

--- task-3.txt ---
Worker task-3 processed: Summarise: cherries are red

=== END ===
```

The output directory has a generated suffix; the transcript above illustrates the messages. Worker completion order is non-deterministic (parallel). The synthesizer always processes in alphabetical order.

---

## Adapting to Real Claude Subagents

Replace the `worker.sh` body with a real agent call:

```bash
# Replace the simulation block in worker.sh with:
# Set WORKER_MODEL from the provider model catalog before running.
: "${WORKER_MODEL:?set a verified model ID}"
result=$(claude --model "$WORKER_MODEL" -p "$(cat "$TASK_FILE")")
[[ -n "$result" ]] || { printf 'empty worker result\n' >&2; exit 1; }
# Model catalog: https://docs.anthropic.com/en/docs/about-claude/models
```

Or using the Anthropic Messages SDK (direct API calls, not an agent harness):

```python
# Python equivalent for SDK-based dispatch
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

async def worker(task_id: str, payload: str) -> tuple[str, str]:
    response = await client.messages.create(
        model="<current-sonnet-model>",  # check https://docs.anthropic.com/en/docs/about-claude/models
        max_tokens=256,
        messages=[{"role": "user", "content": payload}],
    )
    return task_id, response.content[0].text

async def orchestrate(tasks: dict[str, str]) -> dict[str, str]:
    results = await asyncio.gather(*(worker(k, v) for k, v in tasks.items()))
    return dict(results)
```

---

## Key Patterns Demonstrated

| Pattern | Where | Purpose |
|---------|-------|---------|
| Fan-out dispatch | `orchestrator.sh` dispatch loop | All workers start before any wait |
| Collect-then-synthesize | `orchestrator.sh` wait loop | Parent waits for all workers before proceeding |
| Atomic output write | `worker.sh` output write | `mv` prevents synthesizer from reading partial files |
| Abort synthesis on partial failure | `orchestrator.sh` failure gate | Abort synthesis if any worker failed |
| Order-independent workers | `worker.sh` design | No worker reads another's output |

---

## What to Read Next

- Cost discipline for large waves: `cost-discipline.md`
- Output contracts between worker and synthesizer: `output-contracts.md`
- Runtime smoke tests before production dispatch: `runtime-smoke-tests.md`
- Operational guardrails (timeouts, retries, circuit breakers): `operational-guardrails.md`

Offline regression check (no API calls): `python3 scripts/test_wave_recipe.py` from this skill directory.
