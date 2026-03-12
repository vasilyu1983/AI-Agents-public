# Agent Debugging Patterns

> Operational playbook for diagnosing and fixing agent failures — trace replay, failure classification, root cause analysis, and systematic debugging workflows.

**Freshness anchor:** January 2026 — covers OpenTelemetry 1.x, LangSmith v2, Langfuse 2.x, LangGraph runtime.

---

## Failure Classification Decision Tree

```
Agent failed or produced wrong output
│
├── Did the agent stop responding?
│   ├── YES → Timeout / Rate Limit / Crash
│   │   ├── Check: API response codes (429, 503, 500)
│   │   ├── Check: Token limit exceeded (context window overflow)
│   │   └── Check: Tool execution hung (external API timeout)
│   └── NO → Agent produced output
│       │
│       ├── Is the output factually wrong?
│       │   ├── YES → Hallucination
│       │   │   ├── Check: Was retrieval context relevant?
│       │   │   ├── Check: Did the model ignore provided context?
│       │   │   └── Check: Was the question outside training data?
│       │   └── NO → Output is factual but wrong action
│       │       │
│       │       ├── Did the agent call the wrong tool?
│       │       │   ├── YES → Tool Selection Error
│       │       │   │   ├── Check: Tool descriptions ambiguous
│       │       │   │   ├── Check: Too many tools available (>15)
│       │       │   │   └── Check: Missing tool for the task
│       │       │   └── NO → Right tool, wrong parameters
│       │       │       ├── Check: Parameter schema unclear
│       │       │       ├── Check: Required params missing
│       │       │       └── Check: Type coercion failure
│       │       │
│       │       └── Did the agent loop?
│       │           ├── YES → Loop Detection
│       │           │   ├── Check: Identical tool calls repeated
│       │           │   ├── Check: Error→retry→same error cycle
│       │           │   └── Check: Planning→replanning without action
│       │           └── NO → Logic / Reasoning Error
│       │               ├── Check: Multi-step plan went off track
│       │               ├── Check: Misinterpreted user intent
│       │               └── Check: Lost context mid-conversation
```

---

## Quick Reference: Failure Modes and Fixes

| Failure Mode | Symptom | Root Cause | Fix |
|---|---|---|---|
| Infinite loop | Same tool called 3+ times | No exit condition in agent logic | Add max iteration guard + loop detection |
| Context overflow | Truncated responses, missing info | Conversation history too long | Implement sliding window or summarization |
| Tool timeout | Agent hangs mid-execution | External API unresponsive | Add per-tool timeout (default 30s) |
| Hallucinated tool call | Agent invokes nonexistent tool | Tool list changed between turns | Pin tool definitions per session |
| Parameter drift | Wrong types in tool arguments | Schema mismatch or ambiguous names | Add Pydantic/Zod validation on tool inputs |
| Premature termination | Agent says "done" too early | Misclassified task as complete | Add completion verification step |
| Cascading error | One tool failure breaks chain | No error recovery between steps | Add per-step error handling with fallback |
| Rate limit cascade | Multiple 429s, then crash | Burst of parallel tool calls | Implement exponential backoff + concurrency limit |

---

## Trace Replay Debugging

### When to Use
- Use when: agent produced wrong output and you need to understand the step-by-step reasoning
- Use when: reproducing a failure reported by a user
- Use when: comparing a failing run against a known-good run

### OpenTelemetry Trace Analysis

```python
# Instrument agent with OpenTelemetry spans
from opentelemetry import trace

tracer = trace.get_tracer("agent.debugging")

def run_agent_step(step_input):
    with tracer.start_as_current_span("agent.step") as span:
        span.set_attribute("step.input_tokens", count_tokens(step_input))
        span.set_attribute("step.tool_name", step_input.get("tool", "none"))
        span.set_attribute("step.iteration", step_input.get("iteration", 0))

        result = execute_step(step_input)

        span.set_attribute("step.output_tokens", count_tokens(result))
        span.set_attribute("step.status", "success" if result.ok else "error")
        span.set_attribute("step.error_type", result.error_type or "none")
        return result
```

