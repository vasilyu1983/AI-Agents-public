# Migration from Visual Workflow Tools (n8n, Langflow, Agent Builder)

## Table of Contents

- [When to Migrate](#when-to-migrate)
- [Migration Process](#migration-process)
- [n8n Node → Python Mapping](#n8n-node--python-mapping)
- [What Visual Tools Hide](#what-visual-tools-hide)
- [Common Gaps to Close](#common-gaps-to-close)
- [Before / After Example](#before--after-example)
- [Check](#check)

**Purpose.** Port a bot from a visual workflow tool (n8n, Langflow, OpenAI Agent Builder, CustomGPT-as-backend) to native Python without losing behavior or introducing regressions.

## When to Migrate

Migrate when any of the following are true:

- The workflow graph has grown past ~15 nodes and is hard to reason about
- You need proper unit tests, CI, and staged deployments
- You need observability deeper than the tool's built-in execution view
- Secrets are hardcoded in node config (Telegram bot tokens in HTTP URL fields are common)
- You need features the visual tool doesn't support: compliance filtering, conversation memory, rate limiting, structured logging
- You have multiple implementations (n8n + Agent Builder + CustomGPT) drifting from each other

Do not migrate just because "Python is better." If the n8n bot works, the ops team owns it, and it covers your needs, leave it alone.

## Migration Process

1. **Export all prompts verbatim.** n8n stores system prompts in Set/Config nodes as string values inside the workflow JSON. Extract them exactly — do not rewrite during migration. Rewriting mixes two risk sources (port correctness + prompt changes) and makes regressions impossible to attribute.

2. **Map every node to a Python function.** See [mapping table below](#n8n-node--python-mapping). Write the 1:1 port first, refactor after.

3. **Move secrets immediately.** Before porting any logic, grep the workflow JSON for tokens in URL fields, hardcoded API keys, and auth headers. Move them to env vars or a secret manager. This is the only step you should do before the 1:1 port — every other change waits.

4. **Identify what the workflow graph hides.** Dedup, channel routing, mirroring/logging, webhook handling, and retry logic are often embedded in the graph structure. Make them explicit Python modules.

5. **Extract integration contracts.** For every external API the workflow calls, document: URL pattern, auth method, payload shape, response parsing, retry/timeout. These become typed client methods.

6. **Merge multiple implementations.** If the bot exists as n8n + Agent Builder + CustomGPT, the Python version should absorb the best of all — n8n's channel logic, Agent Builder's guardrails, CustomGPT's prompt quality. Do a feature matrix before writing code.

7. **Add what visual tools couldn't.** Typical gaps: post-generation compliance filter, conversation memory, structured observability, rate limiting, input validation, graceful failure on non-critical paths. See [Common Gaps](#common-gaps-to-close).

8. **Run both in parallel behind a feature flag.** Route a small percentage of traffic to the Python version. Compare outputs on the same inputs. Only cut over when the diff is understood.

## n8n Node → Python Mapping

| n8n node | Python equivalent | Notes |
|----------|------------------|-------|
| Set / Config | Module-level constants or Pydantic `Settings` class | Extract string values exactly |
| IF / Switch | `if`/`elif` in a routing function, or a LangGraph conditional edge | Collapse multiple Switches into one router where possible |
| HTTP Request | `httpx.AsyncClient` method on a typed client | Add retry via `tenacity` or `httpx-retries` |
| Code (JavaScript) | Python function — port logic directly | Rare footgun: JS truthy/falsy ≠ Python |
| OpenAI Chat Model | `openai.AsyncOpenAI` or `anthropic.AsyncAnthropic` client | Add structured output via `response_format` or tool calls |
| Webhook trigger | FastAPI endpoint | Add signature verification |
| Schedule trigger | APScheduler, cron, or Temporal | Depends on reliability needs |
| Merge | `asyncio.gather` or sequential combine | Semantics differ — verify |
| Split In Batches | Async generator + semaphore | |
| Wait | `asyncio.sleep` | |
| Error Trigger / Catch | try/except with structured logging | Often absent in n8n workflows — add it |
| Credentials | Secret manager + env vars | Never hardcode |
| Function Item | Pure Python function taking the item dict | |
| Set node used for "memory" | Explicit state dict or Pydantic model | Make the state schema typed |

## What Visual Tools Hide

These are embedded in the workflow graph and become explicit modules in Python:

- **Deduplication.** Visual tools often dedup implicitly by event ID in a trigger. Port as Redis TTL keys at two levels: exact event ID (15-min TTL) and normalized text hash (8-sec TTL). In-memory dedup breaks on restart and doesn't scale across instances.
- **Channel routing.** The workflow graph encodes channel logic through node positioning. Extract as an explicit router module.
- **Mirroring / shadow logging.** A parallel branch that forwards messages to a monitoring channel (Ghost Scribe pattern) becomes an explicit async task, fire-and-forget with a metric.
- **Webhook signature verification.** Often skipped in visual tools. Add it in the FastAPI dependency.
- **Retry and backoff.** Visual tools retry with default settings. Python lets you configure exponential backoff with jitter and circuit breakers.

## Common Gaps to Close

Visual-tool bots that migrate to Python usually need these added:

- **Post-generation compliance filter.** Block investment advice, tipping-off language, unmasked PII before the response reaches the user. Regex for fast cases, LLM for ambiguous. Essential for regulated domains.
- **Conversation memory.** Visual tools store "last N messages" which is anti-pattern A1. Replace with typed fact extraction — see [`bot-memory-integration.md`](bot-memory-integration.md).
- **Structured observability.** JSON logs with `conversation_id` + `trace_id` on every line. Prometheus metrics for containment, escalation, latency, cost.
- **Rate limiting.** Per-user, per-channel, and global. Redis token bucket or `slowapi`.
- **Input validation.** Max length, encoding, null bytes, unicode tag-block stripping. Run before the LLM call.
- **Prompt injection defense.** See [`injection-and-jailbreak-defense.md`](injection-and-jailbreak-defense.md). Spotlighting, canary tokens, tool-output sanitization.
- **Silent-failure accounting.** Non-critical paths (Telegram mirror, analytics write) should fail without breaking the main path — but emit a metric so silent failures are visible.

## Before / After Example

### Before — n8n HTTP Request node (Telegram send)

```json
{
  "parameters": {
    "url": "https://api.telegram.org/bot1234567890:AAH-HARDCODED-TOKEN/sendMessage",
    "method": "POST",
    "body": "={{ { chat_id: $json.chat_id, text: $json.text } }}"
  }
}
```

Problems: token in URL field, no retry, no timeout, no error handling, no metric, crashes the whole workflow if the send fails.

### After — Python async client

```python
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

log = structlog.get_logger()

class TelegramClient:
    def __init__(self, token: str, client: httpx.AsyncClient):
        self._token = token
        self._client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def _post(self, method: str, payload: dict) -> dict:
        url = f"https://api.telegram.org/bot{self._token}/{method}"
        r = await self._client.post(url, json=payload, timeout=10.0)
        r.raise_for_status()
        return r.json()

    async def send_message(self, chat_id: int, text: str) -> Optional[dict]:
        """Ghost Scribe mirror — fire-and-forget. Returns None on failure."""
        try:
            return await self._post("sendMessage", {"chat_id": chat_id, "text": text})
        except Exception as e:
            log.warn("telegram.send_failed", chat_id=chat_id, error=str(e))
            metrics.telegram_send_failed_total.inc()
            return None  # non-critical path, do not propagate
```

Gains: token from env/secret manager, typed client, retry with backoff, timeout, structured log on failure, metric for silent-failure accounting, documented non-critical semantics.

## Check

Migration is complete when: (1) parallel-running diff between n8n and Python versions shows no unexplained behavior delta over a representative traffic sample, (2) every secret is in a secret manager (zero matches for known token prefixes in the codebase), (3) the Python version has tests for every critical path (routing, compliance filter, escalation, dedup), (4) the n8n workflow is disabled or reduced to a trigger-only proxy, and (5) observability gives you better visibility than n8n's execution view did.
