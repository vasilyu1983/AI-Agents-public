# Non-Interactive And Blueprint Patterns

Use this reference when orchestration must run in CI, batch, or script-driven mode, or when you need a deterministic-plus-agentic blueprint rather than ad hoc worker fan-out.

## Table of Contents

- [Non-Interactive Mode And CI Integration](#non-interactive-mode-and-ci-integration)
- [Claude Code Non-Interactive Flags](#claude-code-non-interactive-flags)
- [Output Format Choice](#output-format-choice)
- [Fan-Out Script Pattern](#fan-out-script-pattern)
- [Auto-Mode Fallback](#auto-mode-fallback)
- [Codex Equivalent](#codex-equivalent)
- [Blueprint Orchestration](#blueprint-orchestration)
- [Node Types](#node-types)
- [Blueprint Template](#blueprint-template)
- [Verification Loop Constraints](#verification-loop-constraints)
- [Mapping To Claude Code And Codex](#mapping-to-claude-code-and-codex)

## Non-Interactive Mode And CI Integration

For CI pipelines, batch processing, and fan-out scripts, agent teams are usually the wrong surface because they require interactive mode. Prefer deterministic dispatch scripts plus isolated worker invocations that return structured output.

Use this mode when:

- a pipeline must launch many bounded jobs predictably
- the lead is a script, not a conversational operator
- output has to be parsed by another tool or stored as JSONL

## Claude Code Non-Interactive Flags

```bash
# One-off query, plain text output
claude -p "Explain what this project does"

# Structured JSON for scripts
claude -p "List all API endpoints" --output-format json

# Streaming JSON for real-time processing
claude -p "Analyze this log file" --output-format stream-json

# Scope permissions for batch safety
claude -p "Migrate file X" --allowedTools "Edit,Bash(git commit *)"

# Auto mode for uninterrupted runs
claude --permission-mode auto -p "fix all lint errors"
```

## Output Format Choice

| Format | When |
|--------|------|
| `text` | Interactive use, human reading |
| `json` | Parsing final results in scripts, capturing structured findings |
| `stream-json` | Long-running tasks, real-time progress in pipelines, streaming into another tool |

`stream-json` emits one JSON object per line, so it can be piped into `jq`, a log aggregator, or a progress UI without waiting for the full run to complete.

## Fan-Out Script Pattern

```bash
# Generate task list, then dispatch in parallel
claude -p "List all files matching X" --output-format json | jq -r '.files[]' > tasks.txt

parallel -j 4 --joblog migrate.log \
  'claude -p "Migrate {}. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)" \
    --output-format json' \
  :::: tasks.txt
```

## Auto-Mode Fallback

Auto mode (`--permission-mode auto`) aborts if the classifier repeatedly blocks actions. In a non-interactive run there is no human fallback, so budget retries at the script level rather than inside the agent. Log the failure, move on, and let the lead reconcile the failed tasks later.

## Codex Equivalent

Codex uses its own CLI and runtime controls for non-interactive execution. The architecture is the same:

- deterministic dispatch script
- isolated worker execution
- structured output for parsing and reconciliation

Use the platform-specific details in [ai-coding-agents-sessions](../../ai-coding-agents-sessions/SKILL.md) and [ai-coding-agents-remote-runtime](../../ai-coding-agents-remote-runtime/SKILL.md) instead of hardcoding them into the orchestration skill.

## Blueprint Orchestration

Production harnesses often alternate between fixed deterministic steps and open-ended agentic loops in a single orchestration flow. This is the blueprint pattern.

Use it when:

- setup and verification are fixed and reproducible
- planning or diagnosis still needs a tool-using agent
- you want explicit checkpoints between implementation and verification

## Node Types

| Node Type | Runs | Examples |
|-----------|------|----------|
| Deterministic | Fixed bash or CI steps, always the same | Checkout, install deps, run tests, lint, commit, open PR |
| Agentic | LLM loop with tools, may vary | Read spec, plan changes, implement, diagnose failures |

## Blueprint Template

```text
Wave 0 [Deterministic]: Prepare workspace
  - checkout, install, run baseline tests, capture state

Wave 1 [Agentic]: Plan and implement
  - worker reads spec + context artifacts
  - plans changes, implements, writes tests

Wave 2 [Deterministic]: Verify
  - run full test suite, lint, type-check
  - capture pass/fail output

Wave 3 [Agentic]: Fix failures (max 2 iterations)
  - worker reads failure output
  - diagnoses and fixes
  - re-runs verification

Wave 4 [Deterministic]: Deliver
  - format, commit, open PR
  -> human review
```

## Verification Loop Constraints

Cap agentic verification loops so the system does not spin indefinitely.

| Constraint | Recommended Default |
|-----------|---------------------|
| Max CI rounds per task | 2-3 |
| Local lint/type-check | Run before push |
| Test selection | Affected tests only, not full suite |
| Hard stop | After third attempt, escalate to human with diagnosis |

If a failure persists after two fix iterations, treat it as structural and escalate rather than retrying in place.

## Mapping To Claude Code And Codex

| Blueprint Step | Claude Code | Codex |
|---------------|-------------|-------|
| Deterministic nodes | Parent thread runs bash commands | Main thread runs commands |
| Agentic nodes | Subagent with `isolation: worktree` | Spawned worker thread |
| Verification gate | Parent checks subagent output and runs tests | Parent checks worker output |
| Human review | PR opened, lead thread reports to user | PR opened, session ends |

For the fuller harness architecture, including planner-generator-evaluator patterns, see `agents-subagents`.