### Trace Analysis Checklist

- [ ] Export trace as JSON from collector (Jaeger, Zipkin, or Grafana Tempo)
- [ ] Identify the span where behavior diverged from expected
- [ ] Check span attributes for token counts (context overflow indicator)
- [ ] Compare tool call sequence against expected plan
- [ ] Look for retry spans (indicates transient failures)
- [ ] Check latency per span (identify bottleneck tools)
- [ ] Verify parent-child span relationships (correct nesting)

### LangSmith Debugging Workflow

| Step | Action | What to Look For |
|---|---|---|
| 1 | Open failing run in LangSmith UI | Red status indicators on steps |
| 2 | Expand each LLM call | Full prompt sent and response received |
| 3 | Check retrieval steps | Were correct documents retrieved? |
| 4 | Compare tool inputs/outputs | Did tool return expected format? |
| 5 | Inspect token usage per step | Approaching context limit? |
| 6 | Use "Compare" view | Diff against a successful run |
| 7 | Tag run for regression set | Add to golden test dataset |

### Langfuse Debugging Workflow

| Step | Action | What to Look For |
|---|---|---|
| 1 | Filter traces by error score | Focus on lowest-scoring runs |
| 2 | Open trace timeline view | Identify where the chain broke |
| 3 | Check generation details | Model, temperature, token counts |
| 4 | Review observation scores | Human or automated eval scores |
| 5 | Inspect event metadata | Custom attributes logged by agent |
| 6 | Export trace for local replay | Reproduce with identical inputs |

---

## Conversation Replay Patterns

### Deterministic Replay Setup

```python
# Save full conversation state for replay
import json
from datetime import datetime

class ConversationRecorder:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events = []

    def record(self, event_type: str, data: dict):
        self.events.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,  # "user_input", "llm_call", "tool_call", "tool_result"
            "data": data
        })

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump({
                "session_id": self.session_id,
                "events": self.events
            }, f, indent=2)

# Replay with mocked tool responses
class ConversationReplayer:
    def __init__(self, recording_path: str):
        with open(recording_path) as f:
            self.recording = json.load(f)
        self.tool_responses = self._extract_tool_responses()

    def _extract_tool_responses(self) -> dict:
        responses = {}
        for event in self.recording["events"]:
            if event["type"] == "tool_result":
                key = event["data"]["tool_call_id"]
                responses[key] = event["data"]["result"]
        return responses
```

### Replay Comparison Checklist

- [ ] Replay produces same tool call sequence
- [ ] If different: identify first divergence point
- [ ] Check if divergence is due to model non-determinism (set temperature=0)
- [ ] Check if divergence is due to changed tool responses
- [ ] Check if system prompt or tools changed between original and replay
- [ ] Document the delta for root cause analysis

---

## Log Analysis Patterns

### Structured Logging for Agents

```python
import structlog

logger = structlog.get_logger()

# Log every decision point
logger.info("agent.planning",
    task=user_query,
    available_tools=[t.name for t in tools],
    selected_plan=plan.steps,
    confidence=plan.confidence
)

logger.info("agent.tool_call",
    tool=tool_name,
    params=sanitized_params,  # redact PII
    attempt=retry_count,
    timeout_ms=timeout
)

logger.info("agent.tool_result",
    tool=tool_name,
    status="success" | "error",
    result_tokens=token_count,
    latency_ms=elapsed
)

logger.info("agent.step_complete",
    iteration=step_number,
    total_tokens_used=cumulative_tokens,
    remaining_budget=max_tokens - cumulative_tokens
)
```

### Log Grep Patterns

| What You're Looking For | grep/rg Pattern |
|---|---|
| All errors in a session | `rg "status.*error" --json \| jq '.session_id=="<id>"'` |
| Loop detection | `rg "agent.tool_call" \| sort \| uniq -c \| sort -rn` |
| Token budget exhaustion | `rg "remaining_budget" \| awk '$NF < 1000'` |
| Slow tools | `rg "latency_ms" \| awk '$NF > 5000'` |
| Rate limit hits | `rg "429\|rate.limit\|too.many.requests"` |
| Context window overflow | `rg "context_length_exceeded\|max_tokens"` |

