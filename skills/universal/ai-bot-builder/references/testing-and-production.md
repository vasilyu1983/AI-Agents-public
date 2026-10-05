# Testing And Production

## Table of Contents

- [Test Pyramid for Bots](#test-pyramid-for-bots)
- [Test Surfaces](#test-surfaces)
- [Observability](#observability)
- [Handoffs](#handoffs)

Use this file when the bot moves from prototype to a maintained system — whether built with LangGraph, plain async Python, or any other framework.

## Test Pyramid for Bots

Structure tests in three tiers. Run fast tiers in CI on every push; slow tiers on demand or nightly.

### Tier 1: Unit Tests (deterministic, fast, no external deps)

Test every pure node function independently. Nodes that are `(state_dict) → partial_state_dict` are trivially testable.

**What to test:**
- Greeting detector: regex matches for all greeting patterns, rejects greetings-with-support-signals
- Fast-path overrides: "speak to human", "connect to human", Telegram password reset
- Quality gate: length threshold (160 chars), weak-signal phrases ("not sure", "can't find")
- Compliance filter: investment advice, tipping-off language, unmasked PII (email, phone, card)
- Envelope normalization: SunCo webhook parsing, gate logic for all filtered event types
- Input validation: empty, too long, null bytes, encoding
- PII scrubber: ordering matters — card regex before phone regex (phone patterns are greedy)

**Example:**
```python
from bot.nodes.greeting import greeting_detector
from bot.models import Decision

def test_greeting_with_support_signal_is_not_greeting():
    result = greeting_detector({"text": "Hi, my card is blocked"})
    assert result["is_greeting_only"] is False
    assert "decision" not in result
```

### Tier 2: Integration Tests (mocked HTTP, no real APIs)

Use `respx` (for httpx) or `responses` (for requests) to mock external service responses. Test request shapes, auth headers, retry behavior, and error handling.

**What to test:**
- LLM client: request payload structure, JSON schema in structured output, response parsing, retry on 500
- Ticketing client: message send with idempotency key, passControl payload, auth headers
- Telegram client: Ghost Scribe prefix format, returns None on failure (non-critical path)
- Conversation history: verify history messages are included in LLM request for support tiers

**Example:**
```python
@respx.mock
@pytest.mark.asyncio
async def test_retries_on_500(client):
    route = respx.post(OPENAI_URL)
    route.side_effect = [
        httpx.Response(500), httpx.Response(500),
        httpx.Response(200, json=success_response),
    ]
    result = await client.spam_filter("Hello", PROMPT)
    assert result.status == "CLEAN"
    assert route.call_count == 3
```

### Tier 3: Golden Eval Harness (real conversations, split deterministic/LLM)

Build a golden test suite from real reviewed conversations (support specialist feedback, 02_examples.md, QA screenshots). Store as JSON fixtures with expected decision + route.

**Split eval into two files:**

1. **Deterministic eval** (no API key needed, runs in CI):
   - Test greeting detection against golden greeting cases
   - Test fast-path overrides against golden escalation/Telegram cases
   - Verify support questions don't false-positive as greetings or fast-paths

2. **LLM eval** (requires OPENAI_API_KEY, runs on demand):
   - Test router classification against golden cases (expected route + confidence)
   - Test support tier answers for non-empty, grounded responses
   - Skip with `@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"))`

**Golden case format:**
```json
{
  "id": "not_in_scope_telegram_password",
  "input": "How do I reset my Telegram password?",
  "expected_decision": "NOT_IN_SCOPE",
  "expected_route": "NOT_IN_SCOPE",
  "fast_path": true,
  "description": "Telegram password reset — caught by fast-path"
}
```

**Rules:**
- Treat LLM eval failures as signals to investigate, not hard blockers — model behavior drifts
- Re-baseline golden cases after prompt changes
- Include negative examples from reviewer feedback (bot mistakes that should not recur)
- Run deterministic eval in CI; LLM eval before deployments

### Rubric-graded revision loop (outcome verification at runtime)

Golden evals catch regressions offline. For bots where a single bad answer is expensive (compliance, financial guidance, irreversible actions), add a *runtime* outcome check before the answer leaves the bot.

The pattern (Anthropic "verify with outcome grader" cookbook, 2026): a separate, isolated grader agent scores the draft answer against an explicit rubric; if it fails, the bot revises and re-grades, capped at a small `max_iterations` (2–3). Keep the grader's prompt and context isolated from the generating agent — a grader that sees the generator's chain-of-thought rubber-stamps it.

- Use only when output quality is load-bearing and a wrong answer is costly — it doubles (or triples) token cost and latency per turn.
- Rubric must be concrete and checkable ("cites a KB section ID", "does not state a number not present in retrieved context"), not "is helpful".
- Cap iterations and fail closed: if still failing at `max_iterations`, hand off to a human rather than ship the last attempt.
- This is a runtime guard, not a substitute for the golden eval harness — keep both.
- Evidence grade C (vendor cookbook, no independent benchmark). Validate the iteration cap against your own latency budget before adopting.

## Test Surfaces

- State transitions and routing logic
- Tool-call nodes (mocked at the HTTP layer)
- Retry and fallback behavior (circuit breaker activation, fallback responses)
- Checkpoint and resume paths
- Approval paths (human-in-the-loop gates)
- Compliance filter (investment advice, tipping-off, PII leakage)
- PII scrubber ordering (card before phone — phone regex eats card numbers)
- Channel mirroring (Ghost Scribe sends correct prefix, doesn't block on failure)

## Observability

- Trace node execution, tool calls, state transitions, and failure reasons.
- Keep graph-level IDs (trace_id, conversation_id) so a run can be replayed or audited later.
- Log every decision to an analytics table: conversation_id, message_id, decision, route, confidence, tier_used, processing_ms.
- Use structlog with JSON output — every log line includes conversation_id + trace_id for correlation.
- Prometheus metrics: `bot_messages_total`, `bot_handoff_total`, `bot_response_duration_seconds`, `bot_openai_call_duration_seconds`.
- Pair LangGraph-specific traces with the broader guidance in `qa-observability`.

## Handoffs

- Product UX and streaming belong in `software-ai-integration`.
- Tool surface design belongs in `agents-mcp`.
- Eval packs and regressions belong in `qa-agent-testing`.