---

## Step-Through Debugging Workflow

### Manual Step-Through Protocol

| Step | Action | Decision |
|---|---|---|
| 1 | Freeze agent at step N | Inspect full state before LLM call |
| 2 | Print the exact prompt being sent | Is context correct and complete? |
| 3 | Count tokens in prompt | Within model's context window? |
| 4 | Run LLM call in isolation | Does response make sense given prompt? |
| 5 | If tool call: validate parameters | Do params match tool schema? |
| 6 | Execute tool with validated params | Does tool return expected format? |
| 7 | Feed tool result back to agent | Does agent interpret result correctly? |
| 8 | Advance to step N+1 | Repeat until failure point found |

### Breakpoint Patterns

```python
# Add conditional breakpoints to agent loop
class DebuggableAgent:
    def __init__(self, agent, breakpoints=None):
        self.agent = agent
        self.breakpoints = breakpoints or {}

    async def run(self, input_msg):
        for step in self.agent.iterate(input_msg):
            # Break on specific tool
            if step.tool_name in self.breakpoints.get("tools", []):
                await self._debug_pause(step, "tool_breakpoint")

            # Break on high token usage
            if step.total_tokens > self.breakpoints.get("max_tokens", float("inf")):
                await self._debug_pause(step, "token_limit")

            # Break on Nth iteration
            if step.iteration >= self.breakpoints.get("max_iterations", float("inf")):
                await self._debug_pause(step, "iteration_limit")

            # Break on error
            if step.status == "error" and self.breakpoints.get("break_on_error", False):
                await self._debug_pause(step, "error")

    async def _debug_pause(self, step, reason):
        print(f"BREAKPOINT [{reason}] at step {step.iteration}")
        print(f"  Tool: {step.tool_name}")
        print(f"  Tokens used: {step.total_tokens}")
        print(f"  Last result: {step.last_result[:200]}")
        input("Press Enter to continue...")
```

---

## Root Cause Analysis Template

```
INCIDENT: [Brief description]
SEVERITY: [P0-P3]
SESSION ID: [trace/session identifier]

TIMELINE:
- [timestamp] Step N: [what happened]
- [timestamp] Step N+1: [what happened]
- [timestamp] Failure point: [what went wrong]

ROOT CAUSE:
- Category: [tool_error | hallucination | loop | timeout | logic_error]
- Specific cause: [detailed explanation]
- Contributing factors: [list]

FIX:
- Immediate: [what was done to resolve]
- Preventive: [what will prevent recurrence]
- Detection: [what monitoring/alert catches this faster]

REGRESSION TEST:
- Input: [the failing input]
- Expected: [correct behavior]
- Added to: [test suite name]
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|---|---|---|
| Logging only final output | Cannot trace intermediate failures | Log every LLM call + tool call + result |
| Retrying without classification | Infinite retry on permanent failures | Classify error as transient vs permanent first |
| Debugging in production | Risk of side effects, no reproducibility | Replay traces locally with mocked tools |
| Adding print statements | No structure, lost after session | Use structured logging with trace IDs |
| Ignoring token counts | Miss context overflow as root cause | Track cumulative tokens at every step |
| Testing with real APIs only | Flaky, slow, expensive | Mock tool responses for deterministic tests |
| No max iteration guard | Agent can loop forever | Hard limit of 10-25 iterations per task |
| Debugging the model instead of the prompt | Model behavior is a function of input | Focus on what the prompt/context contains |

---

## Cross-References

- `guardrails-implementation.md` — layer guardrails to prevent many failure modes
- `voice-multimodal-agents.md` — modality-specific debugging patterns
- `../ai-llm/references/structured-output-patterns.md` — output parsing failures
- `../ai-llm-inference/references/streaming-patterns.md` — mid-stream error handling
- `../ai-prompt-engineering/references/prompt-testing-ci-cd.md` — regression test infrastructure
